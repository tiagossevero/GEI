# EXPLORAÇÃO DETALHADA - PROJETO GEI

## Sumário Executivo

O **GEI (Gestão Estratégica de Informações)** v3.0 é um sistema inteligente de **Monitoramento Fiscal** desenvolvido para a **Receita Estadual de Santa Catarina**. Sua principal função é identificar automaticamente grupos econômicos (conjuntos de empresas relacionadas) e analisar múltiplas dimensões de risco fiscal, utilizando técnicas avançadas de Big Data, Machine Learning e análise estatística.

---

## 1. PROPÓSITO PRINCIPAL

**Objetivo Central:** Identificar padrões clandestinos de grupos econômicos e analisar indicadores de:
- Confusão patrimonial (mistura de bens empresa/sócios)
- Planejamento tributário abusivo
- Anomalias operacionais (contas compartilhadas, padrões coordenados)
- Risco fiscal multidimensional

**Usuários-Alvo:** Auditores e servidores da Receita Estadual SC

---

## 2. ESTRUTURA DO PROJETO

```
/home/user/GEI/
├── GEI.py                                    # Dashboard Streamlit (318 KB, 6900+ linhas)
├── GEI Cálculo (1).ipynb                     # Notebook de cálculo de métricas
├── GEI Cálculo-Exemplo (2).ipynb             # Exemplo simplificado
├── GEIC.ipynb                                # Análise consolidada abrangente (2.1 MB)
├── GEIC-exemplo (5).ipynb                    # Exemplo GEIC
├── GEIG.ipynb                                # Análise global do sistema (412 KB)
└── GEI.json                                  # Dados de configuração (566 KB)
```

---

## 3. COMPONENTES PRINCIPAIS

### 3.1 GEI.py - Dashboard Interativo Streamlit

**Tamanho:** 318 KB (6900+ linhas de código)

**Funcionalidades Principais:**

#### Análises de Machine Learning (534-1400 linhas)
```python
analise_machine_learning()
```
- **K-Means:** Clustering em 2-5 clusters
- **DBSCAN:** Detecção de outliers (eps, min_samples customizáveis)
- **Isolation Forest:** Detecção de anomalias (30% contaminação)
- **Modo Consenso:** Executa 3 algoritmos e compara resultados
- **PCA:** Redução de dimensionalidade (2-10 componentes)
- **Métricas:** Silhouette Score, Davies-Bouldin Score, Calinski-Harabasz Score

#### Dashboard Executivo (4655-4720 linhas)
```python
dashboard_executivo()
```
- KPIs principais (total grupos, receita, risco)
- Gráficos de distribuição
- Top grupos por risco

#### Análise Pontual de CNPJs (2726-4650 linhas)
```python
analise_pontual()
```
- Busca por CNPJ/grupo
- Análise de similaridade (7 dimensões)
- Relatório PDF automatizado

#### 10 Menus Temáticos
| Menu | Funções | Linhas |
|------|---------|--------|
| **Contadores** | Análise de contadores, grupos de risco | 5124-5225 |
| **Pagamentos** | Meios de pagamento, confusão patrimonial | 5226-5289 |
| **Funcionários** | RAIS/CAGED, receita/funcionário | 5290-5371 |
| **C115** | Risco grupo econômico, convênio 115 | 5372-5444 |
| **CCS** | Contas compartilhadas, sobreposições | 5445-5620 |
| **Financeiro** | Distribuição receita, evolução PGDAS | 5621-5744 |
| **NFe** | Inconsistências documentos | 5745-5971 |
| **Indícios** | Catalogação de indícios fiscais | 5972-6000 |
| **Vínculos** | Sócios compartilhados | 6001-6048 |
| **Dossiê** | Relatório PDF completo | 6049-6637 |

---

### 3.2 Notebooks - Processamento Big Data (PySpark)

#### **GEI Cálculo (1).ipynb** (82 KB)
**Propósito:** Consolidação de métricas

