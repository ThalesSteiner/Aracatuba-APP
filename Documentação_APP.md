# Documentação das Bibliotecas

## 1. `streamlit as st`
O `streamlit` é uma biblioteca que permite criar interfaces de usuário interativas para aplicativos de dados. Ele facilita a construção de dashboards, visualizações e formulários de entrada para interagir com dados em tempo real.

---

## 2. `time`
A biblioteca `time` fornece funções para medir o tempo de execução de um programa, pausar a execução e manipular dados relacionados ao tempo, como atrasos e datas.

---

## 3. `pandas as pd`
O `pandas` é uma biblioteca de manipulação e análise de dados, amplamente utilizada para trabalhar com tabelas (DataFrames) e séries temporais. Ela oferece funções poderosas para filtrar, agrupar e transformar dados.

---

## 4. `numpy as np`
O `numpy` é uma biblioteca fundamental para computação científica em Python. Ela fornece suporte para arrays multidimensionais e funções matemáticas avançadas, permitindo operações eficientes com grandes conjuntos de dados.

---

## 5. `streamlit_extras.metric_cards import style_metric_cards`
Essa biblioteca oferece componentes adicionais para o Streamlit, permitindo a criação de cartões métricos estilizados para exibir indicadores de maneira visualmente atrativa.

---

## 6. `plotly.express as px`
O `plotly.express` é uma biblioteca de visualização de dados que facilita a criação de gráficos interativos, como gráficos de linha, barras, dispersão, mapas, entre outros, com poucas linhas de código.

---

## 7. `streamlit_extras.grid import grid`
Esta biblioteca adiciona funcionalidades extras ao Streamlit para exibir dados de forma organizada em um layout de grid, o que pode ser útil para tabelas e outras representações visuais de dados.

---

## 8. `boto3`
O `boto3` é a biblioteca oficial da Amazon Web Services (AWS) para Python. Ela fornece uma interface fácil de usar para interagir com os serviços da AWS, como S3, DynamoDB, EC2, entre outros.

---

## 9. `requests`
A biblioteca `requests` facilita o envio de requisições HTTP em Python, permitindo interagir com APIs web, fazer requisições GET, POST, PUT, DELETE, e manipular as respostas.

---

## 10. `datetime`
O `datetime` é uma biblioteca para manipulação de datas e horas. Ela permite operações como comparação de datas, formatação de datas e cálculos com intervalos de tempo.

---

## 11. `Aws_pedidos import AWS`
Esta biblioteca personalizada provavelmente oferece funcionalidades específicas para integrar e interagir com os serviços da AWS relacionados a pedidos, como o acesso a bancos de dados ou armazenamento de dados relacionados a pedidos.

---

## 12. `json`
A biblioteca `json` fornece ferramentas para trabalhar com dados no formato JSON (JavaScript Object Notation). Ela permite converter dados Python para JSON e vice-versa.

---

## 13. `folium`
O `folium` é uma biblioteca para criar mapas interativos com o Leaflet.js em Python. Ela permite adicionar marcadores, polígonos e outros elementos aos mapas, sendo útil para visualização geográfica.

---

## 14. `streamlit_folium import st_folium`
Essa biblioteca adiciona suporte para exibir mapas criados com o `folium` diretamente no Streamlit, permitindo integrar mapas interativos aos aplicativos.

---

## 15. `folium.plugins import MarkerCluster`
O `MarkerCluster` é um plugin do `folium` usado para agrupar marcadores em um mapa, o que ajuda a melhorar a visualização quando há muitos pontos de dados sobrepostos.

---

## 16. `Funções_APP import Funções`
Essa biblioteca personalizada provavelmente contém funções específicas para o aplicativo, como processamento de dados, validações ou outras operações necessárias para o fluxo do sistema.

---

