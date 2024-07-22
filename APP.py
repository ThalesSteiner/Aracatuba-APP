import streamlit as st
import time
import pandas as pd
import numpy as np
from streamlit_extras.metric_cards import style_metric_cards
import plotly.express as px
from streamlit_extras.grid import grid
import boto3
import requests
from datetime import datetime
import streamlit_authenticator as stauth
from Aws_pedidos import AWS


class MultiplasTelas:
    def __init__(self):
        self.tamanho_max_cartela = 128
        self.user = "ADMIN"
        self.senha = "123"
        self.meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        self.estoque_cartela = self.Gerar_estoque(150, 250)
        self.estoque_parafusos = self.Gerar_estoque(10000, 25000)
        self.df_gerar = False
        self.df_pedidos = False
        self.buscar_cliente = False
        self.empresas =  ["Nenhuma"] + self.buscar_clientes()
        self.lista_abas = []


    @st.cache_data
    def buscar_clientes(_self):
        return AWS().buscar_clientes()


    def Controle_coleta(self):
        st.title("Controle de Coleta")
        mygrid =  grid(2, 2, 1, vertical_align="bottom")
        # Definindo variáveis para armazenar os valores inseridos pelo usuário
        data_recebimento = st.date_input("Data de recebimento", format="DD/MM/YYYY")
        Mês = st.selectbox("Mês referência", self.meses)
        ID_compra = st.text_input("ID compra")
        Nome_empresa = st.selectbox("Nome empresa", self.empresas)
        Valor = st.number_input("Valor")
        Forma_pagamento = st.radio("Selecione suas opções:", ["PIX", "Dinheiro", "Débito","Boleto"])

        if st.button("Confirmar Ordens"):
            st.success(f"Ordem confirmada, pedido {ID_compra} da empresa {Nome_empresa} no valor de {Valor} enviado")
            time.sleep(3)
            mensagem = st.empty()

    def cadastro_empresa(self):
        tab1, tab2 ,tab3= st.tabs(["Empresa", "Expositor", "Rota"])
        with tab1:
            st.title("Cadastro de Empresas")
            st.write("Dados Gerais",)
            my_grid = grid(3, 2, [2,1,1], [2,1,1], vertical_align="bottom")
            #row1
            Nome_nova_empresa = my_grid.text_input("Nome / Razão social")
            Nome_representante = my_grid.text_input("Nome do representante")
            Cpf_cnpj = my_grid.text_input("CPF / CNPJ")
            #row2
            Telefone_contato = my_grid.text_input("Número para contato")
            Gmail = my_grid.text_input("Gmail")
            #row3
            Cidade = my_grid.text_input("Cidade")
            Uf = my_grid.text_input("UF")
            Cep = my_grid.text_input("CEP")

            #row4
            Rua = my_grid.text_input("Rua")
            Numero = my_grid.text_input("Numero")
            Complemento = my_grid.text_input("Complemento")

            #Rota = st.selectbox("Selecione a Rota:", ["Rota 1", "Rota 2", "Rota 3"])
            Data_cadastro = st.date_input("Data do cadastro", format="DD/MM/YYYY")
        

            if st.button("Confirmar Cadastro"):
                st.success(f"Cadastro da empresa {Nome_nova_empresa} feito com sucesso!")
                time.sleep(3)
                mensagem = st.empty()
        with tab2:
            st.title("Cadastro de Expositor")
            st.date_input("Data", format="DD/MM/YYYY")
            my_grid = grid(2, 2, vertical_align="bottom")
            #row1
            empresa = my_grid.selectbox("Nome da empresa", self.empresas)
            my_grid.text_input("Vendedor")
            #row2
            my_grid.text_input("Quantidade")
            my_grid.number_input("Valor")

            if st.button("Confirmar"):
                st.success(f"Expositor da empresa {empresa} vendido com sucesso!")
        with tab3:
            st.title("Cadastro nova rota")
            st.date_input("Data de cadastro", format="DD/MM/YYYY")
            my_grid = grid(1, 1, vertical_align="bottom")
            #row1
            Rota = my_grid.text_input("Nome da Rota")
            #row2
            my_grid.text_area("Descrição da rota")

            if st.button("Cadastar Rota"):
                st.success(f"Nova rota cadastrada com sucesso!")

    def cadastro_novo_pedido(self):
        st.title("Cadastro de novos pedidos")
        lista = []
        for i in range(1, self.tamanho_max_cartela+1):
            lista.append({"Cartela": f"Cartela {i}", "Quantidade": 0})
        df2 = pd.DataFrame(lista)
        edited_df = st.data_editor(df2, height=500, width=400)

        st.selectbox("loja", self.empresas)

        st.radio("Forma de Venda", ["Consignado", "Venda"])

        st.number_input("Valor da Cartela")


        if st.button("Confirmar Cadastro"):
                st.success(f"Cadastro da empresa feito com sucesso!")
                print(edited_df["Quantidade"].tolist())
                mensagem = st.empty()
    


    def Separar_pedido(self):
        st.title("Cadastro de novos pedidos")
        uploaded_file = st.file_uploader("Escolha um arquivo")
        if uploaded_file is not None:
            try:
                # Get the file contents as bytes
                bytes_data = uploaded_file.getvalue()

                # Determine the file type based on the filename extension
                filename = uploaded_file.name
                file_extension = filename.split(".")[-1]

                # Convert data to DataFrame based on file type
                if file_extension == "csv":
                    df_pedidos = pd.read_csv(bytes_data.decode("utf-8"))
                elif file_extension == "xlsx":
                    df_pedidos = pd.read_excel(bytes_data, engine="openpyxl")
                else:
                    st.error(f"Unsupported file type: {file_extension}")
                    return

            except Exception as e:
                st.error(f"Error reading file: {e}")

            df_pedidos.fillna(0, inplace=True)
            Lista_pedido_1 = df_pedidos.iloc[3:37, 0:2].values.tolist() + df_pedidos.iloc[3:37, 2:4].values.tolist() + df_pedidos.iloc[3:37, 4:6].values.tolist() + df_pedidos.iloc[3:29, 6:8].values.tolist()
            Lista_pedido_2 = df_pedidos.iloc[3:37, 9:11].values.tolist() + df_pedidos.iloc[3:37, 11:13].values.tolist() + df_pedidos.iloc[3:37, 13:15].values.tolist() + df_pedidos.iloc[3:29, 15:17].values.tolist()
            Lista_pedido_3 = df_pedidos.iloc[3:37, 18:20].values.tolist() + df_pedidos.iloc[3:37, 20:22].values.tolist() + df_pedidos.iloc[3:37, 22:24].values.tolist() + df_pedidos.iloc[3:29, 24:26].values.tolist()

            # Criar DataFrames
            df_pedido_1 = pd.DataFrame(Lista_pedido_1, columns=['Tamanho', 'Quantidade'])
            df_pedido_2 = pd.DataFrame(Lista_pedido_2, columns=['Tamanho', 'Quantidade'])
            df_pedido_3 = pd.DataFrame(Lista_pedido_3, columns=['Tamanho', 'Quantidade'])

            st.title("Tabela de Pedidos")
            my_grid = grid(3,3, vertical_align="bottom")
            loja1 = my_grid.selectbox("Escolha a Loja", self.empresas, key="loja1")
            loja2 = my_grid.selectbox("Escolha a Loja", self.empresas, key="loja2")
            loja3 = my_grid.selectbox("Escolha a Loja", self.empresas, key="loja3")
            my_grid.dataframe(df_pedido_1, width=400, height=500)
            my_grid.dataframe(df_pedido_2, width=400, height=500)
            my_grid.dataframe(df_pedido_3, width=400, height=500)
            lojas = [loja1, loja2, loja3]
            nenhuma_count = sum([loja1 == "Nenhuma", loja2 == "Nenhuma", loja3 == "Nenhuma"])
            lojas_iguais = len(set(lojas)) < 3
            if nenhuma_count == 3:
                st.warning("Nenhuma loja selecionada por favor trocar")
            else:
                if st.button("Enviar Pedido"):
                    self.enviar_pedido(loja1, df_pedido_1, loja2, df_pedido_2, loja3, df_pedido_3)
                    st.success("Pedido enviado")



    def enviar_pedido(self, loja1, pedido1, loja2, pedido2, loja3, pedido3):
        
        Lojas = [loja1, loja2, loja3]
        data_frame = [pedido1, pedido2, pedido3]
        data_frame2 = []
        i = 0
        for dataf in data_frame:
            if Lojas[i] != "Nenhuma":
                df = dataf[dataf['Quantidade'] != 0]
                df['Tamanho'] = [str(i) for i in df['Tamanho']]
                df['Quantidade'] = [str(i) for i in df['Quantidade']]
                dict_chave_valor = dict(zip(df['Tamanho'], df['Quantidade']))
                id = int(AWS().Gerar_novo_id())
                data = self.Data_hora()
                dic = {"ID": id,
                    "Data": data,
                    "Pedidos": dict_chave_valor}
                AWS().adicionar_pedido_tabela_pedidos(Lojas[i],dic)
                AWS().adicionar_pedido_tabela_pedidosID(dic)
                st.success(f"Pedido da empresa {Lojas[i]}")
            else:
                pass
            i += 1
        #st.write(self.Data_hora())
        #st.write(data_frame2)
        


    def Data_hora(self):
        try:
            response = requests.get('http://worldtimeapi.org/api/timezone/America/Sao_Paulo')
            # Extrair a data e hora atuais da resposta
            data_hora_atual = response.json()['datetime']
            data_formatada = data_hora_atual[0:10]
            Hora = data_hora_atual[11:19]
            st.write(data_formatada, Hora)
            return f"{data_formatada} {Hora}"
        except:
            hora_sistema = datetime.now()
            hora_sistema_formatada = hora_sistema.strftime('%Y-%m-%d %H:%M:%S')
            st.write("Data e hora do sistema (formatada):", hora_sistema_formatada)
            return f"{hora_sistema_formatada}"


    def Login(self):
        st.title("Login")

        # Widgets para entrada de usuário e senha
        username_input = st.text_input("Nome de usuário")
        password_input = st.text_input("Senha", type="password")

        # Botão de login
        if st.button("Login"):
            if self.autenticacao(username_input, password_input):
                st.success("Login bem-sucedido!")
                self.main()
            else:
                st.error("Credenciais inválidas. Tente novamente.")

    def autenticacao(self, username, password):
        if username == self.user and password == self.senha:
            return True
        else:
            return False

    def gerar_dado(self):
        dados = {'Ano': [], 'Mês': [], 'Loja': []}
        lojas = self.empresas
        mês = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
        anos = list(range(2011, 2024))

        # Preenchendo o dicionário com os valores aleatórios
        for ano in anos:
            for mes in mês:
                for loja in lojas:
                    dados['Ano'].append(ano)
                    dados['Mês'].append(mes)
                    dados['Loja'].append(loja)

        df = pd.DataFrame(dados)
        lista_cartela = []
        for x in range(128):
            lista_cartela.append(f"C{x+1}")

        for i in range(len(lista_cartela)):
            lista_cartela_nova = np.random.randint(0,8,len(df))
            df[lista_cartela[i]] = lista_cartela_nova
        soma_linhas = df.iloc[:, 3:].sum(axis=1)
        df.insert(3, "Quantidade", soma_linhas)
        self.df_pedidos = df


    def adicionar_cliente(self, nome):
        AWS.adicionar_cliente()




    def Dashboard(self):
        if self.df_pedidos == False:
            self.gerar_dado()
        
        df = self.df_pedidos

        try:
            st.title("Pedidos")
            tabela_completa = st.toggle('Tabela Completa')
            lista_concatenada = list(map(lambda x, y: x +" "+ y, list(map(str, df["Ano"].tolist())), df["Mês"].tolist()))
            df.insert(3, "Ano mês", lista_concatenada)

            lista_empresas = ["Todos"] + df['Loja'].unique().tolist()
            my_grid = grid(4, vertical_align="bottom")

            loja = my_grid.multiselect("Escolha as Lojas", lista_empresas)
            mês = my_grid.multiselect("Escolha o Mês", ["Todos"] + self.meses)
            ano = my_grid.multiselect("Escolha o Ano", ["todos"] + list(range(2011, 2023)))
            rota = my_grid.multiselect("Escolha a Rota", ["todos", "Rota1", "Rota2", "Rota3"])

            df_filtrado = df.copy()

            if "todos" not in ano:
                df_filtrado = df_filtrado[df_filtrado["Ano"].isin(ano)]

            if "Todos" not in mês:
                df_filtrado = df_filtrado[df_filtrado["Mês"].isin(mês)]

            if "Todos" not in loja:
                df_filtrado = df_filtrado[df_filtrado["Loja"].isin(loja)]


            #Dataframes filtrados

            df_venda_quantidade = df_filtrado.groupby("Loja")["Quantidade"].mean()
            df_venda_quantidade = df_venda_quantidade.reset_index()
            
            df_venda_quantidade_media = df_filtrado.groupby("Loja")["Loja"].sum()
            df_venda_quantidade_media = df_venda_quantidade.reset_index()

            df_venda_quantidade_media_desvio_padrao = df_filtrado.groupby("Loja")["Quantidade"].std()
            df_venda_quantidade_media_desvio_padrao = df_venda_quantidade_media_desvio_padrao.reset_index()

            df_venda_por_mês = df_filtrado.groupby("Mês")["Quantidade"].sum()
            df_venda_por_mês = df_venda_por_mês.reset_index()
            
            

            df_venda_por_ano = df_filtrado.groupby(["Ano"])["Quantidade"].sum()
            df_venda_por_ano = df_venda_por_ano.reset_index()

            df_venda_media_ano_por_mês = df_filtrado.groupby(["Ano mês"])["Quantidade"].sum()
            df_venda_media_ano_por_mês = df_venda_media_ano_por_mês.reset_index()

            dics_venda_total_cartela = {"Cartela": [], "Quantidade": []}
            dics_media_total_cartela = {"Cartela": [], "Quantidade": []}

            cartela = df.columns[5:].tolist()

            for cart in cartela:
                dics_venda_total_cartela["Cartela"].append(cart)
                dics_venda_total_cartela["Quantidade"].append(df_filtrado[cart].sum())
            
            for cart in cartela:
                dics_media_total_cartela["Cartela"].append(cart)
                dics_media_total_cartela["Quantidade"].append(df_filtrado[cart].mean())
            


            df_venda_por_cartela = pd.DataFrame(dics_venda_total_cartela)
            df_venda_media_por_cartela = pd.DataFrame(dics_media_total_cartela)


            print(df_venda_por_cartela)

            df_estoque = df_venda_media_por_cartela.copy()
            df_estoque["Quantidade"] = self.estoque_parafusos["Quantidade"] - df_venda_por_cartela["Quantidade"]
            print(df_estoque)



            if not df_venda_quantidade.empty:  # Verificar se o dataframe df_dash não está vazio
                my_grid = grid(4, vertical_align="bottom")
                vendas_totais = sum(df_filtrado["Quantidade"].tolist())*2
                quantidade = sum(df_filtrado["Quantidade"].tolist())
                media_vendas = round(np.mean(df_venda_quantidade["Quantidade"]),2)
                desvio = round(np.std(df_venda_quantidade["Quantidade"]),2)
                
                my_grid.metric(label="Vendas totais", value=f"R$: {round(vendas_totais,2)}")
                my_grid.metric(label="Total de parafusos", value= quantidade)
                my_grid.metric(label="Média", value=media_vendas)
                my_grid.metric(label="Desvio padrão", value=desvio)
                style_metric_cards()
            

            my_grid = grid(2, 2, 2, 2, 2,vertical_align="bottom")

            #Row1
            if "Todos" not in loja:
                fig = px.pie(df_venda_quantidade, values="Quantidade", names="Loja", width=700, height=700)
                my_grid.plotly_chart(fig, theme="streamlit")

            fig = px.bar(df_venda_quantidade_media, title="Média vendas por loja", x="Quantidade", y="Loja", width=600, height=700)
            fig.update_layout(yaxis=dict(categoryorder='total ascending'))
            mini = min(df_venda_quantidade_media["Quantidade"].tolist())
            maxi = max(df_venda_quantidade_media["Quantidade"].tolist()) 
            fig.update_layout(xaxis=dict(range=[mini-2, maxi]))
            my_grid.plotly_chart(fig, theme="streamlit")

            my_grid.plotly_chart(self.projetar_grafico(df_venda_quantidade_media, "Média vendas por loja", "Quantidade", "Loja", "Sim"), theme="streamlit" )
            
            my_grid.plotly_chart(self.projetar_grafico(df_venda_quantidade_media_desvio_padrao, "Desvio padrão das médias vendas por loja ", "Quantidade", "Loja", "Sim"), theme="streamlit" )

            my_grid.plotly_chart(self.projetar_grafico(df_venda_por_mês, "Vendas totais de cartela", "Quantidade", "Mês", "Sim", "Sim"), theme="streamlit" )

            my_grid.plotly_chart(self.projetar_grafico(df_venda_media_ano_por_mês, "Maiores vendas por Ano/Mês", "Quantidade", "Ano mês", "Sim", "Sim"), theme="streamlit")

            my_grid.plotly_chart(self.projetar_grafico(df_venda_por_ano, "Melhores vendas por Ano", "Ano", "Quantidade", "Sim", "Não"), theme="streamlit")

            my_grid.plotly_chart(self.projetar_grafico(df_venda_por_cartela, "Venda total de cartela", "Quantidade", "Cartela", "Sim", "Sim"), theme="streamlit")

            my_grid.plotly_chart(self.projetar_grafico(df_venda_media_por_cartela, "Venda média de cartela", "Quantidade", "Cartela", "Sim" , "Sim"), theme="streamlit")
            
            try:
                df_estoque_positivo = df_estoque[df_estoque["Quantidade"] > 0]
                my_grid.dataframe(df_estoque_positivo,  width=700, height=400)
            except:
                my_grid.error("Todos Parafusos precisam ser reposto")

            try:
                df_estoque_negativo = df_estoque[df_estoque["Quantidade"] <= 0]
                my_grid.dataframe(df_estoque_negativo,  width=700, height=400)

            except:
                my_grid.success("Nenhuma cartela precisa ser reposto")

            time.sleep(1)

            if tabela_completa:
                st.dataframe(df, width=700, height=400)
            else:
                st.dataframe(df_filtrado, width=700, height=400)

            
            my_grid = grid(2, 2, 2, vertical_align="bottom")

            my_grid.title("Vendas totais das empresas no periodo analisado")
            time.sleep(0.5)
            try:
                my_grid.dataframe(df_venda_quantidade, width=700, height=400)
            except:
                st.error("Coloque mais meses para avaliação")
            time.sleep(0.5)
            my_grid.dataframe(df_venda_por_mês, width=700, height=400)
            time.sleep(0.5)
            my_grid.dataframe(df_venda_por_ano, width=700, height=400)
            time.sleep(0.5)
            my_grid.dataframe(df_venda_media_ano_por_mês, width=700, height=400)
        except:
            st.error("Coloque um periodo")



    def projetar_grafico(self, dataframe, Titulo, x, y, ordenar="Não", suavizar="Sim"):
        fig = px.bar(dataframe, title=Titulo, x=x, y=y, width=500, height=700)
        if suavizar == "Sim":
            mini = min(dataframe[x].tolist())
            maxi = max(dataframe[x].tolist()) 
            fig.update_layout(xaxis=dict(range=[mini-(0.1*mini), maxi]))
        if ordenar == "Sim":
            fig.update_layout(yaxis=dict(categoryorder='total ascending'))
        return fig

    def Gerar_estoque(self, min, max):
        dics = {"Cartela": [], "Quantidade": []}
        self.gerar_dado == True
        for i in range(self.tamanho_max_cartela):
            dics["Cartela"].append(f"Cartela {i+1}")
            dics["Quantidade"].append(np.random.randint(min, max))
        return pd.DataFrame(dics)
    
    def Estoque(self):
        df = self.estoque_cartela
        df2 = self.estoque_parafusos



        tab1, tab2 = st.tabs(["Estoque cartela","Estoque caixa"])
        with tab1:
            st.title("Estoque cartela")
            st.dataframe(df)
        with tab2:
            st.title("Estoque parafusos")
            st.dataframe(df2)

    
    def criar_usuario(self):
        st.write("Criar usuarios")
        nome =  st.text_input("Nome usuario")
        login  = st.text_input("Nome do login")
        senha =  st.text_input("Senha")
        credencial = st.selectbox("Nivel de acesso", ["1", "2", "3","4"])
        if st.button("Enviar"):
            dic = {
                "Usuario": str(login),
                "Senha": str(senha),
                "Nome": str(nome),
                "Credencial": str(credencial)
            }
            AWS().adicionar_usuario(dic)
            
            st.success("Usuario cadastrado")
        
    def main(self, lista):
        
        self.lista_abas = lista

        pagina_selecionada = st.sidebar.selectbox("Navegar", self.lista_abas)

        #if pagina_selecionada == "Login":
        #    self.Login()
        if pagina_selecionada == "Cadastro de Empresa":
            self.cadastro_empresa()
        elif pagina_selecionada == "Cadastrar novo pedido":
            self.cadastro_novo_pedido()
        elif pagina_selecionada == "Controle de Coleta":
            self.Controle_coleta()
        elif pagina_selecionada == "Separar pedido":
            self.Separar_pedido()
        elif pagina_selecionada == "Estoque":
            self.Estoque()
        elif pagina_selecionada == "Dashboard":
            self.Dashboard()
        elif pagina_selecionada == "Criar Usuario":
            self.criar_usuario()
        