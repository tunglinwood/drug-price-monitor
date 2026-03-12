#!/usr/bin/env python3
"""
密码哈希生成器
Password Hash Generator for Streamlit Authenticator

使用方法:
    python3 hash_password.py your_password

输出:
    bcrypt 哈希密码，复制到 auth_config.yaml
"""
import sys
import bcrypt

def hash_password(password: str) -> str:
    """生成 bcrypt 哈希密码"""
    # 生成盐值并哈希密码
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def main():
    if len(sys.argv) < 2:
        print("❌ 用法：python3 hash_password.py <你的密码>")
        print("\n示例:")
        print("  python3 hash_password.py MySecurePassword123")
        sys.exit(1)
    
    password = sys.argv[1]
    
    # 生成哈希
    hashed = hash_password(password)
    
    print("="*60)
    print("✅ 密码哈希生成成功！")
    print("="*60)
    print(f"\n原始密码：{password}")
    print(f"\nbcrypt 哈希:")
    print(hashed)
    print("\n" + "="*60)
    print("📝 使用方法:")
    print("  1. 复制上面的哈希值")
    print("  2. 打开 auth_config.yaml")
    print("  3. 替换对应用户的 password 字段")
    print("="*60)

if __name__ == "__main__":
    main()
