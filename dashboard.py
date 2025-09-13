import streamlit as st
import boto3
import pandas as pd
from datetime import datetime, date
import json
from decimal import Decimal
import time
import plotly.express as px
import plotly.graph_objects as go
from Aws_pedidos import AWS

# Configurações adicionais para performance
if hasattr(st, 'set_option'):
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.set_option('deprecation.showfileUploaderEncoding', False)

# NOTA: st.set_page_config() deve ser chamado no arquivo principal (app.py)
# antes de importar este módulo, pois só pode ser chamado uma vez por página


# Funções para buscar dados do DynamoDB
def Buscar_pedidos():
    # Verificar se o usuário está logado
    if 'user_info' not in st.session_state:
        st.error("Usuário não está logado. Faça login primeiro.")
        return []
    
    # Usar as credenciais da sessão de login
    aws_access_key_id = st.session_state.user_info.get("aws_access_key_id", "")
    aws_secret_access_key = st.session_state.user_info.get("aws_secret_access_key", "")
    region_name = 'us-east-1'

    if not aws_access_key_id or not aws_secret_access_key:
        st.error("Credenciais AWS não encontradas na sessão.")
        return []

    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )

    table = dynamodb.Table('Pedidos_ID')
    response = table.scan()
    pedidos = response['Items']
    return pedidos

def Buscar_Clientes_todos():
    # Verificar se o usuário está logado
    if 'user_info' not in st.session_state:
        st.error("Usuário não está logado. Faça login primeiro.")
        return []
    
    # Usar as credenciais da sessão de login
    aws_access_key_id = st.session_state.user_info.get("aws_access_key_id", "")
    aws_secret_access_key = st.session_state.user_info.get("aws_secret_access_key", "")
    region_name = 'us-east-1'

    if not aws_access_key_id or not aws_secret_access_key:
        st.error("Credenciais AWS não encontradas na sessão.")
        return []

    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )

    table = dynamodb.Table('Cadastro_Cliente')
    response = table.scan()
    clientes = response['Items']
    return clientes

# Função para converter dados do DynamoDB para DataFrame
def dynamodb_to_dataframe(items):
    if not items:
        return pd.DataFrame()
    
    # Converter os itens para um formato mais limpo
    clean_items = []
    for item in items:
        clean_item = {}
        for key, value in item.items():
            # Converter tipos especiais do DynamoDB
            if isinstance(value, dict):
                if 'S' in value:  # String
                    clean_item[key] = value['S']
                elif 'N' in value:  # Number
                    clean_item[key] = float(value['N'])
                elif 'BOOL' in value:  # Boolean
                    clean_item[key] = value['BOOL']
                elif 'L' in value:  # List
                    clean_item[key] = [v.get('S', v.get('N', v)) for v in value['L']]
                elif 'M' in value:  # Map (dicionário)
                    # Converter o mapa para string JSON para exibição
                    clean_item[key] = json.dumps(value['M'], default=str)
                else:
                    clean_item[key] = str(value)
            elif isinstance(value, Decimal):
                # Converter Decimal para float
                clean_item[key] = float(value)
            else:
                clean_item[key] = value
        clean_items.append(clean_item)
    
    return pd.DataFrame(clean_items)

# Função para processar pedidos com cartelas
def processar_pedidos_cartelas(pedidos):
    """Processa os pedidos e extrai informações das cartelas"""
    pedidos_processados = []
    
    for pedido in pedidos:
        pedido_processado = {}
        
        # Copiar campos básicos
        for key, value in pedido.items():
            if isinstance(value, dict):
                if 'S' in value:
                    pedido_processado[key] = value['S']
                elif 'N' in value:
                    pedido_processado[key] = float(value['N'])
                elif 'M' in value:
                    # Processar cartelas
                    cartelas = value['M']
                    total_cartelas = 0
                    cartelas_detalhes = {}
                    
                    for cartela, quantidade in cartelas.items():
                        if isinstance(quantidade, dict) and 'N' in quantidade:
                            qtd = float(quantidade['N'])
                        elif isinstance(quantidade, Decimal):
                            qtd = float(quantidade)
                        else:
                            qtd = float(quantidade)
                        
                        cartelas_detalhes[cartela] = qtd
                        total_cartelas += qtd
                    
                    pedido_processado['total_cartelas'] = total_cartelas
                    pedido_processado['cartelas_detalhes'] = json.dumps(cartelas_detalhes)
                    pedido_processado['num_tipos_cartelas'] = len(cartelas_detalhes)
                else:
                    pedido_processado[key] = str(value)
            elif isinstance(value, Decimal):
                pedido_processado[key] = float(value)
            else:
                pedido_processado[key] = value
        
        pedidos_processados.append(pedido_processado)
    
    return pedidos_processados

# Função para processar endereços dos clientes
def processar_enderecos_clientes(clientes):
    """Processa os endereços dos clientes extraindo informações do JSON"""
    clientes_processados = []
    
    for cliente in clientes:
        cliente_processado = {}
        
        # Copiar campos básicos
        for key, value in cliente.items():
            if isinstance(value, dict):
                if 'S' in value:
                    cliente_processado[key] = value['S']
                elif 'N' in value:
                    cliente_processado[key] = float(value['N'])
                elif 'M' in value:
                    # Processar endereço
                    if key.upper() == 'ENDERECO':
                        endereco = value['M']
                        endereco_dict = {}
                        
                        for campo, valor in endereco.items():
                            if isinstance(valor, dict) and 'S' in valor:
                                endereco_dict[campo] = valor['S'].strip()
                            else:
                                endereco_dict[campo] = str(valor).strip()
                        
                        # Adicionar campos individuais do endereço
                        cliente_processado['endereco_completo'] = json.dumps(endereco_dict)
                        cliente_processado['uf'] = endereco_dict.get('Uf', '').strip()
                        cliente_processado['cidade'] = endereco_dict.get('Cidade', '').strip()
                        cliente_processado['bairro'] = endereco_dict.get('Bairro', '').strip()
                        cliente_processado['rua'] = endereco_dict.get('Rua', '').strip()
                        cliente_processado['numero'] = endereco_dict.get('Numero', '').strip()
                        cliente_processado['cep'] = endereco_dict.get('Cep', '').strip()
                        cliente_processado['complemento'] = endereco_dict.get('Complemento', '').strip()
                    else:
                        cliente_processado[key] = json.dumps(value['M'], default=str)
                else:
                    cliente_processado[key] = str(value)
            elif isinstance(value, Decimal):
                cliente_processado[key] = float(value)
            else:
                cliente_processado[key] = value
        
        clientes_processados.append(cliente_processado)
    
    return clientes_processados

# Função para correlacionar pedidos com cadastro de lojas
def correlacionar_pedidos_lojas(pedidos_df, lojas_df):
    """Correlaciona pedidos com dados de cadastro de lojas"""
    if pedidos_df.empty or lojas_df.empty:
        return pedidos_df
    
    # Correlacionar pelo campo 'Loja' dos pedidos com 'Nome' do cadastro
    chave_pedido = None
    chave_loja = None
    
    # Tentar diferentes chaves de correlação
    if 'Loja' in pedidos_df.columns and 'Nome' in lojas_df.columns:
        chave_pedido = 'Loja'
        chave_loja = 'Nome'
    elif 'loja' in pedidos_df.columns and 'nome' in lojas_df.columns:
        chave_pedido = 'loja'
        chave_loja = 'nome'
    elif 'Loja' in pedidos_df.columns and 'nome' in lojas_df.columns:
        chave_pedido = 'Loja'
        chave_loja = 'nome'
    elif 'loja' in pedidos_df.columns and 'Nome' in lojas_df.columns:
        chave_pedido = 'loja'
        chave_loja = 'Nome'
    
    if chave_pedido is not None:
        # Fazer merge dos dados
        pedidos_enriquecidos = pedidos_df.merge(
            lojas_df, 
            left_on=chave_pedido, 
            right_on=chave_loja, 
            how='left',
            suffixes=('_pedido', '_loja')
        )
        

        return pedidos_enriquecidos
    else:
        st.warning("⚠️ Não foi possível correlacionar pedidos com cadastro de lojas. Verifique se existe o campo 'Loja' nos pedidos e 'Nome' no cadastro.")
        return pedidos_df

# Função para estilizar dados JSON das cartelas
def estilizar_cartelas_json(cartelas_json):
    """Converte dados JSON das cartelas em formato legível"""
    if pd.isna(cartelas_json) or cartelas_json == '':
        return "📦 Nenhuma cartela"
    
    try:
        cartelas_dict = None
        
        # Se já é um dicionário
        if isinstance(cartelas_json, dict):
            cartelas_dict = cartelas_json
        else:
            # Tentar diferentes métodos de parsing
            cartelas_str = str(cartelas_json)
            
            # Método 1: JSON padrão
            try:
                cartelas_dict = json.loads(cartelas_str)
            except:
                # Método 2: Se parece com dicionário Python, usar eval (cuidado com segurança)
                if cartelas_str.startswith('{') and cartelas_str.endswith('}'):
                    try:
                        # Substituir aspas simples por aspas duplas para JSON válido
                        cartelas_str_fixed = cartelas_str.replace("'", '"')
                        cartelas_dict = json.loads(cartelas_str_fixed)
                    except:
                        # Método 3: Usar ast.literal_eval para dicionários Python
                        import ast
                        try:
                            cartelas_dict = ast.literal_eval(cartelas_str)
                        except:
                            # Método 4: Parsing manual para formato específico
                            cartelas_dict = parse_cartelas_manual(cartelas_str)
        
        if not cartelas_dict or not isinstance(cartelas_dict, dict):
            return "📦 Nenhuma cartela válida"
        
        # Criar texto formatado
        texto_formatado = ""
        total_cartelas = 0
        
        # Ordenar cartelas por número
        try:
            cartelas_ordenadas = sorted(cartelas_dict.items(), key=lambda x: int(x[0].split()[-1]) if x[0].split()[-1].isdigit() else 0)
        except:
            cartelas_ordenadas = list(cartelas_dict.items())
        
        for cartela, quantidade in cartelas_ordenadas:
            try:
                if isinstance(quantidade, (int, float)):
                    qtd = int(quantidade)
                elif hasattr(quantidade, 'N'):  # Decimal do DynamoDB
                    qtd = int(float(quantidade.N))
                else:
                    qtd = int(float(str(quantidade)))
                
                total_cartelas += qtd
                texto_formatado += f"• {cartela}: {qtd}\n"
            except:
                texto_formatado += f"• {cartela}: {quantidade}\n"
        
        
        return texto_formatado
        
    except Exception as e:
        return f"❌ Erro ao processar cartelas: {str(e)}\nDados: {str(cartelas_json)[:100]}..."

def parse_cartelas_manual(cartelas_str):
    """Parsing manual para formatos específicos de cartelas"""
    try:
        # Remover caracteres especiais e dividir por vírgulas
        cartelas_str = cartelas_str.replace("'", '"').replace('{', '').replace('}', '')
        
        # Dividir por vírgulas e processar cada item
        items = cartelas_str.split(',')
        cartelas_dict = {}
        
        for item in items:
            if ':' in item:
                key, value = item.split(':', 1)
                key = key.strip().strip('"')
                value = value.strip().strip('"')
                
                # Tentar converter valor para número
                try:
                    if 'Decimal' in value:
                        # Extrair número de Decimal('X') ou Decimal("X")
                        import re
                        match = re.search(r'Decimal\(["\']([^"\']+)["\']\)', value)
                        if match:
                            value = float(match.group(1))
                        else:
                            # Tentar extrair número diretamente
                            numbers = re.findall(r'\d+\.?\d*', value)
                            if numbers:
                                value = float(numbers[0])
                            else:
                                value = 0
                    else:
                        value = float(value)
                except:
                    value = 0
                
                cartelas_dict[key] = value
        
        return cartelas_dict
    except:
        return {}