## 17. `openpyxl`
O `openpyxl` é uma biblioteca para trabalhar com arquivos Excel (XLSX). Ela permite ler, escrever e manipular planilhas de forma eficiente, incluindo formatação, cálculos e manipulação de células.

---

## 18. `openpyxl.utils.dataframe import dataframe_to_rows`
Essa função do `openpyxl` converte um DataFrame do `pandas` em um formato de linha para inserção em uma planilha Excel.

---

## 19. `openpyxl.utils.get_column_letter`
Esta função do `openpyxl` converte números de colunas em letras, permitindo manipular referências de colunas no formato Excel (A, B, C, etc.).

---

## 20. `openpyxl.utils.range_boundaries`
A função `range_boundaries` é usada para obter as fronteiras de um intervalo de células no formato de coordenadas de planilha, facilitando operações como leitura ou escrita em intervalos específicos.

---

## 21. `geopy.distance import geodesic`
A biblioteca `geopy` fornece ferramentas para trabalhar com geolocalização. A função `geodesic` calcula a distância geodésica entre dois pontos na superfície da Terra.

---

## 22. `io.BytesIO`
A classe `BytesIO` da biblioteca `io` permite manipular dados binários em memória, funcionando como um arquivo, mas sem a necessidade de acessar o disco, útil para processar imagens e arquivos.

---

## 23. `PIL import Image`
A biblioteca `Pillow` (PIL) é usada para abrir, manipular e salvar arquivos de imagem em diversos formatos, como PNG, JPEG, GIF, entre outros.


# Sistema de Controle de Pedidos e Empresas

Este sistema permite o gerenciamento de pedidos e cadastro de empresas. Ele inclui funcionalidades de cadastro, consulta e edição de pedidos, além de permitir o cadastro e edição de empresas. Abaixo está a descrição das principais funcionalidades implementadas.

## Funcionalidades

### 1. **Controle de Coleta**

Permite ao usuário cadastrar e confirmar pedidos de coleta, informando detalhes como ID do pedido, data de recebimento, valor, status e forma de pagamento.

#### Campos:
- **ID da compra**
- **Data de recebimento**
- **Nome da empresa**
- **Valor do pedido**
- **Detalhe do pedido** (se algum débito ficou pendente)
- **Forma de pagamento**

#### Ações:
- Ao clicar no botão "Confirmar Ordens", o sistema armazena as informações no banco de dados (AWS).

---

### 2. **Consulta de Pedidos**

Esta seção permite ao usuário consultar os pedidos cadastrados. Existem duas opções de consulta:

#### 2.1 **Consulta de Débito**
- Pesquisa por pedidos não pagos. O usuário pode buscar pedidos que estão com débito.

#### 2.2 **Consulta de Pedido**
- Permite ao usuário consultar um pedido informando o ID ou selecionando uma empresa. O sistema exibe os detalhes do pedido, como status, valor, débito e forma de pagamento.

---

### 3. **Cadastro de Empresas**

Permite ao usuário cadastrar novas empresas ou consultar empresas já cadastradas. As informações de cada empresa incluem dados gerais e endereço.

#### Campos de Cadastro:
- **Nome/Razão Social**
- **Representante**
- **CPF/CNPJ**
- **Contatos** (telefone, whatsapp, email)
- **Endereço** (rua, número, bairro, cidade, UF, CEP, complemento)
- **Localização** (latitude e longitude)

#### Ações:
- Ao clicar em "Confirmar Cadastro", os dados da empresa são salvos na base de dados (AWS).

---

### 4. **Edição de Empresas**

Permite editar os dados de uma empresa já cadastrada, como status (ativo/inativo), nome, telefone, endereço, entre outros.

#### Campos de Edição:
- **Nome da empresa**
- **Status** (ativo ou inativo)
- **Telefone e email de contato**
- **Endereço completo**

#### Ações:
- Após editar os dados, o usuário pode salvar as alterações no banco de dados.

---

## Documentação das Funções

### `cadastro_novo_pedido`

