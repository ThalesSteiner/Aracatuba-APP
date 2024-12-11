# Documentação do Código

## Visão Geral

Este código implementa uma aplicação em **Streamlit** que inclui uma tela de login e controle de acesso com base nas credenciais dos usuários. Após o login bem-sucedido, o usuário é redirecionado para diferentes telas de acordo com seu nível de acesso. O sistema valida as credenciais por meio de uma API AWS.

### Estrutura de Arquivos

- **APP**: Módulo contendo a classe `MultiplasTelas`, responsável por gerenciar as diferentes telas que o usuário pode acessar.
- **Aws_pedidos**: Módulo que interage com a API AWS para validar as credenciais de login.

## Funções e Métodos

### Classe `Iniciar`

A classe `Iniciar` contém métodos responsáveis por verificar as credenciais do usuário e iniciar a aplicação com base no nível de acesso.

#### Método `__init__(self)`
Construtor da classe. Não realiza nenhuma ação.

#### Método `check_credentials(username, password)`
Função estática que valida as credenciais do usuário.

- **Parâmetros**:
  - `username`: Nome de usuário.
  - `password`: Senha do usuário.
  
- **Retorno**:
  - Retorna uma tupla com um valor booleano indicando sucesso ou falha e os dados do usuário (se validado) ou um código de erro.

- **Exceções**:
  - Trata exceções como `json.JSONDecodeError`, `KeyError`, e `IndexError` ao processar a resposta da API.

#### Método `main()`
Função estática que gerencia o fluxo principal da aplicação.

- **Descrição**:
  - Inicializa a variável de sessão `logged_in` para controle de login.
  - Exibe a tela de login e chama o método `check_credentials()` para validar as credenciais do usuário.
  - Se o login for bem-sucedido, o usuário é redirecionado para as telas apropriadas.

#### Método `iniciar()`
Função estática que determina quais telas o usuário pode acessar com base na sua credencial.

- **Descrição**:
  - Verifica a credencial do usuário armazenada na sessão e define a lista de telas que ele pode acessar.
  - Exibe as telas utilizando a classe `MultiplasTelas`.

### Controle de Sessão com `st.session_state`

A aplicação utiliza o objeto `st.session_state` do Streamlit para armazenar o estado do login e informações do usuário. As chaves principais são:
- `logged_in`: Indica se o usuário está logado.
- `user_info`: Armazena as informações do usuário após um login bem-sucedido.

### Fluxo de Execução

1. **Login**: 
   - O usuário insere seu nome de usuário e senha.
   - A aplicação chama o método `check_credentials()` para validar as credenciais.
   - Se o login for bem-sucedido, a sessão é atualizada e o fluxo é redirecionado para o método `iniciar()`.

2. **Tela Principal**:
   - Dependendo da credencial do usuário, são exibidas diferentes opções de telas.
   - A classe `MultiplasTelas` é chamada para renderizar as telas disponíveis com base nas permissões do usuário.
