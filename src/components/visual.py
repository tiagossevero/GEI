"""
Módulo de Componentes Visuais Reutilizáveis
Contém funções para criar KPIs, gráficos, tabelas e outros elementos visuais
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Optional, Any, Tuple
import numpy as np

from ..config.settings import (
    CORES, PALETAS, PLOTLY_CONFIG, PLOTLY_LAYOUT,
    NIVEIS_RISCO, formatar_moeda, formatar_numero,
    formatar_percentual, classificar_risco
)

# =============================================================================
# COMPONENTES DE KPI
# =============================================================================

def criar_kpi(
    label: str,
    valor: Any,
    delta: Optional[str] = None,
    help_text: Optional[str] = None,
    formato: str = 'numero'
) -> None:
    """
    Cria um KPI (métrica) formatado

    Args:
        label: Título do KPI
        valor: Valor a exibir
        delta: Variação (opcional)
        help_text: Texto de ajuda (opcional)
        formato: Tipo de formatação ('numero', 'moeda', 'percentual')
    """
    if formato == 'moeda':
        valor_formatado = formatar_moeda(valor)
    elif formato == 'percentual':
        valor_formatado = formatar_percentual(valor)
    elif formato == 'numero':
        valor_formatado = formatar_numero(valor)
    else:
        valor_formatado = str(valor)

    st.metric(
        label=label,
        value=valor_formatado,
        delta=delta,
        help=help_text
    )

def criar_grid_kpis(kpis: List[Dict], colunas: int = 4) -> None:
    """
    Cria um grid de KPIs

    Args:
        kpis: Lista de dicionários com configurações dos KPIs
              Exemplo: [{'label': 'Total', 'valor': 100, 'formato': 'numero'}]
        colunas: Número de colunas no grid
    """
    cols = st.columns(colunas)

    for idx, kpi in enumerate(kpis):
        col_idx = idx % colunas
        with cols[col_idx]:
            criar_kpi(
                label=kpi.get('label', ''),
                valor=kpi.get('valor', 0),
                delta=kpi.get('delta'),
                help_text=kpi.get('help'),
                formato=kpi.get('formato', 'numero')
            )

def criar_kpi_colorido(
    label: str,
    valor: Any,
    cor: str = CORES['primaria'],
    icone: str = "📊"
) -> None:
    """
    Cria um KPI com fundo colorido e ícone

    Args:
        label: Título do KPI
        valor: Valor a exibir
        cor: Cor de fundo (hex)
        icone: Ícone a exibir
    """
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {cor}22 0%, {cor}44 100%);
        border-left: 4px solid {cor};
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    ">
        <div style="font-size: 2em; margin-bottom: 5px;">{icone}</div>
        <div style="color: #666; font-size: 0.9em; margin-bottom: 5px;">{label}</div>
        <div style="font-size: 2em; font-weight: bold; color: {cor};">{valor}</div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# GRÁFICOS DE DISTRIBUIÇÃO
# =============================================================================

def criar_histograma(
    df: pd.DataFrame,
    coluna: str,
    titulo: str,
    bins: int = 30,
    cor: str = CORES['primaria'],
    mostrar_estatisticas: bool = True
) -> go.Figure:
    """
    Cria um histograma

    Args:
        df: DataFrame com dados
        coluna: Nome da coluna para o histograma
        titulo: Título do gráfico
        bins: Número de bins
        cor: Cor das barras
        mostrar_estatisticas: Se True, exibe média e mediana

    Returns:
        Figura Plotly
    """
    fig = px.histogram(
        df,
        x=coluna,
        nbins=bins,
        title=titulo,
        color_discrete_sequence=[cor]
    )

    if mostrar_estatisticas and not df[coluna].isna().all():
        media = df[coluna].mean()
        mediana = df[coluna].median()

        fig.add_vline(x=media, line_dash="dash", line_color="red",
                     annotation_text=f"Média: {media:.2f}")
        fig.add_vline(x=mediana, line_dash="dash", line_color="green",
                     annotation_text=f"Mediana: {mediana:.2f}")

    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

def criar_boxplot(
    df: pd.DataFrame,
    coluna_y: str,
    coluna_x: Optional[str] = None,
    titulo: str = "",
    cor: str = CORES['primaria']
) -> go.Figure:
    """
    Cria um boxplot

    Args:
        df: DataFrame com dados
        coluna_y: Coluna para o eixo Y
        coluna_x: Coluna para agrupar (opcional)
        titulo: Título do gráfico
        cor: Cor das caixas

    Returns:
        Figura Plotly
    """
    if coluna_x:
        fig = px.box(df, x=coluna_x, y=coluna_y, title=titulo,
                    color_discrete_sequence=[cor])
    else:
        fig = px.box(df, y=coluna_y, title=titulo,
                    color_discrete_sequence=[cor])

    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

def criar_violinplot(
    df: pd.DataFrame,
    coluna_y: str,
    coluna_x: Optional[str] = None,
    titulo: str = "",
    cor: str = CORES['primaria']
) -> go.Figure:
    """
    Cria um violin plot

    Args:
        df: DataFrame com dados
        coluna_y: Coluna para o eixo Y
        coluna_x: Coluna para agrupar (opcional)
        titulo: Título do gráfico
        cor: Cor

    Returns:
        Figura Plotly
    """
    if coluna_x:
        fig = px.violin(df, x=coluna_x, y=coluna_y, title=titulo,
                       color_discrete_sequence=[cor], box=True)
    else:
        fig = px.violin(df, y=coluna_y, title=titulo,
                       color_discrete_sequence=[cor], box=True)

    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

# =============================================================================
# GRÁFICOS DE BARRAS E COLUNAS
# =============================================================================

def criar_grafico_barras(
    df: pd.DataFrame,
    x: str,
    y: str,
    titulo: str,
    orientacao: str = 'v',
    cor: Optional[str] = None,
    cor_coluna: Optional[str] = None,
    top_n: Optional[int] = None
) -> go.Figure:
    """
    Cria um gráfico de barras

    Args:
        df: DataFrame com dados
        x: Coluna para eixo X
        y: Coluna para eixo Y
        titulo: Título do gráfico
        orientacao: 'v' para vertical, 'h' para horizontal
        cor: Cor única das barras
        cor_coluna: Coluna para definir cores
        top_n: Mostrar apenas os top N valores

    Returns:
        Figura Plotly
    """
    df_plot = df.copy()

    if top_n:
        df_plot = df_plot.nlargest(top_n, y)

    if cor_coluna:
        fig = px.bar(df_plot, x=x, y=y, title=titulo, orientation=orientacao,
                    color=cor_coluna, color_continuous_scale=PALETAS['sequencial'])
    else:
        cor_final = cor or CORES['primaria']
        fig = px.bar(df_plot, x=x, y=y, title=titulo, orientation=orientacao,
                    color_discrete_sequence=[cor_final])

    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

def criar_grafico_barras_agrupadas(
    df: pd.DataFrame,
    x: str,
    y: List[str],
    titulo: str,
    labels: Optional[Dict] = None
) -> go.Figure:
    """
    Cria gráfico de barras agrupadas

    Args:
        df: DataFrame com dados
        x: Coluna para eixo X
        y: Lista de colunas para agrupar
        titulo: Título do gráfico
        labels: Dicionário de labels customizados

    Returns:
        Figura Plotly
    """
    fig = go.Figure()

    for idx, coluna in enumerate(y):
        fig.add_trace(go.Bar(
            x=df[x],
            y=df[coluna],
            name=labels.get(coluna, coluna) if labels else coluna,
            marker_color=PALETAS['categorica'][idx % len(PALETAS['categorica'])]
        ))

    fig.update_layout(
        title=titulo,
        barmode='group',
        **PLOTLY_LAYOUT
    )
    return fig

def criar_grafico_barras_empilhadas(
    df: pd.DataFrame,
    x: str,
    y: List[str],
    titulo: str,
    labels: Optional[Dict] = None
) -> go.Figure:
    """
    Cria gráfico de barras empilhadas

    Args:
        df: DataFrame com dados
        x: Coluna para eixo X
        y: Lista de colunas para empilhar
        titulo: Título do gráfico
        labels: Dicionário de labels customizados

    Returns:
        Figura Plotly
    """
    fig = go.Figure()

    for idx, coluna in enumerate(y):
        fig.add_trace(go.Bar(
            x=df[x],
            y=df[coluna],
            name=labels.get(coluna, coluna) if labels else coluna,
            marker_color=PALETAS['categorica'][idx % len(PALETAS['categorica'])]
        ))

    fig.update_layout(
        title=titulo,
        barmode='stack',
        **PLOTLY_LAYOUT
    )
    return fig

# =============================================================================
# GRÁFICOS DE PIZZA E DONUT
# =============================================================================

def criar_grafico_pizza(
    df: pd.DataFrame,
    values: str,
    names: str,
    titulo: str,
    hole: float = 0,
    mostrar_percentual: bool = True
) -> go.Figure:
    """
    Cria gráfico de pizza ou donut

    Args:
        df: DataFrame com dados
        values: Coluna com valores
        names: Coluna com nomes
        titulo: Título do gráfico
        hole: Tamanho do buraco (0 = pizza, 0.4 = donut)
        mostrar_percentual: Se True, mostra percentuais

    Returns:
        Figura Plotly
    """
    fig = px.pie(
        df,
        values=values,
        names=names,
        title=titulo,
        hole=hole,
        color_discrete_sequence=PALETAS['categorica']
    )

    if mostrar_percentual:
        fig.update_traces(textposition='inside', textinfo='percent+label')

    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

# =============================================================================
# GRÁFICOS DE LINHA E ÁREA
# =============================================================================

def criar_grafico_linha(
    df: pd.DataFrame,
    x: str,
    y: str | List[str],
    titulo: str,
    marcadores: bool = True,
    area: bool = False
) -> go.Figure:
    """
    Cria gráfico de linha

    Args:
        df: DataFrame com dados
        x: Coluna para eixo X
        y: Coluna ou lista de colunas para eixo Y
        titulo: Título do gráfico
        marcadores: Se True, mostra marcadores
        area: Se True, preenche área abaixo da linha

    Returns:
        Figura Plotly
    """
    if isinstance(y, str):
        y = [y]

    fig = go.Figure()

    for idx, coluna in enumerate(y):
        if area:
            fig.add_trace(go.Scatter(
                x=df[x],
                y=df[coluna],
                name=coluna,
                mode='lines+markers' if marcadores else 'lines',
                fill='tonexty' if idx > 0 else 'tozeroy',
                line=dict(color=PALETAS['categorica'][idx % len(PALETAS['categorica'])])
            ))
        else:
            fig.add_trace(go.Scatter(
                x=df[x],
                y=df[coluna],
                name=coluna,
                mode='lines+markers' if marcadores else 'lines',
                line=dict(color=PALETAS['categorica'][idx % len(PALETAS['categorica'])])
            ))

    fig.update_layout(title=titulo, **PLOTLY_LAYOUT)
    return fig

# =============================================================================
# GRÁFICOS DE DISPERSÃO
# =============================================================================

def criar_grafico_dispersao(
    df: pd.DataFrame,
    x: str,
    y: str,
    titulo: str,
    cor_coluna: Optional[str] = None,
    tamanho_coluna: Optional[str] = None,
    texto_hover: Optional[str] = None,
    linha_tendencia: bool = False
) -> go.Figure:
    """
    Cria gráfico de dispersão

    Args:
        df: DataFrame com dados
        x: Coluna para eixo X
        y: Coluna para eixo Y
        titulo: Título do gráfico
        cor_coluna: Coluna para definir cores
        tamanho_coluna: Coluna para definir tamanho dos pontos
        texto_hover: Coluna para texto ao passar mouse
        linha_tendencia: Se True, adiciona linha de tendência

    Returns:
        Figura Plotly
    """
    kwargs = {
        'data_frame': df,
        'x': x,
        'y': y,
        'title': titulo
    }

    if cor_coluna:
        kwargs['color'] = cor_coluna
        kwargs['color_continuous_scale'] = PALETAS['sequencial']

    if tamanho_coluna:
        kwargs['size'] = tamanho_coluna

    if texto_hover:
        kwargs['hover_name'] = texto_hover

    if linha_tendencia:
        kwargs['trendline'] = 'ols'

    fig = px.scatter(**kwargs)
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

def criar_scatter_matrix(
    df: pd.DataFrame,
    colunas: List[str],
    titulo: str,
    cor_coluna: Optional[str] = None
) -> go.Figure:
    """
    Cria matriz de dispersão (scatter matrix)

    Args:
        df: DataFrame com dados
        colunas: Lista de colunas para a matriz
        titulo: Título do gráfico
        cor_coluna: Coluna para definir cores

    Returns:
        Figura Plotly
    """
    if cor_coluna:
        fig = px.scatter_matrix(df, dimensions=colunas, color=cor_coluna, title=titulo)
    else:
        fig = px.scatter_matrix(df, dimensions=colunas, title=titulo)

    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

# =============================================================================
# GRÁFICOS DE HEATMAP E CORRELAÇÃO
# =============================================================================

def criar_heatmap(
    df: pd.DataFrame,
    titulo: str,
    anotacoes: bool = True,
    colorscale: str = 'RdBu_r'
) -> go.Figure:
    """
    Cria heatmap

    Args:
        df: DataFrame (matriz) com dados
        titulo: Título do gráfico
        anotacoes: Se True, mostra valores nas células
        colorscale: Escala de cores

    Returns:
        Figura Plotly
    """
    fig = go.Figure(data=go.Heatmap(
        z=df.values,
        x=df.columns,
        y=df.index,
        colorscale=colorscale,
        text=df.values if anotacoes else None,
        texttemplate='%{text:.2f}' if anotacoes else None,
        textfont={"size": 10}
    ))

    fig.update_layout(title=titulo, **PLOTLY_LAYOUT)
    return fig

def criar_matriz_correlacao(
    df: pd.DataFrame,
    colunas: Optional[List[str]] = None,
    titulo: str = "Matriz de Correlação",
    metodo: str = 'pearson'
) -> go.Figure:
    """
    Cria matriz de correlação

    Args:
        df: DataFrame com dados
        colunas: Lista de colunas (se None, usa todas numéricas)
        titulo: Título do gráfico
        metodo: Método de correlação ('pearson', 'spearman', 'kendall')

    Returns:
        Figura Plotly
    """
    if colunas is None:
        df_corr = df.select_dtypes(include=[np.number]).corr(method=metodo)
    else:
        df_corr = df[colunas].corr(method=metodo)

    return criar_heatmap(df_corr, titulo, anotacoes=True, colorscale='RdBu_r')

# =============================================================================
# GRÁFICOS 3D
# =============================================================================

def criar_dispersao_3d(
    df: pd.DataFrame,
    x: str,
    y: str,
    z: str,
    titulo: str,
    cor_coluna: Optional[str] = None,
    tamanho: int = 5
) -> go.Figure:
    """
    Cria gráfico de dispersão 3D

    Args:
        df: DataFrame com dados
        x, y, z: Colunas para os três eixos
        titulo: Título do gráfico
        cor_coluna: Coluna para definir cores
        tamanho: Tamanho dos pontos

    Returns:
        Figura Plotly
    """
    if cor_coluna:
        fig = px.scatter_3d(df, x=x, y=y, z=z, color=cor_coluna, title=titulo)
    else:
        fig = px.scatter_3d(df, x=x, y=y, z=z, title=titulo)

    fig.update_traces(marker=dict(size=tamanho))
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

# =============================================================================
# GRÁFICOS DE FUNIL E GAUGE
# =============================================================================

def criar_gauge(
    valor: float,
    titulo: str,
    max_valor: float = 100,
    cor_baixo: str = "#2ca02c",
    cor_medio: str = "#ff9800",
    cor_alto: str = "#d62728"
) -> go.Figure:
    """
    Cria gráfico gauge (velocímetro)

    Args:
        valor: Valor atual
        titulo: Título do gráfico
        max_valor: Valor máximo da escala
        cor_baixo, cor_medio, cor_alto: Cores para faixas

    Returns:
        Figura Plotly
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=valor,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': titulo},
        gauge={
            'axis': {'range': [None, max_valor]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, max_valor * 0.4], 'color': cor_baixo},
                {'range': [max_valor * 0.4, max_valor * 0.8], 'color': cor_medio},
                {'range': [max_valor * 0.8, max_valor], 'color': cor_alto}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_valor * 0.9
            }
        }
    ))

    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

