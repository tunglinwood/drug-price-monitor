"""
化合物监控系统 - Streamlit Dashboard
交互式 Web 界面
带认证和权限控制
"""
import streamlit as st
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

# 导入认证模块
from auth import check_auth, login_page, has_permission, get_current_user, get_current_role

# 页面配置
st.set_page_config(
    page_title="化合物监控系统 - 登录",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .metric-value {
        font-size: 36px;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 14px;
        color: #666;
    }
    .status-success { color: #28a745; }
    .status-warning { color: #ffc107; }
    .status-error { color: #dc3545; }
    .compound-row {
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        background-color: #f8f9fa;
    }
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 40px;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ========== 认证检查 ==========
if not check_auth():
    # 显示登录页面
    config = load_auth_config()
    if config:
        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days'],
        )
        st.session_state['authenticator'] = authenticator
        
        if login_page(authenticator):
            st.rerun()
    else:
        st.error("认证配置错误，请联系管理员")
    st.stop()

# 用户已登录，继续加载 Dashboard
st.session_state['page_title'] = "化合物监控系统"

# 标题
st.title("🧪 化合物监控系统")
st.markdown(f"**更新时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 加载数据
@st.cache_data
def load_data():
    """加载最新的监控数据"""
    import os
    
    # 尝试从本地文件加载（本地开发）
    if os.path.exists('monitor_output/latest_dashboard.json'):
        try:
            with open('monitor_output/latest_dashboard.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"加载本地数据失败：{e}")
    
    # 尝试从 GitHub 加载（Streamlit Cloud）
    try:
        import pandas as pd
        url = "https://raw.githubusercontent.com/tunglinwood/drug-price-monitor/main/compounds.csv"
        df = pd.read_csv(url)
        
        # 转换为 Dashboard 格式
        compounds = []
        for _, row in df.iterrows():
            compounds.append({
                "name": row.get('chem_name', ''),
                "status": "partial" if row.get('SMILES') else "not_found",
                "clinical_stage": row.get('Stage', '未知'),
                "pubchem_cid": None,
                "molecular_weight": None,
                "papers_count": 0,
                "patents_count": 0,
            })
        
        return {
            "summary": {
                "total_compounds": len(compounds),
                "found": sum(1 for c in compounds if c['status'] == 'success'),
                "not_found": sum(1 for c in compounds if c['status'] == 'not_found'),
                "success_rate": f"{sum(1 for c in compounds if c['status'] != 'not_found')/len(compounds)*100:.1f}%",
                "with_papers": 0,
                "with_patents": 0,
                "last_update": datetime.now().isoformat()
            },
            "compounds": compounds
        }
    except Exception as e:
        st.error(f"加载 GitHub 数据失败：{e}")
        return None

dashboard = load_data()

if dashboard is None:
    st.error("❌ 未找到监控数据，请先运行监控系统")
    st.stop()

# 侧边栏
st.sidebar.title("🔧 控制面板")

# 数据刷新
if st.sidebar.button("🔄 刷新数据"):
    st.cache_data.clear()
    dashboard = load_data()
    st.rerun()

# 导出选项
st.sidebar.markdown("### 📤 导出")
if st.sidebar.button("📊 导出 CSV"):
    # 转换 DataFrame
    df = pd.DataFrame(dashboard['compounds'])
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    st.sidebar.download_button(
        label="📥 下载 CSV",
        data=csv,
        file_name=f"compounds_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

if st.sidebar.button("📄 导出 JSON"):
    json_str = json.dumps(dashboard, indent=2, ensure_ascii=False)
    st.sidebar.download_button(
        label="📥 下载 JSON",
        data=json_str,
        file_name=f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

# 摘要卡片
st.markdown("### 📊 监控摘要")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{dashboard['summary']['total_compounds']}</div>
        <div class="metric-label">总化合物</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: #28a745;">{dashboard['summary']['found']}</div>
        <div class="metric-label">找到信息</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: #dc3545;">{dashboard['summary']['not_found']}</div>
        <div class="metric-label">未找到</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{dashboard['summary']['success_rate']}</div>
        <div class="metric-label">成功率</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    papers = dashboard['summary'].get('with_papers', 0)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: #17a2b8;">{papers}</div>
        <div class="metric-label">📄 有论文</div>
    </div>
    """, unsafe_allow_html=True)

# 筛选器
st.markdown("### 🔍 筛选化合物")
col1, col2, col3 = st.columns(3)

with col1:
    search_term = st.text_input("🔎 搜索名称", "")

with col2:
    status_filter = st.selectbox(
        "状态",
        ["全部", "success", "partial", "not_found"]
    )

with col3:
    stage_filter = st.selectbox(
        "临床阶段",
        ["全部", "临床 III 期", "临床 II 期", "临床 I 期", "临床前", "未知"]
    )

# 应用筛选
compounds = dashboard['compounds']
filtered = compounds

if search_term:
    filtered = [c for c in filtered if search_term.lower() in c['name'].lower()]

if status_filter != "全部":
    filtered = [c for c in filtered if c['status'] == status_filter]

if stage_filter != "全部":
    filtered = [c for c in filtered if c.get('clinical_stage') == stage_filter]

# 化合物列表
st.markdown(f"### 📋 化合物列表 ({len(filtered)}/{len(compounds)})")

# 创建 DataFrame
df = pd.DataFrame(filtered)

if not df.empty:
    # 状态图标映射
    status_emoji = {"success": "✅", "partial": "⚠️", "not_found": "❌"}
    df['status_icon'] = df['status'].map(status_emoji)
    
    # 显示表格
    display_df = df[['status_icon', 'name', 'clinical_stage', 'pubchem_cid', 'molecular_weight', 'papers_count']].copy()
    display_df.columns = ['状态', '化合物名称', '临床阶段', 'PubChem CID', '分子量', '论文数']
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "状态": st.column_config.TextColumn(width="small"),
            "化合物名称": st.column_config.TextColumn(width="medium"),
            "临床阶段": st.column_config.TextColumn(width="medium"),
            "PubChem CID": st.column_config.NumberColumn(format="%d", width="medium"),
            "分子量": st.column_config.NumberColumn(format="%.1f", width="small"),
            "论文数": st.column_config.NumberColumn(format="%d", width="small")
        }
    )
else:
    st.warning("⚠️ 没有符合条件的化合物")

# 详细信息
st.markdown("### 🔬 详细信息")

if len(filtered) > 0:
    # 选择化合物
    compound_names = [c['name'] for c in filtered]
    selected_name = st.selectbox("选择化合物查看详情", compound_names)
    
    # 找到选中的化合物
    selected = next((c for c in filtered if c['name'] == selected_name), None)
    
    if selected:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**化合物名称:** {selected['name']}")
            st.markdown(f"**状态:** {selected.get('status_emoji', '')} {selected['status']}")
            
            if selected.get('clinical_stage'):
                st.markdown(f"**临床阶段:** {selected['clinical_stage']}")
            
            if selected.get('pubchem_cid'):
                cid = selected['pubchem_cid']
                st.markdown(f"**PubChem CID:** [{cid}](https://pubchem.ncbi.nlm.nih.gov/compound/{cid})")
            
            if selected.get('molecular_weight'):
                st.markdown(f"**分子量:** {selected['molecular_weight']}")
        
        with col2:
            # 论文信息
            if selected.get('papers') and len(selected['papers']) > 0:
                st.markdown("**📄 相关论文:**")
                for paper in selected['papers']:
                    st.markdown(f"- {paper.get('title', 'N/A')}")
                    st.markdown(f"  - *{paper.get('journal', 'N/A')}* ({paper.get('year', 'N/A')})")
                    if paper.get('url'):
                        st.markdown(f"  - [链接]({paper['url']})")
            
            # 供应商链接
            if selected.get('supplier_urls'):
                st.markdown("**🏪 供应商链接:**")
                for supplier, url in selected['supplier_urls'].items():
                    st.markdown(f"- {supplier}: [访问]({url})")
        
        # 完整 JSON 数据
        with st.expander("📄 查看原始 JSON 数据"):
            st.json(selected)

# 自动刷新选项
st.sidebar.markdown("### ⚙️ 设置")
auto_refresh = st.sidebar.checkbox("自动刷新 (每 5 分钟)", value=False)

if auto_refresh:
    import time
    time.sleep(300)
    st.rerun()

# 页脚
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 12px;'>
        化合物监控系统 v1.0 | 最后更新：{last_update}
    </div>
    """.format(last_update=dashboard['summary'].get('last_update', '未知')),
    unsafe_allow_html=True
)
