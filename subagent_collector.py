"""
Subagent 结果自动收集器
监听 Subagent 完成事件，自动提取结果并保存
"""
import json
from datetime import datetime
from pathlib import Path

class SubagentResultCollector:
    """Subagent 结果收集器"""
    
    def __init__(self, results_dir: str = "subagent_results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
    
    def save_result(self, compound_name: str, result_data: dict):
        """保存单个 Subagent 结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{compound_name.replace('/', '_')}_{timestamp}.json"
        filepath = self.results_dir / filename
        
        # 添加元数据
        result_data['_metadata'] = {
            'compound': compound_name,
            'search_timestamp': timestamp,
            'collected_at': datetime.now().isoformat()
        }
        
        # 保存结果
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 已保存 {compound_name} 结果：{filepath}")
        return filepath
    
    def get_all_results(self) -> list:
        """获取所有 Subagent 结果"""
        results = []
        
        for filepath in sorted(self.results_dir.glob("*.json")):
            with open(filepath, 'r', encoding='utf-8') as f:
                result = json.load(f)
                results.append(result)
        
        return results
    
    def clear_old_results(self, keep_days: int = 7):
        """清理旧结果（保留最近 7 天）"""
        import time
        
        cutoff_time = time.time() - (keep_days * 24 * 60 * 60)
        
        for filepath in self.results_dir.glob("*.json"):
            if filepath.stat().st_mtime < cutoff_time:
                filepath.unlink()
                print(f"🗑️ 已删除旧结果：{filepath}")


# 示例：如何从 OpenClaw 消息中提取结果
def extract_result_from_message(message_content: str, compound_name: str):
    """
    从 OpenClaw 消息中提取 Subagent 结果
    
    参数:
        message_content: Subagent 完成消息的完整内容
        compound_name: 化合物名称
    
    返回:
        dict: 解析后的结果
    """
    import re
    
    # 提取 JSON 部分
    json_match = re.search(r'```json\s*(.*?)\s*```', message_content, re.DOTALL)
    
    if json_match:
        result_json = json_match.group(1)
        result_data = json.loads(result_json)
        return result_data
    else:
        # 如果没有 JSON 块，尝试直接解析
        try:
            result_data = json.loads(message_content)
            return result_data
        except:
            print(f"❌ 无法解析结果：{compound_name}")
            return None


if __name__ == "__main__":
    # 测试
    collector = SubagentResultCollector()
    
    # 示例结果
    test_result = {
        "compound": "TEST-001",
        "company": "测试公司",
        "status": "partial",
        "papers": [{"pmid": "12345", "title": "Test Paper"}],
        "patents": [],
        "clinical_trials": []
    }
    
    collector.save_result("TEST-001", test_result)
    
    # 获取所有结果
    all_results = collector.get_all_results()
    print(f"\n📊 共收集 {len(all_results)} 个结果")
