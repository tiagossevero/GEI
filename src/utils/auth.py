"""
Módulo de Autenticação
Gerencia autenticação e controle de acesso ao dashboard
"""

import streamlit as st
import hashlib
from ..config.settings import SENHA_DASHBOARD

def check_password() -> bool:
    """
    Verifica autenticação do usuário

    Returns:
        True se autenticado, False caso contrário
    """
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        _exibir_tela_login()
        return False

    return True

def _exibir_tela_login():
    """Exibe tela de login"""
    st.markdown(
        "<div style='text-align: center; padding: 50px;'>"
        "<h1>🔐 Acesso Restrito</h1>"
        "<p style='color: #666; font-size: 1.1em;'>"
        "Sistema GEI - Gestão Estratégica de Informações<br>"
        "Receita Estadual de Santa Catarina"
        "</p>"
        "</div>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha_input = st.text_input(
            "Digite a senha:",
            type="password",
            key="pwd_input",
            placeholder="Senha de acesso"
        )

        if st.button("🔓 Entrar", use_container_width=True, type="primary"):
            if senha_input == SENHA_DASHBOARD:
                st.session_state.authenticated = True
                st.success("✅ Autenticação realizada com sucesso!")
                st.rerun()
            else:
                st.error("❌ Senha incorreta. Tente novamente.")

    st.stop()

def logout():
    """Realiza logout do usuário"""
    st.session_state.authenticated = False
    st.rerun()

def hash_password(password: str) -> str:
    """
    Gera hash SHA256 da senha

    Args:
        password: Senha em texto plano

    Returns:
        Hash SHA256 da senha
    """
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_hash(password: str, hash_stored: str) -> bool:
    """
    Verifica se senha corresponde ao hash armazenado

    Args:
        password: Senha em texto plano
        hash_stored: Hash armazenado

    Returns:
        True se senha é válida, False caso contrário
    """
    return hash_password(password) == hash_stored
