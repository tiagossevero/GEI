# Sistema GEI - Versão Monolítica

Este documento descreve como executar a versão monolítica do Sistema GEI (Gestão Estratégica de Informações).

## 📋 Sobre

O arquivo `app_monolitico.py` consolida todas as funcionalidades do Sistema GEI em um único arquivo Python, facilitando a execução em ambientes onde não é possível ter múltiplos módulos.

## 🚀 Como Executar

### Pré-requisitos

Certifique-se de ter instalado:
- Python 3.8 ou superior
- Todas as dependências listadas em `requirements.txt`

### Instalação de Dependências

```bash
pip install -r requirements.txt
```

### Configuração

1. **Credenciais do Banco de Dados**

   Crie o arquivo `.streamlit/secrets.toml` com suas credenciais:

   ```toml
   [impala_credentials]
   user = "seu_usuario"
   password = "sua_senha"
   ```

2. **Senha do Dashboard**

   Por padrão, a senha é `tsevero654`. Para alterá-la, edite a constante `SENHA_DASHBOARD` no arquivo `app_monolitico.py`:

   ```python
   SENHA_DASHBOARD = "sua_nova_senha"
   ```

### Execução

Para iniciar o dashboard, execute:

```bash
streamlit run app_monolitico.py
```

O sistema abrirá automaticamente no navegador padrão em `http://localhost:8501`

## 📊 Funcionalidades

O sistema monolítico inclui todas as funcionalidades do Sistema GEI v4.0:

### 1. Dashboard Executivo
- KPIs principais (Total de Grupos, Grupos Críticos, Score Médio, Total CNPJs)
- Distribuição de Score de Risco (histograma)
- Grupos por Nível de Risco (pizza/donut)
- Top 15 Grupos por Receita
- Top 15 Grupos por Quantidade de CNPJs
- Insights Gerais do Sistema
- Exportação em Excel e CSV

### 2. Análise Pontual
- Busca por Número do Grupo ou CNPJ
- Resumo do Grupo (KPIs)
- Medidor de Risco (Gauge)
- Detalhes de Risco
- Insights Automáticos
- Lista de CNPJs do Grupo
- Exportação de Dossiê (PDF e Excel)

### 3. Ranking de Grupos
- Ranking configurável (10-100 grupos)
- Visualização em tabela formatada
- Gráfico de barras do Top 20
- Exportação em Excel e CSV

### 4. Machine Learning
- Algoritmos: K-Means, DBSCAN, Hierárquico, Isolation Forest
- Redução de dimensionalidade (PCA)
- Análise de consenso entre algoritmos
- Visualizações 2D e 3D
- Métricas de qualidade (Silhouette, Davies-Bouldin)

### 5. Análise de Redes
- Visualização de redes societárias
- Identificação de sócios compartilhados
- Grafo interativo de conexões

### 6. Análise Multidimensional
- Matriz de correlação configurável
- Scatter Matrix para até 5 métricas
- Análise de padrões entre variáveis

### 7. Insights Automáticos
- Insights gerais do sistema
- Top 10 grupos prioritários para investigação
- Geração automática baseada em regras de negócio

### 8. Dossiê Completo
- Geração de dossiê em PDF
- Inclui: Resumo Executivo, CNPJs, Análise de Risco, Sócios, Observações

### 9. Configurações
- Informações do sistema
- Limpeza de cache
- Documentação de funcionalidades

## 🔧 Filtros Globais

Disponíveis na sidebar para todas as páginas:
- **Score de Risco:** Slider de 0-100%
- **Níveis de Risco:** Multiselect (CRÍTICO, ALTO, MÉDIO, BAIXO)

## 🗄️ Estrutura de Dados

O sistema se conecta ao banco Impala e carrega as seguintes tabelas:

1. `gei_percent` - Dados principais dos grupos
2. `gei_cnpj` - CNPJs dos grupos
3. `gei_cadastro` - Dados cadastrais
4. `gei_contador` - Informações de contadores
5. `gei_socios_compartilhados` - Sócios em comum
6. `gei_c115_ranking_risco_grupo_economico` - Convênio 115
7. `gei_funcionarios_metricas_grupo` - Métricas de funcionários
8. `gei_pagamentos_metricas_grupo` - Métricas de pagamentos
9. `gei_c115_metricas_grupos` - Métricas C115
10. `gei_ccs_metricas_grupo` - Métricas de contas compartilhadas
11. `gei_ccs_ranking_risco` - Ranking CCS

## 📦 Dependências Principais

```
streamlit >= 1.28.0
pandas
numpy
plotly >= 5.17.0
scikit-learn >= 1.3.0
scipy >= 1.11.0
sqlalchemy >= 2.0.0
impyla >= 0.18.0
reportlab >= 4.0.0
openpyxl >= 3.1.0
```

## 🔐 Segurança

- Autenticação por senha na tela inicial
- Conexão SSL com o banco de dados
- Credenciais armazenadas em arquivo separado (secrets.toml)
- Não incluir secrets.toml no controle de versão

## 📈 Performance

- **Cache:** Dados principais (1h), Dossiê (5min), Análises (30min)
- **Limites:** CNPJ (50k), Sócios (30k), Inconsistências (1k)
- **Progress Bar:** Carregamento visível na sidebar

## 🆘 Solução de Problemas

### Erro de Conexão com Banco
- Verifique as credenciais em `.streamlit/secrets.toml`
- Confirme conectividade com o servidor Impala
- Teste a conexão SSL

### Erro de Memória
- Reduza os limites de consulta nas constantes
- Limpe o cache nas Configurações
- Ajuste os filtros globais para reduzir o volume de dados

### Erro de Importação
- Reinstale as dependências: `pip install -r requirements.txt`
- Verifique a versão do Python (mínimo 3.8)

## 📝 Notas

- O arquivo monolítico tem ~3.500 linhas de código
- Todas as funcionalidades do projeto modular estão incluídas
- Ideal para deployment em ambientes restritos
- Performance equivalente à versão modular

## 📞 Suporte

Para questões e suporte, consulte a documentação original do projeto ou entre em contato com a equipe de desenvolvimento.

---

**Sistema GEI v4.0 - Receita Estadual de Santa Catarina**