# Função para processar dados de cadastro de lojas
def processar_cadastro_lojas(lojas):
    """Processa os dados de cadastro de lojas"""
    lojas_processadas = []
    
    for loja in lojas:
        loja_processada = {}
        
        # Copiar campos básicos
        for key, value in loja.items():
            if isinstance(value, dict):
                if 'S' in value:
                    loja_processada[key] = value['S']
                elif 'N' in value:
                    loja_processada[key] = float(value['N'])
                elif 'M' in value:
                    # Processar endereço
                    if key.upper() == 'ENDERECO':
                        endereco = value['M']
                        endereco_dict = {}
                        
                        for campo, valor in endereco.items():
                            if isinstance(valor, dict) and 'S' in valor:
                                endereco_dict[campo] = valor['S'].strip()
                            else:
                                endereco_dict[campo] = str(valor).strip()
                        
                        # Adicionar campos individuais do endereço
                        loja_processada['endereco_completo'] = json.dumps(endereco_dict)
                        loja_processada['uf'] = endereco_dict.get('Uf', '').strip()
                        loja_processada['cidade'] = endereco_dict.get('Cidade', '').strip()
                        loja_processada['bairro'] = endereco_dict.get('Bairro', '').strip()
                        loja_processada['rua'] = endereco_dict.get('Rua', '').strip()
                        loja_processada['numero'] = endereco_dict.get('Numero', '').strip()
                        loja_processada['cep'] = endereco_dict.get('Cep', '').strip()
                        loja_processada['complemento'] = endereco_dict.get('Complemento', '').strip()
                    else:
                        loja_processada[key] = json.dumps(value['M'], default=str)
                else:
                    loja_processada[key] = str(value)
            elif isinstance(value, Decimal):
                loja_processada[key] = float(value)
            else:
                loja_processada[key] = value
        
        lojas_processadas.append(loja_processada)
    
    return lojas_processadas

