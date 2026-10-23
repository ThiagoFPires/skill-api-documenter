"""
Template oficial reutilizável para geração de PDFs de documentação de APIs da Tek-System
Utilizado pela skill 'tek-api-documenter' do Google Antigravity.

Incorpora os timbrados institucionais oficiais da Tek-System (cabeçalho com onda dupla
azul-marinho/vinho, logo corporativo e rodapé estilizado), com paginação automática
e diagramação executiva.
"""

import os
import argparse
from typing import List, Tuple, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Preformatted,
    KeepTogether,
    HRFlowable,
)

# Caminho padrão para os assets de timbrados
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_TIMBRADO = os.path.join(BASE_DIR, "assets", "timbrados", "timbrado_default.png")


def create_canvas_maker(
    timbrado_path: Optional[str] = None,
    footer_text: str = "Tek-System Informática — Documentação Técnica de Integração API",
):
    """
    Retorna uma função de callback para desenhar o timbrado de fundo e o rodapé
    institucional em todas as páginas do documento.
    """
    resolved_timbrado = timbrado_path if timbrado_path and os.path.exists(timbrado_path) else DEFAULT_TIMBRADO

    def draw_background_and_footer(canvas, doc):
        canvas.saveState()

        # 1. Desenha o timbrado oficial como imagem de fundo (se o arquivo existir)
        if resolved_timbrado and os.path.exists(resolved_timbrado):
            try:
                canvas.drawImage(
                    resolved_timbrado,
                    0,
                    0,
                    width=A4[0],
                    height=A4[1],
                    preserveAspectRatio=False,
                    mask="auto",
                )
            except Exception as e:
                print(f"[Aviso] Falha ao renderizar imagem de timbrado: {e}")

        # 2. Linha divisória sutil acima do rodapé
        canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
        canvas.setLineWidth(0.5)
        canvas.line(18 * mm, 17 * mm, A4[0] - 18 * mm, 17 * mm)

        # 3. Textos do rodapé e número de página
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#475569"))
        canvas.drawString(18 * mm, 13 * mm, footer_text)
        canvas.drawRightString(A4[0] - 18 * mm, 13 * mm, f"Página {doc.page}")

        canvas.restoreState()

    return draw_background_and_footer


def create_document(
    output_path: str,
    title: str = "Documentação Técnica de API — Tek-System",
    author: str = "Tek-System Informática",
) -> SimpleDocTemplate:
    """
    Cria a instância do SimpleDocTemplate com margens perfeitamente calibradas
    para a zona segura dos timbrados oficiais da Tek-System:
      - Top margin: 38mm (respeita a onda superior e o logo da Tek-System)
      - Bottom margin: 23mm (respeita a linha de rodapé e a onda inferior)
      - Left / Right: 18mm
    """
    return SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=38 * mm,
        bottomMargin=23 * mm,
        title=title,
        author=author,
    )


def get_tek_styles():
    """
    Retorna o conjunto de estilos tipográficos padronizado da Tek-System.
    Cores da marca:
      - Azul Marinho Tek: #002060 / #0F172A
      - Vinho / Burgundy Tek: #800000 / #991B1B
      - Slate Corporativo: #334155 / #475569
    """
    styles = getSampleStyleSheet()

    s_title = ParagraphStyle(
        "TekBannerTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15.5,
        leading=20,
        textColor=colors.white,
        spaceAfter=3,
    )

    s_subtitle = ParagraphStyle(
        "TekBannerSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#E2E8F0"),
    )

    s_h1 = ParagraphStyle(
        "TekH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#002060"),
        spaceBefore=9,
        spaceAfter=4,
    )

    s_h2 = ParagraphStyle(
        "TekH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.8,
        leading=13.5,
        textColor=colors.HexColor("#800000"),
        spaceBefore=7,
        spaceAfter=3,
    )

    s_body = ParagraphStyle(
        "TekBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E293B"),
        alignment=TA_JUSTIFY,
        spaceAfter=4,
    )

    s_th = ParagraphStyle(
        "TekTH",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
    )

    s_td = ParagraphStyle(
        "TekTD",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.2,
        leading=11.5,
        textColor=colors.HexColor("#1E293B"),
    )

    s_code = ParagraphStyle(
        "TekCode",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#F8FAFC"),
    )

    return {
        "title": s_title,
        "subtitle": s_subtitle,
        "h1": s_h1,
        "h2": s_h2,
        "body": s_body,
        "th": s_th,
        "td": s_td,
        "code": s_code,
    }


