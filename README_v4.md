# Sistema GEI v4.0 - Gestão Estratégica de Informações

## 📋 Descrição

Sistema de **Dashboard de Monitoramento Fiscal** desenvolvido para a **Receita Estadual de Santa Catarina** para identificação e análise de grupos econômicos com potencial risco fiscal.

**Versão:** 4.0.0 (Refatorada e Otimizada)
**Data:** 2025

---

## 🎯 Funcionalidades Principais

### 1. 📊 Dashboard Executivo
- **KPIs em tempo real:** Total de grupos, grupos críticos, score médio, total de CNPJs
- **Visualizações interativas:** Histogramas, gráficos de pizza, barras
- **Análises top N:** Top grupos por receita e quantidade de CNPJs
- **Insights automáticos:** Geração automática de insights do sistema
- **Exportação:** Excel e CSV

### 2. 🎯 Análise Pontual
- **Busca por CNPJ ou número de grupo**
- **Medidor de risco (Gauge)**
- **Detalhes multidimensionais de risco**
- **Insights automáticos do grupo**
- **Lista de CNPJs do grupo**
- **Exportação de dossiê em PDF e Excel**

### 3. 📈 Ranking de Grupos
- **Top N grupos ordenados por risco** (configurável: 10-100)
- **Tabela interativa com múltiplas métricas**
- **Visualização em gráfico de barras**
- **Exportação em Excel e CSV**

### 4. 🤖 Machine Learning
- **Algoritmos implementados:**
  - K-Means Clustering
  - DBSCAN (Density-based)
  - Clustering Hierárquico
  - Isolation Forest (detecção de anomalias)
  - Local Outlier Factor
- **PCA para redução de dimensionalidade**
- **Análise de consenso** (múltiplos algoritmos simultaneamente)
- **Métricas de qualidade:** Silhouette, Davies-Bouldin, Calinski-Harabasz
- **Visualizações 2D e 3D interativas**
- **Otimização de hiperparâmetros**

### 5. 🔗 Análise de Redes Societárias
- **Visualização de grafo de relacionamentos**
- **Identificação de sócios compartilhados**
- **Análise de interconexões**
- **Tabela detalhada de vínculos**

### 6. 📐 Análise Multidimensional
- **Matriz de correlação entre métricas**
- **Scatter matrix para exploração visual**
- **Análise de múltiplas variáveis simultaneamente**
- **Heatmaps interativos**

### 7. 💡 Insights Automáticos
- **Insights gerais do sistema**
- **Top 10 grupos prioritários para investigação**
- **Análise automática baseada em regras de negócio:**
  - Detecção de pulverização de receita
  - Identificação de confusão patrimonial
  - Anomalias cadastrais
  - Risco elevado em Convênio 115
  - Contas bancárias compartilhadas
  - Múltiplos indícios fiscais

### 8. 📋 Dossiê Completo
- **Geração de relatório PDF completo**
- **Inclui:**
  - Resumo executivo
  - Lista de CNPJs
  - Análise de risco multidimensional
  - Sócios compartilhados
  - Indícios fiscais
  - Contas bancárias compartilhadas
  - Observações e recomendações

### 9. ⚙️ Configurações
- **Informações do sistema**
- **Gerenciamento de cache**
- **Documentação integrada**

---

## 🏗️ Arquitetura Refatorada

### Estrutura de Diretórios

```
GEI/
├── app.py                          # Aplicativo principal Streamlit
├── requirements.txt                # Dependências do projeto
├── README_v4.md                    # Documentação (este arquivo)
│
├── src/                            # Código-fonte modular
│   ├── __init__.py
│   │
│   ├── config/                     # Configurações
│   │   ├── __init__.py
│   │   ├── settings.py             # Constantes e configurações
│   │   └── database.py             # Conexão com banco de dados
│   │
│   ├── data/                       # Gerenciamento de dados
│   │   ├── __init__.py
│   │   └── loader.py               # Carregamento e cache
│   │
│   ├── components/                 # Componentes visuais
│   │   ├── __init__.py
│   │   ├── visual.py               # Componentes de visualização
│   │   └── insights.py             # Geração de insights
│   │
│   ├── ml/                         # Machine Learning
│   │   ├── __init__.py
│   │   └── clustering.py           # Algoritmos de clustering
│   │
│   ├── reports/                    # Exportação de relatórios
│   │   ├── __init__.py
│   │   └── export.py               # PDF, Excel, CSV
│   │
│   ├── utils/                      # Utilitários
│   │   ├── __init__.py
│   │   └── auth.py                 # Autenticação
│   │
│   └── pages/                      # (Reservado para expansão futura)
│
└── .streamlit/
    └── secrets.toml                # Credenciais (não versionado)
```

