from Aws_pedidos import AWS
import pandas as pd
import streamlit as st
from streamlit_extras.grid import grid
import re
import os
import requests
from PyPDF2 import PdfMerger
from fpdf import FPDF
from io import BytesIO
from PIL import Image


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
    
    def baixar_imagem(self, url, nome):
        nome_seguro = re.sub(r'[\/:*?"<>|]', '', nome)
        caminho_imagem = os.path.join(self.imagem_pasta, f'Imagem_catalogo_{nome_seguro}.png')
        
        if not os.path.exists(caminho_imagem):
            response = requests.get(url)
            if response.status_code == 200:
                with open(caminho_imagem, 'wb') as f:
                    f.write(response.content)
        return caminho_imagem
    
    
    def gerar_pdf(self, codigos_selecionados):
        self.pdf = FPDF('L', 'mm', (200, 300))
        self.imagem_pasta = "imagens_catalogo"
        os.makedirs(self.imagem_pasta, exist_ok=True)
        produtos = AWS().buscar_produtos_catalogo()
        produtos_filtrados = sorted([produto for produto in produtos if produto['Codigo'] in codigos_selecionados], key=lambda p: p['Codigo'])
        
        categorias = {}
        for produto in produtos_filtrados:
            categorias.setdefault(produto['Tipo_material'], []).append(produto)
        
        x_offset, y_offset, colunas, linhas = 20, 40, 3, 2
        produtos_por_pagina = colunas * linhas
        
        for tipo, itens in categorias.items():
            for i, produto in enumerate(itens):
                if i % produtos_por_pagina == 0:
                    self.pdf.add_page()
                    self.pdf.set_font('Arial', 'B', 20)
                    self.pdf.cell(0, 10, f'{tipo}', ln=True, align='C')
                
                caminho_imagem = self.baixar_imagem(produto['link_imagem'], produto['Nome_produto'])
                x, y = x_offset + (i % colunas) * 85, y_offset + ((i // colunas) % linhas) * 65
                self.add_product(produto, x, y)


        catalogo_path = 'catalogo_produtos.pdf'
        self.pdf.output(catalogo_path)
        
        merger = PdfMerger()
        merger.append('Capa araçatuba.pdf')
        merger.append(catalogo_path)
        output_path = 'Catalogo_Aracatuba.pdf'
        merger.write(output_path)
        merger.close()
        
        return output_path
    
    def add_product(self, produto, x, y):
        nome, preco, codigo, imagem_url = produto['Nome_produto'], float(produto['Valor_produto']), produto['Codigo'], produto['link_imagem']
        caminho_imagem = self.baixar_imagem(imagem_url, nome)

        # Adicionar o retângulo de contorno do produto
        self.pdf.set_xy(x, y)
        self.pdf.cell(80, 60, border=1)
        
        # Adicionar a imagem do produto
        x_image, y_image = x + 15, y + 5
        self.pdf.image(caminho_imagem, x=x_image, y=y_image, w=50, h=35)
        
        # Adicionar nome, código e preço do produto
        self.pdf.set_xy(x, y + 45)
        self.pdf.set_font('Arial', '', 9)
        self.pdf.cell(80, 5, nome, ln=True, align='C')
        self.pdf.set_xy(x, y + 50)
        self.pdf.cell(80, 5, f'{codigo}', ln=True, align='C')
        self.pdf.set_xy(x, y + 55)
        self.pdf.set_text_color(255, 0, 0)
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.cell(80, 5, f'R${preco:.2f}', ln=True, align='C')
        self.pdf.set_text_color(0, 0, 0)
        
    def upload_image_to_s3(self, file, filename):
        try:
            self.s3.upload_fileobj(file, self.bucket_name, filename, ExtraArgs={'ACL': 'public-read'})
            url = f'https://{self.bucket_name}.s3.amazonaws.com/{filename}'
            return url
        except Exception as e:
            print(f"Erro ao enviar: {e}")
            return None

    def download_image_from_url(self, url):
        response = requests.get(url)
        response.raise_for_status()  # Levanta um erro para respostas 4xx ou 5xx
        return BytesIO(response.content)

    def save_image_locally(self, image_data, filename):
        image = Image.open(image_data)
        image.save(filename)
        return image

    def display_image(self, image, caption):
        st.image(image, caption=caption)