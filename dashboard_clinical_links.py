# 化合物列表
st.markdown(f"### 📋 化合物列表 ({len(filtered)}/{len(compounds)})")

# 创建 DataFrame
df = pd.DataFrame(filtered)

if not df.empty:
    # 状态图标映射
    status_emoji = {"success": "✅", "partial": "⚠️", "not_found": "❌", "discontinued": "❌"}
    df['status_icon'] = df['status'].map(status_emoji)
    
    # 为每个化合物添加临床阶段链接
    def get_clinical_trial_link(row):
        """获取临床试验链接"""
        trial_links = row.get('clinical_trial_links', {})
        
        # 优先使用具体 NCT 编号
        nct_links = {k: v for k, v in trial_links.items() if k.startswith('📋')}
        if nct_links:
            return list(nct_links.values())[0]
        
        # 否则使用 ClinicalTrials.gov 搜索
        return trial_links.get('ClinicalTrials.gov Search', '')
    
    df['clinical_stage_link'] = df.apply(get_clinical_trial_link, axis=1)
    
    # 显示表格
    display_df = df[['status_icon', 'name', 'clinical_stage', 'clinical_stage_link', 'pubchem_cid', 'molecular_weight', 'papers_count']].copy()
    display_df.columns = ['状态', '化合物名称', '临床阶段', '临床阶段链接', 'PubChem CID', '分子量', '论文数']
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "状态": st.column_config.TextColumn(width="small"),
            "化合物名称": st.column_config.TextColumn(width="medium"),
            "临床阶段": st.column_config.LinkColumn(
                "临床阶段",
                width="medium",
                help="点击打开临床试验页面"
            ),
            "临床阶段链接": None,  # 隐藏列
            "PubChem CID": st.column_config.NumberColumn(format="%d", width="medium"),
            "分子量": st.column_config.NumberColumn(format="%.1f", width="small"),
            "论文数": st.column_config.NumberColumn(format="%d", width="small"),
        }
    )
else:
    st.warning("⚠️ 没有符合条件的化合物")
