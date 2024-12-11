# Documentação da Classe `AWS`

## Introdução
A classe `AWS` fornece um conjunto de métodos para interagir com serviços da AWS, como DynamoDB e S3. Esta classe foi projetada para realizar operações CRUD (Criar, Ler, Atualizar, Deletar) em tabelas DynamoDB, além de gerenciar credenciais de conexão.

---

## Inicialização
A classe não possui argumentos obrigatórios em seu construtor.

```python
class AWS:
    def __init__(self):
        pass
```

---

## Métodos de Conexão

### `aws_conexão`
Estabelece uma conexão com o DynamoDB utilizando credenciais armazenadas na sessão.

#### Parâmetros
Nenhum.

#### Retorno
Instância do recurso `dynamodb`.

---

### `aws_conexão_client`
Estabelece uma conexão com o DynamoDB no nível de cliente.

#### Parâmetros
Nenhum.

#### Retorno
Instância do cliente `dynamodb`.

---

### `aws_conexão_s3`
Estabelece uma conexão com o serviço S3 utilizando credenciais armazenadas na sessão.

#### Parâmetros
Nenhum.

#### Retorno
Instância do cliente `s3`.

---

## Operações de Leitura

### `buscar_clientes`
Recupera a lista de clientes armazenada na tabela `Clientes_Lista`.

#### Retorno
Uma lista de clientes.

---

### `buscar_pedido_ID`
Busca um pedido na tabela `Pedidos_ID` com base em um `ID`.

#### Parâmetros
- `ID` (int): O identificador do pedido.

#### Retorno
Um dicionário com os detalhes do pedido ou `None` caso não seja encontrado.

---

### `buscar_pedido_controle_coleta`
Busca um pedido na tabela `Controle_Coleta` com base no `ID`.

#### Parâmetros
- `ID` (int): O identificador do pedido.

#### Retorno
Um dicionário com os detalhes do pedido ou `None` caso não seja encontrado.

---

### `buscar_cadastro_empresa`
Recupera os detalhes de uma empresa cadastrada na tabela `Cadastro_Cliente`.

#### Parâmetros
- `Nome` (str): O nome da empresa.

#### Retorno
Um dicionário com os detalhes da empresa ou `None` caso não seja encontrado.

---

### `buscar_Estoque`
Recupera os detalhes do estoque na tabela `Estoque_Parafusos`.

#### Parâmetros
- `Estoque` (str): O identificador do estoque.

#### Retorno
Um dicionário com os detalhes do estoque ou `None` caso não seja encontrado.

---

## Operações de Escrita

### `adicionar_cliente`
Adiciona um cliente na tabela `Clientes`.

#### Parâmetros
- `nome` (str): O nome do cliente.

#### Retorno
Nenhum.

---

### `adicionar_cliente_tabela_Cliente_lista`
Adiciona um cliente à lista de clientes na tabela `Clientes_Lista`.

#### Parâmetros
- `cliente_nome` (str): O nome do cliente.

#### Retorno
Resposta da atualização ou `None` em caso de erro.

---

### `adicionar_loja_tabela_pedidos`
Cadastra uma loja na tabela `Pedidos` com uma lista inicial de pedidos vazia.

#### Parâmetros
- `nome` (str): O nome da loja.

#### Retorno
Nenhum.

---

### `adicionar_pedido_tabela_pedidos`
Adiciona um pedido na tabela `Pedidos` associado a uma loja.

#### Parâmetros
- `nome_cliente` (str): O nome do cliente.
- `id` (int): O identificador do pedido.

#### Retorno
`"Sucesso"` ou `"Falha"`.

---

### `adicionar_pedido_tabela_pedidosID`
Adiciona um pedido na tabela `Pedidos_ID`.

#### Parâmetros
- `Pedido` (dict): Um dicionário representando o pedido.

#### Retorno
Nenhum.

---

### `adicionar_pedido_tabela_pedidos_gerais`
Adiciona um pedido na tabela `Pedidos_Gerais`.

#### Parâmetros
- `Data` (str): A data do pedido.
- `Id` (str): O identificador do pedido.
- `pedido` (dict): Os detalhes do pedido.

#### Retorno
Nenhum.

---

### `Adicionar_estoque_cartela`
Atualiza o estoque de parafusos na tabela `Estoque_Parafusos`.

#### Parâmetros
- `Estoque` (str): O nome do estoque.
- `Estoque_produto` (int): A quantidade a ser adicionada.

#### Retorno
Nenhum.

---

## Outros Métodos

### `adicionar_pedido_nao_pago`
Adiciona um pedido à lista de pedidos não pagos na tabela `Controle_Divida`.

#### Parâmetros
- `loja` (str): O nome da loja.
- `Id` (str): O identificador do pedido.

#### Retorno
Resposta da atualização ou `None` em caso de erro.

---

## Tratamento de Erros
Quase todos os métodos incluem blocos `try-except` para captura e exibição de erros. Caso ocorra um erro, uma mensagem é exibida no console e, em alguns casos, uma resposta `False` é retornada.

---

## Observações Gerais
1. As credenciais da AWS são recuperadas da sessão `st.session_state`.
2. As tabelas e atributos mencionados no código devem existir no DynamoDB para evitar erros.
3. O uso de credenciais sensíveis no código deve ser feito com cautela, garantindo boas práticas de segurança.

