# Aracatuba Parafusos 🔨

Aplicação desenvolvida com **Streamlit** para gerenciamento de acessos, login, e telas personalizadas baseadas em permissões.

## Funcionalidades

- 🔒 Sistema de login com autenticação via **AWS API**.
- 🧩 Permissões de acesso personalizadas por nível de credencial.
- 📊 Interface responsiva e ampla (`layout="wide"`) para exibição das ferramentas.
- 📂 Integração com o componente `MultiplasTelas` para navegação entre diferentes módulos.

## Tecnologias Utilizadas

- **Python 3.12**
- **Streamlit** para a interface.
- **AWS** para autenticação e gerenciamento de credenciais.
- **JSON** para troca de dados.

## Estrutura do Código

### Classes Principais

#### `Iniciar`
Responsável pela lógica de autenticação e gerenciamento das telas.

- **Métodos**:
  - `check_credentials(username, password)`: Verifica as credenciais do usuário usando uma API AWS.
  - `main()`: Gerencia o fluxo principal, como login e redirecionamento.
  - `iniciar()`: Define os acessos com base na credencial e inicializa as telas do sistema.

### Dependências

- `MultiplasTelas`: Gerencia as telas da aplicação com base nas permissões do usuário.
- `AWS`: Classe utilizada para validar credenciais na API AWS.

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/aracatuba-parafusos.git

Configuração
Antes de executar a aplicação, configure as credenciais e permissões da API AWS no arquivo Aws_pedidos.py.

Uso
Acesse a página inicial e realize o login com suas credenciais.
Após o login bem-sucedido, as telas disponíveis serão exibidas com base no nível de acesso do usuário.
Navegue entre as funcionalidades, como controle de coleta, cadastro de empresa, ou dashboard.
Credenciais e Permissões
Os níveis de acesso são definidos da seguinte forma:

1 (Básico): Consulta de pedidos, cadastro de novo pedido, entre outros.

2 (Intermediário): Acesso a pedidos, separação, rotas, e catálogos.

3 (Avançado): Controle completo, incluindo coleta e rotas de clientes.

4 (Administrador): Acesso total a todas as funcionalidades.
Personalização

Para personalizar as telas ou as permissões de acesso:

Edite o método iniciar() na classe Iniciar.
Altere a lógica de credenciais conforme necessário.



