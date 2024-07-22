import boto3
from boto3.dynamodb.conditions import Key, Attr
import requests
import json
import streamlit as st

class AWS:
    def __init__(self):
        pass
    
    def aws_conexão(self):
        st.session_state.user_info.get("aws_secret_access_key", "")
        aws_access_key_id = st.session_state.user_info.get("aws_access_key_id", "")
        aws_secret_access_key = st.session_state.user_info.get("aws_secret_access_key", "")
        region_name = 'us-east-1' 

        # Conectar ao DynamoDB usando as credenciais e a região fornecidas
        self.dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id  = aws_access_key_id,
            aws_secret_access_key  = aws_secret_access_key,
            region_name=region_name
        )
    
    def buscar_clientes(self):
        self.aws_conexão()
        table = self.dynamodb.Table('Clientes')
        response = table.scan()
        clientes = response['Items']
        #st.info("Empresas buscadas")
        return [cliente['Nome'] for cliente in clientes]

    def adicionar_cliente(self, nome):
        self.aws_conexão()
        table = self.dynamodb.Table('Clientes')
        table.put_item(
            Item={
                'Nome': nome
            }
        )
        print(f"Cliente {nome} adicionado com sucesso!")
    

    def adicionar_loja_tabela_pedidos(self, nome):
        self.aws_conexão()
        try:
            table = self.dynamodb.Table('Pedidos')
            response = table.put_item(
                Item={
                    'Nome': nome,
                    'Pedidos': []
                }
            )
            print(f"Cliente {nome} cadastrado com sucesso!")
        except Exception as e:
            print(f"Erro ao cadastrar cliente: {e}")
    
    
    def adicionar_pedido_tabela_pedidos(self, nome_cliente, Pedido):
        self.aws_conexão()
        try:
            table = self.dynamodb.Table('Pedidos')
            # Converta Pedido para string
            Pedido_str = str(Pedido)
            
            # Primeiro, verifica se o cliente já tem pedidos
            response = table.get_item(Key={'Nome': nome_cliente})
            if 'Item' not in response:
                # Se o cliente não existir, cria um novo item com a lista de pedidos
                table.put_item(Item={'Nome': nome_cliente, 'Pedidos': [Pedido_str]})
                print(f"Pedido '{Pedido_str}' adicionado ao novo cliente {nome_cliente}.")
            else:
                # Se o cliente já existir, atualiza a lista de pedidos
                table.update_item(
                    Key={'Nome': nome_cliente},
                    UpdateExpression='SET Pedidos = list_append(Pedidos, :pedido)',
                    ExpressionAttributeValues={
                        ':pedido': [Pedido_str]
                    },
                    ReturnValues='UPDATED_NEW'
                )
                print(f"Pedido '{Pedido_str}' adicionado ao cliente {nome_cliente}.")
            return "Sucesso"
        except Exception as e:
            print(f"Erro ao adicionar pedido: {e}")
            return "Falha"


    
    def adicionar_pedido_tabela_pedidosID(self, Pedido):
        print("-------------------------------")
        self.aws_conexão()
        try:
            table = self.dynamodb.Table("Pedidos_ID")
            table.put_item(Item=Pedido)
            print("Pedido adicionado com sucesso.")
        except Exception as e:
            print(f"Erro ao adicionar pedido: {e}")


        
    def Gerar_novo_id(self):
        self.aws_conexão()
        table = self.dynamodb.Table('Counters')
        response = table.update_item(
            Key={
                'CounterName': 'PurchaseID'
            },
            UpdateExpression='SET CounterValue = CounterValue + :inc',
            ExpressionAttributeValues={
                ':inc': 1
            },
            ReturnValues="UPDATED_NEW"
        )
        return response['Attributes']['CounterValue']

    def adicionar_usuario(self, Credencial):
        self.aws_conexão()
        try:
            table = self.dynamodb.Table('Usuario_senhas')
            response = table.put_item(
                Item=Credencial
            )
            print(f"Credencial {Credencial[0]} cadastrado com sucesso!")
        except Exception as e:
            print(f"Erro ao cadastrar cliente: {e}")
    
    def Validar_login(self, login, senha):
        self.aws_conexão()
        try:
            table = self.dynamodb.Table("Usuario_senhas")
            # Faça a chamada para consultar a tabela
            response = table.query(
                KeyConditionExpression=Key('Usuario').eq(login),
                FilterExpression=Attr('Senha').eq(senha)
            )

            # Verifique os itens retornados
            items = response.get('Items', [])
            if items:
                print("Item(s) encontrado(s):", items)
                return True
            else:
                print("Item não encontrado")
                return False
        except Exception as e:
            print(f"Erro ao validar cliente: {e}")
            return False
    
    def Validar_login_api(self, login):
        url = "https://ccgss8scpj.execute-api.us-east-1.amazonaws.com/Teste"
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, data=json.dumps(login), headers=headers)

        print(response.status_code)
        print(response.json())
        return response.json()
    
    