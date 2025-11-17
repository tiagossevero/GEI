"""
Sistema GEI - Gestão Estratégica de Informações
Dashboard de Monitoramento Fiscal v4.0 - Refatorado e Otimizado
Receita Estadual de Santa Catarina
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Importações dos módulos do sistema
from src.config import (
    get_impala_engine, CORES, PALETAS,
    formatar_moeda, formatar_numero, formatar_percentual,
    classificar_risco, NIVEIS_RISCO
)
from src.data import (
    carregar_todos_os_dados,
    carregar_dossie_completo,
    carregar_ranking_geral,
    carregar_estatisticas_gerais,
    buscar_grupo_por_cnpj,
    aplicar_filtros,
    filtrar_por_score,
    filtrar_por_nivel_risco
)
from src.components import (
    criar_kpi, criar_grid_kpis, criar_kpi_colorido,
    criar_histograma, criar_boxplot, criar_grafico_barras,
    criar_grafico_pizza, criar_grafico_linha, criar_grafico_dispersao,
    criar_heatmap, criar_matriz_correlacao, criar_dispersao_3d,
    criar_gauge, exibir_tabela_formatada, criar_grafico_rede,
    gerar_insights_grupo, gerar_insights_gerais, exibir_insights,
    calcular_correlacoes, identificar_outliers
)
from src.ml import (
    preparar_dados_ml, aplicar_pca, executar_consenso,
    encontrar_melhor_k, visualizar_clusters_2d, visualizar_clusters_3d,
    grafico_elbow, comparar_algoritmos
)
from src.reports import (
    criar_botao_download_excel, criar_botao_download_csv,
    criar_botao_download_pdf
)
from src.utils import check_password, logout

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================

st.set_page_config(
    page_title="GEI - Monitoramento Fiscal v4.0",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }

    div[data-testid="stPlotlyChart"] {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        background-color: #ffffff;
    }

    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 2px solid #2c3e50;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# AUTENTICAÇÃO
# =============================================================================

if not check_password():
    st.stop()

# =============================================================================
# INICIALIZAÇÃO
# =============================================================================

# Conectar ao banco
engine = get_impala_engine()

if engine is None:
    st.error("❌ Não foi possível conectar ao banco de dados. Verifique as configurações.")
    st.stop()

# Carregar dados
dados = carregar_todos_os_dados(engine)

if not dados or dados.get('percent', pd.DataFrame()).empty:
    st.error("❌ Não foi possível carregar os dados do sistema.")
    st.stop()

# =============================================================================
# SIDEBAR - NAVEGAÇÃO E FILTROS
# =============================================================================

with st.sidebar:
    st.image("https://via.placeholder.com/200x80/1F77B4/FFFFFF?text=GEI+v4.0", use_container_width=True)

    st.markdown("### 🔐 Usuário Autenticado")
    if st.button("🚪 Sair", use_container_width=True):
        logout()

    st.markdown("---")

    st.markdown("### 📋 Navegação")

    pagina = st.radio(
        "Selecione a página:",
        [
            "📊 Dashboard Executivo",
            "🎯 Análise Pontual",
            "📈 Ranking de Grupos",
            "🤖 Machine Learning",
            "🔗 Análise de Redes",
            "📐 Análise Multidimensional",
            "💡 Insights Automáticos",
            "📋 Dossiê Completo",
            "⚙️ Configurações"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")

    st.markdown("### 🔍 Filtros Globais")

    # Filtro de score
    score_range = st.slider(
        "Score de Risco (%)",
        0, 100, (0, 100),
        help="Filtrar grupos por faixa de score"
    )

    # Filtro de nível de risco
    niveis_selecionados = st.multiselect(
        "Níveis de Risco",
        options=['CRÍTICO', 'ALTO', 'MÉDIO', 'BAIXO'],
        default=['CRÍTICO', 'ALTO'],
        help="Filtrar por níveis de risco"
    )

    # Aplicar filtros
    df_filtrado = dados['percent'].copy()
    if 'score_final_percent' in df_filtrado.columns:
        df_filtrado = filtrar_por_score(df_filtrado, score_range[0], score_range[1], 'score_final_percent')
    if 'nivel_risco_final' in df_filtrado.columns and niveis_selecionados:
        df_filtrado = filtrar_por_nivel_risco(df_filtrado, niveis_selecionados, 'nivel_risco_final')

# =============================================================================
# PÁGINA 1: DASHBOARD EXECUTIVO
# =============================================================================

if pagina == "📊 Dashboard Executivo":
    st.markdown("<h1 class='main-header'>📊 Dashboard Executivo</h1>", unsafe_allow_html=True)

    # Carregar estatísticas
    stats = carregar_estatisticas_gerais(engine)

    # KPIs Principais
    st.markdown("### 📌 Indicadores Principais")

    kpis = [
        {
            'label': 'Total de Grupos',
            'valor': stats.get('total_grupos', 0),
            'formato': 'numero',
            'help': 'Total de grupos econômicos monitorados'
        },
        {
            'label': 'Grupos Críticos',
            'valor': stats.get('grupos_criticos', 0),
            'formato': 'numero',
            'help': 'Grupos com score >= 80%'
        },
        {
            'label': 'Score Médio',
            'valor': stats.get('score_medio', 0),
            'formato': 'numero',
            'help': 'Score médio de risco de todos os grupos'
        },
        {
            'label': 'Total CNPJs',
            'valor': stats.get('total_cnpjs', 0),
            'formato': 'numero',
            'help': 'Total de CNPJs monitorados'
        }
    ]

    criar_grid_kpis(kpis, colunas=4)

    st.markdown("---")

    # Gráficos Principais
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Distribuição de Score de Risco")
        if not df_filtrado.empty and 'score_final_percent' in df_filtrado.columns:
            fig_hist = criar_histograma(
                df_filtrado,
                'score_final_percent',
                'Distribuição de Score de Risco',
                bins=30,
                cor=CORES['primaria'],
                mostrar_estatisticas=True
            )
            st.plotly_chart(fig_hist, use_container_width=True, config={'displayModeBar': True})
        else:
            st.info("Dados não disponíveis")

    with col2:
        st.markdown("### 🎯 Grupos por Nível de Risco")
        if not df_filtrado.empty and 'nivel_risco_final' in df_filtrado.columns:
            dist_risco = df_filtrado['nivel_risco_final'].value_counts().reset_index()
            dist_risco.columns = ['Nível', 'Quantidade']

            fig_pizza = criar_grafico_pizza(
                dist_risco,
                values='Quantidade',
                names='Nível',
                titulo='Distribuição por Nível de Risco',
                hole=0.4,
                mostrar_percentual=True
            )
            st.plotly_chart(fig_pizza, use_container_width=True)
        else:
            st.info("Dados não disponíveis")

    st.markdown("---")

    # Análises Adicionais
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### 💰 Top 15 Grupos por Receita")
        if not df_filtrado.empty and 'receita_maxima' in df_filtrado.columns:
            top_receita = df_filtrado.nlargest(15, 'receita_maxima')[['num_grupo', 'receita_maxima', 'score_final_percent']]

            fig_barras = criar_grafico_barras(
                top_receita,
                x='num_grupo',
                y='receita_maxima',
                titulo='Top 15 Grupos por Receita Máxima',
                orientacao='v',
                cor=CORES['secundaria']
            )
            st.plotly_chart(fig_barras, use_container_width=True)
        else:
            st.info("Dados não disponíveis")

    with col4:
        st.markdown("### 🏢 Top 15 Grupos por Quantidade de CNPJs")
        if not df_filtrado.empty and 'qtd_cnpjs' in df_filtrado.columns:
            top_cnpjs = df_filtrado.nlargest(15, 'qtd_cnpjs')[['num_grupo', 'qtd_cnpjs', 'score_final_percent']]

            fig_barras_cnpj = criar_grafico_barras(
                top_cnpjs,
                x='num_grupo',
                y='qtd_cnpjs',
                titulo='Top 15 Grupos por Quantidade de CNPJs',
                orientacao='v',
                cor=CORES['sucesso']
            )
            st.plotly_chart(fig_barras_cnpj, use_container_width=True)
        else:
            st.info("Dados não disponíveis")

    st.markdown("---")

    # Insights Gerais
    st.markdown("### 💡 Insights Gerais do Sistema")
    insights_gerais = gerar_insights_gerais(df_filtrado)
    exibir_insights(insights_gerais)

    # Exportação
    st.markdown("---")
    st.markdown("### 📥 Exportar Dados")

    col_exp1, col_exp2 = st.columns(2)

    with col_exp1:
        criar_botao_download_excel(
            {'Dashboard': df_filtrado.head(1000)},
            nome_arquivo='dashboard_executivo',
            label='📥 Download Dashboard (Excel)'
        )

    with col_exp2:
        criar_botao_download_csv(
            df_filtrado.head(1000),
            nome_arquivo='dashboard_executivo',
            label='📥 Download Dashboard (CSV)'
        )

# =============================================================================
# PÁGINA 2: ANÁLISE PONTUAL
# =============================================================================

elif pagina == "🎯 Análise Pontual":
    st.markdown("<h1 class='main-header'>🎯 Análise Pontual de Grupo</h1>", unsafe_allow_html=True)

    st.markdown("### 🔍 Buscar Grupo")

    col_busca1, col_busca2 = st.columns(2)

    with col_busca1:
        num_grupo_input = st.text_input(
            "Número do Grupo",
            placeholder="Digite o número do grupo",
            help="Informe o número do grupo econômico"
        )

    with col_busca2:
        cnpj_input = st.text_input(
            "ou CNPJ",
            placeholder="Digite o CNPJ",
            help="Informe um CNPJ para buscar seu grupo"
        )

    # Determinar grupo a buscar
    num_grupo_buscar = None

    if cnpj_input:
        with st.spinner("Buscando grupo do CNPJ..."):
            num_grupo_buscar = buscar_grupo_por_cnpj(engine, cnpj_input)
            if num_grupo_buscar:
                st.success(f"✅ CNPJ encontrado no grupo {num_grupo_buscar}")
            else:
                st.error("❌ CNPJ não encontrado na base de dados")
    elif num_grupo_input:
        num_grupo_buscar = num_grupo_input

    # Exibir análise se grupo foi encontrado
    if num_grupo_buscar:
        with st.spinner("Carregando dados do grupo..."):
            # Buscar dados principais
            dados_grupo = dados['percent'][dados['percent']['num_grupo'] == num_grupo_buscar]

            if dados_grupo.empty:
                st.error(f"❌ Grupo {num_grupo_buscar} não encontrado")
            else:
                grupo_serie = dados_grupo.iloc[0]

                # Carregar dossiê completo
                dossie = carregar_dossie_completo(engine, num_grupo_buscar)

                st.markdown("---")

                # KPIs do Grupo
                st.markdown("### 📌 Resumo do Grupo")

                kpis_grupo = [
                    {'label': 'Número do Grupo', 'valor': num_grupo_buscar, 'formato': 'texto'},
                    {'label': 'CNPJs', 'valor': grupo_serie.get('qtd_cnpjs', 0), 'formato': 'numero'},
                    {'label': 'Score', 'valor': grupo_serie.get('score_final_percent', 0), 'formato': 'numero'},
                    {'label': 'Nível', 'valor': grupo_serie.get('nivel_risco_final', 'N/A'), 'formato': 'texto'}
                ]

                cols_kpi = st.columns(4)
                for idx, kpi_info in enumerate(kpis_grupo):
                    with cols_kpi[idx]:
                        if kpi_info['formato'] == 'numero':
                            criar_kpi(kpi_info['label'], kpi_info['valor'], formato='numero')
                        else:
                            st.metric(kpi_info['label'], kpi_info['valor'])

                st.markdown("---")

                # Gauge de Risco
                col_gauge, col_detalhes = st.columns([1, 2])

                with col_gauge:
                    st.markdown("### 🎯 Medidor de Risco")
                    score = grupo_serie.get('score_final_percent', 0)
                    fig_gauge = criar_gauge(
                        valor=score,
                        titulo="Score de Risco",
                        max_valor=100,
                        cor_baixo="#2ca02c",
                        cor_medio="#ff9800",
                        cor_alto="#d62728"
                    )
                    st.plotly_chart(fig_gauge, use_container_width=True)

                with col_detalhes:
                    st.markdown("### 📋 Detalhes de Risco")

                    detalhes_risco = {
                        'Sócios Compartilhados': formatar_numero(grupo_serie.get('socios_compartilhados', 0)),
                        'Contas Compartilhadas': formatar_numero(grupo_serie.get('contas_compartilhadas', 0)),
                        'Total de Indícios': formatar_numero(grupo_serie.get('total_indicios', 0)),
                        'Receita Máxima': formatar_moeda(grupo_serie.get('receita_maxima', 0)),
                        'Risco C115': grupo_serie.get('nivel_risco_c115', 'N/A')
                    }

                    for label, valor in detalhes_risco.items():
                        st.markdown(f"**{label}:** {valor}")

                st.markdown("---")

                # Insights Automáticos
                st.markdown("### 💡 Insights Automáticos")
                insights = gerar_insights_grupo(grupo_serie, dossie)
                exibir_insights(insights)

                st.markdown("---")

                # CNPJs do Grupo
                st.markdown("### 🏢 CNPJs do Grupo")
                if not dossie.get('cnpjs', pd.DataFrame()).empty:
                    exibir_tabela_formatada(
                        dossie['cnpjs'][['cnpj', 'nm_razao_social', 'nm_fantasia', 'nm_municipio']].head(50),
                        altura=300
                    )
                else:
                    st.info("Nenhum CNPJ encontrado")

                st.markdown("---")

                # Exportar Dossiê
                st.markdown("### 📥 Exportar Dossiê")

                col_pdf, col_excel = st.columns(2)

                with col_pdf:
                    criar_botao_download_pdf(
                        num_grupo_buscar,
                        grupo_serie,
                        dossie,
                        label='📄 Download Dossiê (PDF)'
                    )

                with col_excel:
                    dados_export = {
                        'Dados Principais': pd.DataFrame([grupo_serie]),
                        'CNPJs': dossie.get('cnpjs', pd.DataFrame()),
                        'Sócios': dossie.get('socios', pd.DataFrame()),
                        'Indícios': dossie.get('indicios', pd.DataFrame())
                    }

                    criar_botao_download_excel(
                        dados_export,
                        nome_arquivo=f'dossie_grupo_{num_grupo_buscar}',
                        label='📊 Download Dossiê (Excel)'
                    )

# =============================================================================
# PÁGINA 3: RANKING
# =============================================================================

elif pagina == "📈 Ranking de Grupos":
    st.markdown("<h1 class='main-header'>📈 Ranking de Grupos por Risco</h1>", unsafe_allow_html=True)

    st.markdown("### 🏆 Top Grupos de Maior Risco")

    # Configurar quantidade
    top_n = st.slider("Quantidade de grupos no ranking", 10, 100, 30, step=10)

    # Ordenar e pegar top N
    if not df_filtrado.empty and 'score_final_percent' in df_filtrado.columns:
        top_grupos = df_filtrado.nlargest(top_n, 'score_final_percent')

        # Adicionar ranking
        top_grupos['ranking'] = range(1, len(top_grupos) + 1)

        # Selecionar colunas relevantes
        colunas_exibir = ['ranking', 'num_grupo', 'qtd_cnpjs', 'score_final_percent',
                         'nivel_risco_final', 'receita_maxima', 'socios_compartilhados',
                         'contas_compartilhadas', 'total_indicios']

        colunas_disponiveis = [col for col in colunas_exibir if col in top_grupos.columns]

        # Exibir tabela
        exibir_tabela_formatada(
            top_grupos[colunas_disponiveis],
            colunas_moeda=['receita_maxima'] if 'receita_maxima' in colunas_disponiveis else None,
            altura=600
        )

        # Gráfico de barras
        st.markdown("---")
        st.markdown("### 📊 Visualização do Ranking")

        fig_ranking = criar_grafico_barras(
            top_grupos.head(20),
            x='num_grupo',
            y='score_final_percent',
            titulo=f'Top 20 Grupos por Score de Risco',
            orientacao='v',
            cor=CORES['perigo']
        )

        st.plotly_chart(fig_ranking, use_container_width=True)

        # Exportação
        st.markdown("---")
        st.markdown("### 📥 Exportar Ranking")

        col_rank1, col_rank2 = st.columns(2)

        with col_rank1:
            criar_botao_download_excel(
                {'Ranking': top_grupos},
                nome_arquivo='ranking_grupos',
                label='📥 Download Ranking (Excel)'
            )

        with col_rank2:
            criar_botao_download_csv(
                top_grupos,
                nome_arquivo='ranking_grupos',
                label='📥 Download Ranking (CSV)'
            )

    else:
        st.info("Dados não disponíveis para gerar ranking")

# =============================================================================
# PÁGINA 4: MACHINE LEARNING
# =============================================================================

elif pagina == "🤖 Machine Learning":
    st.markdown("<h1 class='main-header'>🤖 Análise de Machine Learning</h1>", unsafe_allow_html=True)

    st.markdown("""
    Esta página permite aplicar algoritmos de **Machine Learning** para identificar padrões
    e anomalias nos grupos econômicos monitorados.
    """)

    st.markdown("---")

    # Preparar dados
    st.markdown("### ⚙️ Configurações")

    col_ml1, col_ml2, col_ml3 = st.columns(3)

    with col_ml1:
        n_clusters = st.slider("Número de Clusters (K-Means)", 2, 10, 3)

    with col_ml2:
        eps_dbscan = st.slider("EPS (DBSCAN)", 0.1, 2.0, 0.5, step=0.1)

    with col_ml3:
        contamination = st.slider("Contaminação (Isolation Forest)", 0.05, 0.5, 0.1, step=0.05)

    if st.button("🚀 Executar Análise de ML", type="primary"):
        with st.spinner("Preparando dados..."):
            df_clean, X_scaled, scaler = preparar_dados_ml(df_filtrado)

            if len(df_clean) < 10:
                st.error("Dados insuficientes para análise de ML (mínimo 10 registros)")
            else:
                # Aplicar PCA
                st.markdown("---")
                st.markdown("### 📐 Redução de Dimensionalidade (PCA)")

                X_pca, pca_model, var_explicada = aplicar_pca(X_scaled, n_components=3)

                st.success(f"✅ PCA aplicado com sucesso! Variância explicada: {var_explicada:.2f}%")

                # Executar consenso
                st.markdown("---")
                st.markdown("### 🔬 Análise de Consenso - Múltiplos Algoritmos")

                resultados = executar_consenso(X_scaled, n_clusters, eps_dbscan, contamination)

                # Exibir métricas
                st.markdown("#### 📊 Métricas de Qualidade")

                metricas_df = pd.DataFrame({
                    'Algoritmo': [res['nome'] for res in resultados.values()],
                    'Silhouette': [res['metricas'].get('silhouette', 'N/A') for res in resultados.values()],
                    'Davies-Bouldin': [res['metricas'].get('davies_bouldin', 'N/A') for res in resultados.values()],
                    'N Clusters/Anomalias': [
                        res['metricas'].get('n_clusters', res['metricas'].get('n_anomalias', 'N/A'))
                        for res in resultados.values()
                    ]
                })

                st.dataframe(metricas_df, use_container_width=True)

                # Visualização comparativa
                st.markdown("---")
                st.markdown("### 📊 Visualização Comparativa")

                fig_comp = comparar_algoritmos(resultados, X_pca)
                st.plotly_chart(fig_comp, use_container_width=True)

                # Visualização 3D
                st.markdown("---")
                st.markdown("### 🎨 Visualização 3D (K-Means)")

                labels_km = resultados['kmeans']['labels']
                fig_3d = visualizar_clusters_3d(X_pca, labels_km, df_clean, "Clusters K-Means em 3D")
                st.plotly_chart(fig_3d, use_container_width=True)

    else:
        st.info("👆 Configure os parâmetros e clique em 'Executar Análise de ML' para começar")

# =============================================================================
# PÁGINA 5: ANÁLISE DE REDES
# =============================================================================

elif pagina == "🔗 Análise de Redes":
    st.markdown("<h1 class='main-header'>🔗 Análise de Redes Societárias</h1>", unsafe_allow_html=True)

    st.markdown("""
    Visualize as conexões entre grupos econômicos através de sócios compartilhados
    e outras relações societárias.
    """)

    st.markdown("---")

    # Selecionar grupo para análise
    num_grupo_rede = st.text_input(
        "Número do Grupo para Análise de Rede",
        placeholder="Digite o número do grupo"
    )

    if num_grupo_rede:
        with st.spinner("Carregando dados da rede..."):
            # Carregar sócios compartilhados
            if not dados.get('socios_compartilhados', pd.DataFrame()).empty:
                df_socios = dados['socios_compartilhados'][
                    dados['socios_compartilhados']['num_grupo'] == num_grupo_rede
                ]

                if not df_socios.empty:
                    # Criar nós e arestas
                    nos = []
                    arestas = []

                    # Nó central (grupo)
                    nos.append({
                        'id': f'grupo_{num_grupo_rede}',
                        'label': f'Grupo {num_grupo_rede}',
                        'value': 20
                    })

                    # Nós de sócios
                    for idx, row in df_socios.iterrows():
                        cpf = row['cpf_socio']
                        qtd = row['qtd_empresas']

                        nos.append({
                            'id': f'socio_{cpf}',
                            'label': f'CPF {cpf[:6]}...',
                            'value': min(qtd * 2, 15)
                        })

                        # Aresta
                        arestas.append({
                            'source': f'grupo_{num_grupo_rede}',
                            'target': f'socio_{cpf}',
                            'value': min(qtd, 5)
                        })

                    # Criar gráfico de rede
                    fig_rede = criar_grafico_rede(
                        nos,
                        arestas,
                        f'Rede de Sócios do Grupo {num_grupo_rede}'
                    )

                    st.plotly_chart(fig_rede, use_container_width=True)

                    # Tabela de sócios
                    st.markdown("---")
                    st.markdown("### 👥 Sócios Compartilhados")

                    exibir_tabela_formatada(df_socios, altura=400)

                else:
                    st.info("Nenhum sócio compartilhado encontrado para este grupo")
            else:
                st.warning("Dados de sócios não disponíveis")
    else:
        st.info("Digite o número de um grupo para visualizar sua rede societária")

# =============================================================================
# PÁGINA 6: ANÁLISE MULTIDIMENSIONAL
# =============================================================================

elif pagina == "📐 Análise Multidimensional":
    st.markdown("<h1 class='main-header'>📐 Análise Multidimensional</h1>", unsafe_allow_html=True)

    st.markdown("""
    Explore correlações e padrões multidimensionais entre diferentes métricas de risco.
    """)

    st.markdown("---")

    # Selecionar colunas para análise
    colunas_numericas = df_filtrado.select_dtypes(include=[np.number]).columns.tolist()

    colunas_selecionadas = st.multiselect(
        "Selecione as métricas para análise",
        options=colunas_numericas,
        default=colunas_numericas[:min(6, len(colunas_numericas))],
        help="Selecione até 10 métricas"
    )

    if len(colunas_selecionadas) >= 2:
        # Matriz de Correlação
        st.markdown("### 🔥 Matriz de Correlação")

        fig_corr = criar_matriz_correlacao(
            df_filtrado,
            colunas=colunas_selecionadas,
            titulo="Matriz de Correlação entre Métricas",
            metodo='pearson'
        )

        st.plotly_chart(fig_corr, use_container_width=True)

        st.markdown("---")

        # Scatter Matrix
        if len(colunas_selecionadas) <= 5:
            st.markdown("### 📊 Scatter Matrix")

            from plotly.subplots import make_subplots
            import plotly.express as px

            fig_scatter = px.scatter_matrix(
                df_filtrado,
                dimensions=colunas_selecionadas,
                title="Matriz de Dispersão"
            )

            fig_scatter.update_traces(diagonal_visible=False)
            st.plotly_chart(fig_scatter, use_container_width=True)

    else:
        st.info("Selecione pelo menos 2 métricas para análise")

# =============================================================================
# PÁGINA 7: INSIGHTS AUTOMÁTICOS
# =============================================================================

elif pagina == "💡 Insights Automáticos":
    st.markdown("<h1 class='main-header'>💡 Insights Automáticos</h1>", unsafe_allow_html=True)

    st.markdown("""
    Insights gerados automaticamente pelo sistema com base em análise de padrões e regras de negócio.
    """)

    st.markdown("---")

    # Insights gerais
    st.markdown("### 🌐 Insights Gerais do Sistema")

    insights_sistema = gerar_insights_gerais(df_filtrado)
    exibir_insights(insights_sistema)

    st.markdown("---")

    # Top grupos com insights
    st.markdown("### 🔝 Grupos Prioritários para Investigação")

    if not df_filtrado.empty and 'score_final_percent' in df_filtrado.columns:
        top_investigacao = df_filtrado.nlargest(10, 'score_final_percent')

        for idx, (_, grupo) in enumerate(top_investigacao.iterrows(), 1):
            with st.expander(f"#{idx} - Grupo {grupo['num_grupo']} (Score: {grupo['score_final_percent']:.1f}%)"):
                # Carregar dossiê resumido
                dossie_resumo = {'cnpjs': pd.DataFrame(), 'socios': pd.DataFrame()}

                insights_grupo = gerar_insights_grupo(grupo, dossie_resumo)
                exibir_insights(insights_grupo)

# =============================================================================
# PÁGINA 8: DOSSIÊ COMPLETO
# =============================================================================

elif pagina == "📋 Dossiê Completo":
    st.markdown("<h1 class='main-header'>📋 Gerador de Dossiê Completo</h1>", unsafe_allow_html=True)

    st.markdown("""
    Gere um dossiê completo e detalhado de um grupo econômico com todas as informações disponíveis.
    """)

    st.markdown("---")

    num_grupo_dossie = st.text_input(
        "Número do Grupo",
        placeholder="Digite o número do grupo para gerar o dossiê"
    )

    if num_grupo_dossie and st.button("📄 Gerar Dossiê Completo", type="primary"):
        with st.spinner("Gerando dossiê completo..."):
            # Buscar dados
            dados_grupo_dossie = dados['percent'][dados['percent']['num_grupo'] == num_grupo_dossie]

            if dados_grupo_dossie.empty:
                st.error(f"Grupo {num_grupo_dossie} não encontrado")
            else:
                grupo_dossie_serie = dados_grupo_dossie.iloc[0]
                dossie_completo = carregar_dossie_completo(engine, num_grupo_dossie)

                st.success("✅ Dossiê gerado com sucesso!")

                # Botão de download
                criar_botao_download_pdf(
                    num_grupo_dossie,
                    grupo_dossie_serie,
                    dossie_completo,
                    label='📥 Download Dossiê Completo (PDF)'
                )

# =============================================================================
# PÁGINA 9: CONFIGURAÇÕES
# =============================================================================

elif pagina == "⚙️ Configurações":
    st.markdown("<h1 class='main-header'>⚙️ Configurações do Sistema</h1>", unsafe_allow_html=True)

    st.markdown("### ℹ️ Informações do Sistema")

    st.info("""
    **Sistema:** GEI - Gestão Estratégica de Informações v4.0
    **Desenvolvido para:** Receita Estadual de Santa Catarina
    **Última Atualização:** 2025
    """)

    st.markdown("---")

    st.markdown("### 📊 Estatísticas de Cache")

    if st.button("🔄 Limpar Cache"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.success("✅ Cache limpo com sucesso!")
        st.rerun()

    st.markdown("---")

    st.markdown("### 📚 Sobre o Sistema")

    with st.expander("ℹ️ Funcionalidades"):
        st.markdown("""
        - **Dashboard Executivo:** Visão geral com KPIs e gráficos
        - **Análise Pontual:** Análise detalhada de grupos específicos
        - **Ranking:** Top grupos por risco
        - **Machine Learning:** Clustering e detecção de anomalias
        - **Análise de Redes:** Visualização de vínculos societários
        - **Análise Multidimensional:** Correlações entre métricas
        - **Insights Automáticos:** Geração automática de insights
        - **Dossiê Completo:** Relatórios em PDF
        """)

    with st.expander("🔧 Tecnologias Utilizadas"):
        st.markdown("""
        - **Framework:** Streamlit
        - **Visualização:** Plotly
        - **Machine Learning:** scikit-learn
        - **Banco de Dados:** Impala
        - **Relatórios:** ReportLab, openpyxl
        """)

# =============================================================================
# RODAPÉ
# =============================================================================

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9em;'>"
    "© 2025 Sistema GEI - Receita Estadual de Santa Catarina | v4.0"
    "</div>",
    unsafe_allow_html=True
)