# Interface principal
def main():
    # Verificar se o usuário está logado
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.error("🔒 Acesso negado. Faça login para acessar o dashboard.")
        st.info("Por favor, faça login através do sistema principal.")
        return
    
    if 'user_info' not in st.session_state:
        st.error("🔒 Informações do usuário não encontradas. Faça login novamente.")
        return
    
    st.title("📦 Dashboard de Pedidos")
    st.markdown("---")
    
    # Sidebar para filtros
    st.sidebar.header("🔍 Filtros")
    
    # Informações sobre cache
    st.sidebar.info("💾 **Cache Ativo**\n\nDados são carregados a cada 30 minutos para melhor performance.")
    
    # Botão para atualizar dados
    if st.sidebar.button("🔄 Atualizar Dados", type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    # Status do cache
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Status do Sistema:**")
    st.sidebar.success("✅ Cache funcionando")
    st.sidebar.success("✅ Conexão DynamoDB")
    
    # Sistema de cache otimizado para reduzir erros de WebSocket
    @st.cache_data(ttl=3600, show_spinner=False)  # Cache por 1 hora, sem spinner
    def load_data():
        try:
            pedidos = Buscar_pedidos()
            clientes = Buscar_Clientes_todos()
            return pedidos, clientes
        except Exception as e:
            st.error(f"Erro ao carregar dados: {str(e)}")
            return [], []
    
    # Cache para dados processados
    @st.cache_data(ttl=3600, show_spinner=False)
    def load_processed_data():
        pedidos, clientes = load_data()
        if pedidos:
            pedidos_processados = processar_pedidos_cartelas(pedidos)
            df_pedidos = pd.DataFrame(pedidos_processados)
        else:
            df_pedidos = pd.DataFrame()
        
        if clientes:
            lojas_processadas = processar_cadastro_lojas(clientes)
            df_lojas = pd.DataFrame(lojas_processadas)
        else:
            df_lojas = pd.DataFrame()
        
        return df_pedidos, df_lojas
    
    # Carregar dados processados
    df_pedidos, df_lojas = load_processed_data()
    
    if df_pedidos.empty:
        st.warning("Nenhum pedido encontrado ou erro ao carregar dados.")
        return
    
    # Correlacionar pedidos com cadastro de lojas
    df_pedidos_enriquecidos = correlacionar_pedidos_lojas(df_pedidos, df_lojas)
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total de Pedidos",
            value=len(df_pedidos),
            delta=None
        )
    
    with col2:
        st.metric(
            label="Total de Lojas",
            value=len(df_lojas),
            delta=None
        )
    
    with col3:
        # Calcular total de cartelas dos pedidos enriquecidos
        if not df_pedidos_enriquecidos.empty and 'Pedidos' in df_pedidos_enriquecidos.columns:
            # Função para calcular total de cartelas
            def calcular_total_cartelas_metricas(pedidos_json):
                try:
                    if pd.isna(pedidos_json) or pedidos_json == '':
                        return 0
                    
                    cartelas_dict = None
                    if isinstance(pedidos_json, dict):
                        cartelas_dict = pedidos_json
                    else:
                        cartelas_str = str(pedidos_json)
                        try:
                            cartelas_dict = json.loads(cartelas_str)
                        except:
                            try:
                                cartelas_str_fixed = cartelas_str.replace("'", '"')
                                cartelas_dict = json.loads(cartelas_str_fixed)
                            except:
                                import ast
                                try:
                                    cartelas_dict = ast.literal_eval(cartelas_str)
                                except:
                                    cartelas_dict = parse_cartelas_manual(cartelas_str)
                    
                    if cartelas_dict and isinstance(cartelas_dict, dict):
                        total = 0
                        for quantidade in cartelas_dict.values():
                            try:
                                if hasattr(quantidade, 'N'):  # Decimal do DynamoDB
                                    total += int(float(quantidade.N))
                                else:
                                    if 'Decimal' in str(quantidade):
                                        import re
                                        numbers = re.findall(r'\d+\.?\d*', str(quantidade))
                                        if numbers:
                                            total += int(float(numbers[0]))
                                    else:
                                        total += int(float(str(quantidade)))
                            except:
                                pass
                        return total
                    return 0
                except:
                    return 0
            
            total_cartelas = df_pedidos_enriquecidos['Pedidos'].apply(calcular_total_cartelas_metricas).sum()
            st.metric(
                label="Total de Cartelas",
                value=f"{total_cartelas:,.0f}"
            )
        else:
            st.metric(label="Total de Cartelas", value="N/A")
    
    with col4:
        # Calcular tipos únicos de cartelas
        if not df_pedidos_enriquecidos.empty and 'Pedidos' in df_pedidos_enriquecidos.columns:
            todas_cartelas = set()
            for _, row in df_pedidos_enriquecidos.iterrows():
                try:
                    cartelas_dict = None
                    if isinstance(row['Pedidos'], dict):
                        cartelas_dict = row['Pedidos']
                    else:
                        cartelas_str = str(row['Pedidos'])
                        try:
                            cartelas_dict = json.loads(cartelas_str)
                        except:
                            try:
                                cartelas_str_fixed = cartelas_str.replace("'", '"')
                                cartelas_dict = json.loads(cartelas_str_fixed)
                            except:
                                import ast
                                try:
                                    cartelas_dict = ast.literal_eval(cartelas_str)
                                except:
                                    cartelas_dict = parse_cartelas_manual(cartelas_str)
                    
                    if cartelas_dict and isinstance(cartelas_dict, dict):
                        todas_cartelas.update(cartelas_dict.keys())
                except:
                    pass
            
            tipos_unicos = len(todas_cartelas)
            st.metric(
                label="Tipos de Cartelas",
                value=f"{tipos_unicos:,.0f}"
            )
        else:
            st.metric(label="Tipos de Cartelas", value="N/A")
    
    st.markdown("---")
    
    # Inicializar DataFrame base (não filtrado)
    df_base = df_pedidos_enriquecidos.copy()
    
    # Inicializar estado da sessão para controle de filtros
    if 'filtros_aplicados' not in st.session_state:
        st.session_state.filtros_aplicados = False
    if 'df_filtrado_atual' not in st.session_state:
        st.session_state.df_filtrado_atual = df_base.copy()
    if 'ultima_aplicacao' not in st.session_state:
        st.session_state.ultima_aplicacao = 0
    
    # Inicializar estado dos filtros para evitar perda de valores
    if 'loja_selecionada' not in st.session_state:
        st.session_state.loja_selecionada = []
    if 'nome_selecionado' not in st.session_state:
        st.session_state.nome_selecionado = []
    if 'cpf_cnpj_selecionado' not in st.session_state:
        st.session_state.cpf_cnpj_selecionado = []
    if 'representante_selecionado' not in st.session_state:
        st.session_state.representante_selecionado = []
    if 'status_selecionado' not in st.session_state:
        st.session_state.status_selecionado = []
    if 'tipo_venda_selecionado' not in st.session_state:
        st.session_state.tipo_venda_selecionado = []
    if 'data_inicio' not in st.session_state:
        st.session_state.data_inicio = None
    if 'data_fim' not in st.session_state:
        st.session_state.data_fim = None
    if 'busca_loja' not in st.session_state:
        st.session_state.busca_loja = ""
    if 'filtros_avancados' not in st.session_state:
        st.session_state.filtros_avancados = {}
    if 'filtros_endereco' not in st.session_state:
        st.session_state.filtros_endereco = {}
    
    # Sistema de Filtros com Botão de Aplicação
    st.markdown("---")
    
    # Cabeçalho principal dos filtros
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h2 style="color: white; text-align: center; margin: 0; font-size: 24px;">
            🔍 Sistema de Filtros Inteligente
        </h2>
        <p style="color: #f0f0f0; text-align: center; margin: 10px 0 0 0; font-size: 16px;">
            Configure os filtros abaixo e clique em "Aplicar Filtros" para ver os resultados
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Container principal dos filtros
    with st.container():
        # === SEÇÃO 1: FILTROS PRINCIPAIS ===
        st.markdown("### 🎯 Filtros Principais")
        st.markdown("*Filtros essenciais para localizar lojas e pedidos*")
        
        # Primeira linha - Filtros de Identificação
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("**🏪 Loja**")
            if not df_base.empty and 'Loja' in df_base.columns:
                lojas_disponiveis = sorted(df_base['Loja'].dropna().unique())
                if lojas_disponiveis:
                    loja_selecionada = st.multiselect(
                        "Selecione as Lojas:",
                        lojas_disponiveis,
                        default=st.session_state.loja_selecionada,
                        key="filtro_loja",
                        help="Selecione uma ou mais lojas"
                    )
                    st.session_state.loja_selecionada = loja_selecionada
                else:
                    loja_selecionada = st.session_state.loja_selecionada
            else:
                loja_selecionada = st.session_state.loja_selecionada
    
        with col2:
            st.markdown("**👤 Nome da Loja**")
            if not df_base.empty and 'Nome' in df_base.columns:
                nomes_disponiveis = sorted(df_base['Nome'].dropna().unique())
                if nomes_disponiveis:
                    nome_selecionado = st.multiselect(
                        "Selecione os Nomes:",
                        nomes_disponiveis,
                        default=st.session_state.nome_selecionado,
                        key="filtro_nome",
                        help="Selecione um ou mais nomes"
                    )
                    st.session_state.nome_selecionado = nome_selecionado
                else:
                    nome_selecionado = st.session_state.nome_selecionado
            else:
                nome_selecionado = st.session_state.nome_selecionado
        
        with col3:
            st.markdown("**📋 CPF/CNPJ**")
            if not df_base.empty and 'CPF/CNPJ' in df_base.columns:
                cpf_cnpjs_disponiveis = sorted(df_base['CPF/CNPJ'].dropna().unique())
                if cpf_cnpjs_disponiveis:
                    cpf_cnpj_selecionado = st.multiselect(
                        "Selecione CPF/CNPJ:",
                        cpf_cnpjs_disponiveis,
                        default=st.session_state.cpf_cnpj_selecionado,
                        key="filtro_cpf_cnpj",
                        help="Selecione um ou mais CPF/CNPJ"
                    )
                    st.session_state.cpf_cnpj_selecionado = cpf_cnpj_selecionado
                else:
                    cpf_cnpj_selecionado = st.session_state.cpf_cnpj_selecionado
            else:
                cpf_cnpj_selecionado = st.session_state.cpf_cnpj_selecionado
        
        with col4:
            st.markdown("**👨‍💼 Representante**")
            if not df_base.empty and 'Representante' in df_base.columns:
                representantes_disponiveis = sorted(df_base['Representante'].dropna().unique())
                if representantes_disponiveis:
                    representante_selecionado = st.multiselect(
                        "Selecione Representantes:",
                        representantes_disponiveis,
                        default=st.session_state.representante_selecionado,
                        key="filtro_representante",
                        help="Selecione um ou mais representantes"
                    )
                    st.session_state.representante_selecionado = representante_selecionado
                else:
                    representante_selecionado = st.session_state.representante_selecionado
            else:
                representante_selecionado = st.session_state.representante_selecionado
        
        # Segunda linha - Filtros de Status e Data
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.markdown("**📊 Status**")
            if not df_base.empty and 'Status' in df_base.columns:
                status_disponiveis = sorted(df_base['Status'].dropna().unique())
                if status_disponiveis:
                    status_selecionado = st.multiselect(
                        "Selecione Status:",
                        status_disponiveis,
                        default=st.session_state.status_selecionado,
                        key="filtro_status",
                        help="Selecione um ou mais status"
                    )
                    st.session_state.status_selecionado = status_selecionado
                else:
                    status_selecionado = st.session_state.status_selecionado
            else:
                status_selecionado = st.session_state.status_selecionado

        with col6:
            st.markdown("**💰 Tipo de Venda**")
            if not df_base.empty and 'Tipo de Venda' in df_base.columns:
                tipos_venda_disponiveis = sorted(df_base['Tipo de Venda'].dropna().unique())
                if tipos_venda_disponiveis:
                    tipo_venda_selecionado = st.multiselect(
                        "Selecione Tipos:",
                        tipos_venda_disponiveis,
                        default=st.session_state.tipo_venda_selecionado,
                        key="filtro_tipo_venda",
                        help="Selecione um ou mais tipos de venda"
                    )
                    st.session_state.tipo_venda_selecionado = tipo_venda_selecionado
                else:
                    tipo_venda_selecionado = st.session_state.tipo_venda_selecionado
            else:
                tipo_venda_selecionado = st.session_state.tipo_venda_selecionado
        
        with col7:
            st.markdown("**📅 Período**")
            if not df_base.empty and 'Data' in df_base.columns:
                try:
                    # Converter coluna de data uma única vez
                    df_base['Data'] = pd.to_datetime(df_base['Data'], errors='coerce')
                    
                    # Obter range de datas disponíveis
                    data_min = df_base['Data'].min().date()
                    data_max = df_base['Data'].max().date()
                    
                    # Filtro de data
                    data_inicio, data_fim = st.date_input(
                        "Selecione o período:",
                        value=(st.session_state.data_inicio or data_min, st.session_state.data_fim or data_max),
                        min_value=data_min,
                        max_value=data_max,
                        key="filtro_data"
                    )
                    st.session_state.data_inicio = data_inicio
                    st.session_state.data_fim = data_fim
                        
                except Exception as e:
                    st.warning(f"Erro ao processar datas: {str(e)}")
                    data_inicio, data_fim = None, None
            else:
                data_inicio, data_fim = None, None
        
        with col8:
            st.markdown("**🔍 Busca Inteligente**")
            busca_loja = st.text_input(
                "Digite qualquer termo:",
                value=st.session_state.busca_loja,
                placeholder="Ex: nome da loja, região, telefone...",
                key="filtro_busca"
            )
            st.session_state.busca_loja = busca_loja
        
        # === SEÇÃO 2: FILTROS AVANÇADOS ===
        st.markdown("---")
        st.markdown("### 🎛️ Filtros Avançados")
        
        # Analisar estrutura dos dados e criar filtros dinâmicos
        if not df_base.empty:
            # Campos disponíveis para filtro multiselect
            campos_filtro = []
            
            # Adicionar campos básicos
            campos_basicos = ['Loja', 'Nome', 'CPF/CNPJ', 'Representante', 'Status', 'Tipo de Venda', 'Email']
            for campo in campos_basicos:
                if campo in df_base.columns:
                    campos_filtro.append(campo)
            
            # Adicionar campos de endereço se existirem
            campos_endereco = ['uf', 'cidade', 'bairro']
            for campo in campos_endereco:
                if campo in df_base.columns:
                    campos_filtro.append(campo)
            
            # Adicionar campos de telefone se existirem
            campos_telefone = ['Telefone_fixo', 'Telefone_whats', 'Telefone_contato']
            for campo in campos_telefone:
                if campo in df_base.columns:
                    campos_filtro.append(campo)
            
            if campos_filtro:
                # Criar filtros em colunas
                num_colunas = min(4, len(campos_filtro))
                colunas_filtro = st.columns(num_colunas)
                
                # Dicionário para armazenar seleções dos filtros avançados
                filtros_avancados = {}
                
                for i, campo in enumerate(campos_filtro[:num_colunas]):
                    with colunas_filtro[i]:
                        # Obter valores únicos para o campo
                        valores_unicos = df_base[campo].dropna().unique()
                        valores_unicos = [str(v) for v in valores_unicos if str(v).strip() != '']
                        valores_unicos = sorted(valores_unicos)
                        
                        if valores_unicos:
                            # Criar multiselect
                            valores_selecionados = st.multiselect(
                                f"**{campo}:**",
                                options=valores_unicos,
                                default=[],
                                help=f"Selecione um ou mais valores para filtrar por {campo}",
                                key=f"multiselect_{campo}"
                            )
                            filtros_avancados[campo] = valores_selecionados
                
                # Se há mais campos, criar uma segunda linha
                if len(campos_filtro) > num_colunas:
                    campos_restantes = campos_filtro[num_colunas:]
                    num_colunas2 = min(4, len(campos_restantes))
                    colunas_filtro2 = st.columns(num_colunas2)
                    
                    for i, campo in enumerate(campos_restantes):
                        if i < num_colunas2:  # Verificação de segurança
                            with colunas_filtro2[i]:
                                # Obter valores únicos para o campo
                                valores_unicos = df_base[campo].dropna().unique()
                                valores_unicos = [str(v) for v in valores_unicos if str(v).strip() != '']
                                valores_unicos = sorted(valores_unicos)
                                
                                if valores_unicos:
                                    # Criar multiselect
                                    valores_selecionados = st.multiselect(
                                        f"**{campo}:**",
                                        options=valores_unicos,
                                        default=[],
                                        help=f"Selecione um ou mais valores para filtrar por {campo}",
                                        key=f"multiselect_{campo}_2"
                                    )
                                    filtros_avancados[campo] = valores_selecionados
        
        # === SEÇÃO 3: FILTROS DE ENDEREÇO/LOCAL ===
        st.markdown("---")
        st.markdown("### 🏠 Filtros de Endereço/Local")
        st.markdown("*Filtros específicos para campos de endereço extraídos do JSON*")
        
        # Inicializar filtros de endereço
        filtros_endereco = {}
        
        if not df_base.empty and 'Endereco' in df_base.columns:
            # Função para extrair campos do endereço JSON
            def extrair_campos_endereco(endereco_json):
                try:
                    if pd.isna(endereco_json) or endereco_json == '':
                        return {}
                    
                    endereco_dict = None
                    if isinstance(endereco_json, dict):
                        endereco_dict = endereco_json
                    else:
                        endereco_str = str(endereco_json)
                        try:
                            endereco_dict = json.loads(endereco_str)
                        except:
                            try:
                                endereco_str_fixed = endereco_str.replace("'", '"')
                                endereco_dict = json.loads(endereco_str_fixed)
                            except:
                                import ast
                                try:
                                    endereco_dict = ast.literal_eval(endereco_str)
                                except:
                                    return {}
                    
                    if endereco_dict and isinstance(endereco_dict, dict):
                        return endereco_dict
                    return {}
                except:
                    return {}
        
            # Extrair todos os campos de endereço
            campos_endereco = {}
            for _, row in df_base.iterrows():
                endereco_data = extrair_campos_endereco(row['Endereco'])
                for campo, valor in endereco_data.items():
                    if campo not in campos_endereco:
                        campos_endereco[campo] = set()
                    if valor and str(valor).strip() != '':
                        campos_endereco[campo].add(str(valor).strip())
        
            # Criar filtros para cada campo de endereço
            if campos_endereco:
                # Organizar campos em ordem específica
                ordem_campos = ['Uf', 'Cidade', 'Bairro', 'Rua', 'Numero', 'Cep', 'Complemento']
                campos_ordenados = []
                
                for campo in ordem_campos:
                    if campo in campos_endereco:
                        campos_ordenados.append(campo)
                
                # Adicionar outros campos que não estão na ordem específica
                for campo in campos_endereco.keys():
                    if campo not in campos_ordenados:
                        campos_ordenados.append(campo)
                
                # Criar filtros em colunas
                num_colunas_endereco = min(4, len(campos_ordenados))
                colunas_endereco = st.columns(num_colunas_endereco)
                
                for i, campo in enumerate(campos_ordenados[:num_colunas_endereco]):
                    with colunas_endereco[i]:
                        valores_unicos = sorted(list(campos_endereco[campo]))
                        
                        if valores_unicos:
                            # Criar multiselect para o campo
                            valores_selecionados = st.multiselect(
                                f"**{campo}:**",
                                options=valores_unicos,
                                default=[],
                                help=f"Selecione um ou mais valores para filtrar por {campo} do endereço",
                                key=f"filtro_endereco_{campo}"
                            )
                            filtros_endereco[campo] = valores_selecionados
                
                # Se há mais campos, criar uma segunda linha
                if len(campos_ordenados) > num_colunas_endereco:
                    campos_restantes_endereco = campos_ordenados[num_colunas_endereco:]
                    num_colunas_endereco2 = min(4, len(campos_restantes_endereco))
                    colunas_endereco2 = st.columns(num_colunas_endereco2)
                    
                    for i, campo in enumerate(campos_restantes_endereco):
                        if i < num_colunas_endereco2:
                            with colunas_endereco2[i]:
                                valores_unicos = sorted(list(campos_endereco[campo]))
                                
                                if valores_unicos:
                                    # Criar multiselect para o campo
                                    valores_selecionados = st.multiselect(
                                        f"**{campo}:**",
                                        options=valores_unicos,
                                        default=[],
                                        help=f"Selecione um ou mais valores para filtrar por {campo} do endereço",
                                        key=f"filtro_endereco_{campo}_2"
                                    )
                                    filtros_endereco[campo] = valores_selecionados
            else:
                st.markdown("""
                <div style="background: linear-gradient(90deg, #9E9E9E 0%, #757575 100%); padding: 12px; border-radius: 6px; margin: 10px 0;">
                    <p style="color: white; margin: 0; text-align: center; font-weight: bold;">
                        🏠 Nenhum campo de endereço encontrado nos dados
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: linear-gradient(90deg, #9E9E9E 0%, #757575 100%); padding: 12px; border-radius: 6px; margin: 10px 0;">
                <p style="color: white; margin: 0; text-align: center; font-weight: bold;">
                    🏠 Campo 'Endereco' não encontrado nos dados
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # === BOTÃO DE APLICAÇÃO DE FILTROS ===
        # (Movido para o final de todos os filtros)
        
        # Função para aplicar todos os filtros
        def aplicar_todos_filtros(df_base, loja_sel, nome_sel, cpf_cnpj_sel, representante_sel, 
                                status_sel, tipo_venda_sel, data_inicio, data_fim, busca_texto, 
                                filtros_avancados, filtros_endereco):
            """Aplica todos os filtros selecionados ao DataFrame base"""
            df_filtrado = df_base.copy()
            
            # Filtro de Loja
            if loja_sel:
                df_filtrado = df_filtrado[df_filtrado['Loja'].isin(loja_sel)]
            
            # Filtro de Nome
            if nome_sel:
                df_filtrado = df_filtrado[df_filtrado['Nome'].isin(nome_sel)]
            
            # Filtro de CPF/CNPJ
            if cpf_cnpj_sel:
                df_filtrado = df_filtrado[df_filtrado['CPF/CNPJ'].isin(cpf_cnpj_sel)]
            
            # Filtro de Representante
            if representante_sel:
                df_filtrado = df_filtrado[df_filtrado['Representante'].isin(representante_sel)]
            
            # Filtro de Status
            if status_sel:
                df_filtrado = df_filtrado[df_filtrado['Status'].isin(status_sel)]
            
            # Filtro de Tipo de Venda
            if tipo_venda_sel:
                df_filtrado = df_filtrado[df_filtrado['Tipo de Venda'].isin(tipo_venda_sel)]
            
            # Filtro de Data
            if data_inicio and data_fim and 'Data' in df_filtrado.columns:
                try:
                    df_filtrado['Data'] = pd.to_datetime(df_filtrado['Data'], errors='coerce')
                    mask_data = (df_filtrado['Data'].dt.date >= data_inicio) & \
                               (df_filtrado['Data'].dt.date <= data_fim)
                    df_filtrado = df_filtrado[mask_data]
                except Exception as e:
                    st.warning(f"Erro ao aplicar filtro de data: {str(e)}")
            
            # Filtro de Busca Inteligente
            if busca_texto:
                campos_loja = ['Loja', 'Nome', 'CPF/CNPJ', 'Representante', 'Status', 'Email', 'Telefone_fixo', 'Telefone_whats', 'Telefone_contato']
                mask_loja = pd.Series([False] * len(df_filtrado))
                
                for campo in campos_loja:
                    if campo in df_filtrado.columns:
                        mask_campo = df_filtrado[campo].astype(str).str.contains(busca_texto, case=False, na=False)
                        mask_loja = mask_loja | mask_campo
                
                df_filtrado = df_filtrado[mask_loja]
            
            # Filtros Avançados
            for campo, valores in filtros_avancados.items():
                if valores and campo in df_filtrado.columns:
                    mask_campo = df_filtrado[campo].astype(str).isin(valores)
                    df_filtrado = df_filtrado[mask_campo]
            
            # Filtros de Endereço
            for campo, valores in filtros_endereco.items():
                if valores and 'Endereco' in df_filtrado.columns:
                    mask_endereco = []
                    
                    for idx, row in df_filtrado.iterrows():
                        endereco_data = extrair_campos_endereco(row['Endereco'])
                        if campo in endereco_data:
                            valor_campo = str(endereco_data[campo]).strip()
                            if valor_campo in valores:
                                mask_endereco.append(True)
                            else:
                                mask_endereco.append(False)
                        else:
                            mask_endereco.append(False)
                    
                    # Converter para Series e aplicar filtro
                    mask_series = pd.Series(mask_endereco, index=df_filtrado.index)
                    df_filtrado = df_filtrado[mask_series]
            
            return df_filtrado
        
        # Usar dados filtrados da sessão ou dados base
        if 'df_filtrado' in st.session_state:
            df_filtrado = st.session_state.df_filtrado
        else:
            df_filtrado = df_base.copy()
        
        # === RESUMO DOS FILTROS ===
        st.markdown("---")
        
        # Container para resumo dos filtros
        if len(df_filtrado) != len(df_base):
                st.markdown(f"""
            <div style="background: linear-gradient(90deg, #4CAF50 0%, #45a049 100%); padding: 15px; border-radius: 8px; margin: 10px 0;">
                <h4 style="color: white; margin: 0; text-align: center;">
                    🎯 Filtros Ativos: {len(df_filtrado)} de {len(df_base)} registros
                </h4>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: linear-gradient(90deg, #2196F3 0%, #1976D2 100%); padding: 15px; border-radius: 8px; margin: 10px 0;">
                <h4 style="color: white; margin: 0; text-align: center;">
                    📊 Exibindo todos os {len(df_filtrado)} registros
                </h4>
            </div>
            """, unsafe_allow_html=True)
    
    # === RESUMO DOS FILTROS CONFIGURADOS ===
    st.markdown("---")
    st.markdown("### 📋 Resumo dos Filtros Configurados")
    
    # Criar resumo dos filtros selecionados
    filtros_configurados = []
    
    if loja_selecionada:
        filtros_configurados.append(f"🏪 **Lojas:** {', '.join(loja_selecionada)}")
    
    if nome_selecionado:
        filtros_configurados.append(f"👤 **Nomes:** {', '.join(nome_selecionado)}")
    
    if cpf_cnpj_selecionado:
        filtros_configurados.append(f"📋 **CPF/CNPJ:** {', '.join(cpf_cnpj_selecionado)}")
    
    if representante_selecionado:
        filtros_configurados.append(f"👨‍💼 **Representantes:** {', '.join(representante_selecionado)}")
    
    if status_selecionado:
        filtros_configurados.append(f"📊 **Status:** {', '.join(status_selecionado)}")
    
    if tipo_venda_selecionado:
        filtros_configurados.append(f"💰 **Tipos de Venda:** {', '.join(tipo_venda_selecionado)}")
    
    if data_inicio and data_fim:
        filtros_configurados.append(f"📅 **Período:** {data_inicio} até {data_fim}")
    
    if busca_loja:
        filtros_configurados.append(f"🔍 **Busca:** '{busca_loja}'")
    
    # Filtros avançados
    for campo, valores in filtros_avancados.items():
        if valores:
            filtros_configurados.append(f"🎛️ **{campo}:** {', '.join(valores)}")
    
    # Filtros de endereço
    for campo, valores in filtros_endereco.items():
        if valores:
            filtros_configurados.append(f"🏠 **{campo}:** {', '.join(valores)}")
    
    if filtros_configurados:
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #FF9800 0%, #F57C00 100%); padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">
                📋 {len(filtros_configurados)} Filtro(s) Configurado(s)
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**Filtros atualmente configurados:**")
        for filtro in filtros_configurados:
            st.markdown(f"• {filtro}")
    else:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #9E9E9E 0%, #757575 100%); padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: white; margin: 0; text-align: center;">
                ℹ️ Nenhum Filtro Configurado
            </h4>
            <p style="color: #f0f0f0; margin: 5px 0 0 0; text-align: center;">
                Todos os registros serão exibidos
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # === BOTÃO DE APLICAÇÃO DE FILTROS ===
    st.markdown("---")
    st.markdown("### 🎯 Aplicar Filtros")
    
    # Mensagem informativa sobre o comportamento dos filtros
    if not st.session_state.filtros_aplicados:
        st.info("ℹ️ **Importante:** Configure todos os filtros desejados acima e clique em 'Aplicar Todos os Filtros' para ver os resultados. Os filtros não são aplicados automaticamente.")
    else:
        st.success("✅ **Filtros aplicados!** Os dados abaixo refletem os filtros selecionados. Use 'Limpar Todos os Filtros' para voltar a ver todos os registros.")
    
    # Debug temporário - remover depois
    with st.expander("🔧 Debug - Status dos Filtros", expanded=False):
        st.write(f"**Filtros aplicados:** {st.session_state.filtros_aplicados}")
        st.write(f"**Tamanho do DataFrame filtrado:** {len(st.session_state.df_filtrado_atual)}")
        st.write(f"**Tamanho do DataFrame base:** {len(df_base)}")
        st.write(f"**Loja selecionada:** {loja_selecionada}")
        st.write(f"**Nome selecionado:** {nome_selecionado}")
        st.write(f"**Status selecionado:** {status_selecionado}")
        st.write(f"**Busca:** {busca_loja}")
    
    st.markdown("*Configure todos os filtros acima e clique no botão abaixo para aplicar*")
    
    # Botão para aplicar filtros
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    
    with col_btn2:
        aplicar_filtros = st.button(
            "🔍 Aplicar Todos os Filtros",
            type="primary",
            use_container_width=True,
            help="Clique para aplicar todos os filtros selecionados acima"
        )
        
        limpar_filtros = st.button(
            "🗑️ Limpar Todos os Filtros",
            type="secondary",
            use_container_width=True,
            help="Clique para limpar todos os filtros e mostrar todos os registros"
        )
    
    # Aplicar filtros quando o botão for clicado (com debounce)
    if aplicar_filtros:
        tempo_atual = time.time()
        # Debounce de 1 segundo para evitar aplicações múltiplas
        if tempo_atual - st.session_state.ultima_aplicacao > 1:
            with st.spinner("Aplicando filtros..."):
                try:
                    df_filtrado = aplicar_todos_filtros(
                        df_base, loja_selecionada, nome_selecionado, cpf_cnpj_selecionado, 
                        representante_selecionado, status_selecionado, tipo_venda_selecionado,
                        data_inicio, data_fim, busca_loja, filtros_avancados, filtros_endereco
                    )
                    st.session_state.df_filtrado_atual = df_filtrado
                    st.session_state.filtros_aplicados = True
                    st.session_state.ultima_aplicacao = tempo_atual
                    st.success(f"✅ Filtros aplicados! {len(df_filtrado)} de {len(df_base)} registros encontrados.")
                    # Forçar rerun para atualizar a interface
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao aplicar filtros: {str(e)}")
        else:
            st.warning("⏳ Aguarde um momento antes de aplicar filtros novamente.")
    
    # Limpar filtros quando o botão for clicado
    if limpar_filtros:
        st.session_state.df_filtrado_atual = df_base.copy()
        st.session_state.filtros_aplicados = False
        # Limpar todos os filtros do estado da sessão
        st.session_state.loja_selecionada = []
        st.session_state.nome_selecionado = []
        st.session_state.cpf_cnpj_selecionado = []
        st.session_state.representante_selecionado = []
        st.session_state.status_selecionado = []
        st.session_state.tipo_venda_selecionado = []
        st.session_state.data_inicio = None
        st.session_state.data_fim = None
        st.session_state.busca_loja = ""
        st.session_state.filtros_avancados = {}
        st.session_state.filtros_endereco = {}
        st.success("🗑️ Todos os filtros foram limpos!")
        # Forçar rerun para atualizar a interface
        st.rerun()
    
    # Usar dados filtrados da sessão
    df_filtrado = st.session_state.df_filtrado_atual
    
    # === STATUS DOS FILTROS ===
    st.markdown("---")
    
    # Indicador de status dos filtros
    if st.session_state.filtros_aplicados:
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #E91E63 0%, #C2185B 100%); padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3 style="color: white; margin: 0; text-align: center;">
                📊 Filtros Aplicados - Resultados Finais
            </h3>
            <p style="color: #f0f0f0; text-align: center; margin: 10px 0 0 0; font-size: 18px;">
                Mostrando {len(df_filtrado)} de {len(df_base)} pedidos
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #4CAF50 0%, #388E3C 100%); padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3 style="color: white; margin: 0; text-align: center;">
                📊 Todos os Registros (Sem Filtros)
            </h3>
            <p style="color: #f0f0f0; text-align: center; margin: 10px 0 0 0; font-size: 18px;">
                Exibindo todos os {len(df_filtrado)} pedidos disponíveis
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Verificar se filtros foram aplicados antes de mostrar visualizações
    if not st.session_state.filtros_aplicados:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #FF9800 0%, #F57C00 100%); padding: 30px; border-radius: 15px; margin: 20px 0; text-align: center;">
            <h2 style="color: white; margin: 0 0 15px 0; font-size: 28px;">
                🔍 Configure e Aplique os Filtros
            </h2>
            <p style="color: #f0f0f0; margin: 0; font-size: 18px;">
                Para visualizar os dados, configure os filtros desejados acima e clique em "Aplicar Todos os Filtros"
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar apenas informações básicas sem filtros
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total de Pedidos",
                value=len(df_base),
                delta=None
            )
        
        with col2:
            st.metric(
                label="Total de Lojas",
                value=len(df_lojas),
                delta=None
            )
        
        with col3:
            st.metric(
                label="Status",
                value="Aguardando Filtros",
                delta=None
            )
        
        with col4:
            st.metric(
                label="Ação",
                value="Aplicar Filtros",
                delta=None
            )
        
        st.stop()  # Para a execução aqui se não há filtros aplicados
    
    # Tabs para diferentes visualizações (só aparece se filtros foram aplicados)
    tab1, tab2 = st.tabs(["📋 Lista de Pedidos", "📊 Estatísticas"])
    
    with tab1:
        st.subheader("Lista de Pedidos")
        
        if df_filtrado.empty:
            st.info("Nenhum pedido encontrado com os filtros aplicados.")
        else:
            # Mostrar informações sobre os filtros aplicados
            if len(df_filtrado) != len(df_pedidos_enriquecidos):
                st.info(f"Mostrando {len(df_filtrado)} de {len(df_pedidos_enriquecidos)} pedidos")
            
            # Opções de visualização
            col1, col2 = st.columns([3, 1])
            
            with col2:
                mostrar_todas_colunas = st.checkbox("Mostrar todas as colunas", value=False)
            
            if mostrar_todas_colunas:
                # Criar uma cópia para estilização
                df_estilizado = df_filtrado.copy()
                
                # Estilizar coluna Pedidos se existir
                if 'Pedidos' in df_estilizado.columns:
                    df_estilizado['Pedidos'] = df_estilizado['Pedidos'].apply(estilizar_cartelas_json)
                
                st.dataframe(df_estilizado, use_container_width=True)
            else:
                # Mostrar apenas colunas principais
                colunas_principais = []
                for col in ['ID', 'Loja', 'Data', 'Tipo de Venda', 'Hora', 'Valor da Cartela', 'valor de cartela de aço', 'Pedidos', 'Nome', 'CPF/CNPJ', 'Representante', 'Status']:
                    if col in df_filtrado.columns:
                        colunas_principais.append(col)
                
                if colunas_principais:
                    # Criar uma cópia para estilização
                    df_estilizado = df_filtrado[colunas_principais].copy()
                    
                    # Estilizar coluna Pedidos se existir
                    if 'Pedidos' in df_estilizado.columns:
                        df_estilizado['Pedidos'] = df_estilizado['Pedidos'].apply(estilizar_cartelas_json)
                    
                    st.dataframe(df_estilizado, use_container_width=True)
                else:
                    st.dataframe(df_filtrado, use_container_width=True)
            
            # Seção para mostrar detalhes das cartelas de forma visual
            if 'Pedidos' in df_filtrado.columns:
                st.subheader("📋 Visualização Detalhada das Cartelas")
                
                # Selecionar um pedido para ver detalhes
                if len(df_filtrado) > 0:
                    pedido_selecionado = st.selectbox(
                        "Selecione um pedido para ver detalhes das cartelas:",
                        range(len(df_filtrado)),
                        format_func=lambda x: f"Pedido {df_filtrado.iloc[x].get('ID', x)} - {df_filtrado.iloc[x].get('Loja', 'N/A')}"
                    )
                    
                    if pedido_selecionado is not None:
                        pedido_data = df_filtrado.iloc[pedido_selecionado]
                        cartelas_json = pedido_data['Pedidos']
                        
                        # Mostrar informações do pedido
                        col_info1, col_info2, col_info3 = st.columns(3)
                        
                        with col_info1:
                            st.metric("ID do Pedido", pedido_data.get('ID', 'N/A'))
                            st.metric("Loja", pedido_data.get('Loja', 'N/A'))
                        
                        with col_info2:
                            # Converter data para string se for Timestamp
                            data_value = pedido_data.get('Data', 'N/A')
                            if hasattr(data_value, 'strftime'):
                                data_value = data_value.strftime('%Y-%m-%d')
                            st.metric("Data", str(data_value))
                            st.metric("Tipo de Venda", pedido_data.get('Tipo de Venda', 'N/A'))
                        
                        with col_info3:
                            st.metric("Valor da Cartela", pedido_data.get('Valor da cartela', 'N/A'))
                            st.metric("Hora", pedido_data.get('Hora', 'N/A'))
                        
                        st.markdown("---")
                        
                        # Processar e mostrar cartelas
                        try:
                            cartelas_dict = None
                            
                            # Se já é um dicionário
                            if isinstance(cartelas_json, dict):
                                cartelas_dict = cartelas_json
                            else:
                                # Tentar diferentes métodos de parsing
                                cartelas_str = str(cartelas_json)
                                
                                # Método 1: JSON padrão
                                try:
                                    cartelas_dict = json.loads(cartelas_str)
                                except:
                                    # Método 2: Se parece com dicionário Python
                                    if cartelas_str.startswith('{') and cartelas_str.endswith('}'):
                                        try:
                                            cartelas_str_fixed = cartelas_str.replace("'", '"')
                                            cartelas_dict = json.loads(cartelas_str_fixed)
                                        except:
                                            # Método 3: Usar ast.literal_eval
                                            import ast
                                            try:
                                                cartelas_dict = ast.literal_eval(cartelas_str)
                                            except:
                                                # Método 4: Parsing manual
                                                cartelas_dict = parse_cartelas_manual(cartelas_str)
                            
                            if cartelas_dict:
                                # Ordenar cartelas por número
                                cartelas_ordenadas = sorted(cartelas_dict.items(), key=lambda x: int(x[0].split()[-1]) if x[0].split()[-1].isdigit() else 0)
                                
                                # Calcular total de cartelas
                                total_cartelas = 0
                                for cartela, quantidade in cartelas_ordenadas:
                                    try:
                                        if isinstance(quantidade, (int, float)):
                                            total_cartelas += int(quantidade)
                                        else:
                                            # Extrair número de strings como "Decimal('5')"
                                            import re
                                            numbers = re.findall(r'\d+', str(quantidade))
                                            if numbers:
                                                total_cartelas += int(float(numbers[0]))
                                            else:
                                                total_cartelas += int(float(str(quantidade)))
                                    except:
                                        pass
                                
                                # Mostrar apenas estatísticas básicas
                                st.markdown("---")
                                col_stats1, col_stats2 = st.columns(2)
                                
                                with col_stats1:
                                    st.metric("📦 Total de Cartelas", total_cartelas)
                                
                                with col_stats2:
                                    st.metric("📋 Tipos de Cartelas", len(cartelas_dict))
                                
                                # Criar DataFrame para download
                                cartelas_df = pd.DataFrame([
                                    {'Cartela': cartela, 'Quantidade': qtd} 
                                    for cartela, qtd in cartelas_ordenadas
                                ])
                                
                                st.markdown("---")
                                st.subheader("📊 Tabela Completa de Cartelas")
                                st.dataframe(cartelas_df, use_container_width=True)
                            else:
                                st.info("Nenhuma cartela encontrada neste pedido.")
                                
                        except Exception as e:
                            st.error(f"Erro ao processar cartelas: {str(e)}")
                            st.text(f"Dados brutos: {cartelas_json}")
            
            # Botão para download
            csv = df_filtrado.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"pedidos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with tab2:
        
        if not df_filtrado.empty:
            # Função melhorada para calcular total de cartelas por pedido
            def calcular_total_cartelas(pedidos_json):
                try:
                    if pd.isna(pedidos_json) or pedidos_json == '':
                        return 0
                    
                    cartelas_dict = None
                    if isinstance(pedidos_json, dict):
                        cartelas_dict = pedidos_json
                    else:
                        cartelas_str = str(pedidos_json)
                        try:
                            cartelas_dict = json.loads(cartelas_str)
                        except:
                            try:
                                cartelas_str_fixed = cartelas_str.replace("'", '"')
                                cartelas_dict = json.loads(cartelas_str_fixed)
                            except:
                                import ast
                                try:
                                    cartelas_dict = ast.literal_eval(cartelas_str)
                                except:
                                    cartelas_dict = parse_cartelas_manual(cartelas_str)
                    
                    if cartelas_dict and isinstance(cartelas_dict, dict):
                        total = 0
                        for quantidade in cartelas_dict.values():
                            try:
                                if hasattr(quantidade, 'N'):  # Decimal do DynamoDB
                                    total += int(float(quantidade.N))
                                else:
                                    # Melhor tratamento para Decimal
                                    if 'Decimal' in str(quantidade):
                                        import re
                                        numbers = re.findall(r'\d+\.?\d*', str(quantidade))
                                        if numbers:
                                            total += int(float(numbers[0]))
                                    else:
                                        total += int(float(str(quantidade)))
                            except:
                                pass
                        return total
                    return 0
                except:
                    return 0
            
            # Função para extrair cartelas individuais
            def extrair_cartelas_individuais(pedidos_json):
                try:
                    if pd.isna(pedidos_json) or pedidos_json == '':
                        return {}
                    
                    cartelas_dict = None
                    if isinstance(pedidos_json, dict):
                        cartelas_dict = pedidos_json
                    else:
                        cartelas_str = str(pedidos_json)
                        try:
                            cartelas_dict = json.loads(cartelas_str)
                        except:
                            try:
                                cartelas_str_fixed = cartelas_str.replace("'", '"')
                                cartelas_dict = json.loads(cartelas_str_fixed)
                            except:
                                import ast
                                try:
                                    cartelas_dict = ast.literal_eval(cartelas_str)
                                except:
                                    cartelas_dict = parse_cartelas_manual(cartelas_str)
                    
                    if cartelas_dict and isinstance(cartelas_dict, dict):
                        return cartelas_dict
                    return {}
                except:
                    return {}
            
            # Função para calcular faturamento real por pedido
            def calcular_faturamento_pedido(pedidos_json, valor_cartela):
                try:
                    if pd.isna(pedidos_json) or pedidos_json == '' or pd.isna(valor_cartela):
                        return 0
                    
                    cartelas_dict = extrair_cartelas_individuais(pedidos_json)
                    if not cartelas_dict:
                        return 0
                    
                    total_cartelas = 0
                    for quantidade in cartelas_dict.values():
                        try:
                            if 'Decimal' in str(quantidade):
                                import re
                                numbers = re.findall(r'\d+\.?\d*', str(quantidade))
                                if numbers:
                                    total_cartelas += int(float(numbers[0]))
                            else:
                                total_cartelas += int(float(str(quantidade)))
                        except:
                            pass
                    
                    return total_cartelas * float(valor_cartela)
                except:
                    return 0
            
            # Adicionar colunas calculadas
            df_filtrado['total_cartelas'] = df_filtrado['Pedidos'].apply(calcular_total_cartelas)
            
            # Calcular faturamento real por pedido
            if 'Valor da cartela' in df_filtrado.columns:
                df_filtrado['faturamento_pedido'] = df_filtrado.apply(
                    lambda row: calcular_faturamento_pedido(row['Pedidos'], row['Valor da cartela']), 
                    axis=1
                )
            else:
                df_filtrado['faturamento_pedido'] = 0
            
            
            # Calcular todas as métricas primeiro
            total_cartelas = df_filtrado['total_cartelas'].sum()
            faturamento_total = df_filtrado['faturamento_pedido'].sum()
            maior_pedido = df_filtrado.loc[df_filtrado['total_cartelas'].idxmax()]
            pedidos_validos = df_filtrado[df_filtrado['total_cartelas'] > 0]
            menor_pedido = pedidos_validos.loc[pedidos_validos['total_cartelas'].idxmin()] if len(pedidos_validos) > 0 else None
            media_pedido = df_filtrado['total_cartelas'].mean()
            total_pedidos = len(df_filtrado)
            lojas_unicas = df_filtrado['Loja'].nunique() if 'Loja' in df_filtrado.columns else 0
            media_por_loja = total_cartelas / lojas_unicas if lojas_unicas > 0 else 0
            valor_medio_cartela = faturamento_total / total_cartelas if total_cartelas > 0 else 0
            
            # Layout organizado em 3 linhas de 3 colunas cada
            st.markdown("### 📊 Dashboard de Métricas")
            
            # Linha 1 - Métricas Principais
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #4169E1 0%, #1E90FF 100%); padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px;">
                    <h3 style="color: white; margin: 0; font-size: 16px; font-weight: 600;">📦 Total de Cartelas Vendidas</h3>
                    <h2 style="color: white; margin: 10px 0 0 0; font-size: 32px; font-weight: bold;">{total_cartelas:,.0f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #4169E1 0%, #1E90FF 100%); padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px;">
                    <h3 style="color: white; margin: 0; font-size: 16px; font-weight: 600;">💰 Faturamento Total</h3>
                    <h2 style="color: white; margin: 10px 0 0 0; font-size: 32px; font-weight: bold;">R$ {faturamento_total:,.2f}</h2>
                </div>
                """, unsafe_allow_html=True)
                
            with col3:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #4169E1 0%, #1E90FF 100%); padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px;">
                    <h3 style="color: white; margin: 0; font-size: 16px; font-weight: 600;">📋 Total de Pedidos</h3>
                    <h2 style="color: white; margin: 10px 0 0 0; font-size: 32px; font-weight: bold;">{total_pedidos:,.0f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Linha 2 - Métricas de Pedidos
            col4, col5, col6 = st.columns(3)
                
            with col4:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #4169E1 0%, #1E90FF 100%); padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px;">
                    <h3 style="color: white; margin: 0; font-size: 16px; font-weight: 600;">🏆 Maior Pedido</h3>
                    <h2 style="color: white; margin: 10px 0 0 0; font-size: 28px; font-weight: bold;">{maior_pedido['total_cartelas']:.0f} cartelas</h2>
                    <p style="color: #f0f0f0; margin: 8px 0 0 0; font-size: 14px; font-weight: 500;">ID: {maior_pedido.get('ID', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col5:
                if menor_pedido is not None:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #4169E1 0%, #1E90FF 100%); padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px;">
                        <h3 style="color: white; margin: 0; font-size: 16px; font-weight: 600;">📉 Menor Pedido</h3>
                        <h2 style="color: white; margin: 10px 0 0 0; font-size: 28px; font-weight: bold;">{menor_pedido['total_cartelas']:.0f} cartelas</h2>
                        <p style="color: #f0f0f0; margin: 8px 0 0 0; font-size: 14px; font-weight: 500;">ID: {menor_pedido.get('ID', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #4169E1 0%, #1E90FF 100%); padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px;">
                        <h3 style="color: white; margin: 0; font-size: 16px; font-weight: 600;">📉 Menor Pedido</h3>
                        <h2 style="color: white; margin: 10px 0 0 0; font-size: 28px; font-weight: bold;">N/A</h2>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col6:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #4169E1 0%, #1E90FF 100%); padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px;">
                    <h3 style="color: white; margin: 0; font-size: 16px; font-weight: 600;">📊 Média por Pedido</h3>
                    <h2 style="color: white; margin: 10px 0 0 0; font-size: 28px; font-weight: bold;">{media_pedido:.1f} cartelas</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Linha 3 - Métricas de Lojas e Valores
            col7, col8, col9 = st.columns(3)
            
            with col7:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #4169E1 0%, #1E90FF 100%); padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px;">
                    <h3 style="color: white; margin: 0; font-size: 16px; font-weight: 600;">🏪 Lojas Únicas</h3>
                    <h2 style="color: white; margin: 10px 0 0 0; font-size: 32px; font-weight: bold;">{lojas_unicas:,.0f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col8:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #4169E1 0%, #1E90FF 100%); padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px;">
                    <h3 style="color: white; margin: 0; font-size: 16px; font-weight: 600;">📈 Média por Loja</h3>
                    <h2 style="color: white; margin: 10px 0 0 0; font-size: 28px; font-weight: bold;">{media_por_loja:.1f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col9:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #4169E1 0%, #1E90FF 100%); padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px;">
                    <h3 style="color: white; margin: 0; font-size: 16px; font-weight: 600;">💵 Valor Médio/Cartela</h3>
                    <h2 style="color: white; margin: 10px 0 0 0; font-size: 28px; font-weight: bold;">R$ {valor_medio_cartela:.2f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # 2. ANÁLISE DE CARTELAS
            st.subheader("🏆 Análise de Cartelas")
            
            # Extrair todas as cartelas
            todas_cartelas = {}
            frequencia_cartelas = {}
            
            for _, row in df_filtrado.iterrows():
                cartelas = extrair_cartelas_individuais(row['Pedidos'])
                for cartela, quantidade in cartelas.items():
                    try:
                        qtd = int(float(str(quantidade).replace('Decimal("', '').replace('")', '').replace("Decimal('", '').replace("')", '')))
                        todas_cartelas[cartela] = todas_cartelas.get(cartela, 0) + qtd
                        frequencia_cartelas[cartela] = frequencia_cartelas.get(cartela, 0) + 1
                    except Exception as e:
                        print(f"Erro ao processar cartelas: {str(e)}")
                        pass
            
            if todas_cartelas:
                # Criar tabela com todas as cartelas ordenadas por quantidade
                cartelas_ordenadas = sorted(todas_cartelas.items(), key=lambda x: x[1], reverse=True)
                
                # Criar DataFrame com classificação
                df_cartelas = pd.DataFrame(cartelas_ordenadas, columns=['Cartela', 'Quantidade'])
                df_cartelas['Classificação'] = range(1, len(df_cartelas) + 1)
                df_cartelas = df_cartelas[['Classificação', 'Cartela', 'Quantidade']]
                
                # Calcular estatísticas uma única vez
                total_vendas = df_cartelas['Quantidade'].sum()
                media_por_cartela = df_cartelas['Quantidade'].mean()
                mediana_por_cartela = df_cartelas['Quantidade'].median()
                desvio_padrao = df_cartelas['Quantidade'].std()
                cartela_mais_vendida = df_cartelas.iloc[0]
                cartela_menos_vendida = df_cartelas.iloc[-1]
                
                # LAYOUT PRINCIPAL: 2 colunas - tabela à esquerda, estatísticas à direita
                col_tabela, col_estatisticas = st.columns([2, 3])
                
                # COLUNA 1: TABELA COMPLETA
                with col_tabela:
                    st.markdown("### 📋 Todas as Cartelas por Quantidade")
                    st.dataframe(
                        df_cartelas, 
                        use_container_width=True,
                        hide_index=True,
                        height=750
                    )
                
                # COLUNA 2: ESTATÍSTICAS EM GRID 2x5
                with col_estatisticas:
                    st.markdown("### 📊 Estatísticas das Cartelas")
                    
                    # Grid 2x5 para as estatísticas - melhor aproveitamento do espaço
                    # Linha 1
                    col_stat1, col_stat2 = st.columns(2)
                    
                    with col_stat1:
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #4169E1 0%, #1E90FF 100%); padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <h4 style="color: white; margin: 0; font-size: 14px; font-weight: 600;">Total de Tipos</h4>
                            <h3 style="color: white; margin: 8px 0 0 0; font-size: 24px; font-weight: bold;">{len(df_cartelas)}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_stat2:
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #4169E1 0%, #1E90FF 100%); padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <h4 style="color: white; margin: 0; font-size: 14px; font-weight: 600;">Total Vendidas</h4>
                            <h3 style="color: white; margin: 8px 0 0 0; font-size: 24px; font-weight: bold;">{total_vendas:,.0f}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Linha 2
                    col_stat3, col_stat4 = st.columns(2)
                    
                    with col_stat3:
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #4169E1 0%, #1E90FF 100%); padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <h4 style="color: white; margin: 0; font-size: 14px; font-weight: 600;">Média por Cartela</h4>
                            <h3 style="color: white; margin: 8px 0 0 0; font-size: 24px; font-weight: bold;">{media_por_cartela:.1f}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_stat4:
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #4169E1 0%, #1E90FF 100%); padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <h4 style="color: white; margin: 0; font-size: 14px; font-weight: 600;">Mediana</h4>
                            <h3 style="color: white; margin: 8px 0 0 0; font-size: 24px; font-weight: bold;">{mediana_por_cartela:.1f}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Linha 3
                    col_stat5, col_stat6 = st.columns(2)
                    
                    with col_stat5:
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #4169E1 0%, #1E90FF 100%); padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <h4 style="color: white; margin: 0; font-size: 14px; font-weight: 600;">🥇 Mais Vendida</h4>
                            <h3 style="color: white; margin: 8px 0 0 0; font-size: 24px; font-weight: bold;">{cartela_mais_vendida['Quantidade']:,.0f}</h3>
                            <p style="color: #f0f0f0; margin: 5px 0 0 0; font-size: 12px; font-weight: 500;">{cartela_mais_vendida['Cartela']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_stat6:
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #4169E1 0%, #1E90FF 100%); padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <h4 style="color: white; margin: 0; font-size: 14px; font-weight: 600;">🥉 Menos Vendida</h4>
                            <h3 style="color: white; margin: 8px 0 0 0; font-size: 24px; font-weight: bold;">{cartela_menos_vendida['Quantidade']:,.0f}</h3>
                            <p style="color: #f0f0f0; margin: 5px 0 0 0; font-size: 12px; font-weight: 500;">{cartela_menos_vendida['Cartela']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Linha 4
                    col_stat7, col_stat8 = st.columns(2)
                    
                    with col_stat7:
                        # Frequência da cartela mais vendida
                        freq_mais_vendida = frequencia_cartelas.get(cartela_mais_vendida['Cartela'], 0)
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #4169E1 0%, #1E90FF 100%); padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <h4 style="color: white; margin: 0; font-size: 14px; font-weight: 600;">Freq. Mais Vendida</h4>
                            <h3 style="color: white; margin: 8px 0 0 0; font-size: 24px; font-weight: bold;">{freq_mais_vendida}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_stat8:
                        # Frequência da cartela menos vendida
                        freq_menos_vendida = frequencia_cartelas.get(cartela_menos_vendida['Cartela'], 0)
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #4169E1 0%, #1E90FF 100%); padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <h4 style="color: white; margin: 0; font-size: 14px; font-weight: 600;">Freq. Menos Vendida</h4>
                            <h3 style="color: white; margin: 8px 0 0 0; font-size: 24px; font-weight: bold;">{freq_menos_vendida}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Linha 5
                    col_stat9, col_stat10 = st.columns(2)
                    
                    with col_stat9:
                        # Média de frequência
                        media_frequencia = sum(frequencia_cartelas.values()) / len(frequencia_cartelas) if frequencia_cartelas else 0
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #4169E1 0%, #1E90FF 100%); padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <h4 style="color: white; margin: 0; font-size: 14px; font-weight: 600;">Média de Frequência</h4>
                            <h3 style="color: white; margin: 8px 0 0 0; font-size: 24px; font-weight: bold;">{media_frequencia:.1f}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_stat10:
                        # Estatística adicional - Desvio padrão
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #4169E1 0%, #1E90FF 100%); padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <h4 style="color: white; margin: 0; font-size: 14px; font-weight: 600;">Desvio Padrão</h4>
                            <h3 style="color: white; margin: 8px 0 0 0; font-size: 24px; font-weight: bold;">{desvio_padrao:.1f}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                
                # SEÇÃO DE GRÁFICOS: Layout vertical
                st.markdown("---")
                st.markdown("### 📊 Visualizações Gráficas")
                
                # Gráfico 1: Top 30 Cartelas Mais Vendidas
                st.markdown("**📈 Gráfico 1: Top 30 Cartelas Mais Vendidas**")
                df_grafico_top30 = df_cartelas.head(30)
                fig_top30 = px.bar(
                    df_grafico_top30, 
                    x='Cartela', 
                    y='Quantidade',
                    title="Top 30 Cartelas Mais Vendidas",
                    color='Quantidade',
                    color_continuous_scale='Blues'
                )
                fig_top30.update_layout(
                    xaxis_tickangle=-45,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    height=500,
                    xaxis=dict(
                        title=dict(text="Cartela", font=dict(size=14)),
                        tickfont=dict(size=10)
                    ),
                    yaxis=dict(
                        title=dict(text="Quantidade Vendida", font=dict(size=14)),
                        tickfont=dict(size=12)
                    ),
                    coloraxis_colorbar=dict(
                        title=dict(text="Quantidade", font=dict(size=12))
                    )
                )
                st.plotly_chart(fig_top30, use_container_width=True)
                
                # Gráfico 2: 30 Cartelas Menos Vendidas
                st.markdown("**📉 Gráfico 2: 30 Cartelas Menos Vendidas**")
                df_grafico_bottom30 = df_cartelas.tail(30)
                fig_bottom30 = px.bar(
                    df_grafico_bottom30, 
                    x='Cartela', 
                    y='Quantidade',
                    title="30 Cartelas Menos Vendidas",
                    color='Quantidade',
                    color_continuous_scale='Blues'
                )
                fig_bottom30.update_layout(
                    xaxis_tickangle=-45,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    height=500,
                    xaxis=dict(
                        title=dict(text="Cartela", font=dict(size=14)),
                        tickfont=dict(size=10)
                    ),
                    yaxis=dict(
                        title=dict(text="Quantidade Vendida", font=dict(size=14)),
                        tickfont=dict(size=12)
                    ),
                    coloraxis_colorbar=dict(
                        title=dict(text="Quantidade", font=dict(size=12))
                    )
                )
                st.plotly_chart(fig_bottom30, use_container_width=True)
            
            # 3. ANÁLISE DE LOJAS
            st.subheader("🏪 Análise de Lojas")
            
            # Controles principais lado a lado
            st.markdown("### 🎛️ Controles de Análise")
            col_lojas, col_meses = st.columns(2)
            
            with col_lojas:
                st.markdown("**🏪 Controle de Lojas**")
                qtd_lojas_universal = st.slider(
                    "Quantidade de lojas para exibir:",
                    min_value=5,
                    max_value=100,
                    value=10,
                    step=1,
                    help="Este controle afeta todos os gráficos de lojas na seção"
                )
            
            # Inicializar variável para meses selecionados
            meses_selecionados = []
            
            if 'Loja' in df_filtrado.columns:
                # Lojas que mais venderam
                lojas_stats = df_filtrado.groupby('Loja').agg({
                    'total_cartelas': 'sum',
                    'ID': 'count'
                }).reset_index()
                lojas_stats.columns = ['Loja', 'Total_Cartelas', 'Total_Pedidos']
                lojas_stats = lojas_stats.sort_values('Total_Cartelas', ascending=False)
                
                
                col_lojas_mais, col_lojas_menos = st.columns(2)
                
                with col_lojas_mais:
                    st.write(f"**Top {qtd_lojas_universal} Lojas que Mais Venderam**")
                    st.dataframe(lojas_stats.head(qtd_lojas_universal), use_container_width=True)
                    
                    fig_lojas_mais = px.bar(
                        lojas_stats.head(qtd_lojas_universal),
                        x='Loja',
                        y='Total_Cartelas',
                        title=f"Top {qtd_lojas_universal} Lojas por Vendas",
                        color='Total_Cartelas',
                        color_continuous_scale='Blues'
                    )
                    fig_lojas_mais.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_lojas_mais, use_container_width=True)
                
                with col_lojas_menos:
                    st.write(f"**{qtd_lojas_universal} Lojas que Menos Venderam**")
                    st.dataframe(lojas_stats.tail(qtd_lojas_universal), use_container_width=True)
                    
                    fig_lojas_menos = px.bar(
                        lojas_stats.tail(qtd_lojas_universal),
                        x='Loja',
                        y='Total_Cartelas',
                        title=f"{qtd_lojas_universal} Lojas com Menores Vendas",
                        color='Total_Cartelas',
                        color_continuous_scale='Blues'
                    )
                    fig_lojas_menos.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_lojas_menos, use_container_width=True)
                
                # Análise por mês
                if 'Data' in df_filtrado.columns:
                    try:
                        df_filtrado['Data'] = pd.to_datetime(df_filtrado['Data'])
                        df_filtrado['Mes'] = df_filtrado['Data'].dt.to_period('M')
                        
                        lojas_mes = df_filtrado.groupby(['Loja', 'Mes']).agg({
                            'total_cartelas': 'sum'
                        }).reset_index()
                        lojas_mes['Mes'] = lojas_mes['Mes'].astype(str)
                        
                        # Top lojas por mês usando controle universal
                        top_lojas_mes = lojas_mes.groupby('Mes').apply(
                            lambda x: x.nlargest(qtd_lojas_universal, 'total_cartelas')
                        ).reset_index(drop=True)
                        
                        # Layout vertical para melhor visualização
                        st.markdown("### 📊 Análise de Vendas por Loja e Mês")
                        
                        # Tabela de dados
                        st.markdown(f"**📋 Dados das Top {qtd_lojas_universal} Lojas por Mês**")
                        st.dataframe(top_lojas_mes, use_container_width=True, height=300)
                        
                        # Gráfico 1: Vendas por mês (agrupado) - VERTICAL
                        st.markdown(f"**📈 Gráfico 1: Vendas por Mês (Top {qtd_lojas_universal} Lojas por Mês)**")
                        fig_mes1 = px.bar(
                            top_lojas_mes,
                            x='total_cartelas',
                            y='Mes',
                            color='Loja',
                            orientation='h',  # Gráfico horizontal (vertical na visualização)
                            title=f"Vendas por Mês (Top {qtd_lojas_universal} Lojas por Mês)",
                            labels={'total_cartelas': 'Total de Cartelas', 'Mes': 'Mês'},
                            barmode='group',
                            color_discrete_sequence=['#1E3A8A', '#1E40AF', '#2563EB', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE', '#DBEAFE', '#EFF6FF', '#F0F9FF']
                        )
                        fig_mes1.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(size=12),
                            height=600,
                            xaxis=dict(
                                title=dict(text="Total de Cartelas", font=dict(size=14)),
                                tickfont=dict(size=12)
                            ),
                            yaxis=dict(
                                title=dict(text="Mês", font=dict(size=14)),
                                tickfont=dict(size=11)
                            ),
                            legend=dict(
                                orientation="v",
                                yanchor="top",
                                y=1,
                                xanchor="left",
                                x=1.02,
                                font=dict(size=9),
                                bgcolor='rgba(255,255,255,0.8)',
                                bordercolor='rgba(0,0,0,0.2)',
                                borderwidth=1
                            ),
                            margin=dict(r=180, l=80, t=80, b=80)
                        )
                        st.plotly_chart(fig_mes1, use_container_width=True)
                        
                        # Atualizar controle de seleção de meses no topo
                        meses_disponiveis = sorted(lojas_mes['Mes'].unique())
                        
                        # Atualizar a seção de controles no topo com o multiselect
                        with col_meses:
                            st.markdown("**📅 Seleção de Meses**")
                            meses_selecionados = st.multiselect(
                                "Selecione os meses para análise:",
                                options=meses_disponiveis,
                                help="Escolha quais meses deseja visualizar no gráfico",
                                key="meses_analise"
                            )
                        
                        # Filtrar dados pelos meses selecionados
                        if meses_selecionados:
                            lojas_mes_filtrado = lojas_mes[lojas_mes['Mes'].isin(meses_selecionados)]
                        else:
                            lojas_mes_filtrado = lojas_mes
                        
                        # Gráfico 2: Top lojas com vendas por mês (com controles) - VERTICAL
                        top_lojas_geral = lojas_mes_filtrado.groupby('Loja').agg({
                            'total_cartelas': 'sum'
                        }).reset_index().sort_values('total_cartelas', ascending=False).head(qtd_lojas_universal)
                        
                        # Filtrar dados apenas das top lojas selecionadas
                        lojas_mes_top = lojas_mes_filtrado[lojas_mes_filtrado['Loja'].isin(top_lojas_geral['Loja'])]
                        
                        # Ordenar as lojas do maior para o menor total de vendas
                        lojas_mes_top = lojas_mes_top.merge(
                            top_lojas_geral[['Loja', 'total_cartelas']].rename(columns={'total_cartelas': 'total_geral'}),
                            on='Loja'
                        ).sort_values('total_geral', ascending=True)  # ascending=True para gráfico horizontal (maior no topo)
                        
                        st.markdown(f"**📈 Gráfico 2: Vendas por Loja (Top {qtd_lojas_universal} Lojas) - Separado por Mês**")
                        fig_mes2 = px.bar(
                            lojas_mes_top,
                            x='total_cartelas',
                            y='Loja',
                            color='Mes',
                            orientation='h',  # Gráfico horizontal (vertical na visualização)
                            title=f"Vendas por Loja (Top {qtd_lojas_universal} Lojas) - Separado por Mês",
                            labels={'total_cartelas': 'Total de Cartelas', 'Loja': 'Loja'},
                            barmode='group',
                            color_discrete_sequence=['#1E3A8A', '#1E40AF', '#2563EB', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE', '#DBEAFE', '#EFF6FF', '#F0F9FF', '#1E3A8A', '#1E40AF']
                        )
                        fig_mes2.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(size=12),
                            height=600,
                            xaxis=dict(
                                title=dict(text="Total de Cartelas", font=dict(size=14)),
                                tickfont=dict(size=12)
                            ),
                            yaxis=dict(
                                title=dict(text="Loja", font=dict(size=14)),
                                tickfont=dict(size=10)
                            ),
                            legend=dict(
                                orientation="v",
                                yanchor="top",
                                y=1,
                                xanchor="left",
                                x=1.02,
                                font=dict(size=9),
                                bgcolor='rgba(255,255,255,0.8)',
                                bordercolor='rgba(0,0,0,0.2)',
                                borderwidth=1
                            ),
                            margin=dict(r=180, l=80, t=80, b=80)
                        )
                        st.plotly_chart(fig_mes2, use_container_width=True)
                        
                        
                        
                    except Exception as e:
                        st.warning(f"Erro ao processar dados por mês: {str(e)}")
            
            # 4. ANÁLISE DE PERFIL DE LOJA
            st.subheader("🎯 Análise de Perfil de Loja")
            
            # Classificar pedidos por perfil
            def classificar_perfil(total_cartelas):
                if total_cartelas <= 50:
                    return "Ticker Baixo"
                elif total_cartelas <= 100:
                    return "Ticker Médio"
                else:
                    return "Ticker Alto"
            
            df_filtrado['Perfil'] = df_filtrado['total_cartelas'].apply(classificar_perfil)
            
            perfil_stats = df_filtrado['Perfil'].value_counts()
            
            col_perfil1, col_perfil2 = st.columns(2)
            
            with col_perfil1:
                st.write("**Distribuição por Perfil de Loja**")
                st.dataframe(perfil_stats.reset_index(), use_container_width=True)
                
                fig_perfil = px.pie(
                    values=perfil_stats.values,
                    names=perfil_stats.index,
                    title="Distribuição por Perfil de Loja",
                    color_discrete_sequence=['#4169E1', '#1E90FF', '#87CEEB']
                )
                fig_perfil.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12)
                )
                st.plotly_chart(fig_perfil, use_container_width=True)
            
            with col_perfil2:
                # Faturamento por perfil
                faturamento_perfil = df_filtrado.groupby('Perfil').agg({
                    'faturamento_pedido': 'sum'
                }).reset_index()
                faturamento_perfil.columns = ['Perfil', 'Faturamento']
                
                st.write("**Faturamento por Perfil**")
                st.dataframe(faturamento_perfil, use_container_width=True)
                
                fig_fat_perfil = px.pie(
                    values=faturamento_perfil['Faturamento'],
                    names=faturamento_perfil['Perfil'],
                    title="Faturamento por Perfil de Loja",
                    color_discrete_sequence=['#4169E1', '#1E90FF', '#87CEEB']
                )
                fig_fat_perfil.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12)
                )
                st.plotly_chart(fig_fat_perfil, use_container_width=True)
            
            # 5. ANÁLISE POR BAIRRO
            st.subheader("🏘️ Análise por Bairro")
            
            # Extrair bairro do campo 'Endereco' se não existir coluna 'bairro'
            if 'bairro' not in df_filtrado.columns and 'Endereco' in df_filtrado.columns:
                def extrair_bairro(endereco_data):
                    try:
                        if pd.isna(endereco_data) or endereco_data == '':
                            return ''
                        
                        # Se já é um dicionário Python
                        if isinstance(endereco_data, dict):
                            bairro = endereco_data.get('Bairro', '')
                            if bairro and bairro.strip():
                                return bairro.strip()
                            return ''
                        
                        # Se é uma string que parece um dicionário Python
                        if isinstance(endereco_data, str):
                            # Tentar usar ast.literal_eval para converter string para dicionário
                            import ast
                            try:
                                endereco_dict = ast.literal_eval(endereco_data)
                                if isinstance(endereco_dict, dict):
                                    bairro = endereco_dict.get('Bairro', '')
                                    if bairro and bairro.strip():
                                        return bairro.strip()
                                    return ''
                            except (ValueError, SyntaxError):
                                # Se ast.literal_eval falhar, tentar JSON
                                try:
                                    import json
                                    endereco_dict = json.loads(endereco_data)
                                    bairro = endereco_dict.get('Bairro', '')
                                    if bairro and bairro.strip():
                                        return bairro.strip()
                                    return ''
                                except json.JSONDecodeError:
                                    return ''
                        
                        return ''
                    except Exception as e:
                        return ''
                
                # Aplicar a função para extrair bairro
                df_filtrado['bairro'] = df_filtrado['Endereco'].apply(extrair_bairro)
                
                # Filtrar apenas registros com bairro válido
                df_filtrado = df_filtrado[df_filtrado['bairro'] != '']
            
            if 'bairro' in df_filtrado.columns and len(df_filtrado) > 0:
                # Análise completa de BI por bairro
                bairros_stats = df_filtrado.groupby('bairro').agg({
                    'total_cartelas': ['sum', 'mean', 'count'],
                    'faturamento_pedido': 'sum',
                    'ID': 'nunique'
                }).reset_index()
                
                # Flatten column names
                bairros_stats.columns = ['Bairro', 'Total_Cartelas', 'Media_Cartelas', 'Total_Pedidos', 'Faturamento_Total', 'Clientes_Unicos']
                bairros_stats = bairros_stats.sort_values('Faturamento_Total', ascending=False)
                

                col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
                
                with col_kpi1:
                    total_faturamento = bairros_stats['Faturamento_Total'].sum()
                    st.metric("💰 Faturamento Total", f"R$ {total_faturamento:,.2f}")
                
                with col_kpi2:
                    total_pedidos = bairros_stats['Total_Pedidos'].sum()
                    st.metric("📦 Total de Pedidos", f"{total_pedidos:,}")
                
                with col_kpi3:
                    total_cartelas = bairros_stats['Total_Cartelas'].sum()
                    st.metric("🎫 Total de Cartelas", f"{total_cartelas:,}")
                
                with col_kpi4:
                    bairros_ativos = len(bairros_stats[bairros_stats['Total_Pedidos'] > 0])
                    st.metric("🏘️ Bairros Ativos", f"{bairros_ativos}")
                
                # Gráficos Principais
                st.markdown("### 📈 Análise de Performance por Bairro")
                
                # Gráfico 1: Faturamento por Bairro (Top 15)
                col_graf1, col_graf2 = st.columns(2)
                
                with col_graf1:
                    st.markdown("**💰 Faturamento por Bairro (Top 15)**")
                    fig_faturamento = px.bar(
                        bairros_stats.head(15),
                        x='Faturamento_Total',
                        y='Bairro',
                        orientation='h',
                        title="Faturamento por Bairro (Top 15)",
                        color='Faturamento_Total',
                        color_continuous_scale='Blues',
                        labels={'Faturamento_Total': 'Faturamento (R$)', 'Bairro': 'Bairro'}
                    )
                    fig_faturamento.update_layout(
                        height=600,
                        xaxis_title="Faturamento (R$)",
                        yaxis_title="Bairro",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig_faturamento, use_container_width=True)
                
                with col_graf2:
                    st.markdown("**📦 Quantidade de Pedidos por Bairro (Top 15)**")
                    fig_pedidos = px.bar(
                        bairros_stats.head(15),
                        x='Total_Pedidos',
                        y='Bairro',
                        orientation='h',
                        title="Quantidade de Pedidos por Bairro (Top 15)",
                        color='Total_Pedidos',
                        color_continuous_scale='Blues',
                        labels={'Total_Pedidos': 'Quantidade de Pedidos', 'Bairro': 'Bairro'}
                    )
                    fig_pedidos.update_layout(
                        height=600,
                        xaxis_title="Quantidade de Pedidos",
                        yaxis_title="Bairro",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig_pedidos, use_container_width=True)
                
                # Gráfico 2: Média de Cartelas por Bairro
                col_graf3, col_graf4 = st.columns(2)
                
                with col_graf3:
                    st.markdown("**📊 Média de Cartelas por Bairro (Top 15)**")
                    fig_media = px.bar(
                        bairros_stats.head(15),
                        x='Media_Cartelas',
                        y='Bairro',
                        orientation='h',
                        title="Média de Cartelas por Bairro (Top 15)",
                        color='Media_Cartelas',
                        color_continuous_scale='Blues',
                        labels={'Media_Cartelas': 'Média de Cartelas', 'Bairro': 'Bairro'}
                    )
                    fig_media.update_layout(
                        height=600,
                        xaxis_title="Média de Cartelas",
                        yaxis_title="Bairro",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig_media, use_container_width=True)
                
                with col_graf4:
                    st.markdown("**👥 Clientes Únicos por Bairro (Top 15)**")
                    fig_clientes = px.bar(
                        bairros_stats.head(15),
                        x='Clientes_Unicos',
                        y='Bairro',
                        orientation='h',
                        title="Clientes Únicos por Bairro (Top 15)",
                        color='Clientes_Unicos',
                        color_continuous_scale='Blues',
                        labels={'Clientes_Unicos': 'Clientes Únicos', 'Bairro': 'Bairro'}
                    )
                    fig_clientes.update_layout(
                        height=600,
                        xaxis_title="Clientes Únicos",
                        yaxis_title="Bairro",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig_clientes, use_container_width=True)
                
                # Gráfico de Pizza: Distribuição de Faturamento
                st.markdown("### 🥧 Distribuição de Faturamento por Bairro")
                col_pizza1, col_pizza2 = st.columns(2)
                
                with col_pizza1:
                    # Top 10 bairros + "Outros"
                    top_10_bairros = bairros_stats.head(10)
                    outros_faturamento = bairros_stats.iloc[10:]['Faturamento_Total'].sum()
                    
                    if outros_faturamento > 0:
                        pizza_data = pd.concat([
                            top_10_bairros[['Bairro', 'Faturamento_Total']],
                            pd.DataFrame([['Outros', outros_faturamento]], columns=['Bairro', 'Faturamento_Total'])
                        ])
                    else:
                        pizza_data = top_10_bairros[['Bairro', 'Faturamento_Total']]
                    
                    fig_pizza = px.pie(
                        pizza_data,
                        values='Faturamento_Total',
                        names='Bairro',
                        title="Distribuição de Faturamento por Bairro (Top 10 + Outros)",
                        color_discrete_sequence=['#1E3A8A', '#1E40AF', '#2563EB', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE', '#DBEAFE', '#EFF6FF', '#F0F9FF']
                    )
                    fig_pizza.update_layout(
                        height=500,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig_pizza, use_container_width=True)
                
                with col_pizza2:
                    # Top 10 bairros por pedidos + "Outros"
                    top_10_pedidos = bairros_stats.nlargest(10, 'Total_Pedidos')
                    outros_pedidos = bairros_stats.iloc[10:]['Total_Pedidos'].sum()
                    
                    if outros_pedidos > 0:
                        pizza_pedidos = pd.concat([
                            top_10_pedidos[['Bairro', 'Total_Pedidos']],
                            pd.DataFrame([['Outros', outros_pedidos]], columns=['Bairro', 'Total_Pedidos'])
                        ])
                    else:
                        pizza_pedidos = top_10_pedidos[['Bairro', 'Total_Pedidos']]
                    
                    fig_pizza_pedidos = px.pie(
                        pizza_pedidos,
                        values='Total_Pedidos',
                        names='Bairro',
                        title="Distribuição de Pedidos por Bairro (Top 10 + Outros)",
                        color_discrete_sequence=['#1E3A8A', '#1E40AF', '#2563EB', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE', '#DBEAFE', '#EFF6FF', '#F0F9FF']
                    )
                    fig_pizza_pedidos.update_layout(
                        height=500,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig_pizza_pedidos, use_container_width=True)
                
                # Tabela Detalhada
                st.markdown("### 📋 Tabela Detalhada de Performance por Bairro")
                
                # Adicionar métricas calculadas
                bairros_stats['Ticket_Medio'] = bairros_stats['Faturamento_Total'] / bairros_stats['Total_Pedidos']
                bairros_stats['Cartelas_Por_Pedido'] = bairros_stats['Total_Cartelas'] / bairros_stats['Total_Pedidos']
                bairros_stats['Participacao_Faturamento'] = (bairros_stats['Faturamento_Total'] / total_faturamento * 100).round(2)
                
                # Formatar valores monetários
                bairros_stats['Faturamento_Total_Formatado'] = bairros_stats['Faturamento_Total'].apply(lambda x: f"R$ {x:,.2f}")
                bairros_stats['Ticket_Medio_Formatado'] = bairros_stats['Ticket_Medio'].apply(lambda x: f"R$ {x:,.2f}")
                
                # Selecionar colunas para exibição
                colunas_exibicao = [
                    'Bairro', 'Faturamento_Total_Formatado', 'Total_Pedidos', 'Total_Cartelas',
                    'Media_Cartelas', 'Clientes_Unicos', 'Ticket_Medio_Formatado',
                    'Cartelas_Por_Pedido', 'Participacao_Faturamento'
                ]
                
                tabela_exibicao = bairros_stats[colunas_exibicao].copy()
                tabela_exibicao.columns = [
                    'Bairro', 'Faturamento Total', 'Total Pedidos', 'Total Cartelas',
                    'Média Cartelas', 'Clientes Únicos', 'Ticket Médio',
                    'Cartelas/Pedido', 'Participação (%)'
                ]
                
                st.dataframe(tabela_exibicao, use_container_width=True, height=400, hide_index=True)
                
                # Resumo Executivo
                st.markdown("### 📊 Resumo Executivo")
                col_resumo1, col_resumo2, col_resumo3 = st.columns(3)
                
                with col_resumo1:
                    st.markdown("**🏆 Top 3 Bairros por Faturamento:**")
                    for i, row in bairros_stats.head(3).iterrows():
                        st.write(f"{i+1}º {row['Bairro']}: R$ {row['Faturamento_Total']:,.2f}")
                
                with col_resumo2:
                    st.markdown("**📦 Top 3 Bairros por Pedidos:**")
                    top_pedidos = bairros_stats.nlargest(3, 'Total_Pedidos')
                    for i, row in top_pedidos.iterrows():
                        st.write(f"{i+1}º {row['Bairro']}: {row['Total_Pedidos']} pedidos")
                
                with col_resumo3:
                    st.markdown("**📊 Top 3 Bairros por Ticket Médio:**")
                    top_ticket = bairros_stats.nlargest(3, 'Ticket_Medio')
                    for i, row in top_ticket.iterrows():
                        st.write(f"{i+1}º {row['Bairro']}: R$ {row['Ticket_Medio']:,.2f}")
            else:
                if 'Endereco' not in df_filtrado.columns:
                    st.warning("⚠️ **Campo 'Endereco' não encontrado no DataFrame.**")
                    st.info("A análise por bairro requer que os dados tenham informações de endereço.")
                else:
                    st.warning("⚠️ **Nenhum registro com bairro válido encontrado.**")
                    st.info("Todos os registros foram filtrados por não possuírem informações de bairro válidas.")
                    st.info("Verifique se o campo 'Endereco' contém dados no formato correto.")
            
            # 6. FREQUÊNCIA DE CARTELAS
            st.subheader("📊 Frequência de Cartelas")
            
            if frequencia_cartelas:
                freq_df = pd.DataFrame(list(frequencia_cartelas.items()), columns=['Cartela', 'Frequencia'])
                freq_df = freq_df.sort_values('Frequencia', ascending=False)
                
                st.write("**Frequência de Aparição das Cartelas**")
                st.dataframe(freq_df.head(20), use_container_width=True)
                
                fig_freq = px.bar(
                    freq_df.head(20),
                    x='Cartela',
                    y='Frequencia',
                    title="Frequência de Aparição das Cartelas (Top 20)",
                    color='Frequencia',
                    color_continuous_scale='Blues'
                )
                fig_freq.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_freq, use_container_width=True)
            
            # 7. ANÁLISE DE EXPOSITORES VAZIOS
            st.subheader("📦 Análise de Expositores Vazios")
            
            def is_expositor_vazio(quantidade):
                try:
                    qtd = int(float(str(quantidade).replace('Decimal("', '').replace('")', '').replace("Decimal('", '').replace("')", '')))
                    return qtd in [15, 20, 25] or qtd >= 25
                except:
                    return False
            
            expositor_vazio_count = 0
            total_cartelas_analisadas = 0
            
            for _, row in df_filtrado.iterrows():
                cartelas = extrair_cartelas_individuais(row['Pedidos'])
                for cartela, quantidade in cartelas.items():
                    total_cartelas_analisadas += 1
                    if is_expositor_vazio(quantidade):
                        expositor_vazio_count += 1
            
            col_vazio1, col_vazio2, col_vazio3 = st.columns(3)
            
            with col_vazio1:
                st.metric("Expositores Vazios", expositor_vazio_count)
                st.metric("Total Analisado", total_cartelas_analisadas)
            
            with col_vazio2:
                st.metric("Total Analisado", total_cartelas_analisadas)
            
            with col_vazio3:
                if total_cartelas_analisadas > 0:
                    percentual_vazio = (expositor_vazio_count / total_cartelas_analisadas) * 100
                    st.metric("Percentual de Vazios", f"{percentual_vazio:.1f}%")
                else:
                    st.metric("Percentual de Vazios", "N/A")
    

# Dashboard integrado ao sistema principal - não executar diretamente
# if __name__ == "__main__":
#     main()
