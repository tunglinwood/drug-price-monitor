"""
Drug Price API - 化合物自动询价服务
基于 ChemPrice + PubChem
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
import time

from .config import settings
from .pubchem import name_to_smiles, search_compound
from .chemprice_service import chemprice_service

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="Drug Price API",
    description="自动查询化合物价格的 API 服务 - 基于 ChemPrice (Molport, ChemSpace, MCule)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 数据模型 ====================

class PriceRequest(BaseModel):
    """价格查询请求"""
    compound: str = Field(..., description="化合物名称或 SMILES", examples=["Aspirin", "Paracetamol"])
    sources: Optional[List[str]] = Field(
        default=None, 
        description="指定查询平台：molport, chemspace, mcule (默认全部)",
        examples=[["molport", "chemspace"]]
    )


class PriceResult(BaseModel):
    """单条价格结果"""
    smiles: str
    source: str
    supplier: str
    purity: str
    amount: float
    measure: str
    price_usd: float
    currency: str = "USD"


class PriceResponse(BaseModel):
    """价格查询响应"""
    compound: str
    smiles: str
    name: Optional[str] = None
    molecular_weight: Optional[float] = None
    formula: Optional[str] = None
    prices: List[PriceResult]
    best_price: Optional[PriceResult] = None
    total_results: int
    query_time_ms: float


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str
    api_keys_configured: Dict[str, str]


class CompoundInfo(BaseModel):
    """化合物信息"""
    cid: int
    name: str
    smiles: str
    synonyms: List[str]
    molecular_weight: Optional[float]
    formula: Optional[str]


# ==================== API Endpoints ====================

@app.get("/", tags=["Root"])
async def root():
    """根路径 - API 信息"""
    return {
        "name": "Drug Price API",
        "version": "1.0.0",
        "description": "化合物自动询价服务",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """健康检查 - 检查 API key 配置状态"""
    api_keys = chemprice_service.check_api_keys()
    configured_count = sum(1 for v in api_keys.values() if v == "已配置")
    
    return HealthResponse(
        status="healthy" if configured_count > 0 else "no_api_keys",
        version="1.0.0",
        api_keys_configured=api_keys
    )


@app.post("/api/v1/price", response_model=PriceResponse, tags=["Price"])
async def get_price(request: PriceRequest):
    """
    查询化合物价格
    
    支持输入化合物名称或 SMILES 格式
    自动从 Molport, ChemSpace, MCule 三个平台获取价格
    """
    start_time = time.time()
    
    # 1. 确定 SMILES
    smiles = None
    
    # 先尝试作为 SMILES 解析（简单检查）
    if '(' in request.compound or ')' in request.compound or '[' in request.compound:
        smiles = request.compound
    else:
        # 作为化合物名称查询 PubChem
        smiles = name_to_smiles(request.compound)
    
    if not smiles:
        raise HTTPException(
            status_code=404,
            detail=f"无法找到化合物：{request.compound}。请检查名称或使用 SMILES 格式"
        )
    
    # 2. 获取化合物信息
    compound_info = search_compound(request.compound)
    
    # 3. 查询价格
    prices_data = chemprice_service.get_prices([smiles])
    
    # 4. 转换为响应模型
    prices = [
        PriceResult(
            smiles=p["smiles"],
            source=p["source"],
            supplier=p["supplier"],
            purity=str(p["purity"]),
            amount=float(p["amount"]) if p["amount"] else 0,
            measure=p["measure"],
            price_usd=float(p["price_usd"]) if p["price_usd"] else 0,
            currency=p["currency"]
        )
        for p in prices_data
    ]
    
    # 5. 找出最优价格
    best_price = None
    if prices:
        best = min(prices, key=lambda x: x.price_usd)
        best_price = best
    
    query_time = (time.time() - start_time) * 1000
    
    return PriceResponse(
        compound=request.compound,
        smiles=smiles,
        name=compound_info.get("name") if compound_info else None,
        molecular_weight=compound_info.get("molecular_weight") if compound_info else None,
        formula=compound_info.get("formula") if compound_info else None,
        prices=prices,
        best_price=best_price,
        total_results=len(prices),
        query_time_ms=round(query_time, 2)
    )


@app.get("/api/v1/price/{compound}", response_model=PriceResponse, tags=["Price"])
async def get_price_simple(compound: str):
    """
    简化版价格查询（GET 请求）
    
    示例：/api/v1/price/Aspirin
    """
    request = PriceRequest(compound=compound)
    return await get_price(request)


@app.get("/api/v1/compound/{query}", response_model=CompoundInfo, tags=["Compound"])
async def get_compound_info(query: str):
    """
    查询化合物信息（不查价格）
    
    从 PubChem 获取化合物基本信息
    """
    info = search_compound(query)
    
    if not info:
        raise HTTPException(
            status_code=404,
            detail=f"无法找到化合物：{query}"
        )
    
    return CompoundInfo(**info)


@app.get("/api/v1/smiles/{compound_name}", tags=["Compound"])
async def convert_to_smiles(compound_name: str):
    """
    将化合物名称转换为 SMILES 格式
    """
    smiles = name_to_smiles(compound_name)
    
    if not smiles:
        raise HTTPException(
            status_code=404,
            detail=f"无法转换化合物名称：{compound_name}"
        )
    
    return {
        "compound": compound_name,
        "smiles": smiles
    }


# ==================== 启动事件 ====================

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    logger.info("Drug Price API 启动中...")
    chemprice_service.initialize()
    logger.info("ChemPrice 服务初始化完成")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