#### Descrição
A função `cadastro_novo_pedido` permite o registro de um novo pedido através de um formulário interativo no Streamlit. O usuário deve inserir informações como a loja, data do pedido, tamanho das cartelas, a forma de venda e os valores das cartelas. Com base nas informações fornecidas, o sistema calcula a quantidade total de parafusos e o valor total do pedido.

#### Funcionalidade
- **Entrada de Dados**: O usuário preenche um formulário com os detalhes do pedido.
- **Cálculos Automáticos**: Calcula-se automaticamente a quantidade total de parafusos e o valor do pedido.
- **Validação**: Verifica se todos os campos obrigatórios foram preenchidos e se a quantidade mínima de 50 parafusos foi atendida.
- **Cadastro**: Salva o pedido no banco de dados (DynamoDB), incluindo informações como o ID, loja, data e tipo de venda.
- **Notificação**: Informa ao usuário se o pedido foi registrado com sucesso ou se há problemas com os dados fornecidos.

#### Fluxo de Uso
1. O usuário insere as informações do pedido (como tamanho das cartelas, loja, data, forma de venda e valores).
2. O sistema calcula automaticamente o total de parafusos e o valor total do pedido.
3. O usuário confirma o cadastro do pedido.
4. O pedido é registrado no banco de dados e uma notificação de sucesso ou erro é exibida.

---

### `Separar_pedido`

#### Descrição
A função `Separar_pedido` organiza e separa os pedidos registrados em uma planilha. O usuário fornece os IDs dos pedidos e a data de emissão da nota fiscal. Com essas informações, o sistema cria um arquivo Excel contendo os detalhes dos pedidos, como quantidade de parafusos, valores das cartelas e o total a ser pago.

#### Funcionalidade
- **Carregamento de Dados**: O sistema carrega os dados dos pedidos com base nos IDs fornecidos.
- **Geração de Planilha**: Insere as informações dos pedidos em uma planilha do Excel, incluindo os valores das cartelas e os totais.
- **Cálculos**: Realiza cálculos para determinar os totais de parafusos e valores de cada pedido.
- **Geração do Arquivo Excel**: O sistema gera o arquivo Excel com os detalhes dos pedidos e disponibiliza para download.

#### Fluxo de Uso
1. O usuário fornece os IDs dos pedidos e a data de emissão da nota fiscal.
2. O sistema recupera as informações dos pedidos e preenche a planilha.
3. O arquivo Excel gerado é disponibilizado para download, contendo todos os pedidos separados.

---

## Funcionalidades Adicionais

### 1. **Geração de Dados Simulados (`gerar_dado`)**
   - **Descrição**: Gera dados simulados de pedidos de parafusos para diversas lojas, incluindo informações de data, loja e quantidade de cada tipo de parafuso.
   - **Parâmetros**:
     - `_self`: Instância atual da classe.
     - `empresas`: Lista de lojas.
   - **Saída**: Lista de pedidos com detalhes de cada cartela de parafusos.
   - **Uso**: Esse método é chamado no `Dashboard` para simular e gerar os pedidos exibidos.

---

### 2. **Dashboard Interativo (`Dashboard`)**
   - **Descrição**: Exibe um dashboard com filtros para visualizar os pedidos simulados. Permite ao usuário filtrar por cidade, bairro, loja, mês e ano. Também exibe gráficos analíticos para os dados filtrados.
   - **Fluxo de Uso**:
     1. O usuário seleciona os filtros de cidade, bairro, loja, mês e ano.
     2. O botão "Pesquisar" aplica os filtros e exibe os resultados em tabelas e gráficos.
     3. São apresentados gráficos sobre o total de parafusos vendidos por cartela, data, loja, ano e mês.
   - **Componentes**:
     - **Filtros**: Multiselect para escolher cidade, bairro, loja, mês e ano.
     - **Gráficos**: Gráficos de barras e linhas usando Plotly para exibir a análise dos dados.
     - **Tabelas**: Exibição de dados detalhados em tabelas.