### Módulos Principais

#### 1. **src/config/** - Configurações
- **settings.py:** Todas as constantes, configurações de score, cores, paletas
- **database.py:** Gerenciamento de conexões com Impala, queries pré-definidas

#### 2. **src/data/** - Dados
- **loader.py:** Funções de carregamento com cache otimizado, filtros, agregações

#### 3. **src/components/** - Componentes
- **visual.py:** 25+ componentes visuais reutilizáveis:
  - KPIs, gráficos de barras, pizza, linha, dispersão
  - Heatmaps, correlações, scatter matrix
  - Visualizações 3D, gauges, gráficos de rede
- **insights.py:** Geração automática de insights, análises estatísticas avançadas

#### 4. **src/ml/** - Machine Learning
- **clustering.py:** Algoritmos de clustering, PCA, detecção de anomalias, otimização

#### 5. **src/reports/** - Relatórios
- **export.py:** Exportação em PDF, Excel, CSV com formatação profissional

#### 6. **src/utils/** - Utilitários
- **auth.py:** Sistema de autenticação

---

## 📊 Sistema de Score de Risco

### Dimensões (9 categorias, 50 pontos total)

| Dimensão | Pontos | Métricas |
|----------|--------|----------|
| **Cadastro** | 10 | Razão social, fantasia, CNAE, contador, endereço idênticos |
| **Sócios** | 8 | Sócios compartilhados, índice de interconexão |
| **Financeiro** | 7 | Receita máxima, acima do limite SN |
| **Convênio 115** | 5 | Índice e nível de risco C115 |
| **Indícios** | 5 | Quantidade e tipos de indícios fiscais |
| **CCS** | 5 | Contas compartilhadas, índice de risco |
| **NFe** | 5 | Inconsistências em notas fiscais |
| **Pagamentos** | 3 | Despesas a sócios, confusão patrimonial |
| **Funcionários** | 2 | Proporção receita/funcionário |

### Classificação de Risco

- **🔴 CRÍTICO** (80-100%): Investigação urgente
- **🟠 ALTO** (60-79.99%): Monitoramento próximo
- **🟡 MÉDIO** (40-59.99%): Análise recomendada
- **🟢 BAIXO** (0-39.99%): Operação normal

---

## 🤖 Machine Learning

### Algoritmos Disponíveis

#### Clustering
1. **K-Means**
   - Agrupamento baseado em centróides
   - Rápido e eficiente
   - Requer definição de K clusters

2. **DBSCAN**
   - Baseado em densidade
   - Identifica outliers automaticamente
   - Não requer número de clusters pré-definido

3. **Clustering Hierárquico**
   - Cria hierarquia de clusters
   - Flexível para diferentes linkages

#### Detecção de Anomalias
1. **Isolation Forest**
   - Detecta anomalias extremas
   - Baseado em árvores de decisão
   - Eficiente para grandes datasets

2. **Local Outlier Factor**
   - Baseado em densidade local
   - Identifica outliers contextuais

### Features Utilizadas (21 variáveis)
- Quantidade de CNPJs
- Similaridades cadastrais (5)
- Vínculos societários (3)
- Aspectos financeiros (2)
- Risco C115 (2)
- Indícios fiscais (2)
- Contas compartilhadas (3)
- Inconsistências NFe (1)
- Pagamentos e funcionários (2)

### Métricas de Avaliação
- **Silhouette Score:** Qualidade dos clusters (-1 a 1)
- **Davies-Bouldin Index:** Separação entre clusters (menor = melhor)
- **Calinski-Harabasz Score:** Densidade e separação (maior = melhor)

---

## 📥 Exportação de Dados

### Formatos Suportados

