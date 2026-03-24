"""
化合物监控系统 - Streamlit Dashboard
交互式 Web 界面 - 支持层级 JSON 数据
带简单认证
"""
import streamlit as st
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

# 导入简单认证模块
from simple_auth import require_login, show_user_info, has_permission

# 页面配置
st.set_page_config(
    page_title="GLP-1 化合物监控系统",
    page_icon="🧪",
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
        margin-bottom: 10px;
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
    .status-verified { color: #28a745; }
    .status-pending { color: #ffc107; }
    .status-early { color: #6c757d; }
    .status-terminated { color: #dc3545; }
    .status-approved { color: #007bff; }
    .data-quality-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    .badge-verified { background-color: #28a745; color: white; }
    .badge-partial { background-color: #ffc107; color: black; }
    .badge-pending { background-color: #6c757d; color: white; }
</style>
""", unsafe_allow_html=True)

# ========== 认证检查 ==========
if not require_login():
    st.stop()

# 显示用户信息
show_user_info()

# 用户已登录，继续加载 Dashboard

# 标题
st.title("🧪 GLP-1 化合物监控系统")
st.markdown(f"**更新时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Display data version info
if 'data_loaded_at' in st.session_state:
    st.info(f"📊 **Data Loaded:** {st.session_state['data_loaded_at']} | **Git Commit:** `{st.session_state.get('git_commit', 'Unknown')}`")

# 加载数据
@st.cache_data
def load_data():
    """加载最新的监控数据 from JSON"""
    import os
    
    # 尝试从本地文件加载（本地开发）
    json_path = Path('compounds.json')
    if json_path.exists():
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"加载 JSON 数据失败：{e}")
            return None
    
    # 尝试从 GitHub 加载（Streamlit Cloud）- with cache-busting
    try:
        import requests
        import time
        # Add timestamp to prevent caching
        url = f"https://raw.githubusercontent.com/tunglinwood/drug-price-monitor/main/compounds.json?t={int(time.time())}"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            # Store metadata for display
            st.session_state['data_loaded_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            st.session_state['git_commit'] = data.get('metadata', {}).get('git_commit', 'Unknown')
            return data
        else:
            st.error(f"从 GitHub 加载失败：{response.status_code}")
            return None
    except Exception as e:
        st.error(f"加载 GitHub 数据失败：{e}")
        return None

dashboard = load_data()

if dashboard is None:
    st.error("❌ 未找到监控数据，请先运行监控系统")
    st.stop()

# 提取化合物列表
compounds = dashboard.get('compounds', [])
metadata = dashboard.get('metadata', {})
summary = dashboard.get('summary', {})

# 侧边栏
st.sidebar.title("🔧 控制面板")

# 数据刷新
if st.sidebar.button("🔄 刷新数据"):
    st.cache_data.clear()
    dashboard = load_data()
    if dashboard:
        compounds = dashboard.get('compounds', [])
        metadata = dashboard.get('metadata', {})
        summary = dashboard.get('summary', {})
    st.rerun()

# 导出选项
st.sidebar.markdown("### 📤 导出")
if st.sidebar.button("📊 导出 JSON"):
    json_str = json.dumps(dashboard, indent=2, ensure_ascii=False)
    st.sidebar.download_button(
        label="📥 下载 JSON",
        data=json_str,
        file_name=f"compounds_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

# 摘要卡片
st.markdown("### 📊 监控摘要")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{summary.get('verified_trials', 0)}</div>
        <div class="metric-label">✅ 已验证试验</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{summary.get('pending_verification', 0)}</div>
        <div class="metric-label">⏳ 待验证</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{summary.get('no_trials_early_stage', 0)}</div>
        <div class="metric-label">❌ 早期阶段</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{summary.get('terminated', 0)}</div>
        <div class="metric-label">⚠️ 已终止</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    total = len(compounds)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total}</div>
        <div class="metric-label">📋 总化合物</div>
    </div>
    """, unsafe_allow_html=True)

# 筛选器
st.markdown("### 🔍 筛选化合物")
col1, col2, col3 = st.columns(3)

with col1:
    search_term = st.text_input("🔎 搜索名称", "")

with col2:
    data_quality_filter = st.selectbox(
        "数据质量",
        ["全部", "verified", "partial", "pending_verification"]
    )

with col3:
    stage_filter = st.selectbox(
        "临床阶段",
        ["全部", "Phase 3", "Phase 2", "Phase 1", "Approved", "Terminated", "Preclinical", "Early stage"]
    )

# 应用筛选
filtered = compounds

if search_term:
    filtered = [c for c in filtered if search_term.lower() in c.get('chem_name', '').lower() or search_term.lower() in c.get('company', '').lower()]

if data_quality_filter != "全部":
    filtered = [c for c in filtered if c.get('data_quality') == data_quality_filter]

if stage_filter != "全部":
    filtered = [c for c in filtered if stage_filter.lower() in c.get('stage', '').lower()]

# 化合物列表
st.markdown(f"### 📋 化合物列表 ({len(filtered)}/{len(compounds)})")

if not filtered:
    st.warning("⚠️ 没有符合条件的化合物")
else:
    # 创建 DataFrame 用于显示
    table_data = []
    for comp in filtered:
        # 数据质量徽章
        quality = comp.get('data_quality', 'pending')
        if quality == 'verified':
            quality_badge = '<span class="data-quality-badge badge-verified">✅ VERIFIED</span>'
        elif quality == 'partial':
            quality_badge = '<span class="data-quality-badge badge-partial">⚠️ PARTIAL</span>'
        else:
            quality_badge = '<span class="data-quality-badge badge-pending">⏳ PENDING</span>'
        
        # 临床试验数量
        trials = comp.get('clinical_trials', [])
        trial_count = f"🔬 {len(trials)} trials" if trials else "❌ No trials"
        
        # 关键发现（截断）
        key_findings = comp.get('key_findings', '')[:80] + '...' if len(comp.get('key_findings', '')) > 80 else comp.get('key_findings', '')
        
        table_data.append({
            "状态": quality_badge,
            "化合物名称": comp.get('chem_name', ''),
            "公司": comp.get('company', ''),
            "临床阶段": comp.get('stage', ''),
            "临床试验": trial_count,
            "关键发现": key_findings
        })
    
    df = pd.DataFrame(table_data)
    
    # 显示表格（支持 HTML）
    st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)

# 详细信息
st.markdown("### 🔬 详细信息")

if len(filtered) > 0:
    # 选择化合物
    compound_names = [c.get('chem_name', '') for c in filtered]
    selected_name = st.selectbox("选择化合物查看详情", compound_names)
    
    # 找到选中的化合物
    selected = next((c for c in filtered if c.get('chem_name') == selected_name), None)
    
    if selected:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**化合物名称:** {selected.get('chem_name', '')}")
            
            # 数据质量
            quality = selected.get('data_quality', 'pending')
            if quality == 'verified':
                st.markdown("**数据质量:** ✅ VERIFIED")
            elif quality == 'partial':
                st.markdown("**数据质量:** ⚠️ PARTIAL")
            else:
                st.markdown("**数据质量:** ⏳ PENDING")
            
            st.markdown(f"**临床阶段:** {selected.get('stage', '')}")
            st.markdown(f"**公司:** {selected.get('company', '')}")
            
            # 化学标识符
            chem = selected.get('chemical_identifiers', {})
            if chem.get('pubchem_cid'):
                st.markdown(f"**PubChem CID:** [{chem.get('pubchem_cid')}](https://pubchem.ncbi.nlm.nih.gov/compound/{chem.get('pubchem_cid')})")
            if chem.get('molecular_weight'):
                st.markdown(f"**分子量:** {chem.get('molecular_weight')}")
        
        with col2:
            # 临床试验
            trials = selected.get('clinical_trials', [])
            if trials:
                st.markdown(f"**🏥 临床试验 ({len(trials)}):**")
                for trial in trials:
                    trial_id = trial.get('trial_id', '')
                    phase = trial.get('phase', '')
                    status = trial.get('status', '')
                    url = trial.get('url', '')
                    if url:
                        st.markdown(f"- [{trial_id}]({url}) ({phase}, {status})")
                    else:
                        st.markdown(f"- {trial_id} ({phase}, {status})")
            else:
                st.markdown("**🏥 临床试验:** ❌ No registered trials")
            
            # PubMed 论文
            papers = selected.get('pubmed_papers', [])
            if papers:
                st.markdown(f"**📄 PubMed 论文 ({len(papers)}):**")
                for paper in papers:
                    pmid = paper.get('pmid', '')
                    title = paper.get('title', '')
                    year = paper.get('year', '')
                    if pmid:
                        st.markdown(f"- [{title}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/) ({year})")
                    else:
                        st.markdown(f"- {title} ({year})")
        
        # 关键发现
        key_findings = selected.get('key_findings', '')
        if key_findings:
            st.markdown(f"**💡 关键发现:**")
            st.info(key_findings)
        
        # 备注
        notes = selected.get('notes', '')
        if notes:
            st.markdown(f"**📝 备注:**")
            st.write(notes)

# 页脚
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: #666; font-size: 12px;'>
        GLP-1 化合物监控系统 v2.0 | 最后更新：{metadata.get('last_updated', '未知')} | 数据源：{metadata.get('extraction_method', 'two_step_extraction')}
    </div>
    """,
    unsafe_allow_html=True
)
