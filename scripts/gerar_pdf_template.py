"""
Template oficial reutilizável para geração de PDFs de documentação de APIs da Tek-System
Utilizado pela skill 'tek-api-documenter' do Google Antigravity.

Incorpora os timbrados institucionais oficiais da Tek-System (cabeçalho com onda dupla
azul-marinho/vinho, logo corporativo e rodapé estilizado), com paginação automática
e diagramação executiva calibrada em 4 páginas.
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
    use_timbrado: bool = True,
):
    """
    Retorna uma função de callback para desenhar o timbrado de fundo e o rodapé
    institucional em todas as páginas do documento.
    """
    resolved_timbrado = timbrado_path if timbrado_path and os.path.exists(timbrado_path) else DEFAULT_TIMBRADO

    def draw_background_and_footer(canvas, doc):
        canvas.saveState()

        # 1. Desenha o timbrado oficial como imagem de fundo (se solicitado e existente)
        if use_timbrado and resolved_timbrado and os.path.exists(resolved_timbrado):
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
    use_timbrado: bool = True,
) -> SimpleDocTemplate:
    """
    Cria a instância do SimpleDocTemplate com margens perfeitamente calibradas:
      - Top margin: 38mm com timbrado / 18mm sem timbrado
      - Bottom margin: 23mm
      - Left / Right: 18mm
    """
    return SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=(38 * mm if use_timbrado else 18 * mm),
        bottomMargin=23 * mm,
        title=title,
        author=author,
    )


def get_tek_styles():
    """
    Retorna o conjunto de estilos tipográficos padronizado da Tek-System.
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
        textColor=colors.HexColor("#CBD5E1"),
    )

    s_h1 = ParagraphStyle(
        "TekH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=6,
        spaceAfter=3,
    )

    s_h2 = ParagraphStyle(
        "TekH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.8,
        leading=13,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=5,
        spaceAfter=2,
    )

    s_body = ParagraphStyle(
        "TekBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor("#1E293B"),
        alignment=TA_JUSTIFY,
        spaceAfter=3,
    )

    s_callout = ParagraphStyle(
        "TekCallout",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.3,
        leading=13.5,
        textColor=colors.HexColor("#1E293B"),
    )

    s_callout_prereq = ParagraphStyle(
        "TekCalloutPrereq",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.2,
        leading=11.2,
        textColor=colors.HexColor("#1E293B"),
    )

    s_th = ParagraphStyle(
        "TekTH",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.8,
        leading=11.5,
        textColor=colors.white,
    )

    s_td = ParagraphStyle(
        "TekTD",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1E293B"),
    )

    s_code = ParagraphStyle(
        "TekCode",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8.3,
        leading=11.5,
        textColor=colors.HexColor("#F8FAFC"),
    )

    return {
        "title": s_title,
        "subtitle": s_subtitle,
        "h1": s_h1,
        "h2": s_h2,
        "body": s_body,
        "callout": s_callout,
        "callout_prereq": s_callout_prereq,
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
    """Gera um banner executivo no topo da primeira página com as cores institucionais Tek-System."""
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
                ("TOPPADDING", (0, 0), (0, 0), 7),
                ("BOTTOMPADDING", (0, -1), (-1, -1), 7),
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
    """Gera um bloco formatado para JSON, cURL ou código com fundo escuro."""
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
    border: str = "#2563EB",
    pad_v: float = 7,
) -> Table:
    """Gera uma caixa de destaque (callout) para informações críticas."""
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
                ("TOPPADDING", (0, 0), (-1, -1), pad_v),
                ("BOTTOMPADDING", (0, 0), (-1, -1), pad_v),
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
    pad_v: float = 3.5,
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
                ("TOPPADDING", (0, 0), (-1, -1), pad_v),
                ("BOTTOMPADDING", (0, 0), (-1, -1), pad_v),
            ]
        )
    )
    return t