#### 1. **Excel (.xlsx)**
- Múltiplas abas
- Formatação profissional:
  - Cabeçalhos coloridos
  - Largura automática de colunas
  - Primeira linha congelada
  - Cores da identidade visual

#### 2. **CSV (.csv)**
- Separador: ponto e vírgula (;)
- Encoding: UTF-8 com BOM
- Compatível com Excel Brasil

#### 3. **PDF (.pdf)**
- Dossiê completo formatado
- Logo e identidade visual
- Seções organizadas:
  - Resumo executivo
  - CNPJs do grupo
  - Análise de risco
  - Sócios compartilhados
  - Indícios fiscais
  - Contas compartilhadas
  - Recomendações

---

## 🔧 Tecnologias Utilizadas

### Backend
- **Python 3.9+**
- **Streamlit 1.28+:** Framework web interativo
- **SQLAlchemy 2.0+:** ORM e gerenciamento de conexões
- **Impyla 0.18+:** Driver para Impala

### Processamento de Dados
- **Pandas 2.0+:** Manipulação de dados
- **NumPy 1.24+:** Computação numérica

### Machine Learning
- **scikit-learn 1.3+:** Algoritmos de ML
- **SciPy 1.11+:** Estatística avançada

### Visualização
- **Plotly 5.17+:** Gráficos interativos de alta qualidade

### Exportação
- **ReportLab 4.0+:** Geração de PDF
- **openpyxl 3.1+:** Manipulação de Excel

---

## 🚀 Como Executar

### 1. Pré-requisitos
```bash
# Python 3.9 ou superior
python --version
```

### 2. Clonar Repositório
```bash
git clone <repositorio>
cd GEI
```

### 3. Criar Ambiente Virtual
```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 4. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 5. Configurar Credenciais

Criar arquivo `.streamlit/secrets.toml`:

```toml
[impala_credentials]
user = "seu_usuario_ldap"
password = "sua_senha_ldap"
```

### 6. Executar Aplicação
```bash
streamlit run app.py
```

O dashboard estará disponível em: **http://localhost:8501**

---

## ⚙️ Configurações

### Arquivo: `src/config/settings.py`

#### Alterar Senha do Dashboard
```python
SENHA_DASHBOARD = "nova_senha_aqui"
```

#### Configurar Tempos de Cache
```python
CACHE_TTL_DADOS_PRINCIPAIS = 3600  # 1 hora
CACHE_TTL_DOSSIE = 300             # 5 minutos
```

#### Ajustar Limites de Queries
```python
LIMIT_CNPJ = 50000
LIMIT_SOCIOS = 30000
```

---

## 📊 Banco de Dados

### Conexão
- **Host:** bdaworkernode02.sef.sc.gov.br
- **Porta:** 21050
- **Database:** gessimples
- **Autenticação:** LDAP + SSL/TLS

### Tabelas Principais (17+)

| Tabela | Descrição |
|--------|-----------|
| `gei_percent` | Dados principais consolidados |
| `gei_cnpj` | Relação CNPJ-Grupo (50k limite) |
| `gei_cadastro` | Dados cadastrais |
| `gei_contador` | Informações de contadores |
| `gei_socios_compartilhados` | Sócios em múltiplas empresas |
| `gei_c115_ranking_risco_grupo_economico` | Ranking Convênio 115 |
| `gei_funcionarios_metricas_grupo` | Métricas RAIS/CAGED |
| `gei_pagamentos_metricas_grupo` | Métricas de pagamentos |
| `gei_ccs_metricas_grupo` | Métricas de contas compartilhadas |
| `gei_ccs_cpf_compartilhado` | CPFs em contas compartilhadas |
| `gei_indicios` | Indícios fiscais |
| `gei_nfe_completo` | Notas fiscais com inconsistências |

---

## 🎨 Personalização Visual

### Cores do Sistema
- **Primária:** `#1f77b4` (Azul)
- **Secundária:** `#ff7f0e` (Laranja)
- **Sucesso:** `#2ca02c` (Verde)
- **Perigo:** `#d62728` (Vermelho)
- **Aviso:** `#ff9800` (Laranja Escuro)

### Paletas para Gráficos
- **Risco:** Verde → Amarelo → Laranja → Vermelho
- **Categórica:** 10 cores distintas
- **Sequencial:** Azul claro → Azul escuro

---

