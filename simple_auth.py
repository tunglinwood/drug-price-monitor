"""
简化认证模块
Simple Authentication Module
使用 Streamlit session state，不依赖外部认证库
"""

from datetime import datetime
from pathlib import Path

import bcrypt
import streamlit as st
import yaml
from yaml.loader import SafeLoader

# 配置文件路径
AUTH_CONFIG_PATH = Path(__file__).parent / "auth_config.yaml"

# 角色权限定义
ROLE_PERMISSIONS = {
    "admin": {
        "can_view_dashboard": True,
        "can_export_data": True,
        "can_view_logs": True,
        "can_manage_users": True,
        "can_launch_searches": True,
        "can_delete_data": True,
    },
    "researcher": {
        "can_view_dashboard": True,
        "can_export_data": True,
        "can_view_logs": True,
        "can_manage_users": False,
        "can_launch_searches": True,
        "can_delete_data": False,
    },
    "guest": {
        "can_view_dashboard": True,
        "can_export_data": False,
        "can_view_logs": False,
        "can_manage_users": False,
        "can_launch_searches": False,
        "can_delete_data": False,
    },
}


def load_auth_config():
    """加载认证配置"""
    if not AUTH_CONFIG_PATH.exists():
        return None

    try:
        with open(AUTH_CONFIG_PATH) as f:
            config = yaml.load(f, Loader=SafeLoader)
        return config
    except Exception as e:
        st.error(f"配置文件加载失败：{str(e)}")
        return None


def check_password(password: str, hashed: str) -> bool:
    """验证密码"""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:  # noqa: BLE001
        return False


def get_user_permissions(role: str) -> dict:
    """获取角色权限"""
    return ROLE_PERMISSIONS.get(role, {})


def has_permission(permission: str) -> bool:
    """检查当前用户是否有权限"""
    if not st.session_state.get("logged_in", False):
        return False

    role = st.session_state.get("user_role", "guest")
    permissions = get_user_permissions(role)

    return permissions.get(permission, False)


def login(username: str, password: str) -> tuple:
    """
    简单的登录函数

    Returns:
        (success: bool, message: str, role: str)
    """
    config = load_auth_config()
    if not config:
        return False, "配置文件加载失败", ""

    credentials = config.get("credentials", {})
    usernames = credentials.get("usernames", {})

    if username not in usernames:
        return False, "用户名不存在", ""

    user_data = usernames[username]
    stored_hash = user_data.get("password", "")

    if check_password(password, stored_hash):
        # 登录成功
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.session_state["user_name"] = user_data.get("name", username)
        st.session_state["user_email"] = user_data.get("email", "")
        st.session_state["user_role"] = user_data.get("role", "guest")
        st.session_state["login_time"] = datetime.now()

        return True, "登录成功", user_data.get("role", "guest")
    else:
        return False, "密码错误", ""


def logout():
    """登出"""
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.session_state["user_name"] = None
    st.session_state["user_role"] = None
    st.rerun()


def show_login_form():
    """显示登录表单"""
    st.markdown("""
    # 🔐 化合物监控系统登录
    **Compound Price Monitoring System**
    """)

    with st.form("login_form"):
        username = st.text_input("用户名 / Username")
        password = st.text_input("密码 / Password", type="password")
        submit = st.form_submit_button("登录 / Login", type="primary")

        if submit:
            if not username or not password:
                st.error("请输入用户名和密码")
                return False

            success, message, role = login(username, password)

            if success:
                st.success(f"✅ 登录成功！欢迎，{st.session_state['user_name']}!")
                st.info(f"🎯 角色：{role}")
                return True
            else:
                st.error(f"❌ {message}")
                return False

    return False


def require_login():
    """检查登录状态，未登录则显示登录表单"""
    if not st.session_state.get("logged_in", False):
        if show_login_form():
            st.rerun()
        return False
    return True


def show_user_info():
    """在侧边栏显示用户信息"""
    if st.session_state.get("logged_in", False):
        st.sidebar.success(f"👤 欢迎，{st.session_state.get('user_name', 'User')}!")
        st.sidebar.info(f"🎯 角色：{st.session_state.get('user_role', 'guest')}")

        if st.sidebar.button("🚪 登出 / Logout"):
            logout()