---

### 3. **Atualização de Estoque (`atualizar_estoque`)**
   - **Descrição**: Atualiza o estoque de parafusos nas lojas, ajustando a quantidade com base em pedidos feitos. O método também pode ser usado para ajustar o estoque de uma loja específica.
   - **Parâmetros**:
     - `df`: DataFrame contendo os dados do estoque.
     - `estoque`: Tipo de estoque a ser atualizado (ex: "Parafuso Cartela" ou "Parafuso Caixa").
     - `Id`: Identificador de um pedido específico para ajuste do estoque (opcional).
   - **Fluxo de Uso**:
     1. O usuário edita os dados de estoque ou insere um ID de pedido.
     2. O estoque é atualizado com os valores modificados.
     3. A interface é atualizada após a modificação do estoque.
   - **Saída**: Exibição de uma mensagem de sucesso e atualização dos dados na interface.

---

### 4. **Gestão de Estoque (`Estoque`)**
   - **Descrição**: Interface para visualização e edição do estoque de parafusos (cartela e caixa).
   - **Fluxo de Uso**:
     1. O usuário pode visualizar o estoque atual de cartelas e caixas.
     2. O usuário pode editar o estoque ou buscar um pedido específico para atualizar o estoque.
     3. Após a edição, o usuário clica no botão "Salvar estoque" para atualizar o estoque no sistema.

---

### 5. **Visualização de Rotas de Lojas (`Rotas`)**
   - **Descrição**: Exibe um mapa interativo com a localização das lojas com base nas coordenadas geográficas. A localização das lojas é filtrada por status, loja, bairro e cidade.
   - **Fluxo de Uso**:
     1. O usuário seleciona filtros para o status da loja, lojas específicas, bairros e cidades.
     2. As lojas filtradas são exibidas no mapa usando marcadores do Folium.
   - **Saída**: Exibição de um mapa interativo com a localização das lojas filtradas.

---

## Funções de Rotas

### `Rotas2`
#### Descrição
Calcula as distâncias entre a loja selecionada e outras lojas, exibindo-as em um mapa interativo.

#### Funcionalidade
- **Carregar Dados**: Carrega dados das lojas e bairros de uma região.
- **Interface com o Usuário**: Permite ao usuário selecionar uma loja e definir um raio de busca.
- **Cálculo de Distância**: Calcula as distâncias utilizando coordenadas geográficas e a biblioteca `geopy`.
- **Filtragem de Lojas**: Exibe lojas dentro do raio especificado no mapa.
- **Exibição no Mapa**: Exibe um mapa com as lojas filtradas e suas informações.



## Funções Faltantes

### `cadastro_novo_pedido`
#### Descrição
A função `cadastro_novo_pedido` permite ao usuário registrar novos pedidos de forma interativa, utilizando campos de entrada para fornecer detalhes como loja, data, tipo de venda e quantidade de parafusos. O sistema valida os dados e armazena as informações no banco de dados.

#### Funcionalidade
- **Entrada de Dados**: O usuário preenche um formulário com as informações do pedido.
- **Validação**: Verifica se todos os campos foram preenchidos corretamente e se a quantidade mínima foi atingida.
- **Armazenamento de Dados**: Após a validação, os dados do pedido são salvos no banco de dados.
- **Feedback ao Usuário**: Informa se o pedido foi registrado com sucesso ou se ocorreu algum erro.

---

### `editar_empresa`
#### Descrição
Permite ao usuário editar os dados de uma empresa previamente cadastrada no sistema. O usuário pode alterar informações como nome, telefone, endereço e status da empresa.

#### Funcionalidade
- **Busca de Empresa**: A empresa a ser editada é localizada por seu ID ou nome.
- **Edição de Dados**: O sistema permite alterar informações de cadastro como nome, telefone, endereço e status.
- **Armazenamento de Alterações**: Após a edição, as mudanças são salvas no banco de dados.
- **Validação de Dados**: O sistema verifica se as alterações são válidas antes de salvar.

