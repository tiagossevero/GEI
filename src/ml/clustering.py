"""
Módulo de Machine Learning - Clustering e Detecção de Anomalias
Implementa algoritmos de aprendizado não-supervisionado para identificação de padrões
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, Tuple, Optional, List
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.neighbors import LocalOutlierFactor
import plotly.graph_objects as go
import plotly.express as px

from ..config.settings import ML_FEATURES, CORES, PALETAS

# =============================================================================
# PREPARAÇÃO DE DADOS
# =============================================================================

def preparar_dados_ml(df: pd.DataFrame, features: Optional[List[str]] = None) -> Tuple[pd.DataFrame, np.ndarray, StandardScaler]:
    """
    Prepara dados para Machine Learning

    Args:
        df: DataFrame com dados
        features: Lista de features a usar (se None, usa ML_FEATURES)

    Returns:
        Tupla (df_clean, X_scaled, scaler)
    """
    if features is None:
        features = [f for f in ML_FEATURES if f in df.columns]

    # Remover linhas com valores faltantes
    df_clean = df[features].dropna()

    # Padronizar dados
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_clean)

    return df_clean, X_scaled, scaler

def aplicar_pca(X: np.ndarray, n_components: int = 2) -> Tuple[np.ndarray, PCA, float]:
    """
    Aplica PCA para redução de dimensionalidade

    Args:
        X: Matriz de features
        n_components: Número de componentes principais

    Returns:
        Tupla (X_pca, modelo_pca, variancia_explicada)
    """
    pca = PCA(n_components=n_components)
    X_pca = pca.fit_transform(X)

    variancia_explicada = sum(pca.explained_variance_ratio_) * 100

    return X_pca, pca, variancia_explicada

# =============================================================================
# ALGORITMOS DE CLUSTERING
# =============================================================================

def kmeans_clustering(
    X: np.ndarray,
    n_clusters: int = 3,
    random_state: int = 42
) -> Tuple[np.ndarray, KMeans, Dict[str, float]]:
    """
    Aplica algoritmo K-Means

    Args:
        X: Matriz de features
        n_clusters: Número de clusters
        random_state: Seed para reprodutibilidade

    Returns:
        Tupla (labels, modelo, metricas)
    """
    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = model.fit_predict(X)

    # Calcular métricas
    metricas = {
        'silhouette': silhouette_score(X, labels),
        'davies_bouldin': davies_bouldin_score(X, labels),
        'calinski_harabasz': calinski_harabasz_score(X, labels),
        'inertia': model.inertia_
    }

    return labels, model, metricas

def dbscan_clustering(
    X: np.ndarray,
    eps: float = 0.5,
    min_samples: int = 5
) -> Tuple[np.ndarray, DBSCAN, Dict[str, any]]:
    """
    Aplica algoritmo DBSCAN

    Args:
        X: Matriz de features
        eps: Raio de vizinhança
        min_samples: Número mínimo de amostras por cluster

    Returns:
        Tupla (labels, modelo, metricas)
    """
    model = DBSCAN(eps=eps, min_samples=min_samples)
    labels = model.fit_predict(X)

    # Contar clusters e outliers
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_outliers = list(labels).count(-1)

    metricas = {
        'n_clusters': n_clusters,
        'n_outliers': n_outliers,
        'perc_outliers': (n_outliers / len(labels)) * 100
    }

    # Calcular silhouette apenas se houver mais de 1 cluster
    if n_clusters > 1:
        # Remover outliers para cálculo
        mask = labels != -1
        if mask.sum() > 0:
            metricas['silhouette'] = silhouette_score(X[mask], labels[mask])

    return labels, model, metricas

def hierarchical_clustering(
    X: np.ndarray,
    n_clusters: int = 3,
    linkage: str = 'ward'
) -> Tuple[np.ndarray, AgglomerativeClustering, Dict[str, float]]:
    """
    Aplica clustering hierárquico

    Args:
        X: Matriz de features
        n_clusters: Número de clusters
        linkage: Método de linkage ('ward', 'complete', 'average')

    Returns:
        Tupla (labels, modelo, metricas)
    """
    model = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage)
    labels = model.fit_predict(X)

    metricas = {
        'silhouette': silhouette_score(X, labels),
        'davies_bouldin': davies_bouldin_score(X, labels),
        'calinski_harabasz': calinski_harabasz_score(X, labels)
    }

    return labels, model, metricas

# =============================================================================
# DETECÇÃO DE ANOMALIAS
# =============================================================================

def isolation_forest_anomalies(
    X: np.ndarray,
    contamination: float = 0.1,
    random_state: int = 42
) -> Tuple[np.ndarray, IsolationForest, Dict[str, any]]:
    """
    Detecta anomalias usando Isolation Forest

    Args:
        X: Matriz de features
        contamination: Proporção esperada de outliers
        random_state: Seed para reprodutibilidade

    Returns:
        Tupla (labels, modelo, metricas)
    """
    model = IsolationForest(contamination=contamination, random_state=random_state)
    labels = model.fit_predict(X)

    # 1 = normal, -1 = anomalia
    n_anomalias = list(labels).count(-1)

    metricas = {
        'n_anomalias': n_anomalias,
        'perc_anomalias': (n_anomalias / len(labels)) * 100,
        'scores': model.score_samples(X)
    }

    return labels, model, metricas

def local_outlier_factor_anomalies(
    X: np.ndarray,
    n_neighbors: int = 20,
    contamination: float = 0.1
) -> Tuple[np.ndarray, LocalOutlierFactor, Dict[str, any]]:
    """
    Detecta anomalias usando Local Outlier Factor

    Args:
        X: Matriz de features
        n_neighbors: Número de vizinhos
        contamination: Proporção esperada de outliers

    Returns:
        Tupla (labels, modelo, metricas)
    """
    model = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=contamination)
    labels = model.fit_predict(X)

    n_anomalias = list(labels).count(-1)

    metricas = {
        'n_anomalias': n_anomalias,
        'perc_anomalias': (n_anomalias / len(labels)) * 100,
        'scores': model.negative_outlier_factor_
    }

    return labels, model, metricas

# =============================================================================
# ANÁLISE DE CONSENSO
# =============================================================================

def executar_consenso(
    X: np.ndarray,
    n_clusters: int = 3,
    eps: float = 0.5,
    contamination: float = 0.1
) -> Dict[str, any]:
    """
    Executa múltiplos algoritmos e compara resultados (consenso)

    Args:
        X: Matriz de features
        n_clusters: Número de clusters para K-Means
        eps: Parâmetro eps para DBSCAN
        contamination: Proporção de outliers para Isolation Forest

    Returns:
        Dicionário com resultados de todos os algoritmos
    """
    resultados = {}

    # K-Means
    with st.spinner("Executando K-Means..."):
        labels_km, model_km, metricas_km = kmeans_clustering(X, n_clusters)
        resultados['kmeans'] = {
            'labels': labels_km,
            'model': model_km,
            'metricas': metricas_km,
            'nome': 'K-Means'
        }

    # DBSCAN
    with st.spinner("Executando DBSCAN..."):
        labels_db, model_db, metricas_db = dbscan_clustering(X, eps)
        resultados['dbscan'] = {
            'labels': labels_db,
            'model': model_db,
            'metricas': metricas_db,
            'nome': 'DBSCAN'
        }

    # Hierarchical
    with st.spinner("Executando Clustering Hierárquico..."):
        labels_hc, model_hc, metricas_hc = hierarchical_clustering(X, n_clusters)
        resultados['hierarchical'] = {
            'labels': labels_hc,
            'model': model_hc,
            'metricas': metricas_hc,
            'nome': 'Hierárquico'
        }

    # Isolation Forest
    with st.spinner("Executando Isolation Forest..."):
        labels_if, model_if, metricas_if = isolation_forest_anomalies(X, contamination)
        resultados['isolation_forest'] = {
            'labels': labels_if,
            'model': model_if,
            'metricas': metricas_if,
            'nome': 'Isolation Forest'
        }

    return resultados

# =============================================================================
# OTIMIZAÇÃO DE HIPERPARÂMETROS
# =============================================================================

def encontrar_melhor_k(X: np.ndarray, k_range: range = range(2, 11)) -> Tuple[int, Dict]:
    """
    Encontra melhor número de clusters usando método do cotovelo e silhouette

    Args:
        X: Matriz de features
        k_range: Range de valores de K a testar

    Returns:
        Tupla (melhor_k, metricas_por_k)
    """
    metricas_por_k = {}

    for k in k_range:
        labels, model, metricas = kmeans_clustering(X, k)

        metricas_por_k[k] = {
            'inertia': metricas['inertia'],
            'silhouette': metricas['silhouette'],
            'davies_bouldin': metricas['davies_bouldin'],
            'calinski_harabasz': metricas['calinski_harabasz']
        }

    # Melhor K baseado em silhouette
    melhor_k = max(metricas_por_k.keys(), key=lambda k: metricas_por_k[k]['silhouette'])

    return melhor_k, metricas_por_k

def otimizar_dbscan(X: np.ndarray, eps_range: List[float], min_samples_range: List[int]) -> Dict:
    """
    Otimiza parâmetros do DBSCAN

    Args:
        X: Matriz de features
        eps_range: Lista de valores eps a testar
        min_samples_range: Lista de valores min_samples a testar

    Returns:
        Dicionário com melhores parâmetros e resultados
    """
    melhores_params = None
    melhor_silhouette = -1

    resultados = []

    for eps in eps_range:
        for min_samples in min_samples_range:
            labels, model, metricas = dbscan_clustering(X, eps, min_samples)

            if 'silhouette' in metricas:
                sil = metricas['silhouette']
                if sil > melhor_silhouette:
                    melhor_silhouette = sil
                    melhores_params = {'eps': eps, 'min_samples': min_samples}

            resultados.append({
                'eps': eps,
                'min_samples': min_samples,
                **metricas
            })

    return {
        'melhores_params': melhores_params,
        'melhor_silhouette': melhor_silhouette,
        'todos_resultados': resultados
    }

# =============================================================================
# VISUALIZAÇÕES
# =============================================================================

def visualizar_clusters_2d(
    X_pca: np.ndarray,
    labels: np.ndarray,
    df_original: pd.DataFrame,
    titulo: str = "Visualização de Clusters"
) -> go.Figure:
    """
    Visualiza clusters em 2D após PCA

    Args:
        X_pca: Dados após PCA (2 componentes)
        labels: Labels dos clusters
        df_original: DataFrame original com metadados
        titulo: Título do gráfico

    Returns:
        Figura Plotly
    """
    df_plot = pd.DataFrame({
        'PC1': X_pca[:, 0],
        'PC2': X_pca[:, 1],
        'Cluster': labels.astype(str)
    })

    # Adicionar coluna de identificação se disponível
    if 'num_grupo' in df_original.columns:
        df_plot['num_grupo'] = df_original['num_grupo'].values

    fig = px.scatter(
        df_plot,
        x='PC1',
        y='PC2',
        color='Cluster',
        title=titulo,
        hover_data=['num_grupo'] if 'num_grupo' in df_plot.columns else None,
        color_discrete_sequence=PALETAS['categorica']
    )

    fig.update_traces(marker=dict(size=8, line=dict(width=1, color='white')))
    fig.update_layout(template='plotly_white')

    return fig

def visualizar_clusters_3d(
    X_pca: np.ndarray,
    labels: np.ndarray,
    df_original: pd.DataFrame,
    titulo: str = "Visualização 3D de Clusters"
) -> go.Figure:
    """
    Visualiza clusters em 3D após PCA

    Args:
        X_pca: Dados após PCA (3 componentes)
        labels: Labels dos clusters
        df_original: DataFrame original
        titulo: Título do gráfico

    Returns:
        Figura Plotly
    """
    df_plot = pd.DataFrame({
        'PC1': X_pca[:, 0],
        'PC2': X_pca[:, 1],
        'PC3': X_pca[:, 2] if X_pca.shape[1] > 2 else 0,
        'Cluster': labels.astype(str)
    })

    if 'num_grupo' in df_original.columns:
        df_plot['num_grupo'] = df_original['num_grupo'].values

    fig = px.scatter_3d(
        df_plot,
        x='PC1',
        y='PC2',
        z='PC3',
        color='Cluster',
        title=titulo,
        hover_data=['num_grupo'] if 'num_grupo' in df_plot.columns else None,
        color_discrete_sequence=PALETAS['categorica']
    )

    fig.update_traces(marker=dict(size=5, line=dict(width=0.5, color='white')))
    fig.update_layout(template='plotly_white')

    return fig

def grafico_elbow(metricas_por_k: Dict) -> go.Figure:
    """
    Cria gráfico do método do cotovelo

    Args:
        metricas_por_k: Dicionário com métricas por valor de K

    Returns:
        Figura Plotly
    """
    k_values = sorted(metricas_por_k.keys())
    inertias = [metricas_por_k[k]['inertia'] for k in k_values]
    silhouettes = [metricas_por_k[k]['silhouette'] for k in k_values]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=k_values,
        y=inertias,
        name='Inércia',
        mode='lines+markers',
        yaxis='y'
    ))

    fig.add_trace(go.Scatter(
        x=k_values,
        y=silhouettes,
        name='Silhouette Score',
        mode='lines+markers',
        yaxis='y2'
    ))

    fig.update_layout(
        title='Método do Cotovelo - Seleção de K',
        xaxis=dict(title='Número de Clusters (K)'),
        yaxis=dict(title='Inércia', side='left'),
        yaxis2=dict(title='Silhouette Score', overlaying='y', side='right'),
        template='plotly_white'
    )

    return fig

def comparar_algoritmos(resultados_consenso: Dict, X_pca: np.ndarray) -> go.Figure:
    """
    Cria visualização comparativa de múltiplos algoritmos

    Args:
        resultados_consenso: Resultados de todos os algoritmos
        X_pca: Dados após PCA

    Returns:
        Figura Plotly com subplots
    """
    from plotly.subplots import make_subplots

    n_algoritmos = len(resultados_consenso)
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=[res['nome'] for res in resultados_consenso.values()]
    )

    cores = PALETAS['categorica']

    for idx, (nome, resultado) in enumerate(resultados_consenso.items()):
        row = idx // 2 + 1
        col = idx % 2 + 1

        labels = resultado['labels']
        unique_labels = np.unique(labels)

        for label_idx, label in enumerate(unique_labels):
            mask = labels == label
            fig.add_trace(
                go.Scatter(
                    x=X_pca[mask, 0],
                    y=X_pca[mask, 1],
                    mode='markers',
                    name=f'Cluster {label}',
                    marker=dict(
                        size=6,
                        color=cores[label_idx % len(cores)],
                        line=dict(width=0.5, color='white')
                    ),
                    showlegend=(idx == 0)
                ),
                row=row,
                col=col
            )

    fig.update_layout(
        title_text='Comparação de Algoritmos de Clustering',
        template='plotly_white',
        height=800
    )

    return fig
