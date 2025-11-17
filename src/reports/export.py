"""
Módulo de Exportação de Relatórios
Gera relatórios em PDF, Excel e CSV
"""

import pandas as pd
import streamlit as st
from io import BytesIO
from typing import Dict, List, Optional
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image as RLImage
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from ..config.settings import formatar_moeda, formatar_numero, formatar_percentual

# =============================================================================
# EXPORTAÇÃO PARA EXCEL
# =============================================================================

def exportar_para_excel(
    dados: Dict[str, pd.DataFrame],
    nome_arquivo: str = "relatorio_gei"
) -> BytesIO:
    """
    Exporta múltiplas tabelas para Excel com formatação

    Args:
        dados: Dicionário {nome_aba: dataframe}
        nome_arquivo: Nome do arquivo (sem extensão)

    Returns:
        BytesIO com arquivo Excel
    """
    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for nome_aba, df in dados.items():
            # Limitar nome da aba a 31 caracteres
            nome_aba_clean = nome_aba[:31]

            df.to_excel(writer, sheet_name=nome_aba_clean, index=False)

            # Aplicar formatação
            workbook = writer.book
            worksheet = writer.sheets[nome_aba_clean]

            # Formatar cabeçalho
            header_fill = PatternFill(start_color='1F77B4', end_color='1F77B4', fill_type='solid')
            header_font = Font(bold=True, color='FFFFFF')

            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center', vertical='center')

            # Ajustar largura das colunas
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter

                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass

                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

            # Congelar primeira linha
            worksheet.freeze_panes = 'A2'

    output.seek(0)
    return output

