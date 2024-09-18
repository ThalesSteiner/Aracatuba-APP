from Aws_pedidos import AWS
import pandas as pd
import streamlit as st
from streamlit_extras.grid import grid

class Funções:
    def __init__(self) -> None:
        pass
    
    def Exibir_pedido(self, pedido):
        cartela_aco = [129, 130, 131, 132, 133]
        mygrid = grid(5, 5, vertical_align="bottom")
        valor_cartela = float(pedido["Valor da cartela"])
        valor_aco = float(pedido["valor da cartela aço"])
        # Exibe os dados do pedido em campos de entrada
        mygrid.text_input("Loja", value=pedido["Loja"])
        mygrid.text_input("ID", value=pedido["ID"])
        mygrid.text_input("Data", value=pedido["Data"])
        mygrid.text_input("Hora", value=pedido["Hora"])
        mygrid.text_input("Tipo de Venda", value=pedido["Tipo de Venda"])
        mygrid.text_input("Valor Cartela Normal", value=pedido["Valor da cartela"])
        mygrid.text_input("Valor Cartela de aço", value=valor_aco)

        # Converte os pedidos para um DataFrame e ajusta os tipos de dados
        df = pd.DataFrame(list(pedido["Pedidos"].items()), columns=['Tamanho', 'Quantidade'])
        df['Quantidade'] = pd.to_numeric(df['Quantidade'])

        # Exibe a tabela do pedido
        st.title("Tabela do Pedido")
        df = self.tabela_pedido_formatada(df)
        st.dataframe(df, width=400, height=600)

        # Calcula as quantidades de parafusos normais e de aço
        quantidade_p_aco = []
        for N_cartela, N_parafuso in pedido["Pedidos"].items():
            numero_cartela = int(N_cartela.split(" ")[1])
            if numero_cartela in cartela_aco:
                quantidade_p_aco.append(int(N_parafuso))

        # Calcula quantidades e valores
        quantidade_total = df["Quantidade"].sum()
        quantidade_aco = sum(quantidade_p_aco)
        quantidade_normal = quantidade_total - quantidade_aco


        valor_total = (quantidade_normal * valor_cartela) + (quantidade_aco * valor_aco)

        # Exibe as informações calculadas
        mygrid.text_input("Quantidade de Parafusos normais", value=int(quantidade_normal))
        mygrid.text_input("Quantidade de Parafusos Aço", value=int(quantidade_aco))
        mygrid.text_input("Valor total do pedido", value=f"R$ {valor_total:.2f}")
        
        
        
    
    def tabela_pedido_formatada(self, dataframe):
        # Formatando a tabela para exibição
        df = dataframe.reset_index(drop=True)
        df['Número'] = df['Tamanho'].str.extract(r'(\d+)').astype(int)
        df = df.sort_values(by='Número').drop(columns='Número')
        
        return df
    