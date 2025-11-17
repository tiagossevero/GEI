# Data Schemas - Projeto GEI

Este diretório contém os schemas detalhados de todas as tabelas utilizadas no projeto GEI (Grupos Econômicos Identificados).

## 📁 Estrutura de Diretórios

```
data-schemas/
├── originais/              # Tabelas de fontes externas (9 tabelas)
│   ├── {schema}__{tabela}__describe.txt    # DESCRIBE FORMATTED
│   └── {schema}__{tabela}__sample.txt      # SELECT * LIMIT 10
│
└── intermediarias/         # Tabelas processadas pelo GEI (17 tabelas)
    ├── gessimples__{tabela}__describe.txt
    └── gessimples__{tabela}__sample.txt
```

## 📊 Tabelas Documentadas

### Tabelas Originais (9)
Fontes de dados externas que alimentam o sistema GEI:

1. **usr_sat_ods.vw_ods_contrib** - Dados cadastrais de contribuintes
2. **usr_sat_ods.vw_cad_vinculo** - Vínculos societários
3. **usr_sat_ods.sna_pgdasd_estabelecimento_raw** - PGDAS-D
4. **nfe.nfe** - Notas Fiscais Eletrônicas
5. **c115.c115_dados_cadastrais_dest** - Convênio 115
6. **usr_sat_fsn.fsn_conta_bancaria** - Contas bancárias
7. **rais_caged.vw_rais_vinculos** - RAIS/CAGED
8. **usr_sat_admcc.acc_r66_totalestab** - Meios de pagamento
9. **neaf.empresa_indicio** - Indícios fiscais

### Tabelas Intermediárias (17)
Tabelas consolidadas criadas/mantidas pelo GEI:

#### Principais (11)
1. **gei_percent** - Tabela principal com scores e níveis de risco
2. **gei_cnpj** - Relação CNPJ ↔ Grupo Econômico
3. **gei_cadastro** - Dados cadastrais consolidados
4. **gei_contador** - Contadores dos grupos
5. **gei_socios_compartilhados** - Sócios em múltiplas empresas
6. **gei_c115_ranking_risco_grupo_economico** - Ranking C115
7. **gei_funcionarios_metricas_grupo** - Métricas RAIS/CAGED
8. **gei_pagamentos_metricas_grupo** - Métricas de pagamentos
9. **gei_c115_metricas_grupos** - Métricas C115 adicionais
10. **gei_ccs_metricas_grupo** - Métricas CCS
11. **gei_ccs_ranking_risco** - Ranking CCS

#### Detalhadas CCS (3)
12. **gei_ccs_cpf_compartilhado** - CPFs em múltiplas contas
13. **gei_ccs_sobreposicao_responsaveis** - Períodos sobrepostos
14. **gei_ccs_padroes_coordenados** - Eventos coordenados

#### Inconsistências (3)
15. **gei_indicios** - Indícios fiscais catalogados
16. **gei_nfe_completo** - NFe com inconsistências
17. **gei_pgdas** - PGDAS mensais

---

## 🚀 Como Gerar os Data-Schemas

### Opção 1: Usar o Notebook (Recomendado)

1. Abra o notebook `generate_data_schemas.ipynb` no Jupyter
2. Execute as células sequencialmente
3. Os arquivos serão gerados automaticamente em `data-schemas/`

```bash
jupyter notebook generate_data_schemas.ipynb
```

### Opção 2: Executar o Script Python

No ambiente com acesso ao Spark:

```python
# Dentro de um notebook Jupyter com sessão Spark ativa
exec(open('scripts/generate_data_schemas.py').read())
```

---

## 📋 Formato dos Arquivos

### Arquivo `*__describe.txt`
Contém o resultado do comando `DESCRIBE FORMATTED`:
- Colunas e tipos de dados
- Partições
- Metadados da tabela (localização, formato, etc.)

### Arquivo `*__sample.txt`
Contém:
- Schema detalhado (nome, tipo, nullable)
- Primeiras 10 linhas da tabela
- Exemplo de dados reais

---

## 🔧 Configuração do Banco

**Host:** `bdaworkernode02.sef.sc.gov.br:21050`
**Database:** `gessimples` (tabelas GEI)
**Tipo:** Apache Impala
**Autenticação:** LDAP + SSL/TLS

---

## 📝 Nomenclatura dos Arquivos

Padrão: `{schema}__{tabela}__{tipo}.txt`

**Exemplos:**
- `gessimples__gei_percent__describe.txt`
- `gessimples__gei_percent__sample.txt`
- `usr_sat_ods__vw_ods_contrib__describe.txt`
- `usr_sat_ods__vw_ods_contrib__sample.txt`

---

## ⚙️ Personalização

Para adicionar/remover tabelas, edite as listas no script:

```python
# Em generate_data_schemas.ipynb ou scripts/generate_data_schemas.py

TABELAS_ORIGINAIS = [
    ("schema", "tabela", "Descrição"),
    # Adicione mais tabelas aqui
]

TABELAS_INTERMEDIARIAS = [
    ("gessimples", "nova_tabela", "Descrição"),
    # Adicione mais tabelas aqui
]
```

---

## 📊 Estatísticas

- **Total de tabelas:** 26
- **Total de arquivos gerados:** 52 (2 por tabela)
- **Schemas diferentes:** 7 (usr_sat_ods, usr_sat_fsn, usr_sat_admcc, nfe, c115, rais_caged, neaf, gessimples)
- **Tempo estimado de geração:** 5-10 minutos

---

## 🐛 Troubleshooting

### Erro: "Table not found"
- Verifique se você tem permissão de leitura na tabela
- Confirme que o schema e nome da tabela estão corretos
- Teste com: `spark.sql("SHOW TABLES IN schema").show()`

### Erro: "Session not found"
- Certifique-se de que a sessão Spark está ativa
- Execute a célula de inicialização da sessão primeiro

### Tabela vazia no sample
- Normal se a tabela não tiver dados ainda
- Verifique com: `spark.sql("SELECT COUNT(*) FROM schema.tabela").show()`

---

## 📖 Documentação Adicional

Para mais informações sobre o projeto GEI, consulte:
- `README.md` (raiz do projeto)
- `docs/` (documentação técnica)
- Notebooks de exemplo: `GEIG.ipynb`, `GEIC.ipynb`

---

**Última atualização:** 2025-11-17
**Versão:** 1.0.0