---

### `consulta_debito`
#### Descrição
Permite ao usuário consultar os pedidos que estão com débito ou pendentes. O sistema exibe os pedidos com pagamentos em aberto.

#### Funcionalidade
- **Filtragem de Pedidos**: Exibe todos os pedidos com status de débito ou não pagos.
- **Exibição de Dados**: Apresenta uma tabela com detalhes dos pedidos, como valor, data e loja associada.
- **Validação**: Permite ao usuário validar e editar os dados conforme necessário.

---

### `gerar_dado`
#### Descrição
Gera dados simulados de pedidos para diferentes lojas. Esses dados são usados para realizar testes e gerar relatórios analíticos.

#### Funcionalidade
- **Entrada de Dados**: O usuário seleciona as lojas e o tipo de dado a ser gerado.
- **Simulação**: O sistema gera os dados conforme os parâmetros definidos (quantidade de parafusos, valor do pedido, etc.).
- **Armazenamento**: Os dados gerados são armazenados para uso posterior em relatórios ou consultas.

---

### `atualizar_estoque`
#### Descrição
Atualiza o estoque de parafusos de uma loja, ajustando a quantidade de parafusos disponíveis com base nos pedidos realizados.

#### Funcionalidade
- **Entrada de Dados**: O usuário fornece o ID do pedido e a quantidade de parafusos a ser atualizada.
- **Validação**: O sistema verifica se o estoque tem quantidade suficiente para atender ao pedido.
- **Atualização de Estoque**: Após a validação, o estoque é atualizado no banco de dados.

---

### `estados_estoque`
#### Descrição
Exibe e permite a edição do estoque de parafusos disponíveis nas lojas, incluindo os valores e quantidades de diferentes tipos de parafusos.

#### Funcionalidade
- **Exibição de Estoque**: O sistema exibe o estoque atual de cada tipo de parafuso (cartela, caixa, etc.).
- **Edição de Estoque**: Permite ao usuário editar as quantidades do estoque.
- **Armazenamento de Alterações**: Após a edição, os dados são salvos no banco de dados.

---

### `rotas_estoque`
#### Descrição
Calcula e exibe as rotas de distribuição de pedidos para diferentes lojas, considerando a localização e o estoque disponível.

#### Funcionalidade
- **Cálculo de Distância**: Calcula a distância entre as lojas e determina a rota mais eficiente para o envio de pedidos.
- **Exibição de Rotas**: Exibe um mapa com as rotas entre as lojas, utilizando coordenadas geográficas.
- **Otimize de Rota**: O sistema sugere a rota mais econômica ou eficiente para a distribuição de pedidos.

---

### `relatorio_vendas`
#### Descrição
Gera um relatório de vendas, considerando o total de pedidos, tipos de pagamento e dados de cada loja.

#### Funcionalidade
- **Entrada de Filtros**: O usuário pode aplicar filtros por período de tempo, loja, status de pagamento e outros parâmetros.
- **Geração de Relatório**: O sistema gera um relatório com os dados filtrados, apresentando gráficos e tabelas com as informações.
- **Exportação de Dados**: Permite exportar o relatório gerado para formatos como Excel ou PDF.

---

### `visualizar_rotas`
#### Descrição
Exibe as rotas de distribuição dos pedidos em um mapa, considerando a localização das lojas e os destinos dos pedidos.

#### Funcionalidade
- **Entrada de Filtros**: O usuário define filtros como cidade, bairro ou loja para visualizar as rotas.
- **Exibição no Mapa**: O sistema exibe um mapa interativo com as rotas entre as lojas.
- **Cálculo de Distâncias**: Utiliza coordenadas geográficas para calcular e exibir as distâncias e rotas.