Principais Processamentos:
1. Carregamento de CNPJs (API)
2. Criação de view NFe otimizada
3. Integração CFOP (Classificação Operação Fiscal)
4. **Cálculo de ICMS** - por entrada/saída, emitente/destinatário
5. Processamento CTe (Conhecimento Transporte)
6. Carregamento PGDAS-D
7. Consolidação de notificações
8. Visualizações e análises
9. Exportação em padrão ouro

**Tecnologia:** PySpark + Spark SQL

---

#### **GEIC.ipynb** (2.1 MB)
**Propósito:** Análise consolidada abrangente

**16+ Análises Estruturadas:**
1. Panorama geral (total grupos, CNPJs)
2. Ranking Top 30 grupos de risco
3. Contadores associados a grupos
4. Inconsistências operacionais
5. Confusão patrimonial (pagamentos)
6. Evolução temporal de receitas
7. Análise setorial por CNAE
8. Indícios fiscais por tipo
9. Estrutura societária e interconexões
10. Convênio 115 - risco grupo
11. Faturamento vs funcionários (fantasma)
12. Análise comparativa multi-dimensional
13. Dossiê de grupo específico
14. Dashboard executivo consolidado
15. Análise de rede societária
16. Sumário executivo final

---

#### **GEIG.ipynb** (412 KB)
**Propósito:** Análise global agregada

Focos:
- Carregamento e análise preliminar
- Visão geral e distribuição de risco
- Fatores principais de risco
- Análise setorial por CNAE

---

## 4. TECNOLOGIAS E DEPENDÊNCIAS

### Stack Tecnológico

| Categoria | Tecnologias |
|-----------|-----------|
| **Framework** | Streamlit, PySpark |
| **Dados** | Pandas, NumPy, SQLAlchemy |
| **ML** | scikit-learn (KMeans, DBSCAN, IsolationForest, PCA) |
| **Estatística** | SciPy |
| **Visualização** | Plotly (Express, Graph Objects, Subplots) |
| **Relatórios** | ReportLab |
| **BD** | Impala, SQL |
| **Segurança** | LDAP, SSL/TLS, Hashlib |
| **Outros** | OpenPyXL (Excel) |

### Dependências Críticas

#### Infraestrutura
```
Impala Database Server
  Host: bdaworkernode02.sef.sc.gov.br
  Port: 21050
  Database: gessimples
  Auth: LDAP + SSL/TLS
```

#### Configuração
```
.streamlit/secrets.toml
  [impala_credentials]
  user = "usuario_ldap"
  password = "senha_ldap"
```

#### Tabelas Esperadas (17+ tabelas)
- `gei_percent`: Dados principais consolidados
- `gei_cnpj`: Associação CNPJ-grupo
- `gei_cadastro`: Dados cadastrais
- `gei_contador`: Contadores
- `gei_socios_compartilhados`: Sócios em múltiplas empresas
- `gei_c115_ranking_risco_grupo_economico`: Convênio 115
- `gei_funcionarios_metricas_grupo`: Funcionários
- `gei_pagamentos_metricas_grupo`: Pagamentos
- `gei_c115_metricas_grupos`: Métricas C115
- `gei_ccs_metricas_grupo`: Métricas CCS
- `gei_ccs_ranking_risco`: Ranking CCS
- `gei_indicios`: Indícios fiscais
- `gei_nfe_completo`: NFe detalhadas
- `gei_ccs_cpf_compartilhado`: Contas compartilhadas
- `gei_ccs_sobreposicao_responsaveis`: Sobreposições
- `gei_ccs_padroes_coordenados`: Padrões coordenados
- `usr_sat_ods.vw_ods_contrib`: View de contribuintes

---

## 5. ANÁLISES REALIZADAS

### 5.1 Machine Learning - Clustering
**Algoritmos:** K-Means, DBSCAN, Isolation Forest

