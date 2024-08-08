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
    
    def aws_conexão_client(self):
        st.session_state.user_info.get("aws_secret_access_key", "")
        aws_access_key_id = st.session_state.user_info.get("aws_access_key_id", "")
        aws_secret_access_key = st.session_state.user_info.get("aws_secret_access_key", "")
        region_name = 'us-east-1' 

        # Conectar ao DynamoDB usando as credenciais e a região fornecidas
        self.dynamodb = boto3.client(
            'dynamodb',
            aws_access_key_id  = aws_access_key_id,
            aws_secret_access_key  = aws_secret_access_key,
            region_name=region_name
        )
    
    #Busca as lojas para enviar para o APP
    def buscar_clientes(self):
        self.aws_conexão()
        table = self.dynamodb.Table('Clientes_Lista')
        response = table.scan()
        clientes = response['Items']
        return clientes[0]["Clientes"]
    
    def buscar_pedido_ID(self, ID):
        self.aws_conexão()
        try:
            # Acessar a tabela
            tabela = self.dynamodb.Table('Pedidos_ID')

            # Executar a busca
            resposta = tabela.get_item(
                Key={
                    'ID': ID  # ID é do tipo número
                }
            )

            # Retornar o item encontrado ou None se não encontrado
            return resposta.get('Item')

        except Exception as e:
                print(f"Erro ao buscar item na tabela pedido id: {e}")
                return False

    def buscar_pedido_controle_coleta(self, ID):
        self.aws_conexão()
        try:
            # Acessar a tabela
            tabela = self.dynamodb.Table('Controle_Coleta')

            # Executar a busca
            resposta = tabela.get_item(
                Key={
                    'ID': str(ID)
                }
            )

            # Retornar o item encontrado ou None se não encontrado
            return resposta.get('Item')

        except Exception as e:
                print(f"Erro ao buscar item controle coleta: {e}")
                return False

    def buscar_cadastro_empresa(self, Nome):
        self.aws_conexão()
        try:
            # Acessar a tabela
            tabela = self.dynamodb.Table('Cadastro_Cliente')

            # Executar a busca
            resposta = tabela.get_item(
                Key={
                    'Nome': str(Nome)
                }
            )

            # Retornar o item encontrado ou None se não encontrado
            return resposta.get('Item')

        except Exception as e:
                print(f"Erro ao buscar empresa cadastro de empresa: {e}")
                return False
    
    def buscar_Estoque(self, Estoque):
        self.aws_conexão()
        try:
            # Acessar a tabela
            tabela = self.dynamodb.Table('Estoque_Parafusos')

            # Executar a busca
            resposta = tabela.get_item(
                Key={
                    'Estoque': str(Estoque),

                    
                }
            )

            # Retornar o item encontrado ou None se não encontrado
            return resposta.get('Item')

        except Exception as e:
                print(f"Erro ao buscar empresa cadastro de empresa: {e}")
                return False
    
    #Adiciona o cliente na tabela de cliente, Tabela usada para iniciar todas as lojas no sistema
    def adicionar_cliente(self, nome):
        self.aws_conexão()
        table = self.dynamodb.Table('Clientes')
        table.put_item(
            Item={
                'Nome': nome
            }
        )
        print(f"Cliente {nome} adicionado com sucesso!")


    def adicionar_cliente_tabela_Cliente_lista(self, cliente_nome):
        self.aws_conexão
        table = self.dynamodb.Table('Clientes_Lista')

        # Atualiza o item, adicionando o novo nome à lista
        response = table.update_item(
            Key={'ID': 'ListaClientes'},
            UpdateExpression="SET Clientes = list_append(if_not_exists(Clientes, :empty_list), :cliente_nome)",
            ExpressionAttributeValues={
                ':cliente_nome': [cliente_nome],
                ':empty_list': []
            },
            ReturnValues="UPDATED_NEW"
        )
        return response
    
    #Adiciona a cliente na tabela de Pedido para consultar todas as atividades do cliente
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
    
    #Adiciona Pedido no historico do cliente
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
            print(f"Erro ao adicionar pedido na tabela de pedidos: {e}")
            return "Falha"

    #Adiciona Pedido na tabela de Pedidos com id
    def adicionar_pedido_tabela_pedidosID(self, Pedido):
        self.aws_conexão()
        try:
            table = self.dynamodb.Table("Pedidos_ID")
            table.put_item(Item=Pedido)
            print("Pedido adicionado com sucesso.")
        except Exception as e:
            print(f"Erro ao adicionar pedido a tabela de pedidos ID: {e}")
    
    
    def adicionar_pedido_tabela_pedidos_gerais(self, Nome, Id, pedido):
        self.aws_conexão()
        try:
            table = self.dynamodb.Table("Pedidos_Gerais")
            table.put_item(Item={
                "Nome": str(Nome),
                "ID": str(Id),
                "Pedido": pedido})
            print("Pedido adicionado com sucesso.")
        except Exception as e:
            print(f"Erro ao adicionar pedido a tabela de pedidos ID: {e}")
  
    
    def Adicionar_estoque_cartela(self, Estoque, Estoque_produto):
        self.aws_conexão()
        try:
            table = self.dynamodb.Table("Estoque_Parafusos")
            table.put_item(Item={"Estoque": Estoque,
                                 "Quantidade": Estoque_produto})
            print("Pedido adicionado com sucesso.")
        except Exception as e:
            print(f"Erro ao adicionar pedido a tabela de Estoque: {e}")
    
    def Adicionar_cliente(self, Pedido):
        self.aws_conexão()
        try:
            table = self.dynamodb.Table("Pedidos_ID")
            table.put_item(Item=Pedido)
            print("Pedido adicionado com sucesso.")
        except Exception as e:
            print(f"Erro ao adicionar pedido: {e}")



    def adicionar_pedido_Controle_Coleta(self, Pedido):
        self.aws_conexão()
        try:
            table = self.dynamodb.Table("Controle_Coleta")
            table.put_item(Item=Pedido)
            print("Pedido adicionado com sucesso.")
        except Exception as e:
            print(f"Erro ao adicionar pedido: {e}")
    
    
    #Adiciona o Id do pedido em uma lista de pedidos não pagos     
    def adicionar_pedido_nao_pago(self, loja, Id):
        self.aws_conexão_client()
        try:
            response = self.dynamodb.update_item(
                TableName="Controle_Divida",
                Key={
                    'Loja': {'S': loja}
                },
                UpdateExpression="SET #pedidos = list_append(if_not_exists(#pedidos, :vazia), :pedido)",
                ExpressionAttributeNames={
                    '#pedidos': 'Pedidos_não_pagos'
                },
                ExpressionAttributeValues={
                    ':pedido': {'L': [{'S': Id}]},
                    ':vazia': {'L': []}  # Valor padrão caso o atributo não exista
                },
                ReturnValues="UPDATED_NEW"
            )
            return response
        except Exception as e:
            print(f"Erro ao Adicionar Id do pedido em Controle divida: {e}")
     
    def buscar_pedido_nao_pago(self):
        self.aws_conexão_client()
        # Define a chave do item que deseja buscar
        key = {
            'Loja': {'S': 'Aracatuba Parafusos'}
        }
        
        # Busca o item na tabela
        response = self.dynamodb.get_item(
            TableName='Controle_Divida',
            Key=key
        )
        return response['Item']['Pedidos_não_pagos']['L']
            
    #Retira o Id do pedido em uma lista de pedidos não pagos 
    def remover_pedido_nao_pago(self, loja, pedido_id):
        self.aws_conexão_client()
        try:
            pedidos_nao_pagos = self.buscar_pedido_nao_pago()
            print(f"Pedidos não pagos antes da remoção: {pedidos_nao_pagos}")
            
            pedidos_nao_pagos_list = [item['S'] for item in pedidos_nao_pagos]
            if pedido_id in pedidos_nao_pagos_list:
                pedidos_nao_pagos_list.remove(pedido_id)
                
                # Converte de volta para o formato DynamoDB
                pedidos_nao_pagos_ddb_format = [{'S': pid} for pid in pedidos_nao_pagos_list]
                
                # Atualiza a tabela com a lista modificada
                self.dynamodb.put_item(
                    TableName="Controle_Divida",
                    Item={
                        'Loja': {'S': loja},
                        'Pedidos_não_pagos': {'L': pedidos_nao_pagos_ddb_format}
                    }
                )
                print("Pedido removido com sucesso.")
            else:
                print("ID do pedido não encontrado")
                
        except Exception as e:
            print(f"Erro ao remover ID do pedido em Controle_Divida: {e}")

    
    
    #Gera um novo ID para o pedido que vai para tabela de pedidos com ID
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
    
    #Validar login usando api gateway na função lambda
    def Validar_login_api(self, login):
        url = "https://ccgss8scpj.execute-api.us-east-1.amazonaws.com/Teste"
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url, data=json.dumps(login), headers=headers)
        return response.json()
    
    #Cadastra as informações dos clientes
    def cadastro_cliente_endereço(self, endereço):
        self.aws_conexão()
        try:
            table = self.dynamodb.Table('Cadastro_Cliente')
            response = table.put_item(
                Item=endereço
            )
            print(f"Endereço cadastrado com sucesso!")
        except Exception as e:
            print(f"Erro ao cadastrar cliente: {e}")
    