# =============================================================================
# GRÁFICOS COMPOSTOS E SUBPLOTS
# =============================================================================

def criar_subplots(
    figuras: List[Tuple[go.Figure, str]],
    linhas: int,
    colunas: int,
    titulo_geral: str
) -> go.Figure:
    """
    Cria subplots com múltiplos gráficos

    Args:
        figuras: Lista de tuplas (figura, título)
        linhas: Número de linhas
        colunas: Número de colunas
        titulo_geral: Título geral da figura

    Returns:
        Figura Plotly com subplots
    """
    subplot_titles = [titulo for _, titulo in figuras]

    fig = make_subplots(
        rows=linhas,
        cols=colunas,
        subplot_titles=subplot_titles
    )

    for idx, (figura, _) in enumerate(figuras):
        linha = idx // colunas + 1
        coluna = idx % colunas + 1

        for trace in figura.data:
            fig.add_trace(trace, row=linha, col=coluna)

    fig.update_layout(title_text=titulo_geral, **PLOTLY_LAYOUT)
    return fig

# =============================================================================
# TABELAS FORMATADAS
# =============================================================================

def exibir_tabela_formatada(
    df: pd.DataFrame,
    colunas_moeda: Optional[List[str]] = None,
    colunas_percentual: Optional[List[str]] = None,
    altura: int = 400
) -> None:
    """
    Exibe DataFrame com formatação

    Args:
        df: DataFrame a exibir
        colunas_moeda: Lista de colunas a formatar como moeda
        colunas_percentual: Lista de colunas a formatar como percentual
        altura: Altura da tabela em pixels
    """
    df_exibir = df.copy()

    if colunas_moeda:
        for col in colunas_moeda:
            if col in df_exibir.columns:
                df_exibir[col] = df_exibir[col].apply(formatar_moeda)

    if colunas_percentual:
        for col in colunas_percentual:
            if col in df_exibir.columns:
                df_exibir[col] = df_exibir[col].apply(formatar_percentual)

    st.dataframe(df_exibir, height=altura, use_container_width=True)

