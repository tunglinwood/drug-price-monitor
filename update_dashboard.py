#!/usr/bin/env python3
"""
Dashboard 更新脚本 - 合并所有 Subagent 结果
Dashboard Update Script - Merge all Subagent results

在所有 Subagent 完成后运行此脚本
Run this script AFTER all subagents complete

使用方法:
    python3 update_dashboard.py
"""
import json
from datetime import datetime
from pathlib import Path

def main():
    """主函数"""
    print("="*60)
    print("🔄 更新 Dashboard - 合并所有 Subagent 结果")
    print("="*60)
    
    # 加载现有 Dashboard
    dashboard_path = Path("monitor_output/latest_dashboard.json")
    
    if not dashboard_path.exists():
        print(f"❌ Dashboard 文件不存在：{dashboard_path}")
        return
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        dashboard = json.load(f)
    
    # 扫描 subagent_results 目录
    results_dir = Path("subagent_results")
    
    if not results_dir.exists():
        print(f"❌ Subagent 结果目录不存在：{results_dir}")
        return
    
    # 读取所有最新的 Subagent 结果
    updated_count = 0
    for result_file in results_dir.glob("*.json"):
        try:
            with open(result_file, 'r', encoding='utf-8') as f:
                result = json.load(f)
            
            # 提取化合物名称
            compound_name = result.get('compound', '')
            
            if not compound_name:
                continue
            
            # 在 Dashboard 中查找并更新
            for i, comp in enumerate(dashboard['compounds']):
                if comp.get('name') == compound_name or compound_name in comp.get('name', ''):
                    # 更新化合物数据
                    dashboard['compounds'][i].update(result)
                    updated_count += 1
                    print(f"✅ 更新：{compound_name}")
                    break
            
        except Exception as e:
            print(f"⚠️  读取失败 {result_file.name}: {str(e)}")
    
    # 更新摘要
    dashboard['summary']['last_update'] = datetime.now().isoformat()
    dashboard['summary']['last_full_refresh'] = datetime.now().isoformat()
    
    # 保存更新后的 Dashboard
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        json.dump(dashboard, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"✅ Dashboard 更新完成！")
    print(f"📊 更新了 {updated_count} 个化合物")
    print(f"📄 Dashboard 文件：{dashboard_path}")
    print(f"{'='*60}")
    
    # 提示 Git 提交
    print(f"\n📝 下一步:")
    print(f"   git add -A")
    print(f"   git commit -m 'Daily refresh: {datetime.now().strftime('%Y-%m-%d')}'")
    print(f"   git push origin main")
    print()


if __name__ == "__main__":
    main()
