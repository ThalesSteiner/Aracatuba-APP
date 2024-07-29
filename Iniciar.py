import streamlit as st
from APP import MultiplasTelas  # Supondo que você tenha esta classe implementada em APP.py
from Aws_pedidos import AWS  # Supondo que você tenha esta classe implementada em Aws_pedidos.py
import json

# Configurar a página
st.set_page_config(page_title="Login Page", layout="wide")

class Iniciar:
    def __init__(self):
        pass

    # Função para verificar as credenciais do usuário
    @staticmethod
    def check_credentials(username, password):
        login = {
            "Usuario": username,
            "Senha": password
        }
        try:
            response = AWS().Validar_login_api(login)
            if response["statusCode"] == 200:
                data = json.loads(response["body"])
                item = data[0]
                json_data = {
                    "Nome": item.get("Nome", ""),
                    "aws_access_key_id": item.get("aws_access_key_id", ""),
                    "Senha": item.get("Senha", ""),
                    "Usuario": item.get("Usuario", ""),
                    "Credencial": item.get("Credencial", ""),
                    "aws_secret_access_key": item.get("aws_secret_access_key", "")
                }
                return True, json_data
            elif response["statusCode"] == 403:
                return False, {"statusCode": 403}
            else:
                return False, {"statusCode": response["statusCode"]}
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            st.error(f"Erro ao processar a resposta: {e}")
            return False, None

    # Função principal da aplicação
    @staticmethod
    def main():
        # Inicializar a variável de sessão para o login
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False

        if not st.session_state.logged_in:
            # Exibir tela de login
            st.title("Login")
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")

            if st.button("Login"):
                try:
                    result, user_info = Iniciar.check_credentials(username, password)
                    if result:
                        st.session_state.logged_in = True
                        st.success("Login realizado com sucesso!")
                        st.session_state.user_info = user_info
                        st.rerun(scope="fragment")
                        
                        Iniciar.iniciar()
                    else:
                        st.error("Usuário ou senha incorretos")
                except Exception as e:
                    st.error(f"Erro na função: {e}")
        else:
            # Se o usuário está logado, exibir o conteúdo principal
            Iniciar.iniciar()

    @staticmethod
    def iniciar():
        if 'user_info' not in st.session_state:
            st.error("Informações do usuário não disponíveis.")
            return
        else:
            credencial = st.session_state.user_info.get("Credencial", "")
            Acesso = ["Controle de Coleta", "Cadastro de Empresa", "Cadastrar novo pedido", "Separar pedido", "Estoque", "Dashboard"]

            if credencial == "1":
                Acesso = ["Cadastrar novo pedido", "Cadastro de Empresa", "Controle de Coleta"]
            elif credencial == "2":
                Acesso = ["Separar pedido", "Cadastro de Empresa", "Cadastrar novo pedido", "Estoque"]
            elif credencial == "3":
                Acesso = ["Controle de Coleta", "Cadastro de Empresa", "Cadastrar novo pedido", "Separar pedido", "Estoque"]
            elif credencial == "4":
                Acesso = ["Controle de Coleta", "Cadastro de Empresa", "Cadastrar novo pedido", "Separar pedido", "Estoque", "Dashboard"]
            else:
                st.error("Credencial inválida.")
                return
            
            telas = MultiplasTelas()
            telas.main(lista=Acesso)  # Passando o argumento lista
            
if __name__ == "__main__":
    Iniciar.main()
