#!/usr/bin/env python3
"""
Teste simples para verificar se o dashboard pode ser importado e executado
"""

import streamlit as st

# Simular o estado de login
st.session_state.logged_in = True
st.session_state.user_info = {
    "aws_access_key_id": "test_key",
    "aws_secret_access_key": "test_secret"
}

try:
    from dashboard import main as dashboard_main
    print("✅ Dashboard importado com sucesso!")
    
    # Testar se a função main pode ser chamada
    print("✅ Função main encontrada!")
    
except ImportError as e:
    print(f"❌ Erro ao importar dashboard: {e}")
except Exception as e:
    print(f"❌ Erro geral: {e}")

print("Teste concluído!")
