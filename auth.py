"""
认证和权限管理模块
Authentication and Authorization Module

功能:
- 用户登录/登出
- 角色权限控制
- 会话管理
"""
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
import bcrypt

# 配置文件路径
AUTH_CONFIG_PATH = Path(__file__).parent / "auth_config.yaml"

# 角色权限定义
ROLE_PERMISSIONS = {
    'admin': {
        'can_view_dashboard': True,
        'can_export_data': True,
        'can_view_logs': True,
        'can_manage_users': True,
        'can_launch_searches': True,
        'can_delete_data': True,
    },
    'researcher': {
        'can_view_dashboard': True,
        'can_export_data': True,
        'can_view_logs': True,
        'can_manage_users': False,
        'can_launch_searches': True,
        'can_delete_data': False,
    },
    'guest': {
        'can_view_dashboard': True,
        'can_export_data': False,
        'can_view_logs': False,
        'can_manage_users': False,
        'can_launch_searches': False,
        'can_delete_data': False,
    }
}


def load_auth_config():
    """加载认证配置"""
    if not AUTH_CONFIG_PATH.exists():
        st.error(f"❌ 认证配置文件不存在：{AUTH_CONFIG_PATH}")
        return None
    
    with open(AUTH_CONFIG_PATH, 'r') as f:
        config = yaml.load(f, Loader=SafeLoader)
    
    return config


def check_password(password: str, hashed: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def get_user_permissions(role: str) -> dict:
    """获取角色权限"""
    return ROLE_PERMISSIONS.get(role, {})


def has_permission(permission: str) -> bool:
    """检查当前用户是否有权限"""
    if 'authentication' not in st.session_state:
        return False
    
    if not st.session_state['authentication_status']:
        return False
    
    role = st.session_state['user_info'].get('role', 'guest')
    permissions = get_user_permissions(role)
    
    return permissions.get(permission, False)


def require_permission(permission: str):
    """权限检查装饰器"""
    if not has_permission(permission):
        st.error(f"🔒 权限不足：需要 {permission} 权限")
        st.stop()


def login_page(authenticator):
    """登录页面"""
    st.markdown("""
    # 🔐 化合物监控系统登录
    
    **Compound Price Monitoring System**
    
    请使用您的账号登录
    """)
    
    try:
        authentication_status, name, user_info = authenticator.login('Login', 'main')
        
        if authentication_status:
            # 登录成功
            st.session_state['user_info'] = user_info
            authenticator.logout('Logout', 'sidebar')
            st.sidebar.success(f"👤 欢迎，{name}!")
            st.sidebar.info(f"🎯 角色：{user_info.get('role', 'guest')}")
            return True
        
        elif authentication_status == False:
            st.error('用户名或密码错误')
        elif authentication_status == None:
            st.warning('请输入用户名和密码')
        
        return False
    
    except Exception as e:
        st.error(f"登录失败：{str(e)}")
        return False


def check_auth():
    """检查认证状态"""
    if 'authentication' not in st.session_state:
        # 加载认证配置
        config = load_auth_config()
        if not config:
            return False
        
        # 创建认证器
        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days'],
        )
        
        st.session_state['authenticator'] = authenticator
        return False
    
    return st.session_state.get('authentication_status', False)


def get_current_user():
    """获取当前用户信息"""
    if not check_auth():
        return None
    
    return st.session_state.get('user_info', {})


def get_current_role():
    """获取当前用户角色"""
    user = get_current_user()
    return user.get('role', 'guest') if user else 'guest'