def build_template_pdf(output_path: str, use_timbrado: bool = True):
    """
    Constrói a documentação técnica modelo padrão Tek-System em 4 páginas calibradas,
    utilizando parâmetros genéricos (placeholders).
    """
    doc = create_document(
        output_path,
        title="Modelo Padrão — Documentação Técnica de Integração API",
        author="Tek-System",
        use_timbrado=use_timbrado,
    )
    st = get_tek_styles()
    canvas_callback = create_canvas_maker(use_timbrado=use_timbrado)

    story = []

    # ================= PAGE 1 =================
    banner = banner_header(
        "Documentação Técnica de Integração API — [NOME_INTEGRACAO]",
        "Tek-System ERP / BI — Autenticação (/auth) &amp; [TITULO_FUNCIONALIDADE] (/apidyn/[GRUPO]/[RECURSO])",
        st,
    )
    story.append(banner)
    story.append(Spacer(1, 4))

    story.append(Paragraph("1. Visão Geral e Parâmetros de Conexão", st["h1"]))
    story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#CBD5E1"), spaceAfter=3))
    story.append(
        Paragraph(
            "Esta documentação descreve o fluxo de comunicação para a integração <b>[NOME_INTEGRACAO]</b> com o servidor de aplicação "
            "<b>TekServer Horse</b> no endereço <b>http://[IP_OU_DOMINIO]:[PORTA]</b> (IP externo e porta liberados) e o endpoint de "
            "<b>[TITULO_FUNCIONALIDADE]</b> configurado no módulo de BI (GeradorRelatorioMC).",
            st["body"],
        )
    )
    story.append(
        Paragraph(
            "O fluxo de integração é composto por duas etapas obrigatórias:<br/>"
            "<b>1. Autenticação (POST /auth):</b> Envio do código do sistema, Token do Usuário e Token Consumidor para geração do token JWT (<font name='Courier'>token_Acesso</font>).<br/>"
            "<b>2. Execução da Rota (POST /apidyn/[GRUPO]/[RECURSO]):</b> Chamada autenticada via <i>Bearer Token</i> para envio e processamento dos dados no ERP.",
            st["body"],
        )
    )
    story.append(Spacer(1, 2))

    story.append(
        callout_box(
            "PARÂMETROS OFICIAIS DE CONEXÃO ([NOME_INTEGRACAO])",
            "• <b>URL Base (TekServer Horse / IP Externo):</b> <font name='Courier-Bold' size='10' color='#1D4ED8'>http://[IP_OU_DOMINIO_EXTERNO]:[PORTA]</font><br/>"
            "• <b>Token Consumidor:</b> <font name='Courier-Bold' size='10' color='#1D4ED8'>REC-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX</font><br/>"
            "• <b>Token do Usuário:</b> <font name='Courier-Bold' size='10' color='#1D4ED8'>[TOKEN_DO_USUARIO_ERP]</font>",
            st["callout"],
            bg="#EFF6FF",
            border="#2563EB",
            pad_v=4.5,
        )
    )
    story.append(Spacer(1, 4))

    story.append(Paragraph("Variáveis de Conexão da Integração", st["h2"]))
    vars_data = [
        ["Variável", "Valor Configurado", "Obrigatório", "Descrição"],
        [
            "<font name='Courier'>{{url}}</font>",
            "<font name='Courier'><b>http://[IP]:[PORTA]</b></font>",
            "Sim",
            "Endereço base do serviço HTTPS API no TekServer Horse (IP externo e porta liberados).",
        ],
        [
            "<font name='Courier'>{{consumidor}}</font>",
            "<font name='Courier'><b>REC-XXXX-XXXX...</b></font>",
            "Sim",
            "Token Consumidor habilitado no Tek-System para a integração.",
        ],
        [
            "<font name='Courier'>{{token_usuario}}</font>",
            "<font name='Courier'><b>[TOKEN_USUARIO]</b></font>",
            "Sim",
            "Token de identificação do usuário no Cadastro de Usuários do ERP Tek-System.",
        ],
        [
            "<font name='Courier'>{{tek_acess_token}}</font>",
            "<font name='Courier'>eyJ0eXAiOiJKV1Qi...</font>",
            "Sim (Etapa 2)",
            "Token JWT retornado no atributo <font name='Courier'>token_Acesso</font> pela rota <font name='Courier'>/auth</font>.",
        ],
    ]
    story.append(styled_table(vars_data, [36 * mm, 63 * mm, 24 * mm, 51 * mm], st["th"], st["td"]))
    story.append(Spacer(1, 4))

    story.append(
        callout_box(
            "PRÉ-REQUISITOS OBRIGATÓRIOS DE SISTEMA, REDE E INFRAESTRUTURA",
            "• <b>Instalação da Funcionalidade via Marketplace:</b> Instalação prévia obrigatória da funcionalidade no <b>Marketplace da Tek-System</b> (SoftwareCenter), registrando o componente e a API Dinâmica no catálogo do servidor.<br/>"
            "• <b>Liberação do Usuário na API Dinâmica:</b> O usuário da integração (<font name='Courier'>token_usuario</font>) <b>deve ser expressamente liberado na aba de Usuários Autorizados dentro da API Dinâmica instalada</b> no BI (GeradorRelatorioMC). Sem isso, as requisições serão rejeitadas mesmo com login válido.<br/>"
            "• <b>Configuração do TekServer Horse e Porta:</b> É necessária a configuração do serviço no <b>TekServer Horse</b>, garantindo que a <b>porta configurada (ex: [PORTA])</b> esteja devidamente liberada no firewall do servidor e com redirecionamento de porta (NAT) ativo.<br/>"
            "• <b>Liberação de IP Externo para Conexão:</b> O <b>IP externo público</b> do servidor (ou FQDN/DNS) deve estar liberado para receber conexões externas da internet, garantindo também a liberação dos IPs de origem do parceiro em caso de firewall com restrição por whitelist.",
            st["callout_prereq"],
            bg="#FFFBEB",
            border="#D97706",
            pad_v=4,
        )
    )
    story.append(Spacer(1, 8))

    # ================= PAGE 2 =================
    auth_spec_data = [
        ["Propriedade", "Especificação"],
        ["Nome no Postman", "Auth"],
        ["Método HTTP", "<b>POST</b>"],
        ["Endpoint (URL)", "<font name='Courier'>http://[IP_OU_DOMINIO]:[PORTA]/auth</font> (ou <font name='Courier'>{{url}}/auth</font>)"],
        ["Header Obrigatório", "<font name='Courier'>Content-Type: application/json</font>"],
        ["Autenticação Prévia", "Nenhuma (<i>No Auth</i> — credenciais enviadas no Body JSON)"],
    ]
    story.append(
        KeepTogether(
            [
                Paragraph("2. Rota 1 — Autenticação (/auth)", st["h1"]),
                HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#CBD5E1"), spaceAfter=5),
                Paragraph(
                    "Responsável por validar as credenciais do usuário e o Token Consumidor no servidor Tek-System e emitir o "
                    "token JWT (<font name='Courier'>token_Acesso</font>) para consumo dos endpoints protegidos.",
                    st["body"],
                ),
                styled_table(auth_spec_data, [45 * mm, 129 * mm], st["th"], st["td"]),
            ]
        )
    )
    story.append(Spacer(1, 5))

    auth_body_json = """{
  "Sistema": 1,
  "Token": "{{token_usuario}}",
  "consumidor": "{{consumidor}}"
}"""
    story.append(
        KeepTogether(
            [
                Paragraph("Body da Requisição (JSON)", st["h2"]),
                code_block(auth_body_json, st["code"]),
            ]
        )
    )
    story.append(Spacer(1, 5))

    auth_params_data = [
        ["Campo", "Tipo", "Obrigatório", "Descrição"],
        [
            "<font name='Courier'>Sistema</font>",
            "<font name='Courier'>integer</font>",
            "Sim",
            "Código identificador do módulo no Tek-System (<font name='Courier'>1</font> = Faturamento / ERP).",
        ],
        [
            "<font name='Courier'>Token</font>",
            "<font name='Courier'>string</font>",
            "Sim",
            "Token do usuário cadastrado no ERP Tek-System: <font name='Courier'><b>{{token_usuario}}</b></font>.",
        ],
        [
            "<font name='Courier'>consumidor</font>",
            "<font name='Courier'>string</font>",
            "Sim",
            "Token Consumidor oficial da integração: <font name='Courier'><b>{{consumidor}}</b></font>.",
        ],
    ]
    story.append(
        KeepTogether(
            [
                Paragraph("Descrição dos Parâmetros de Envio (/auth)", st["h2"]),
                styled_table(auth_params_data, [32 * mm, 24 * mm, 24 * mm, 94 * mm], st["th"], st["td"]),
            ]
        )
    )
    story.append(Spacer(1, 5))

    auth_resp_json = """{
  "token_Acesso": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJUZWstU3lzdGVt...<JWT>"
}"""
    story.append(
        KeepTogether(
            [
                Paragraph("Exemplo de Retorno (200 OK — application/json)", st["h2"]),
                code_block(auth_resp_json, st["code"]),
            ]
        )
    )
    story.append(Spacer(1, 5))

    auth_script_js = """const response = pm.response.json();
if (pm.response.code >= 200 && pm.response.code < 300) {
    pm.collectionVariables.unset("tek_acess_token");
    pm.collectionVariables.set("tek_acess_token", response.token_Acesso);
    console.log("Token adicionado com sucesso!");
} else {
    console.log("Falha ao logar conta, o token não foi recuperado");
}"""
    story.append(
        KeepTogether(
            [
                Paragraph("Script Pós-Resposta Configurado no Postman (Tests / After Response)", st["h2"]),
                code_block(auth_script_js, st["code"]),
            ]
        )
    )
    story.append(Spacer(1, 8))

    # ================= PAGE 3 =================
    bi_meta_data = [
        ["Propriedade no BI / Postman", "Valor Configurado"],
        ["Descrição (<font name='Courier'>DESCRICAO_APIDIN</font>)", "[TEK] [DESCRICAO_DA_FUNCIONALIDADE]"],
        ["Código Tek-System (<font name='Courier'>CODIGOTEKSYSTEM_APIDIN</font>)", "<font name='Courier'>[CODIGO_XML_DO_COMPONENTE]</font>"],
        ["Autor (<font name='Courier'>AUTOR_APIDIN</font>)", "TEK-SYSTEM"],
        ["Método HTTP (<font name='Courier'>METODOHTTP_APIDIN</font>)", "<b>POST</b>"],
        ["Grupo / Recurso", "Grupo: <font name='Courier'>[GRUPO]</font> | Recurso: <font name='Courier'>[RECURSO]</font>"],
        ["URL Completa (<font name='Courier'>Path</font>)", "<font name='Courier'>http://[IP_OU_DOMINIO]:[PORTA]/apidyn/[GRUPO]/[RECURSO]</font>"],
        ["Pública / Requer Autenticação", "Pública: <font name='Courier'>S</font> | Requer Autenticação: <font name='Courier'>S</font> (Bearer Token)"],
        ["Header de Autenticação", "<font name='Courier'>Authorization: Bearer {{tek_acess_token}}</font>"],
        ["Direcionamento (<font name='Courier'>DIRECIONAMENTO_APIDIN</font>)", "<font name='Courier'>[UNIT_DELPHI].[METODO_PASCAL]</font>"],
        ["Tipo de Conteúdo de Retorno", "<font name='Courier'>application/json</font> (Registra Log: <font name='Courier'>S</font>)"],
        ["Origem / Instalação", "Instalação prévia obrigatória via <b>Marketplace Tek-System</b>"],
        ["Liberação de Usuários", "Usuário da integração deve estar vinculado na aba <b>Usuários Autorizados</b> da API Dinâmica"],
        ["Servidor / Infraestrutura", "Serviço <b>TekServer Horse</b> com porta ([PORTA]) e IP externo liberados"],
    ]
    story.append(
        KeepTogether(
            [
                Paragraph("3. Rota 2 — [TITULO_FUNCIONALIDADE] (/apidyn/[GRUPO]/[RECURSO])", st["h1"]),
                HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#CBD5E1"), spaceAfter=5),
                Paragraph(
                    "Endpoint dinâmico configurado no módulo de BI (<font name='Courier'>GeradorRelatorioMC</font>). "
                    "[DESCRICAO_DO_OBJETIVO_DA_ROTA].",
                    st["body"],
                ),
                Paragraph("Especificação Técnica e Metadados no BI (Cadastro de APIs Dinâmicas)", st["h2"]),
                styled_table(bi_meta_data, [65 * mm, 109 * mm], st["th"], st["td"]),
            ]
        )
    )
    story.append(Spacer(1, 5))

    api_req_json = """{
  "campo_identificador": "VALOR_EXEMPLO",
  "numero_documento": 12345,
  "ativo": true
}"""
    story.append(
        KeepTogether(
            [
                Paragraph("Exemplo de Body da Requisição (JSON)", st["h2"]),
                code_block(api_req_json, st["code"]),
            ]
        )
    )
    story.append(Spacer(1, 5))

    api_in_data = [
        ["Campo", "Tipo", "Obrigatório", "Descrição"],
        ["<font name='Courier'>campo_identificador</font>", "<font name='Courier'>string</font>", "Sim", "Identificador único do registro ou documento."],
        ["<font name='Courier'>numero_documento</font>", "<font name='Courier'>integer</font>", "Sim", "Número do documento/pedido no sistema."],
        ["<font name='Courier'>ativo</font>", "<font name='Courier'>boolean</font>", "Não", "Indicador de status (opcional)."],
    ]
    story.append(
        KeepTogether(
            [
                Paragraph("Parâmetros de Entrada no Body", st["h2"]),
                styled_table(api_in_data, [35 * mm, 24 * mm, 24 * mm, 91 * mm], st["th"], st["td"]),
            ]
        )
    )
    story.append(Spacer(1, 8))

    # ================= PAGE 4 =================
    api_resp_json = """{
  "status": "sucesso",
  "codigo_registro": 98765,
  "mensagem": "Operação realizada com sucesso",
  "data_processamento": "2026-11-17T12:00:00"
}"""
    story.append(
        KeepTogether(
            [
                Paragraph("Exemplo de Retorno (200 OK — application/json)", st["h2"]),
                code_block(api_resp_json, st["code"]),
            ]
        )
    )
    story.append(Spacer(1, 5))

    api_out_data = [
        ["Campo", "Tipo", "Descrição"],
        ["<font name='Courier'>status</font>", "<font name='Courier'>string</font>", "Status da execução da operação (sucesso ou erro)."],
        ["<font name='Courier'>codigo_registro</font>", "<font name='Courier'>integer</font>", "Código identificador do registro no ERP."],
        ["<font name='Courier'>mensagem</font>", "<font name='Courier'>string</font>", "Mensagem de retorno da regra de negócio."],
        ["<font name='Courier'>data_processamento</font>", "<font name='Courier'>string (ISO 8601)</font>", "Data e hora em que a requisição foi processada pelo TekServer Horse."],
    ]
    story.append(
        KeepTogether(
            [
                Paragraph("Estrutura dos Campos de Retorno", st["h2"]),
                styled_table(api_out_data, [38 * mm, 38 * mm, 98 * mm], st["th"], st["td"]),
            ]
        )
    )
    story.append(Spacer(1, 8))

    story.append(
        KeepTogether(
            [
                Paragraph("4. Exemplos Práticos de Chamada (cURL)", st["h1"]),
                HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#CBD5E1"), spaceAfter=5),
                Paragraph("Passo 1 — Autenticar e obter o token JWT:", st["h2"]),
                code_block(
                    """curl --request POST "http://[IP_OU_DOMINIO]:[PORTA]/auth" \\
  --header "Content-Type: application/json" \\
  --data '{
    "Sistema": 1,
    "Token": "{{token_usuario}}",
    "consumidor": "{{consumidor}}"
  }'""",
                    st["code"],
                ),
                Spacer(1, 5),
                Paragraph("Passo 2 — Executar a Rota Dinâmica no TekServer Horse:", st["h2"]),
                code_block(
                    """curl --request POST "http://[IP_OU_DOMINIO]:[PORTA]/apidyn/[GRUPO]/[RECURSO]" \\
  --header "Authorization: Bearer {{tek_acess_token}}" \\
  --header "Content-Type: application/json" \\
  --data '{
    "campo_identificador": "VALOR_EXEMPLO",
    "numero_documento": 12345,
    "ativo": true
  }'""",
                    st["code"],
                ),
            ]
        )
    )

    doc.build(story, onFirstPage=canvas_callback, onLaterPages=canvas_callback)
    print(f"PDF modelo gerado com sucesso em: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gerador de PDF Modelo Padrão Tek-System")
    parser.add_argument(
        "--output",
        default=os.path.join(BASE_DIR, "templates", "Modelo_Documentacao_API_Template.pdf"),
        help="Caminho do PDF de saída",
    )
    parser.add_argument("--timbrado", default=DEFAULT_TIMBRADO, help="Caminho da imagem PNG de timbrado")
    parser.add_argument("--sem-timbrado", action="store_true", help="Gera sem timbrado de fundo")
    args = parser.parse_args()

    build_template_pdf(args.output, use_timbrado=(not args.sem_timbrado))
