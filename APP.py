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
from Aws_pedidos import AWS
import json
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from Funções_APP import Funções
import plotly.express as px
import pandas as pd



class MultiplasTelas:
    def __init__(self):
        self.tamanho_max_cartela = 128
        self.meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        self.df_pedidos = False
        self.empresas =  ["Nenhuma"] + self.buscar_clientes()


    def Controle_coleta(self):
        tab1, tab2, tab3= st.tabs(["Controle", "Consulta débito", "Consulta pedido"])
        
        with tab1:
            ID_compra = st.text_input("ID compra")
    
            # Definindo variáveis para armazenar os valores inseridos pelo usuário
            data_recebimento = st.date_input("Data de recebimento", format="DD/MM/YYYY")
            mes = data_recebimento.month
            ano = data_recebimento.year
            
            Nome_empresa = st.selectbox("Nome empresa", self.empresas)
            Valor = st.number_input("Valor")
            Detalhe_pedido = st.radio("Algum debito ficou pendente", ["Não", "Sim"])
            if Detalhe_pedido == "Sim":
                Valor_pendente = st.number_input("Valor pendente")    
            Forma_pagamento = st.radio("Selecione forma pagamento:", ["PIX", "Dinheiro", "Débito","Boleto","Cheque"])
            

            if st.button("Confirmar Ordens"):
                if Detalhe_pedido == "Não":
                    Valor_pendente = 0
                    Status = "Quitado"
                    AWS().remover_pedido_nao_pago("Aracatuba Parafusos", str(ID_compra))
                else:
                    Status = "Em debito"
                dic = {
                    "ID": (ID_compra),
                    "Status": str(Status),
                    "Data recebimento": str(data_recebimento),
                    "Nome da empresa": str(Nome_empresa),
                    "Valor": int(Valor),
                    "Debito": str(Detalhe_pedido),
                    "Valor pendente": str(Valor_pendente),
                    "Forma pagamento": str(Forma_pagamento)
                }
                AWS().adicionar_pedido_Controle_Coleta(dic)
                st.success(f"Ordem confirmada, pedido {ID_compra} da empresa {Nome_empresa} no valor de {Valor} enviado")
        with tab2:
            st.title("Consulta de débito")
            debito = st.checkbox("Pesquisar pedidos não pagos")
            if debito:
                buscar = self.buscar_pedidos_nao_pagos()
                Id = st.selectbox("Coloque o ID da consulta", buscar)
                
            else:
                Id = st.text_input("Coloque o ID da consulta")
            if st.button("Pesquisar"):
                try:
                    pedido = AWS().buscar_pedido_controle_coleta(Id)
                    mygrid =  grid(3,2, 3, vertical_align="bottom")
                    mygrid.text_input("Status",  value=pedido["Status"])
                    mygrid.text_input("ID",  value=pedido["ID"])
                    mygrid.text_input("Nome da empresa",  value=pedido["Nome da empresa"])
                    mygrid.text_input("Data recebimento",  value=pedido["Data recebimento"])
                    mygrid.text_input("Forma pagamento",  value=pedido["Forma pagamento"])
                    mygrid.text_input("Valor do pedido",  value=float(pedido["Valor"]))
                    mygrid.text_input("Débito",  value=pedido["Debito"])
                    mygrid.text_input("Valor pendente",  value=pedido["Valor pendente"])

                except:
                    st.warning("Pedido não achado")
            
                    
        with tab3:
            st.title("Consulta de Pedido")

            if st.checkbox("Consultar Empresa"):
                empresa = st.selectbox("Selecione a empresa", self.empresas, key="empresa_selectbox")   
                if empresa != "Nenhuma":             
                    pedido = self.buscar_id_pedidos_lojas(empresa)
                    st.session_state.pedidos_empresa = pedido
                    try:
                        if "pedidos_empresa" in st.session_state:
                            Id = st.selectbox("Selecione o ID", st.session_state.pedidos_empresa, key="id_selectbox")
                            if st.button("Buscar Pedido por Empresa"):
                                Funções().Exibir_pedido(AWS().buscar_pedido_ID(Id))
                    except:
                        st.warning("Erro ao buscar ID")
            else:
                Id = st.text_input("Coloque o ID da consulta", key="Id2")
                if st.button("Pesquisar", key="Botão2"):
                    pedido = AWS().buscar_pedido_ID(Id)
                    Funções().Exibir_pedido(pedido)


    def cadastro_empresa(self):
        tab1, tab2 = st.tabs(["Empresa","Consultar Empresa"])
        with tab1:
            st.title("Cadastro de Empresas")
            st.write("Dados Gerais",)
            my_grid = grid(3, 4, [2,1,1], [2,2,1,1],2, vertical_align="bottom")
            #row1
            Nome_nova_empresa = my_grid.text_input("Nome / Razão social")
            Nome_representante = my_grid.text_input("Nome do representante")
            Cpf_cnpj = my_grid.text_input("CPF / CNPJ")
            #row2
            Telefone_contato = my_grid.text_input("Número de celular")
            Telefone_contato2 = my_grid.text_input("Número Fixo")
            Telefone_contato3 = my_grid.text_input("Número de Whatsapp")
            Gmail = my_grid.text_input("Gmail")
            #row3
            Cidade = my_grid.text_input("Cidade")
            Uf = my_grid.text_input("UF")
            Cep = my_grid.text_input("CEP")

            #row4
            Rua = my_grid.text_input("Rua")
            Bairro = my_grid.text_input("Bairro")
            Numero = my_grid.text_input("Numero")
            Complemento = my_grid.text_input("Complemento")

            longitude  = my_grid.text_input("longitude")
            latitude = my_grid.text_input("latitude")
            
            #Rota = st.selectbox("Selecione a Rota:", ["Rota 1", "Rota 2", "Rota 3"])
            Data_cadastro = st.date_input("Data do cadastro", format="DD/MM/YYYY")
        

            if st.button("Confirmar Cadastro"):
                try:
                    dic = {
                        "Nome": Nome_nova_empresa,
                        "Representante": Nome_representante,
                        "Status": "Ativo",
                        "Data cadastro": Data_cadastro,
                        "CPF/CNPJ": Cpf_cnpj,
                        "Telefone_contato": Telefone_contato,
                        "Telefone_fixo": Telefone_contato2,
                        "Telefone_whats": Telefone_contato3,
                        "Email": Gmail,
                        "Longitude": longitude,
                        "Latitude": latitude,
                        "Endereco": {
                            "Rua": Rua,
                            "Numero": Numero,
                            "Bairro": Bairro,
                            "Cidade": Cidade,
                            "Uf": Uf,
                            "Cep": Cep,
                            "Complemento": Complemento
                        }
                    }
                    print("TESTANDO")
                    AWS().cadastro_cliente_endereço(dic)
                    AWS().adicionar_cliente(Nome_nova_empresa)
                    AWS().adicionar_cliente_tabela_Cliente_lista(Nome_nova_empresa)
                    AWS().adicionar_loja_tabela_pedidos(Nome_nova_empresa)
                    
                    st.success(f"Cadastro da empresa {Nome_nova_empresa} feito com sucesso!")
                except:
                    st.warning(f"Falha ao cadastrar")
                    
            """with tab2:
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
                st.success(f"Nova rota cadastrada com sucesso!")"""
        
        with tab2:
            editar = st.checkbox("Editar empresa")
            st.title("Consulta de Empresa")
            empresa = st.selectbox("Nome da empresa", self.empresas, key="empresa2")
            col1, col2 = st.tabs(["Dados gerais", "Endereço"])

            with col1:
                try:
                    Cadastro = self.buscar_empresa(empresa)
                    if Cadastro["Data cadastro"] == "":
                        Cadastro["Data cadastro"] = "Não cadastrado"
                    mygrid = grid(3, 2, 2, 2, vertical_align="bottom")
                    
                    Nome_nova_empresa = mygrid.text_input("Loja", Cadastro["Nome"])
                    Cpf_cnpj = mygrid.text_input("CPF/CNPJ", Cadastro["CPF/CNPJ"])
                    if editar:
                        Ativo = mygrid.selectbox("Status", ["Ativo", "Inativo"])
                    else:
                        Ativo = mygrid.text_input("Status", Cadastro["Status"])
                    Nome_representante = mygrid.text_input("Representante", Cadastro["Representante"])
                    Telefone_contato = mygrid.text_input("Telefone contato", Cadastro["Telefone_contato"])
                    Data_cadastro = mygrid.text_input("Data do cadastro", Cadastro["Data cadastro"])
                    Gmail = mygrid.text_input("Email", Cadastro["Email"])
                    longitude = mygrid.text_input("Longitude", Cadastro["Longitude"])
                    latitude = mygrid.text_input("Latitude", Cadastro["Latitude"])
                    
                    try:
                        Telefone_contato2 = mygrid.text_input("Telefone fixo", Cadastro["Telefone_fixo"])
                        Telefone_contato3 = mygrid.text_input("Complemento", Cadastro["Telefone_whats"])
                    except:
                        st.warning("Nenhum outro telefone para contato encontrado")
                        
                except:
                    st.warning("Empresa não encontrada")
            
            with col2:
                try:
                    mygrid = grid(3, 2, 2, 1, vertical_align="bottom")
                    Rua = mygrid.text_input("Rua", Cadastro["Endereco"]["Rua"])
                    Numero = mygrid.text_input("Numero", Cadastro["Endereco"]["Numero"])
                    Bairro = mygrid.text_input("Bairro", Cadastro["Endereco"]["Bairro"])
                    Cidade = mygrid.text_input("Cidade", Cadastro["Endereco"]["Cidade"])
                    Uf = mygrid.text_input("Uf", Cadastro["Endereco"]["Uf"])
                    Cep = mygrid.text_input("Cep", Cadastro["Endereco"]["Cep"])
                    Complemento = mygrid.text_input("Complemento", Cadastro["Endereco"]["Complemento"])
                except:
                    st.warning("Empresa não encontrada")
                    
                try:
                    Endereco_anterior = mygrid.text_input("Endereço no antigo sistema", Cadastro["Endereco anterior"])
                except:
                    st.info("Nenhum endereço do antigo sistema foi achado")

            if editar:    
                if st.button("Salvar", key="Botão3"):
                        dic = {
                            "Nome": Nome_nova_empresa,
                            "Representante": Nome_representante,
                            "Status": Ativo,
                            "Data cadastro": Data_cadastro,
                            "CPF/CNPJ": Cpf_cnpj,
                            "Telefone_contato": Telefone_contato,
                            "Telefone_fixo": Telefone_contato2,
                            "Telefone_whats": Telefone_contato3,
                            "Email": Gmail,
                            "Longitude": longitude,
                            "Latitude": latitude,
                            "Endereco": {
                                "Rua": Rua,
                                "Numero": Numero,
                                "Bairro": Bairro,
                                "Cidade": Cidade,
                                "Uf": Uf,
                                "Cep": Cep,
                                "Complemento": Complemento
                            }
                        }
                        AWS().cadastro_cliente_endereço(dic)


    def cadastro_novo_pedido(self):
        st.title("Cadastro de novos pedidos")
        lista = []
        for i in range(1, self.tamanho_max_cartela+1):
            lista.append({"Tamanho": f"Cartela {i}", "Quantidade": 0})
        df2 = pd.DataFrame(lista)
        df = st.data_editor(df2, height=500, width=400)

        loja = st.selectbox("loja", self.empresas)
        
        data = st.date_input("Data do Pedido", format="DD/MM/YYYY")

        venda = st.radio("Forma de Venda", ["Consignado", "Venda"])

        valor_cartela = st.number_input("Valor da Cartela")

        if st.button("Confirmar Cadastro"):
                df = df[df['Quantidade'] != 0]
                #df["Tamanho"] = [cartela.split(" ")[1] for cartela in df["Tamanho"].tolist()]
                pedido = dict(zip(df['Tamanho'], df['Quantidade']))

                if pedido == {'Tamanho': {}, 'Quantidade': {}}:
                    st.warning("Pedido vazio")
                else:
                    try:
                        quantidade_parafusos = sum(df['Quantidade'].tolist())
                        Id = AWS().Gerar_novo_id()
                        dic = {"ID": str(Id),
                            "Loja": loja,
                            "Data": str(data),
                            "Hora": str(self.Data_hora()),
                            "Tipo de Venda": venda,
                            "Valor da cartela": str(valor_cartela),
                            "Pedidos": pedido
                            }
                        
                        controle_coleta = {
                            "ID": (str(Id)),
                            "Status": str("Em debito"),
                            "Data recebimento": str(data),
                            "Nome da empresa": str(loja),
                            "Valor": str(float(quantidade_parafusos) * float(valor_cartela)),
                            "Debito": "Sim",
                            "Valor pendente": str(float(quantidade_parafusos) * float(valor_cartela)),
                            "Forma pagamento": "Não declarada"}
                        
                        data = f"{self.meses[int(data.month)-1]}-{data.year}"
                        AWS().adicionar_pedido_tabela_pedidos(loja,Id)
                        AWS().adicionar_pedido_tabela_pedidos_gerais(data,Id,dic)
                        AWS().adicionar_pedido_tabela_pedidosID(dic)
                        AWS().adicionar_pedido_Controle_Coleta(controle_coleta)
                        AWS().adicionar_pedido_nao_pago("Aracatuba Parafusos", str(Id))
                        self.Aviso_pedido(Id, loja)
                        st.success(f"Cadastro do pedido {Id} da empresa {loja} feito com sucesso!")
                    except:
                        st.warning("ERRO AO CADASTRAR")

    
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
                dic = {"ID": str(id),
                    "Loja": Lojas[i],
                    "Data": data,
                    "Pedidos": dict_chave_valor}
                AWS().adicionar_pedido_tabela_pedidos(Lojas[i],dic)
                AWS().adicionar_pedido_tabela_pedidosID(dic)
                st.success(f"Pedido da empresa {Lojas[i]}")
            else:
                pass
            i += 1
        #st.write(data_frame2)  



    def Data_hora(self):
        try:
            response = requests.get('http://worldtimeapi.org/api/timezone/America/Sao_Paulo')
            # Extrair a data e hora atuais da resposta
            data_hora_atual = response.json()['datetime']
            data_formatada = data_hora_atual[0:10]
            Hora = data_hora_atual[11:19]
            #st.write(data_formatada, Hora)
            return f"{Hora}"
        except:
            hora_sistema = datetime.now()
            hora_sistema_formatada = hora_sistema.strftime('%Y-%m-%d %H:%M:%S')
            #st.write("Data e hora do sistema (formatada):", hora_sistema_formatada)
            return f"{hora_sistema_formatada}"


    @st.cache_data
    def gerar_dado(_self, empresas):
        pedidos = []

        anos = [f"{2017+i}" for i in range(8)]
        meses_do_ano = [
            "Janeiro", "Fevereiro", "Março", "Abril",
            "Maio", "Junho", "Julho", "Agosto",
            "Setembro", "Outubro", "Novembro", "Dezembro"
        ]
        lojas = empresas

        for ano in anos:
            for mes in meses_do_ano:
                for loja in lojas[1:]:
                    repeticao = np.random.randint(25, 80)
                    dic = {"Loja": loja,
                            "Data": f"{mes}-{ano}"}
                    dic2 = {}
                    for z in range(1, repeticao):
                        parafuso = str(np.random.randint(1, 129))
                        quantidade = str(np.random.randint(1, 16))
                        dic2[parafuso] = quantidade
                    dic["Cartela"] = dic2
                    pedidos.append(dic)

        return pedidos


    def Dashboard(self):
        pedidos = self.gerar_dado(self.empresas)
        #st.json(pedidos)
        st.title("Pedidos")
        tabela_completa = st.toggle('Tabela Completa')
        my_grid = grid(2,3, vertical_align="bottom")
        Cidade = my_grid.multiselect("Escolha a Bairro", ["todos", "Rio de janeiro", "São joão de meriti", "Nova Iguaçu"])
        Bairro = my_grid.multiselect("Escolha a Bairro", ["todos", "Piedade", "Meier", "Madureira"])
        #Bairro = my_grid.multiselect("Escolha a Bairro", ["todos", "Rota1", "Rota2", "Rota3"])
        
        loja = my_grid.multiselect("Escolha as Lojas", ["Todos"] + self.empresas)
        mês = my_grid.multiselect("Escolha o Mês", ["Todos"] + self.meses)
        ano = my_grid.multiselect("Escolha o Ano", ["Todos"] + [f"{2017+i}" for i in range(8)])

        
        if st.button("Pesquisar"):
            
            if "Todos" not in loja:
                pedidos = [pedido for pedido in pedidos if pedido['Loja'] in loja]
            if "Todos" not in mês:
                pedidos = [pedido for pedido in pedidos if pedido['Data'].split("-")[0] in mês]
            if "Todos" not in ano:
                pedidos = [pedido for pedido in pedidos if pedido['Data'].split("-")[1] in ano]
                
            # Inicializa os dicionários
            itens = self.tamanho_max_cartela
            dic = {str(i): 0 for i in range(1, itens + 1)}
            datas_unicas = {}
            Anos_unicas = {}
            Mês_unicas = {}
            Lista_lojas = {}
            Venda_total_parafusos = {}

            # Itera sobre os pedidos
            for pedido in pedidos:
                # Atualiza contagem de parafusos
                for cartela, quantidade in pedido["Cartela"].items():
                    dic[cartela] += int(quantidade)
                    if cartela in Venda_total_parafusos:
                        Venda_total_parafusos[cartela] += int(quantidade)
                    else:
                        Venda_total_parafusos[cartela] = int(quantidade)
                
                # Calcula a soma das cartelas
                cartelas = [int(cartela) for cartela in pedido['Cartela']]
                soma_cartelas = sum(cartelas)
                
                # Atualiza a soma para a data correspondente
                data = pedido["Data"]
                if data in datas_unicas:
                    datas_unicas[data] += soma_cartelas
                else:
                    datas_unicas[data] = soma_cartelas

                # Atualiza a soma para o ano correspondente
                ano = data.split("-")[1]
                if ano in Anos_unicas:
                    Anos_unicas[ano] += soma_cartelas
                else:
                    Anos_unicas[ano] = soma_cartelas

                # Atualiza a soma para o mês correspondente
                mes = data.split("-")[0]
                if mes in Mês_unicas:
                    Mês_unicas[mes] += soma_cartelas
                else:
                    Mês_unicas[mes] = soma_cartelas
                
                # Atualiza a soma para a loja correspondente
                loja = pedido["Loja"]
                if loja in Lista_lojas:
                    Lista_lojas[loja] += soma_cartelas
                else:
                    Lista_lojas[loja] = soma_cartelas

            # Calcula a média de cada parafuso
            total_pedidos = len(pedidos)
            Media_cartela = {cartela: round(quantidade / total_pedidos, 2) for cartela, quantidade in dic.items()}
            
            # Converter dados para DataFrame
            df_cartelas = pd.DataFrame(list(dic.items()), columns=['Cartela', 'Total'])
            df_datas = pd.DataFrame(list(datas_unicas.items()), columns=['Data', 'Total'])
            df_anos = pd.DataFrame(list(Anos_unicas.items()), columns=['Ano', 'Total'])
            df_meses = pd.DataFrame(list(Mês_unicas.items()), columns=['Mês', 'Total'])
            df_lojas = pd.DataFrame(list(Lista_lojas.items()), columns=['Loja', 'Total'])

            # Criar gráficos
            fig_cartelas = px.bar(df_cartelas, x='Cartela', y='Total', title='Total de Parafusos por Cartela')
            fig_datas = px.line(df_datas, x='Data', y='Total', title='Total de Cartelas por Data')
            fig_anos = px.bar(df_anos, x='Ano', y='Total', title='Total de Cartelas por Ano')
            fig_meses = px.bar(df_meses, x='Mês', y='Total', title='Total de Cartelas por Mês')
            fig_lojas = px.bar(df_lojas, x='Loja', y='Total', title='Total de Cartelas por Loja')

            
            my_grid = grid(4, vertical_align="bottom")
            
            # Mostrar gráficos no Streamlit
            st.title('Análise de Pedidos Simulados')

            st.subheader('Total de Parafusos por Cartela')
            st.plotly_chart(fig_cartelas)

            st.subheader('Total de Cartelas por Data')
            st.plotly_chart(fig_datas)

            st.subheader('Total de Cartelas por Ano')
            st.plotly_chart(fig_anos)

            st.subheader('Total de Cartelas por Mês')
            st.plotly_chart(fig_meses)

            st.subheader('Total de Cartelas por Loja')
            st.plotly_chart(fig_lojas)
            
            
            st.dataframe(df_cartelas)
            st.dataframe(df_datas)
            st.dataframe(df_anos)
            st.dataframe(df_meses)
            st.dataframe(df_lojas)
        

    """def Dashboard2(self):
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
"""
    
    
    def atualizar_estoque(self, df, estoque, Id=None):
        dic_estoque = df.to_dict()
        Cartela_dataframe = dic_estoque["Cartela"]
        Quantidade_dataframe = dic_estoque["Quantidade"]
        dic_estoque = {cartela: int(quantidade) for cartela, quantidade in zip(Cartela_dataframe.values(), Quantidade_dataframe.values())}
        
        if Id:
            pedido = AWS().buscar_pedido_ID(Id)
            for cartela, quantidade in pedido["Pedidos"].items():
                dic_estoque[cartela] = dic_estoque.get(cartela, 0) - quantidade

        AWS().Adicionar_estoque_cartela(estoque, dic_estoque)
        self.tabela_estoque_formatada.clear()
        st.success("Estoque atualizado")
        time.sleep(2)
        st.rerun()
    
        
    
    def Estoque(self):
        tab1, tab2 = st.tabs(["Estoque cartela", "Estoque caixa"])
        df = self.tabela_estoque_formatada("Parafuso Cartela")
        df2 = self.tabela_estoque_formatada("Parafuso Caixa")

        
        with tab1:
            if st.checkbox("Editar Estoque"):
                dataframe = st.data_editor(df, width=500, height=700)
                if st.button("Salvar estoque"):
                    self.atualizar_estoque(dataframe, "Parafuso Cartela")
            else:
                Id = st.text_input("Buscar ID")
                st.title("Estoque cartela")  
                dataframe = st.dataframe(df, width=500, height=700)
                if st.button("Salvar estoque"):
                    self.atualizar_estoque(df, "Parafuso Cartela", Id)
        
        with tab2:
            if st.checkbox("Editar Estoque", key="Estoque2"):
                dataframe = st.data_editor(df2, width=500, height=700, key="Dataframe2")
                if st.button("Salvar estoque", key="Botão2"):
                    self.atualizar_estoque(dataframe, "Parafuso Caixa")
            else:
                Id = st.text_input("Buscar ID", key="Id2")
                st.title("Estoque cartela")  
                dataframe2 = st.dataframe(df2, width=500, height=700)
                if st.button("Salvar estoque", key="Botão3"):
                    self.atualizar_estoque(df2, "Parafuso Caixa", Id)
    
   
    
    def Rotas(self):
        Cadastro_empresas = self.buscar_cadastro_empresas()

        latitudes = []
        longitudes = []
        lojas = []
        Status = []
        endereços = []
        bairros = []
        cidades = []

        for empresa in Cadastro_empresas:
            try:
                longitudes.append(float(empresa["Longitude"]))
                latitudes.append(float(empresa["Latitude"]))
                lojas.append(empresa["Nome"])
                Status.append(empresa["Status"])
                endereços.append(empresa["Endereco"])
                bairros.append(empresa["Endereco"]["Bairro"])
                cidades.append(empresa["Endereco"]["Cidade"])
            except:
                pass

        if not latitudes or not longitudes:
            st.write("Nenhuma coordenada válida encontrada.")
            return

        lojas.insert(-1, "Todas")
        bairros.insert(-1, "Todos")
        cidades.insert(-1, "Todas")
        
        
        mygrid =  grid(2, 2, vertical_align="bottom")
        # Adicionar filtros
        status_selecionados = mygrid.multiselect("Selecione o status das lojas", options=set(Status), default=["Ativo"])
        lojas_selecionadas = mygrid.multiselect("Selecione as lojas", options=set(lojas), default=["Todas"])
        bairros_selecionados = mygrid.multiselect("Selecione os bairros", options=set(bairros), default=["Todos"])
        cidades_selecionadas = mygrid.multiselect("Selecione as cidades", options=set(cidades), default=["Todas"])


        # Filtrar dados com base nas seleções
        filtro = [
            (lat, lon, loja, statu, endereco2)
            for lat, lon, loja, statu, endereco2 in zip(latitudes, longitudes, lojas, Status, endereços)
            if (statu in status_selecionados) and
            (lojas_selecionadas == ["Todas"] or loja in lojas_selecionadas) and
            (bairros_selecionados == ["Todos"] or endereco2["Bairro"] in bairros_selecionados) and
            (cidades_selecionadas == ["Todas"] or endereco2["Cidade"] in cidades_selecionadas)
        ]

        if not filtro:
            st.write("Nenhuma loja encontrada com os filtros selecionados.")
            return

        mapa = folium.Map(location=[-22.832113794507347, -43.346853465267536], zoom_start=13)
        marker_cluster = MarkerCluster().add_to(mapa)

        for lat, lon, loja, statu, endereco2 in filtro:
            try:
                rua = endereco2['Rua']
                numero = endereco2['Numero']
                bairro = endereco2['Bairro']
                cidade = endereco2['Cidade']
                cep = endereco2['Cep']

                endereco = f"{rua} {numero} {bairro} {cidade} {cep}"
            except:
                endereco = endereco2

            if statu == "Ativo":
                folium.Marker(
                    [lat, lon],
                    popup=folium.Popup(f"{loja} / {endereco}", max_width=300),
                    icon=folium.Icon(icon="cloud")
                ).add_to(mapa)
            elif statu == "Inativo":
                folium.Marker(
                    [lat, lon],
                    popup=folium.Popup(f"{loja}\n{endereco}", max_width=300),
                    icon=folium.Icon(icon="remove", color="red")
                ).add_to(mapa)
            else:
                folium.Marker(
                    [lat, lon],
                    popup=folium.Popup(f"{statu} {loja} {endereco}", max_width=300),
                    icon=folium.Icon(icon="remove", color="purple")
                ).add_to(mapa)

        folium.Marker(
            [-22.832113794507347, -43.346853465267536],
            popup="Araçatuba Material",
            icon=folium.Icon(icon="home", color="orange")
        ).add_to(mapa)

        st_folium(mapa, width=1800, height=800)
    
    
    def main(self, lista):
        
        self.lista_abas = lista
        lista_navegação = []
        
        for pagina_selecionada in self.lista_abas:
            if pagina_selecionada == "Cadastro de Empresa":
                lista_navegação.append(st.Page(self.cadastro_empresa, title= "🏢 Cadastro de Empresa"))
            elif pagina_selecionada == "Cadastrar novo pedido":
                lista_navegação.append(st.Page(self.cadastro_novo_pedido, title="📝 Cadastrar novo pedido"))
            elif pagina_selecionada == "Controle de Coleta":
                lista_navegação.append(st.Page(self.Controle_coleta, title="📦 Controle de Coleta"))
            elif pagina_selecionada == "Separar pedido":
                lista_navegação.append(st.Page(self.Separar_pedido, title="📋 Separar pedido"))
            elif pagina_selecionada == "Estoque":
                lista_navegação.append(st.Page(self.Estoque, title="📊 Estoque"))
            elif pagina_selecionada == "Dashboard":
                lista_navegação.append(st.Page(self.Dashboard, title="📈 Dashboard"))
            elif pagina_selecionada == "Rotas":
                lista_navegação.append(st.Page(self.Rotas, title="🚚 Rotas"))
        
        pg = st.navigation({"Aracatuba parafusos":lista_navegação}, position="sidebar")
        pg.run()


    @st.experimental_dialog("Aviso de pedido")
    def Aviso_pedido(self, id, empresa):
        st.write(f"O pedido ID:{id} da empresa {empresa} foi confirmado")
        if st.button("Confirmar"):
            st.rerun()

    @st.cache_data
    def buscar_empresa(_self, empresa):
        print(f"Função chamada {empresa}")
        return AWS().buscar_cadastro_empresa(empresa)
    
    @st.cache_data
    def buscar_pedidos_nao_pagos(_self):
        print("Pedidos não pagos")
        return [item['S'] for item in AWS().buscar_pedido_nao_pago()]

    @st.cache_data
    def buscar_cadastro_empresas(_self):
        Cadastro_empresas = AWS().Buscar_todos_cadastro_clientes()
        print("Função chamada")
        print(len(Cadastro_empresas))
        return Cadastro_empresas
    
    @st.cache_data
    def tabela_estoque_formatada(_self, Estoque):
        estoque_atual = AWS().buscar_Estoque(Estoque)
        df = pd.DataFrame(estoque_atual)
        df = df.reset_index()
        df2 = pd.DataFrame()
        df2["Cartela"] = df["index"]           
        df2["Quantidade"] = df["Quantidade"]
        df2['Número'] = df2["Cartela"].str.extract('(\d+)').astype(int)
        df2 = df2.sort_values(by='Número').drop(columns='Número')
        #print("Print_tabela chamada")
        return df2
    
    @st.cache_data
    def buscar_clientes(_self):
        return AWS().buscar_clientes()
    
    @st.cache_data
    def buscar_id_pedidos_lojas(_self, empresa):
        return [pedido["S"] for pedido in AWS().buscar_id_pedidos_lojas(empresa)["L"]]