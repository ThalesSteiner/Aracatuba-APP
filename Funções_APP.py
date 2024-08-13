from Aws_pedidos import AWS
import pandas as pd
import streamlit as st


class Funções:
    def __init__(self) -> None:
        pass
    
    def Exibir_pedido(self, pedido):
        mygrid = st.columns((2, 2, 2, 2))

        mygrid[0].text_input("Loja", value=pedido["Loja"])
        mygrid[1].text_input("ID", value=pedido["ID"])
        mygrid[2].text_input("Data", value=pedido["Data"])
        mygrid[3].text_input("Hora", value=pedido["Hora"])
        mygrid[0].text_input("Tipo de Venda", value=pedido["Tipo de Venda"])
        mygrid[1].text_input("Valor Cartela", value=pedido["Valor da cartela"])

        df = pd.DataFrame(list(pedido["Pedidos"].items()), columns=['Tamanho', 'Quantidade'])
        df['Quantidade'] = pd.to_numeric(df['Quantidade'])
        
        st.title("Tabela do Pedido")
        st.dataframe(df, width=400, height=600)
        
        mygrid[2].text_input("Quantidade de Parafusos", value=sum(df["Quantidade"]))
        mygrid[3].text_input("Valor total do pedido:", value=(sum(df["Quantidade"]) * float(pedido["Valor da cartela"])))