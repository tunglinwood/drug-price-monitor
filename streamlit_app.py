"""
化合物监控系统 - Streamlit Dashboard
交互式 Web 界面
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
if not require_login():
    st.stop()

# 显示用户信息
show_user_info()

# 用户已登录，继续加载 Dashboard

# 标题
st.title("🧪 化合物监控系统")
st.markdown(f"**更新时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Load version info
try:
    version_url = "https://raw.githubusercontent.com/tunglinwood/drug-price-monitor/main/version.json?t=" + str(int(datetime.now().timestamp()))
    version_data = pd.read_json(version_url, typ='series')
    st.info(f"📌 **Data Version:** {version_data.get('version', 'unknown')} | **Compounds:** {version_data.get('compounds', '?')}")
except:
    pass

# 加载数据
@st.cache_data(ttl=300)  # Cache for 5 minutes max
def load_data(_cache_buster):
    """加载最新的监控数据"""
    import os
    import sys
    
    # ALWAYS load from CSV - it's the source of truth
    # Local JSON file is outdated
    try:
        import pandas as pd
        import time
        # Aggressive cache-busting
        cache_buster = f"{int(time.time())}_{int(time.time()*1000) % 10000}"
        url = f"https://raw.githubusercontent.com/tunglinwood/drug-price-monitor/main/compounds.csv?cb={cache_buster}"
        df = pd.read_csv(url)
        
        # 转换为 Dashboard 格式
        compounds = []
        for idx, row in df.iterrows():
            notes = row.get('Notes', '')
            # Determine status from notes emoji
            if '✅' in str(notes):
                status = 'found'
            elif '❌ 已终止' in str(notes):
                status = 'discontinued'
            elif '❌' in str(notes):
                status = 'not_found'
            else:
                status = 'partial'
            
            # Get Stage value with explicit fallback
            stage_val = row.get('Stage', '未知')
            if stage_val is None or (isinstance(stage_val, float) and str(stage_val) == 'nan'):
                stage_val = '未知'
            
            # Get chemical structure data from CSV (case-sensitive column names)
            smiles_val = row.get('SMILES', '')
            inchikey_val = row.get('InChIKey', '')
            iupac_val = row.get('IUPAC', '')
            clinical_trials_val = row.get('clinical_trials', '')
            
            compounds.append({
                "name": row.get('chem_name', ''),
                "company": row.get('Company', ''),
                "stage": stage_val,
                "status": status,
                "notes": str(notes),
                "clinical_stage": stage_val,
                "smiles": str(smiles_val) if smiles_val else '',
                "inchikey": str(inchikey_val) if inchikey_val else '',
                "iupac": str(iupac_val) if iupac_val else '',
                "clinical_trials_raw": str(clinical_trials_val) if clinical_trials_val else '',
                "pubchem_cid": None,
                "molecular_weight": None,
                "papers_count": 0,
                "patents_count": 0,
            })
        
        found_count = sum(1 for c in compounds if c['status'] == 'found')
        not_found_count = sum(1 for c in compounds if c['status'] == 'not_found')
        discontinued_count = sum(1 for c in compounds if c['status'] == 'discontinued')
        
        return {
            "summary": {
                "total_compounds": len(compounds),
                "found": found_count,
                "not_found": not_found_count,
                "discontinued": discontinued_count,
                "success_rate": f"{(found_count + sum(1 for c in compounds if c['status'] == 'partial'))/len(compounds)*100:.1f}%",
                "with_papers": 0,
                "with_patents": 0,
                "last_update": datetime.now().isoformat()
            },
            "compounds": compounds
        }
    except Exception as e:
        st.error(f"加载 GitHub 数据失败：{e}")
        return None

# Cache buster - changes every hour to force periodic reload
cache_buster = datetime.now().strftime('%Y-%m-%d-%H')
dashboard = load_data(cache_buster)

if dashboard is None:
    st.error("❌ 未找到监控数据，请先运行监控系统")
    st.stop()

# 侧边栏
st.sidebar.title("🔧 控制面板")

# 数据刷新
if st.sidebar.button("🔄 刷新数据"):
    st.cache_data.clear()
    cache_buster = datetime.now().strftime('%Y-%m-%d-%H-%M')
    dashboard = load_data(cache_buster)
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
col1, col2, col3 = st.columns(3)

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

# 筛选器
st.markdown("### 🔍 筛选化合物")
col1, col2, col3 = st.columns(3)

with col1:
    search_term = st.text_input("🔎 搜索名称", "")

with col2:
    status_filter = st.selectbox(
        "状态",
        ["全部", "found", "partial", "not_found", "discontinued"]
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
    status_emoji = {"found": "✅", "partial": "⚠️", "not_found": "❌", "discontinued": "❌"}
    df['status_icon'] = df['status'].map(status_emoji)
    
    # Ensure clinical_stage column exists and has data
    # The compounds list already has 'clinical_stage' from CSV 'Stage' column
    if 'clinical_stage' not in df.columns:
        df['clinical_stage'] = '未知'
    else:
        # Fill any None/NaN values with '未知'
        df['clinical_stage'] = df['clinical_stage'].fillna('未知')
        # Convert empty strings to '未知'
        df.loc[df['clinical_stage'] == '', 'clinical_stage'] = '未知'
    
    if 'pubchem_cid' not in df.columns:
        df['pubchem_cid'] = None
    if 'molecular_weight' not in df.columns:
        df['molecular_weight'] = None
    if 'papers_count' not in df.columns:
        df['papers_count'] = 0
    if 'notes' not in df.columns:
        df['notes'] = ''
    # smiles, inchikey, iupac, clinical_trials_raw are populated from CSV in compounds list
    
    # Format clinical trials as clickable hyperlinks
    def format_trials(trials_str):
        if not trials_str or trials_str == '' or 'No trials' in trials_str or 'pending' in trials_str.lower():
            return trials_str if trials_str else 'No trials registered'
        
        # Parse trial data (format: NCT_ID|Phase|Status|URL;NCT_ID|Phase|Status|URL)
        trials = trials_str.split(';')
        formatted = []
        for trial in trials:
            parts = trial.split('|')
            if len(parts) >= 4:
                nct_id, phase, status, url = parts[0], parts[1], parts[2], parts[3]
                formatted.append(f'<a href="{url}" target="_blank">🔬 {nct_id}</a> ({phase}, {status})')
            elif len(parts) == 1:
                formatted.append(trial)
        
        # Show first 3 trials + count if more
        if len(formatted) > 3:
            return f"{'<br>'.join(formatted[:3])}<br><em>...and {len(formatted)-3} more trials</em>"
        return '<br>'.join(formatted) if formatted else 'No trials registered'
    
    df['clinical_trials'] = df['clinical_trials_raw'].apply(format_trials)
    
    # 显示表格 - include clinical trials column with hyperlinks
    display_df = df[['status_icon', 'name', 'clinical_stage', 'clinical_trials', 'smiles', 'inchikey', 'iupac', 'notes']].copy()
    display_df.columns = ['状态', '化合物名称', '临床阶段', '临床试验', 'SMILES', 'InChIKey', 'IUPAC', '备注']
    
    # Convert DataFrame to HTML with clickable links
    st.markdown(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)
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