**Entrada:** 10.000+ grupos com 21 features
```
Features ML:
- qtd_cnpjs
- razao_social_identica, fantasia_identica, cnae_identico, contador_identico, endereco_identico
- socios_compartilhados, indice_interconexao, perc_cnpjs_com_socios
- receita_maxima, acima_limite_sn
- indice_risco_c115, nivel_risco_c115_num
- total_indicios, indice_risco_indicios
- contas_compartilhadas, indice_risco_ccs, nivel_risco_ccs_num
- score_inconsistencias_nfe
- indice_risco_pagamentos, indice_risco_fat_func
```

**Saída:** Classificação em clusters + score de consenso

### 5.2 Análises Fiscais
- Indícios Fiscais (10 tipos: cliente, email, telefone, endereço, IP, etc.)
- Inconsistências NFe (valores duplicados)
- Confusão Patrimonial (pagamentos empresa vs. sócios)
- Limite Simples Nacional (receita > R$ 4.8M)

### 5.3 Análises de Anomalias
- **CCS:** Contas bancárias com múltiplos CNPJs
- **Sobreposições:** Responsáveis em períodos coincidentes
- **Padrões:** Aberturas/encerramentos coordenados
- **Receita/Func:** Desproporções extremas

### 5.4 Análises de Risco
**Score ML (Customizado - 9 dimensões):**
- Cadastro (10 pts): Identidades compartilhadas
- Sócios (8 pts): Compartilhamento
- Financeiro (7 pts): Limite, receita
- C115 (5 pts): Risco grupo
- Indícios (5 pts): Quantidade/tipos
- CCS (5 pts): Contas compartilhadas
- NFe (5 pts): Inconsistências
- Pagamentos (3 pts): A sócios
- Funcionários (2 pts): Receita/funcionário

### 5.5 Análises Temáticas
- Análise de Contadores
- Meios de Pagamento
- RAIS/CAGED
- Convênio 115
- Procuração Bancária
- Financeira
- Setorial (CNAE)

---

## 6. PRINCIPAIS FUNÇÕES DO GEI.py

### Conexão e Carregamento
```python
get_impala_engine()                 # Conexão ao banco Impala
carregar_todos_os_dados()           # Carrega 10 tabelas (cache 1h)
executar_query_analise()            # Query customizadas
carregar_dossie_completo()          # 10+ tabelas de um grupo (cache 5min)
```

### Análises
```python
analise_machine_learning()          # ML com consenso de 3 algoritmos
analise_pontual()                   # CNPJ específico
dashboard_executivo()               # Dashboard principal
mostrar_detalhes_grupo()            # Detalhes de grupo
```

### Menus (10 análises temáticas)
```python
menu_contadores()                   # Análise contadores
menu_pagamentos()                   # Meios pagamento
menu_funcionarios()                 # RAIS/CAGED
menu_c115()                         # Convênio 115
menu_ccs()                          # Contas bancárias
menu_financeiro()                   # Análise financeira
inconsistencias_nfe()               # NFe
indicios_fiscais()                  # Indícios
vinculos_societarios()              # Sócios
dossie_grupo()                      # Dossiê PDF
menu_analises()                     # Análises avançadas
```

### Utilitários
```python
aplicar_filtros()                   # Filtros dinâmicos
formatar_moeda()                    # Formatação valores
criar_filtros_sidebar()             # Interface filtros
gerar_pdf_analise_pontual()         # PDF CNPJs
gerar_pdf_dossie()                  # PDF dossiê
ranking_grupos()                    # Ranking
```

---

## 7. FLUXO DE DADOS

```
┌─────────────────────────────────────┐
│ Impala BD (bdaworkernode02:21050)   │
│ Database: gessimples                │
│ Auth: LDAP + SSL/TLS                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Notebooks (Cálculo, GEIC, GEIG)     │
│ - PySpark processing                │
│ - SQL queries                       │
│ - Consolidação métricas             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Tabelas Consolidadas (gei_*)        │
│ - gei_percent (principal)           │
│ - gei_cnpj, gei_contador, etc.      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ GEI.py - Streamlit Dashboard        │
│ - Cache (TTL 1h/5min)               │
│ - Análises em tempo real            │
│ - Visualizações Plotly              │
│ - Relatórios PDF (ReportLab)        │
│ - Interface: 11 páginas + ML        │
└─────────────────────────────────────┘
```