# =============================================================================
# GRÁFICOS DE REDE
# =============================================================================

def criar_grafico_rede(
    nos: List[Dict],
    arestas: List[Dict],
    titulo: str
) -> go.Figure:
    """
    Cria gráfico de rede (network graph)

    Args:
        nos: Lista de dicionários com nós {'id': str, 'label': str, 'value': float}
        arestas: Lista de dicionários com arestas {'source': str, 'target': str, 'value': float}
        titulo: Título do gráfico

    Returns:
        Figura Plotly
    """
    # Criar posições usando algoritmo de layout circular
    n_nos = len(nos)
    posicoes = {}
    for i, no in enumerate(nos):
        angulo = 2 * np.pi * i / n_nos
        posicoes[no['id']] = (np.cos(angulo), np.sin(angulo))

    # Criar traces para arestas
    edge_traces = []
    for aresta in arestas:
        x0, y0 = posicoes[aresta['source']]
        x1, y1 = posicoes[aresta['target']]

        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(width=aresta.get('value', 1), color='#888'),
            hoverinfo='none',
            showlegend=False
        )
        edge_traces.append(edge_trace)

    # Criar trace para nós
    node_x = [posicoes[no['id']][0] for no in nos]
    node_y = [posicoes[no['id']][1] for no in nos]
    node_text = [no['label'] for no in nos]
    node_size = [no.get('value', 10) for no in nos]

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        textposition="top center",
        marker=dict(
            size=node_size,
            color=CORES['primaria'],
            line=dict(width=2, color='white')
        ),
        showlegend=False
    )

    # Criar figura
    fig = go.Figure(data=edge_traces + [node_trace])

    fig.update_layout(
        title=titulo,
        showlegend=False,
        hovermode='closest',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        **PLOTLY_LAYOUT
    )

    return fig