def banner_header(
    title: str,
    subtitle: str,
    styles,
    bg_color: str = "#002060",
    border_color: str = "#800000",
) -> Table:
    """
    Gera um banner executivo no topo da primeira página com as cores institucionais Tek-System.
    """
    content = [
        [Paragraph(title, styles["title"])],
        [Paragraph(subtitle, styles["subtitle"])],
    ]
    t = Table(content, colWidths=[174 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg_color)),
                ("LINEBEFORE", (0, 0), (0, -1), 4, colors.HexColor(border_color)),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                ("TOPPADDING", (0, 0), (0, 0), 10),
                ("BOTTOMPADDING", (0, -1), (-1, -1), 10),
                ("TOPPADDING", (0, 1), (-1, 1), 2),
            ]
        )
    )
    return t


def code_block(
    text: str,
    style: ParagraphStyle,
    bg_color: str = "#0F172A",
    border_color: str = "#334155",
) -> Table:
    """Gera um bloco formatado para JSON, cURL ou Pascal com fundo escuro."""
    pre = Preformatted(text.strip(), style)
    t = Table([[pre]], colWidths=[174 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg_color)),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor(border_color)),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return t


def callout_box(
    title: str,
    body: str,
    s_body: ParagraphStyle,
    bg: str = "#EFF6FF",
    border: str = "#1E40AF",
) -> Table:
    """Gera uma caixa de destaque (callout) para informações críticas (ex: Token Consumidor)."""
    p = Paragraph(f"<b>{title}</b><br/>{body}", s_body)
    t = Table([[p]], colWidths=[174 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg)),
                ("LINEBEFORE", (0, 0), (0, -1), 3.5, colors.HexColor(border)),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#BFDBFE")),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return t


def styled_table(
    data: List[List[str]],
    col_widths: List[float],
    s_header: ParagraphStyle,
    s_cell: ParagraphStyle,
    header_bg: str = "#002060",
) -> Table:
    """Gera uma tabela técnica com cabeçalho corporativo e linhas alternadas."""
    formatted_rows = []
    for r_idx, row in enumerate(data):
        formatted_row = []
        for cell in row:
            if isinstance(cell, str):
                formatted_row.append(Paragraph(cell, s_header if r_idx == 0 else s_cell))
            else:
                formatted_row.append(cell)
        formatted_rows.append(formatted_row)

    t = Table(formatted_rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_bg)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
            ]
        )
    )
    return t


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gerador de PDF com Timbrado Oficial Tek-System")
    parser.add_argument("--output", default="documento_exemplo.pdf", help="Caminho do PDF de saída")
    parser.add_argument("--timbrado", default=DEFAULT_TIMBRADO, help="Caminho da imagem PNG de timbrado")
    args = parser.parse_args()

    doc = create_document(args.output, title="Exemplo de Documentação Técnica")
    st = get_tek_styles()
    canvas_callback = create_canvas_maker(timbrado_path=args.timbrado)

    story = [
        banner_header(
            "Documentação Técnica de API — Tek-System",
            "Módulo de Integração Corporativa / APIs Dinâmicas",
            st,
        ),
        Spacer(1, 10),
        callout_box(
            "Configuração de Acesso — Token Consumidor",
            "Para autenticação no endpoint <code>/auth</code>, o cabeçalho exige o parâmetro <b>consumidor</b>.",
            st["body"],
        ),
        Spacer(1, 8),
        Paragraph("1. Visão Geral da Rota", st["h1"]),
        Paragraph("Este documento foi gerado automaticamente com o timbrado corporativo da Tek-System.", st["body"]),
    ]

    doc.build(story, onFirstPage=canvas_callback, onLaterPages=canvas_callback)
    print(f"PDF de teste gerado com sucesso em: {args.output}")