## 📈 Melhorias da Versão 4.0

### Arquitetura
✅ **Código 100% modular e reutilizável**
✅ **Separação de responsabilidades**
✅ **Imports organizados por pacotes**

### Performance
✅ **Sistema de cache otimizado** (múltiplos TTLs)
✅ **Queries otimizadas** com limites configuráveis
✅ **Carregamento paralelo** de dados

### Funcionalidades
✅ **25+ componentes visuais** reutilizáveis
✅ **5 algoritmos de ML** (vs 3 na v3.0)
✅ **Insights automáticos** com 10+ tipos de análises
✅ **Análise multidimensional** com correlações
✅ **Visualizações 3D** interativas
✅ **Exportação profissional** em 3 formatos

### UX/UI
✅ **9 páginas** especializadas
✅ **Filtros globais** na sidebar
✅ **Navegação intuitiva** por radio buttons
✅ **Design consistente** com identidade visual
✅ **Gráficos interativos** com Plotly

### Documentação
✅ **Docstrings** em todas as funções
✅ **Type hints** em parâmetros
✅ **Comentários inline** explicativos
✅ **README completo** (este arquivo)

---

## 🔒 Segurança

### Implementado
- ✅ Autenticação por senha
- ✅ Credenciais em arquivo secrets.toml (não versionado)
- ✅ Conexão SSL/TLS com Impala
- ✅ Autenticação LDAP no banco

### Recomendações para Produção
- 🔐 Implementar autenticação multifator (MFA)
- 🔐 Usar hash para senhas (bcrypt)
- 🔐 Implementar controle de acesso baseado em roles (RBAC)
- 🔐 Adicionar logs de auditoria
- 🔐 Configurar HTTPS para a aplicação

---

## 🐛 Troubleshooting

### Erro de Conexão com Banco
```
Verifique:
1. Credenciais em .streamlit/secrets.toml
2. Conectividade com bdaworkernode02.sef.sc.gov.br:21050
3. Permissões do usuário LDAP
4. Certificados SSL
```

### Cache não está funcionando
```bash
# Limpar cache manualmente
streamlit cache clear
```

### Importação de módulos falha
```bash
# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

### Gráficos não aparecem
```
Verifique:
1. Versão do Plotly >= 5.17.0
2. Compatibilidade do navegador
3. JavaScript habilitado
```

---

## 📝 Changelog

### v4.0.0 (2025) - Refatoração Completa
- **Arquitetura modular completa**
- **25+ componentes visuais reutilizáveis**
- **5 algoritmos de Machine Learning**
- **Sistema de insights automáticos**
- **Exportação profissional (PDF, Excel, CSV)**
- **Análise de redes societárias**
- **Análise multidimensional**
- **Documentação completa**

### v3.0 (2024) - Versão Anterior
- Dashboard com 15 páginas
- 3 algoritmos de ML
- Sistema de score customizado
- Geração de PDF básica

---

## 📞 Suporte

**Desenvolvido para:**
Receita Estadual de Santa Catarina

**Dúvidas e Suporte:**
Contate o departamento de TI da SEFAZ/SC

---

## 📄 Licença

© 2025 Receita Estadual de Santa Catarina
Todos os direitos reservados.

Este sistema é de uso exclusivo da Receita Estadual de Santa Catarina.
Reprodução, distribuição ou uso não autorizado são estritamente proibidos.

---

## 🚀 Próximas Melhorias Sugeridas

### Curto Prazo
- [ ] Autenticação via Active Directory
- [ ] Dashboard de administração
- [ ] Logs de auditoria detalhados
- [ ] Notificações por e-mail
- [ ] Agendamento de relatórios

### Médio Prazo
- [ ] API REST para integração
- [ ] Modelo preditivo de risco (ML supervisionado)
- [ ] Análise de séries temporais
- [ ] Detecção de fraude em tempo real
- [ ] Mobile responsivo

### Longo Prazo
- [ ] Integração com outras bases de dados
- [ ] Deep Learning para análise de padrões complexos
- [ ] Sistema de recomendação de ações fiscais
- [ ] Dashboard em tempo real com WebSockets
- [ ] Expansão para outras Secretarias da Fazenda

---

**Desenvolvido com ❤️ para a Receita Estadual de Santa Catarina**