---

## 8. MÉTRICAS E SCORES

### Score ML Customizado (Percentual 0-100%)
Ponderação: 9 dimensões totalizando 50 pontos máximos

| Dimensão | Pontos | Indicadores |
|----------|--------|-------------|
| Cadastro | 10 | Razão social, fantasia, CNAE, contador, endereço |
| Sócios | 8 | Compartilhamento, interconexão |
| Financeiro | 7 | Limite SN, receita |
| C115 | 5 | Índice, nível risco |
| Indícios | 5 | Quantidade, tipos |
| CCS | 5 | Contas, sobreposições |
| NFe | 5 | Inconsistências |
| Pagamentos | 3 | A sócios |
| Funcionários | 2 | Receita/funcionário |

### Outros Scores
- **Score Final CCS:** Risco específico contas bancárias
- **Score Final Avançado:** Consolidação múltiplas dimensões
- **Índice Risco Indicios:** Normalizado (0-1)

### Níveis de Risco (C115)
- CRÍTICO (3)
- ALTO (2)
- MÉDIO (1)
- BAIXO (0)

---

## 9. SEGURANÇA E AUTENTICAÇÃO

1. **Senha do Dashboard:** `tsevero654` (hardcoded)
2. **Credenciais Impala:** LDAP + senha
3. **SSL/TLS:** Comunicação com banco
4. **Session State:** Streamlit para manter autenticação

---

## 10. PERFORMANCE E OTIMIZAÇÕES

### Caching
- Dados principais: TTL 3600s (1 hora)
- Dossiês: TTL 300s (5 minutos)
- Decoradores: `@st.cache_resource`, `@st.cache_data`

### Query Optimization
- LIMIT em queries (50k-10k registros)
- Índices esperados em BD
- PySpark para big data

### Renderização
- Gráficos Plotly (interativos)
- DataFrames pagináveis
- Expanders para detalhes

---

## 11. CASOS DE USO

### Auditor Fiscal
1. Acessa Dashboard Executivo
2. Analisa Top 30 grupos de risco
3. Clica em grupo de interesse
4. Visualiza Dossiê completo
5. Exporta PDF para investigação

### Gerente de Receita
1. Monitora KPIs principais
2. Analisa distribuição de risco
3. Consulta ranking por CNAE
4. Acompanha tendências temporais

### Data Analyst
1. Executa análise pontual
2. Investiga padrões específicos
3. Realiza análise de ML
4. Compara consenso de algoritmos

---

## 12. LIMITAÇÕES E CONSIDERAÇÕES

1. **Dependência de BD Impala:** Sistema offline sem acesso
2. **Credenciais Hardcoded:** Senha no código (risco segurança)
3. **PySpark Obrigatório:** Notebooks precisam Spark cluster
4. **Tabelas Esperadas:** Falha se tabelas não existirem
5. **LDAP Corporativo:** Requer usuário corporativo

---

## CONCLUSÃO

O **GEI** é um sistema sofisticado de inteligência fiscal que combina:
- **Big Data:** PySpark para processar millions de registros
- **ML:** 3 algoritmos com consenso automático
- **Análise Estatística:** Múltiplas dimensões de risco
- **Visualização:** Dashboards interativos com Plotly
- **Relatórios:** PDFs profissionais e exportações

Propósito central: **Identificar grupos econômicos clandestinos e analisar risco fiscal multidimensional** para Receita Estadual SC.

---

**Arquivo gerado:** 2025-11-16  
**Versão Analisada:** GEI v3.0  
**Tecnologias:** Streamlit, PySpark, scikit-learn, Plotly, Impala