def criar_botao_download_excel(
    dados: Dict[str, pd.DataFrame],
    nome_arquivo: str = "relatorio_gei",
    label: str = "📥 Download Excel"
) -> None:
    """
    Cria botão de download para Excel

    Args:
        dados: Dicionário com DataFrames
        nome_arquivo: Nome do arquivo
        label: Texto do botão
    """
    excel_data = exportar_para_excel(dados, nome_arquivo)

    st.download_button(
        label=label,
        data=excel_data,
        file_name=f"{nome_arquivo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# =============================================================================
# EXPORTAÇÃO PARA CSV
# =============================================================================

def exportar_para_csv(df: pd.DataFrame) -> BytesIO:
    """
    Exporta DataFrame para CSV

    Args:
        df: DataFrame a exportar

    Returns:
        BytesIO com arquivo CSV
    """
    output = BytesIO()
    df.to_csv(output, index=False, encoding='utf-8-sig', sep=';')
    output.seek(0)
    return output

def criar_botao_download_csv(
    df: pd.DataFrame,
    nome_arquivo: str = "dados",
    label: str = "📥 Download CSV"
) -> None:
    """
    Cria botão de download para CSV

    Args:
        df: DataFrame
        nome_arquivo: Nome do arquivo
        label: Texto do botão
    """
    csv_data = exportar_para_csv(df)

    st.download_button(
        label=label,
        data=csv_data,
        file_name=f"{nome_arquivo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

# =============================================================================
# EXPORTAÇÃO PARA PDF - DOSSIÊ COMPLETO
# =============================================================================

class PDFDossie:
    """Classe para geração de dossiê em PDF"""

    def __init__(self, num_grupo: str):
        self.num_grupo = num_grupo
        self.story = []
        self.styles = getSampleStyleSheet()
        self._configurar_estilos()

    def _configurar_estilos(self):
        """Configura estilos personalizados"""
        # Estilo de título
        self.styles.add(ParagraphStyle(
            name='TituloCustom',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1F77B4'),
            spaceAfter=12,
            alignment=TA_CENTER
        ))

        # Estilo de subtítulo
        self.styles.add(ParagraphStyle(
            name='SubtituloCustom',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=10,
            spaceBefore=10
        ))

        # Estilo de texto normal
        self.styles.add(ParagraphStyle(
            name='NormalCustom',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))

    def adicionar_titulo_principal(self, titulo: str):
        """Adiciona título principal"""
        self.story.append(Paragraph(titulo, self.styles['TituloCustom']))
        self.story.append(Spacer(1, 0.3*inch))

    def adicionar_secao(self, titulo: str):
        """Adiciona título de seção"""
        self.story.append(Paragraph(titulo, self.styles['SubtituloCustom']))
        self.story.append(Spacer(1, 0.1*inch))

    def adicionar_paragrafo(self, texto: str):
        """Adiciona parágrafo de texto"""
        self.story.append(Paragraph(texto, self.styles['NormalCustom']))

    def adicionar_tabela(self, dados: List[List], larguras: Optional[List] = None):
        """Adiciona tabela formatada"""
        if not dados:
            return

        # Criar tabela
        tabela = Table(dados, colWidths=larguras)

        # Estilo da tabela
        estilo = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F77B4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ])

        tabela.setStyle(estilo)
        self.story.append(tabela)
        self.story.append(Spacer(1, 0.2*inch))

    def adicionar_kpis(self, kpis: Dict[str, str]):
        """Adiciona KPIs em formato de tabela"""
        dados = [['Métrica', 'Valor']]
        dados.extend([[k, v] for k, v in kpis.items()])

        self.adicionar_tabela(dados, larguras=[3*inch, 3*inch])

    def adicionar_quebra_pagina(self):
        """Adiciona quebra de página"""
        self.story.append(PageBreak())

    def gerar_pdf(self, dados_grupo: pd.Series, dossie: Dict[str, pd.DataFrame]) -> BytesIO:
        """
        Gera PDF completo do dossiê

        Args:
            dados_grupo: Série com dados principais do grupo
            dossie: Dicionário com dados completos

        Returns:
            BytesIO com PDF
        """
        output = BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)

        # Título
        self.adicionar_titulo_principal(f"DOSSIÊ DO GRUPO ECONÔMICO {self.num_grupo}")

        # Data de geração
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.adicionar_paragrafo(f"<b>Data de Geração:</b> {data_atual}")
        self.adicionar_paragrafo("<b>Sistema GEI - Gestão Estratégica de Informações</b>")
        self.adicionar_paragrafo("<b>Receita Estadual de Santa Catarina</b>")
        self.story.append(Spacer(1, 0.3*inch))

        # Seção 1: Resumo Executivo
        self.adicionar_secao("1. RESUMO EXECUTIVO")

        kpis_resumo = {
            'Número do Grupo': str(self.num_grupo),
            'Quantidade de CNPJs': formatar_numero(dados_grupo.get('qtd_cnpjs', 0)),
            'Score de Risco': f"{dados_grupo.get('score_final_percent', 0):.1f}%",
            'Nível de Risco': dados_grupo.get('nivel_risco_final', 'N/A'),
            'Receita Máxima': formatar_moeda(dados_grupo.get('receita_maxima', 0))
        }

        self.adicionar_kpis(kpis_resumo)

        # Seção 2: CNPJs do Grupo
        self.adicionar_secao("2. CNPJs DO GRUPO")

        if not dossie.get('cnpjs', pd.DataFrame()).empty:
            df_cnpjs = dossie['cnpjs'].head(20)  # Limitar a 20 CNPJs

            dados_tabela = [['CNPJ', 'Razão Social', 'Município']]
            for _, row in df_cnpjs.iterrows():
                dados_tabela.append([
                    str(row.get('cnpj', ''))[:18],
                    str(row.get('nm_razao_social', ''))[:40],
                    str(row.get('nm_municipio', ''))[:20]
                ])

            self.adicionar_tabela(dados_tabela, larguras=[1.5*inch, 3*inch, 1.5*inch])
        else:
            self.adicionar_paragrafo("Nenhum CNPJ encontrado.")

        self.adicionar_quebra_pagina()

        # Seção 3: Análise de Risco
        self.adicionar_secao("3. ANÁLISE DE RISCO MULTIDIMENSIONAL")

        kpis_risco = {
            'Score Cadastral': f"{dados_grupo.get('razao_social_identica', 0) + dados_grupo.get('fantasia_identica', 0)}",
            'Sócios Compartilhados': formatar_numero(dados_grupo.get('socios_compartilhados', 0)),
            'Contas Compartilhadas': formatar_numero(dados_grupo.get('contas_compartilhadas', 0)),
            'Total de Indícios': formatar_numero(dados_grupo.get('total_indicios', 0)),
            'Risco C115': dados_grupo.get('nivel_risco_c115', 'N/A')
        }

        self.adicionar_kpis(kpis_risco)

        # Seção 4: Sócios Compartilhados
        if not dossie.get('socios', pd.DataFrame()).empty:
            self.adicionar_secao("4. SÓCIOS COMPARTILHADOS")

            df_socios = dossie['socios'].head(15)
            dados_socios = [['CPF Sócio', 'Qtd Empresas']]

            for _, row in df_socios.iterrows():
                dados_socios.append([
                    str(row.get('cpf_socio', '')),
                    formatar_numero(row.get('qtd_empresas', 0))
                ])

            self.adicionar_tabela(dados_socios, larguras=[3*inch, 2*inch])

        # Seção 5: Indícios Fiscais
        if not dossie.get('indicios', pd.DataFrame()).empty:
            self.adicionar_quebra_pagina()
            self.adicionar_secao("5. INDÍCIOS FISCAIS")

            df_indicios = dossie['indicios'].head(20)

            # Agrupar por tipo
            indicios_por_tipo = df_indicios.groupby('tx_descricao_indicio').size().reset_index(name='Quantidade')

            dados_indicios = [['Tipo de Indício', 'Quantidade']]
            for _, row in indicios_por_tipo.iterrows():
                dados_indicios.append([
                    str(row['tx_descricao_indicio'])[:40],
                    formatar_numero(row['Quantidade'])
                ])

            self.adicionar_tabela(dados_indicios, larguras=[4*inch, 1.5*inch])

        # Seção 6: Contas Compartilhadas
        if not dossie.get('ccs_compartilhadas', pd.DataFrame()).empty:
            self.adicionar_quebra_pagina()
            self.adicionar_secao("6. CONTAS BANCÁRIAS COMPARTILHADAS")

            df_ccs = dossie['ccs_compartilhadas'].head(15)
            dados_ccs = [['Banco', 'Agência', 'Conta', 'CNPJs']]

            for _, row in df_ccs.iterrows():
                dados_ccs.append([
                    str(row.get('nm_banco', ''))[:15],
                    str(row.get('cd_agencia', '')),
                    str(row.get('nr_conta', ''))[:10],
                    formatar_numero(row.get('qtd_cnpjs_usando_conta', 0))
                ])

            self.adicionar_tabela(dados_ccs, larguras=[1.5*inch, 1*inch, 1.5*inch, 1*inch])

        # Seção Final: Observações
        self.adicionar_quebra_pagina()
        self.adicionar_secao("7. OBSERVAÇÕES E RECOMENDAÇÕES")

        score = dados_grupo.get('score_final_percent', 0)
        if score >= 80:
            recomendacao = "GRUPO DE RISCO CRÍTICO - Recomenda-se investigação fiscal urgente e detalhada."
        elif score >= 60:
            recomendacao = "GRUPO DE ALTO RISCO - Recomenda-se monitoramento próximo e análise aprofundada."
        elif score >= 40:
            recomendacao = "GRUPO DE MÉDIO RISCO - Recomenda-se acompanhamento periódico."
        else:
            recomendacao = "GRUPO DE BAIXO RISCO - Manter em monitoramento padrão."

        self.adicionar_paragrafo(f"<b>Recomendação:</b> {recomendacao}")

        # Rodapé
        self.story.append(Spacer(1, 0.5*inch))
        self.adicionar_paragrafo("<i>Este documento foi gerado automaticamente pelo Sistema GEI.</i>")
        self.adicionar_paragrafo("<i>As informações contidas neste dossiê são confidenciais e de uso exclusivo da Receita Estadual.</i>")

        # Construir PDF
        doc.build(self.story)
        output.seek(0)

        return output

def gerar_dossie_pdf(num_grupo: str, dados_grupo: pd.Series, dossie: Dict[str, pd.DataFrame]) -> BytesIO:
    """
    Função wrapper para gerar dossiê em PDF

    Args:
        num_grupo: Número do grupo
        dados_grupo: Dados principais do grupo
        dossie: Dados completos do dossiê

    Returns:
        BytesIO com PDF
    """
    gerador = PDFDossie(num_grupo)
    return gerador.gerar_pdf(dados_grupo, dossie)

def criar_botao_download_pdf(
    num_grupo: str,
    dados_grupo: pd.Series,
    dossie: Dict[str, pd.DataFrame],
    label: str = "📥 Download PDF"
) -> None:
    """
    Cria botão de download para PDF do dossiê

    Args:
        num_grupo: Número do grupo
        dados_grupo: Dados do grupo
        dossie: Dossiê completo
        label: Texto do botão
    """
    pdf_data = gerar_dossie_pdf(num_grupo, dados_grupo, dossie)

    st.download_button(
        label=label,
        data=pdf_data,
        file_name=f"dossie_grupo_{num_grupo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf"
    )
