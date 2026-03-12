# 🔐 认证系统设置指南

## 📋 概述

已为 Streamlit Dashboard 添加了完整的认证和权限控制系统。

**功能:**
- ✅ 用户名/密码登录
- ✅ 角色权限管理 (管理员/研究员/访客)
- ✅ 会话管理 (30 天 cookie)
- ✅ bcrypt 密码哈希
- ✅ 兼容 Streamlit Cloud

---

## 🚀 快速开始

### 步骤 1: 生成密码哈希

```bash
cd ~/.openclaw/workspace/drug-price-api

# 为每个用户生成哈希密码
python3 hash_password.py AdminPassword123
python3 hash_password.py ResearcherPass456
python3 hash_password.py GuestPass789
```

**输出示例:**
```
✅ 密码哈希生成成功！

原始密码：AdminPassword123

bcrypt 哈希:
$2b$12$KIXxJQk8Z9vZ8Z9vZ8Z9vO...
```

---

### 步骤 2: 配置用户账户

编辑 `auth_config.yaml`:

```yaml
credentials:
  usernames:
    admin:
      email: admin@drugmonitor.com
      name: System Administrator
      password: $2b$12$KIXxJQk8Z9vZ8Z9vZ8Z9vO...  # 粘贴你的哈希
      role: admin
    
    researcher1:
      email: researcher1@company.com
      name: Research User 1
      password: $2b$12$...  # 粘贴你的哈希
      role: researcher
    
    guest:
      email: guest@company.com
      name: Guest User
      password: $2b$12$...  # 粘贴你的哈希
      role: guest
```

---

### 步骤 3: 设置 Cookie 密钥

在 `auth_config.yaml` 中设置随机密钥:

```yaml
cookie:
  expiry_days: 30
  key: 随机字符串_至少_32_字符_长
  name: drug_monitor_cookie
```

**生成随机密钥:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

### 步骤 4: 提交到 GitHub

```bash
cd ~/.openclaw/workspace/drug-price-api

# ⚠️ 重要：不要提交 auth_config.yaml 到公开仓库!
# 添加 .gitignore 规则
echo "auth_config.yaml" >> .gitignore
echo "*.env" >> .gitignore

# 提交其他文件
git add -A
git commit -m "feat: 添加认证和权限控制系统"
git push
```

---

### 步骤 5: 配置 Streamlit Cloud

1. **访问:** https://share.streamlit.io

2. **选择你的应用:** drug-price-monitor

3. **添加 Secrets:**
   - Settings → Secrets
   - 上传 `auth_config.yaml` (从本地复制内容)

4. **重新部署:**
   - 点击 "Clear cache and redeploy"

---

## 🎯 角色权限

### Admin (管理员)
- ✅ 查看 Dashboard
- ✅ 导出数据 (CSV/JSON)
- ✅ 查看日志
- ✅ 管理用户
- ✅ 启动搜索任务
- ✅ 删除数据

### Researcher (研究员)
- ✅ 查看 Dashboard
- ✅ 导出数据 (CSV/JSON)
- ✅ 查看日志
- ✅ 启动搜索任务
- ❌ 管理用户
- ❌ 删除数据

### Guest (访客)
- ✅ 查看 Dashboard
- ❌ 导出数据
- ❌ 查看日志
- ❌ 启动搜索
- ❌ 管理用户
- ❌ 删除数据

---

## 📱 使用方式

### 登录流程

1. **访问 Dashboard:**
   ```
   https://tunglinwood-drug-price-monitor-g2n6ki5f2v8xczavexxlvd.streamlit.app
   ```

2. **输入用户名和密码**

3. **点击 "Login"**

4. **成功登录后:**
   - 侧边栏显示用户名和角色
   - 根据权限显示/隐藏功能
   - 30 天内自动登录 (cookie)

---

### 添加新用户

**方法 1: 编辑配置文件**

```yaml
# auth_config.yaml
credentials:
  usernames:
    newuser:
      email: newuser@company.com
      name: New User
      password: $2b$12$...  # 哈希密码
      role: researcher
```

**方法 2: 使用管理员界面** (开发中)

```python
# 管理员可以添加用户
if has_permission('can_manage_users'):
    # 显示添加用户表单
    ...
```

---

## 🔒 安全最佳实践

### 1. 保护配置文件

```bash
# 不要提交到 Git
echo "auth_config.yaml" >> .gitignore

# 设置文件权限 (Linux/Mac)
chmod 600 auth_config.yaml
```

### 2. 使用强密码

```bash
# 生成安全密码
python3 -c "import secrets; print(secrets.token_urlsafe(16))"
```

### 3. 定期更新密码

```bash
# 每 90 天更新一次
# 1. 生成新哈希
python3 hash_password.py NewSecurePassword

# 2. 更新 auth_config.yaml

# 3. 重新部署
git push
```

### 4. 监控登录日志

```python
# 在 auth.py 中添加日志
import logging
logging.info(f"User {username} logged in at {datetime.now()}")
```

---

## 🐛 故障排除

### Q: 登录失败 "Username not found"

**A:** 检查 `auth_config.yaml`:
```yaml
# 确保用户名正确
usernames:
  admin:  # ← 这里是用户名
    email: admin@drugmonitor.com
```

### Q: 登录后立即登出

**A:** 检查 cookie 配置:
```yaml
cookie:
  key: 确保密钥至少 32 字符
  expiry_days: 30
```

### Q: 权限不生效

**A:** 检查角色定义:
```yaml
admin:
  role: admin  # ← 确保角色名正确
```

### Q: Streamlit Cloud 部署失败

**A:** 
1. 确保 `streamlit-authenticator` 在 requirements.txt
2. 在 Streamlit Cloud Secrets 中上传 auth_config.yaml
3. 清除缓存并重新部署

---

## 📊 高级功能

### 自定义权限

编辑 `auth.py`:

```python
ROLE_PERMISSIONS = {
    'admin': {
        'can_view_dashboard': True,
        'can_export_data': True,
        'can_view_logs': True,
        'can_manage_users': True,
        'can_launch_searches': True,
        'can_delete_data': True,
        'can_edit_compounds': True,  # 新权限
    },
    # ...
}
```

### 添加登录日志

```python
# 在 auth.py 中添加
def log_login(username, status):
    with open('login.log', 'a') as f:
        f.write(f"{datetime.now()} - {username} - {status}\n")
```

### 双因素认证 (2FA)

```python
# 使用 pyotp 实现 TOTP
import pyotp

totp = pyotp.TOTP('base32secret...')
otp_code = totp.now()
```

---

## 🎊 完成检查清单

- [ ] 生成所有用户密码哈希
- [ ] 配置 auth_config.yaml
- [ ] 设置 cookie 密钥
- [ ] 添加 auth_config.yaml 到 .gitignore
- [ ] 测试本地登录
- [ ] 上传配置到 Streamlit Cloud Secrets
- [ ] 重新部署 Dashboard
- [ ] 测试所有角色权限
- [ ] 分享登录信息给团队

---

**认证系统已就绪！** 🔐

有任何问题随时询问！🚀
