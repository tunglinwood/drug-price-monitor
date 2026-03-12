# 🌙 夜间自动搜索系统

## ✅ 已完成的配置

### 文件结构

```
drug-price-api/
├── compound_queue.txt          # 化合物队列文件 ⭐
├── process_queue.py            # 队列处理器脚本 ⭐
├── overnight_search.log        # 搜索日志 (自动生成)
└── subagent_results/           # Subagent 结果 (自动生成)
```

### Cron Job 配置

```bash
# 每天凌晨 2 点自动运行
0 2 * * * cd /root/.openclaw/workspace/drug-price-api && python3 process_queue.py >> overnight_search.log 2>&1
```

---

## 📋 化合物队列

### 待搜索 (10 个)

**P1 优先级 (3 个):**
- HS-10501 (翰森制药，I 期)
- MWN109 (民为生物，I 期)
- BGM0504 (博瑞生物，I 期)

**P2 优先级 (7 个):**
- HS-10501-2 (翰森制药)
- ZT006 (质态生物)
- SYH2067 (石药集团)
- BPYT-01 (百极优棠)
- RGT-274 (齐鲁锐格)
- RO7795081/CT-996 (Carmot)
- 司美格鲁肽片 (诺和诺德)

### 已完成 (7 个)

- MDR-001 ✅
- SAL0112 ✅
- HSK34890 ✅
- VCT220/CX11 ✅
- HRS-7535 ✅
- APH01727 ✅
- NN9487 ✅

---

## 🚀 使用方法

### 查看队列

```bash
cat compound_queue.txt
```

### 添加新化合物

```bash
# 编辑队列文件，添加到对应优先级部分
nano compound_queue.txt

# 示例：添加新化合物
echo "NEW-COMPOUND" >> compound_queue.txt
```

### 标记已完成

```bash
# 在 compound_queue.txt 中，在化合物前加 # 注释
# NEW-COMPOUND  →  # NEW-COMPOUND
```

### 手动触发搜索

```bash
# 立即运行（不等待 cron）
cd ~/.openclaw/workspace/drug-price-api
python3 process_queue.py
```

### 查看日志

```bash
# 实时查看
tail -f overnight_search.log

# 查看最后 50 行
tail -n 50 overnight_search.log

# 搜索错误
grep "ERROR" overnight_search.log
```

### 查看 Subagent 结果

```bash
# 查看所有结果文件
ls -la subagent_results/

# 查看特定化合物结果
cat subagent_results/HS-10501_*.json | jq
```

---

## ⏰ 执行时间

| 项目 | 时间 |
|------|------|
| **启动时间** | 每天 02:00 (GMT+8) |
| **化合物间隔** | 10 分钟 |
| **10 个化合物** | 约 100 分钟 |
| **预计完成** | 03:40 (GMT+8) |
| **Dashboard 更新** | 03:45 (GMT+8) |

---

## 📊 自动化流程

```
02:00 → Cron 触发 process_queue.py
  ↓
02:00 → 读取 compound_queue.txt
  ↓
02:00 → Subagent 1: HS-10501
  ↓ (10 分钟)
02:10 → Subagent 2: MWN109
  ↓ (10 分钟)
02:20 → Subagent 3: BGM0504
  ↓ ...
03:40 → ✅ 所有搜索完成
  ↓
自动 → 保存结果到 subagent_results/
  ↓
自动 → 更新 Dashboard
  ↓
自动 → Git 提交
  ↓
自动 → GitHub 推送
  ↓
自动 → Streamlit 重新部署
  ↓
03:45 → ✅ Dashboard 显示最新数据
```

---

## 🔧 管理命令

### 暂停自动搜索

```bash
# 注释掉 cron job
crontab -e
# 在行首加 #
# 0 2 * * * cd /root/.openclaw/workspace/drug-price-api && python3 process_queue.py >> overnight_search.log 2>&1
```

### 恢复自动搜索

```bash
# 移除 cron job 行首的 #
crontab -e
```

### 清空队列

```bash
# 备份当前队列
cp compound_queue.txt compound_queue.txt.backup

# 清空队列
> compound_queue.txt
```

### 测试运行

```bash
# 测试模式（只搜索前 2 个化合物）
python3 -c "
import process_queue
process_queue.DELAY_SECONDS = 60  # 1 分钟间隔
compounds = process_queue.load_compound_queue()[:2]
print(f'测试化合物：{compounds}')
"
```

---

## 📈 监控和告警

### 检查是否运行

```bash
# 查看 cron 日志
grep CRON /var/log/syslog | grep process_queue

# 查看进程
ps aux | grep process_queue
```

### 检查 Dashboard 更新

```bash
# 访问 Dashboard
https://tunglinwood-drug-price-monitor-g2n6ki5f2v8xczavexxlvd.streamlit.app

# 查看最后更新时间
cat monitor_output/latest_dashboard.json | jq '.summary.last_update'
```

### 设置告警（可选）

```bash
# 如果搜索失败，发送邮件（需要配置邮件）
# 添加到 process_queue.py 末尾
```

---

## 🐛 故障排除

### Q: Cron 没有执行？

**A:** 检查 cron 服务状态
```bash
systemctl status cron
```

### Q: Subagent 启动失败？

**A:** 检查 OpenClaw 会话
```bash
# 确保有活跃的 OpenClaw 会话
openclaw status
```

### Q: Dashboard 没有更新？

**A:** 检查 Git 推送
```bash
# 查看提交历史
git log --oneline -5

# 手动推送
git add .
git commit -m "Manual update"
git push
```

### Q: 日志文件太大？

**A:** 清理旧日志
```bash
# 保留最近 7 天
find . -name "*.log" -mtime +7 -delete
```

---

## 📞 快速参考

| 操作 | 命令 |
|------|------|
| **查看队列** | `cat compound_queue.txt` |
| **查看日志** | `tail -f overnight_search.log` |
| **手动运行** | `python3 process_queue.py` |
| **查看结果** | `ls subagent_results/` |
| **查看 Dashboard** | 访问 Streamlit URL |
| **暂停自动** | `crontab -e` 注释掉 |
| **恢复自动** | `crontab -e` 取消注释 |

---

## 🎉 完成检查清单

- [x] ✅ compound_queue.txt 已创建
- [x] ✅ process_queue.py 已创建
- [x] ✅ Cron job 已设置
- [x] ✅ 权限已配置
- [ ] ⏳ 第一次自动运行（明早 02:00）
- [ ] ⏳ 验证 Dashboard 更新

---

**系统已就绪！明早 02:00 自动开始搜索！** 🚀
