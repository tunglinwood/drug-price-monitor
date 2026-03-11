"""
OpenClaw Subagent 自动触发器
当 Subagent 完成时，自动调用此脚本更新 Dashboard
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# 导入收集器
from subagent_collector import SubagentResultCollector


def on_subagent_complete(compound_name: str, result_data: dict):
    """
    Subagent 完成时的回调函数
    
    参数:
        compound_name: 化合物名称
        result_data: Subagent 返回的结果数据
    """
    print(f"\n🎯 Subagent 完成：{compound_name}")
    
    # 1. 保存结果
    collector = SubagentResultCollector()
    filepath = collector.save_result(compound_name, result_data)
    
    # 2. 更新 Dashboard
    print("\n🔄 更新 Dashboard...")
    os.system("python update_dashboard_from_subagents.py")
    
    # 3. 自动提交到 Git（如果在 Git 环境中）
    if Path(".git").exists():
        print("\n📤 提交到 Git...")
        os.system(f"git add subagent_results/{filepath.name}")
        os.system(f"git add monitor_output/latest_dashboard.json")
        os.system(f"git commit -m '🤖 Auto: {compound_name} 搜索结果'")
        
        # 自动推送（如果配置了远程）
        if os.getenv("AUTO_PUSH", "false").lower() == "true":
            print("\n🚀 推送到 GitHub...")
            os.system("git push origin main")
            print("✅ 已推送到 GitHub，Streamlit Cloud 将自动重新部署")
    
    print(f"\n✅ {compound_name} 处理完成！")


def main():
    """主函数 - 从命令行参数或环境变量读取结果"""
    
    # 从命令行参数读取
    if len(sys.argv) >= 3:
        compound_name = sys.argv[1]
        result_json = sys.argv[2]
        
        try:
            result_data = json.loads(result_json)
            on_subagent_complete(compound_name, result_data)
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败：{e}")
            sys.exit(1)
    
    # 从环境变量读取（GitHub Actions 模式）
    elif os.getenv("SUBAGENT_COMPOUND") and os.getenv("SUBAGENT_RESULT"):
        compound_name = os.getenv("SUBAGENT_COMPOUND")
        result_json = os.getenv("SUBAGENT_RESULT")
        
        try:
            result_data = json.loads(result_json)
            on_subagent_complete(compound_name, result_data)
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败：{e}")
            sys.exit(1)
    
    else:
        print("用法:")
        print("  python auto_integration.py <化合物名称> '<JSON 结果>'")
        print("\n或使用环境变量:")
        print("  export SUBAGENT_COMPOUND=MDR-001")
        print("  export SUBAGENT_RESULT='{...}'")
        print("  python auto_integration.py")
        sys.exit(1)


if __name__ == "__main__":
    main()
