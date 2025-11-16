# 📊 GEI - Gestão Estratégica de Informações v3.0

> Dashboard de Monitoramento Fiscal para Receita Estadual de Santa Catarina

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![Machine Learning](https://img.shields.io/badge/ML-scikit--learn-orange)
![Status](https://img.shields.io/badge/Status-Ativo-success)

---

## 📑 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades Principais](#-funcionalidades-principais)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Como Usar](#-como-usar)
- [Análises Disponíveis](#-análises-disponíveis)
- [Score de Risco](#-score-de-risco)
- [Machine Learning](#-machine-learning)
- [Arquitetura de Dados](#-arquitetura-de-dados)
- [Segurança](#-segurança)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)

---

## 🎯 Sobre o Projeto

O **GEI (Gestão Estratégica de Informações)** é um sistema avançado de inteligência fiscal desenvolvido para a **Receita Estadual de Santa Catarina**. Seu propósito é **identificar automaticamente grupos econômicos** (conjuntos de múltiplas empresas relacionadas) e analisar **9 dimensões de risco fiscal**.

### Objetivos Principais

- 🔍 **Identificação de Grupos Econômicos**: Detectar empresas relacionadas através de múltiplos critérios
- 📊 **Análise Multidimensional**: Avaliar 9 dimensões de risco fiscal
- 🤖 **Machine Learning**: Clustering e detecção de anomalias com 3 algoritmos
- 📈 **Visualização Interativa**: Dashboard com gráficos dinâmicos e KPIs
- 📄 **Geração de Relatórios**: Dossiês completos em PDF

### Problemas que Resolve

- ✅ Confusão patrimonial (mistura de bens empresa/sócios)
- ✅ Planejamento tributário abusivo
- ✅ Anomalias operacionais (contas compartilhadas, padrões coordenados)
- ✅ Inconsistências fiscais
- ✅ Sonegação através de grupos econômicos

---

## 🚀 Funcionalidades Principais

### 1. Dashboard Executivo
- 📊 KPIs em tempo real (total grupos, receita, risco)
- 📈 Gráficos de distribuição e tendências
- 🏆 Ranking Top 30 grupos de maior risco

### 2. Machine Learning
- **K-Means**: Clustering em 2-5 grupos por perfil de risco
- **DBSCAN**: Detecção de outliers com parâmetros ajustáveis
- **Isolation Forest**: Identificação de anomalias (30% contaminação)
- **Modo Consenso**: Executa os 3 algoritmos e compara resultados
- **PCA**: Redução de dimensionalidade (2-10 componentes)

### 3. Análise Pontual de CNPJs
- 🔎 Busca por CNPJ ou número de grupo
- 📊 Análise de similaridade em 7 dimensões
- 📄 Geração automática de PDF detalhado

### 4. 10 Menus Temáticos de Análise

| Menu | Descrição |
|------|-----------|
| **Contadores** | Análise de contadores associados a grupos de risco |
| **Meios de Pagamento** | Detecção de confusão patrimonial |
| **Funcionários** | Análise RAIS/CAGED |
| **Convênio 115** | Risco de grupo econômico |
| **Contas Bancárias** | Contas compartilhadas (CCS) |
| **Análise Financeira** | Distribuição receita, evolução PGDAS |
| **Inconsistências NFe** | Valores duplicados e irregularidades |
| **Indícios Fiscais** | Catalogação de 10 tipos de indícios |
| **Vínculos Societários** | Sócios compartilhados |
| **Dossiê Completo** | Relatório PDF abrangente |

---

## 🛠️ Tecnologias Utilizadas

### Backend & Processamento
```
Python 3.x          # Linguagem principal
Streamlit           # Framework de dashboard
Pandas              # Manipulação de dados
NumPy               # Computação numérica
PySpark             # Processamento distribuído
```

### Machine Learning
```
scikit-learn        # Algoritmos de ML
├─ KMeans           # Clustering
├─ DBSCAN           # Detecção de outliers
├─ IsolationForest  # Detecção de anomalias
├─ PCA              # Redução de dimensionalidade
└─ Métricas         # Silhouette, Davies-Bouldin, Calinski-Harabasz
```

### Visualização & Relatórios
```
Plotly              # Gráficos interativos
├─ Express          # Gráficos rápidos
├─ Graph Objects    # Gráficos customizados
└─ Subplots         # Múltiplos gráficos

ReportLab           # Geração de PDFs
OpenPyXL            # Exportação Excel
```

### Banco de Dados
```
Impala              # Data warehouse
SQLAlchemy          # ORM
LDAP                # Autenticação
SSL/TLS             # Segurança
```

### Outras Bibliotecas
```
SciPy               # Estatística avançada
Hashlib             # Criptografia
```

---

## 📋 Requisitos

### Infraestrutura Obrigatória

- **Impala Server**: `bdaworkernode02.sef.sc.gov.br:21050`
- **Database**: `gessimples`
- **Autenticação**: LDAP com SSL/TLS

### Tabelas de Banco de Dados (17+)

```sql
gei_percent
gei_cnpj
gei_cadastro
gei_contador
gei_socios_compartilhados
gei_c115_ranking_risco_grupo_economico
gei_funcionarios_metricas_grupo
gei_pagamentos_metricas_grupo
gei_c115_metricas_grupos
gei_ccs_metricas_grupo
gei_ccs_ranking_risco
gei_indicios
gei_nfe_completo
gei_ccs_cpf_compartilhado
gei_ccs_sobreposicao_responsaveis
gei_ccs_padroes_coordenados
```

### Dependências Python

```bash
streamlit
pandas
numpy
plotly
scipy
scikit-learn
sqlalchemy
openpyxl
reportlab
pyspark
```

---

## 💻 Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/GEI.git
cd GEI
```

### 2. Crie Ambiente Virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instale Dependências

```bash
pip install -r requirements.txt
```

### 4. Configure Credenciais

Crie o arquivo `.streamlit/secrets.toml`:

```toml
[ldap]
username = "seu_usuario"
password = "sua_senha"
```

### 5. Execute o Sistema

```bash
streamlit run GEI.py
```

O sistema estará disponível em: `http://localhost:8501`

---

## 📁 Estrutura do Projeto

```
GEI/
│
├── GEI.py                          # Aplicação principal Streamlit
├── GEI.json                        # Configurações/dados
│
├── 📓 Notebooks
│   ├── GEI Cálculo (1).ipynb       # Consolidação e cálculo de métricas
│   ├── GEI Cálculo-Exemplo (2).ipynb
│   ├── GEIC.ipynb                  # Análise consolidada abrangente (16+ análises)
│   ├── GEIG.ipynb                  # Análise global agregada
│   └── GEIC-exemplo (5).ipynb
│
├── .streamlit/
│   └── secrets.toml                # Credenciais (NÃO versionar)
│
└── README.md                       # Este arquivo
```

---

## 🎮 Como Usar

### 1. Acesso ao Sistema

1. Execute `streamlit run GEI.py`
2. Digite a senha de acesso: `tsevero654` (padrão)
3. Aguarde carregamento dos dados

### 2. Navegação

Use a **barra lateral** para acessar:

- 🏠 **Dashboard Executivo**: Visão geral e KPIs
- 🔍 **Análise Pontual**: Busca por CNPJ
- 🤖 **Machine Learning**: Clustering e anomalias
- 📊 **Análises Temáticas**: 10 menus especializados

### 3. Análise de um Grupo

1. Vá em **"Análise Pontual de CNPJs"**
2. Digite o CNPJ ou número do grupo
3. Clique em **"Gerar Análise"**
4. Visualize os resultados e baixe o PDF

### 4. Clustering

1. Acesse **"Análise de Machine Learning"**
2. Escolha o algoritmo (K-Means, DBSCAN, Isolation Forest ou Consenso)
3. Configure parâmetros
4. Execute análise
5. Visualize resultados e métricas

---

## 📊 Análises Disponíveis

### Análises Fiscais

| Tipo | Descrição | Indicadores |
|------|-----------|-------------|
| **Indícios Fiscais** | 10 tipos de indícios | Cliente, email, telefone, endereço, IP, etc. |
| **Inconsistências NFe** | Valores duplicados | NFe com valores idênticos |
| **Confusão Patrimonial** | Pagamentos a sócios | Empresa pagando despesas pessoais |
| **Planejamento Tributário** | Estruturas abusivas | Fraudes no Simples Nacional |

### Análises de Clustering

| Algoritmo | Uso | Parâmetros |
|-----------|-----|------------|
| **K-Means** | Agrupamento em clusters | 2-5 clusters |
| **DBSCAN** | Detecção de outliers | eps, min_samples |
| **Isolation Forest** | Detecção de anomalias | contamination=0.3 |
| **Consenso** | Validação cruzada | Comparação dos 3 algoritmos |

### Análises de Anomalias

- **CCS**: Contas bancárias compartilhadas
- **Sobreposições**: Responsáveis em períodos coincidentes
- **Padrões Coordenados**: Aberturas/encerramentos no mesmo dia
- **Receita/Funcionários**: Desproporções extremas

### Análises de Risco

- **Score Customizado**: 9 dimensões (0-100%)
- **Nível C115**: CRÍTICO/ALTO/MÉDIO/BAIXO
- **Índice Risco CCS**: Contas compartilhadas
- **Ranking de Risco**: Top 30 grupos

---

## 🎯 Score de Risco

O sistema calcula um **score customizado de 0 a 100%** baseado em **9 dimensões**:

| Dimensão | Peso | Indicadores |
|----------|------|-------------|
| **1. Cadastro** | 10 pts | Razão social, fantasia, CNAE, contador, endereço |
| **2. Sócios** | 8 pts | Compartilhamento, interconexão |
| **3. Financeiro** | 7 pts | Limite SN, receita |
| **4. Convênio 115** | 5 pts | Índice, nível risco |
| **5. Indícios** | 5 pts | Quantidade, tipos |
| **6. CCS** | 5 pts | Contas, sobreposições |
| **7. NFe** | 5 pts | Inconsistências |
| **8. Pagamentos** | 3 pts | A sócios |
| **9. Funcionários** | 2 pts | Receita/funcionário |
| **TOTAL** | **50 pts** | **Percentual 0-100%** |

### Classificação de Risco

```
🔴 CRÍTICO:   Score > 80%
🟠 ALTO:      Score 60-80%
🟡 MÉDIO:     Score 40-60%
🟢 BAIXO:     Score < 40%
```

---

## 🤖 Machine Learning

### Algoritmos Disponíveis

#### 1. K-Means
```python
# Clustering em 2-5 grupos
# Útil para: Segmentação de perfis de risco
# Métricas: Silhouette Score, Inércia
```

#### 2. DBSCAN
```python
# Detecção de outliers baseada em densidade
# Útil para: Identificar grupos anômalos
# Parâmetros ajustáveis: eps, min_samples
```

#### 3. Isolation Forest
```python
# Detecção de anomalias
# Útil para: Identificar comportamentos atípicos
# Contamination: 30%
```

#### 4. Modo Consenso
```python
# Executa os 3 algoritmos simultaneamente
# Útil para: Validação cruzada de resultados
# Compara: Consistência entre algoritmos
```

### Métricas de Avaliação

| Métrica | Descrição | Melhor Valor |
|---------|-----------|--------------|
| **Silhouette Score** | Coesão e separação de clusters | Próximo a 1 |
| **Davies-Bouldin** | Similaridade intra/inter cluster | Próximo a 0 |
| **Calinski-Harabasz** | Razão de variância | Maior valor |

### PCA (Redução de Dimensionalidade)

- **Componentes**: 2-10
- **Uso**: Visualização e otimização
- **Variância**: Mantém 95%+ da informação

---

## 🏗️ Arquitetura de Dados

### Fluxo de Dados

```
┌─────────────────────────────────────┐
│  Impala Database                     │
│  bdaworkernode02:21050               │
│  Database: gessimples                │
└──────────────┬──────────────────────┘
               │
               ▼ (PySpark + SQL)
┌─────────────────────────────────────┐
│  Notebooks de Processamento          │
│  ├─ GEI Cálculo: Métricas            │
│  ├─ GEIC: Análise Consolidada        │
│  └─ GEIG: Análise Global             │
└──────────────┬──────────────────────┘
               │
               ▼ (Consolidação)
┌─────────────────────────────────────┐
│  Tabelas gei_* (consolidadas)        │
│  17+ tabelas especializadas          │
└──────────────┬──────────────────────┘
               │
               ▼ (Cache TTL 1h/5min)
┌─────────────────────────────────────┐
│  GEI.py Dashboard                    │
│  ├─ Análises em tempo real           │
│  ├─ Visualizações Plotly             │
│  ├─ Relatórios PDF                   │
│  └─ Interface: 11+ páginas           │
└─────────────────────────────────────┘
```

### Cache e Performance

- **Dados Gerais**: TTL 3600s (1 hora)
- **Dossiês**: TTL 300s (5 minutos)
- **Query Optimization**: LIMIT em queries (50k-10k registros)
- **Renderização**: Plotly interativo, DataFrames pagináveis

---

## 🔒 Segurança

### Autenticação

- 🔐 **Sistema de Login**: Senha obrigatória
- 🔑 **LDAP**: Integração com Active Directory
- 🔒 **SSL/TLS**: Conexões criptografadas
- 📝 **Session State**: Gerenciamento de sessão

### Proteção de Dados

- ⚠️ **Secrets**: Credenciais em `secrets.toml` (não versionado)
- 🔒 **Criptografia**: Hashlib para senhas
- 🛡️ **SSL Context**: Verificação desabilitada para ambiente interno

### Boas Práticas

1. **NUNCA** versione o arquivo `secrets.toml`
2. Altere a senha padrão (`tsevero654`)
3. Use HTTPS em produção
4. Restrinja acesso ao servidor Impala
5. Mantenha logs de acesso

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. **Fork** o projeto
2. Crie uma **branch** para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. **Commit** suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. **Push** para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um **Pull Request**

### Padrões de Código

- Use **PEP 8** para Python
- Documente funções complexas
- Adicione testes quando possível
- Mantenha compatibilidade com Python 3.x

---

## 📄 Licença

Este projeto é de propriedade da **Receita Estadual de Santa Catarina** e é destinado exclusivamente para uso interno.

⚠️ **CONFIDENCIAL**: Este sistema contém dados fiscais sensíveis. Uso não autorizado é proibido.

---

## 📞 Suporte

Para questões técnicas ou suporte:

- 📧 **Email**: suporte@sef.sc.gov.br
- 🌐 **Portal**: https://www.sef.sc.gov.br
- 📱 **Telefone**: (48) XXXX-XXXX

---

## 📚 Documentação Adicional

- **Análise Técnica Detalhada**: `README_ANALISE_PROJETO.md`
- **Visão Geral**: `VISAO_GERAL.txt`
- **Notebooks**: Ver arquivos `.ipynb` para exemplos práticos

---

## 🏆 Créditos

Desenvolvido pela equipe de **Inteligência Fiscal** da Receita Estadual de Santa Catarina.

**Versão**: 3.0
**Última Atualização**: Novembro 2024

---

<div align="center">

**🚀 GEI - Inteligência Fiscal de Ponta 🚀**

*Combatendo sonegação através de tecnologia e dados*

</div>
