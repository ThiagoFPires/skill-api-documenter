---
name: tek-api-documenter
description: >-
  Use esta skill sempre que o usuário solicitar documentar, realizar engenharia reversa ou gerar PDF de integração de APIs do ERP Tek-System / BI (como SSW, marketplaces, e-commerce, transportadoras ou rotas dinâmicas personalizadas). A skill fornece scripts automatizados em PowerShell para extração não-intrusiva de parâmetros e scripts do Postman Desktop e inspeção de memória do TekServer.exe (DataSnap XML), além de template corporativo em ReportLab com os timbrados oficiais da Tek-System para gerar PDFs executivos de alto padrão.
---

# Tek-System API Documenter & Reverse-Engineering Runbook

Esta skill automatiza todo o ciclo de vida de especificação e documentação de APIs corporativas do ecossistema **Tek-System ERP / BI**:
1. **Descoberta Automatizada (Opção 1)** via scripts não-intrusivos no Postman Desktop e memória do TekServer.
2. **Engenharia Reversa de Contratos** (captura de `/auth`, tokens consumidores `REC-...`, payloads JSON de entrada e saída).
3. **Diagramação Executiva em PDF** utilizando os **timbrados oficiais da Tek-System** (cabeçalho com onda dupla azul-marinho/vinho, logo institucional e paginação automática).

---

## 1. Gatilhos de Ativação

Ative esta skill quando o usuário solicitar:
- *"Documente a rota de integração da Tek-System (ex: SSW, Mercado Livre, Magalu, transportadoras)."*
- *"Descubra os parâmetros abertos no meu Postman e no BI."*
- *"Gere uma documentação em Markdown e PDF com o timbrado da empresa."*
- *"Faça engenharia reversa do endpoint dinâmico `/apidyn/...` no TekServer."*

---

## 2. Ferramentas e Scripts Utilitários Inclusos

A pasta `scripts/` da skill conta com ferramentas prontas para execução:

| Script | Finalidade | Comando Recomendado |
|---|---|---|
| `scripts/extract_postman.ps1` | Varre os bancos LevelDB (IndexedDB e Local Storage) do Postman sem precisar fechar o aplicativo. Extrai variáveis (`url`, `consumidor`, `token_usuario`, `tek_acess_token`) e endpoints `/auth` e `/apidyn/...`. | `powershell -ExecutionPolicy Bypass -File scripts/extract_postman.ps1 -SearchFilter "ssw"` |
| `scripts/inspect_tekserver.ps1` | Scanner de memória Win32 (64-bit) que lê os metadados XML DataSnap de `TekServer.exe` ou `GeradorRelatorioMC.exe`, extraindo nome da unit, rota, observações, schemas JSON de envio e retorno. | `powershell -ExecutionPolicy Bypass -File scripts/inspect_tekserver.ps1 -SearchKeyword "confirmar_entrega"` |
| `scripts/gerar_pdf_template.py` | Motor Python ReportLab pré-configurado com a identidade visual da Tek-System, margens milimétricas para o timbrado oficial e blocos estruturados. | `python scripts/gerar_pdf_template.py --output "Documentacao.pdf"` |

---

## 3. Procedimento de Extração e Documentação

### Passo 1: Descoberta de Conexão no Postman Desktop
Execute o extrator do Postman:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts/extract_postman.ps1" -ExportJson "postman_descoberto.json"
```
O script retornará:
- **`url`**: Host base (ex: `http://170.246.146.28:8080` ou `{{url}}`).
- **`consumidor`**: Token Consumidor (padrão `REC-...`, essencial para o `/auth`).
- **`token_usuario`**: Identificador do usuário ERP autenticador.
- **`tek_acess_token`**: Exemplo de JWT emitido após login.
- **Endpoints mapeados**: Rotas ativas nas abas e coleções locais.

### Passo 2: Descoberta de Contratos Dinâmicos no TekServer
Se o usuário estiver com o cadastro da API aberto no BI (`GeradorRelatorioMC.exe`) ou executou o `TekServer.exe`:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts/inspect_tekserver.ps1" -ExportJson "apis_tek.json"
```
Campos capturados do DataSnap XML:
- **`DESCRICAO_APIDIN`**: Nome legível da funcionalidade.
- **`Path`**: Caminho relativo oficial (ex: `/apidyn/ssw/ecommerce_confirmar_entrega_oc`).
- **`METODOHTTP_APIDIN`**: Verbo HTTP (`POST`, `GET`, etc.).
- **`DIRECIONAMENTO_APIDIN`**: Handler Delphi/Pascal interno (ex: `TEK_APIECOMMERCES_ENDPOINT_CONFIRMACAO_ENTREGA.Main`).
- **`REQUER_AUTENTICACAO_APIDIN`**: Flag indicando exigência de Bearer Token.
- **`OBSERVACAO_APIDIN`**: Contratos JSON decodificados de envio e resposta.

> [!TIP]
> Caso o script retorne 0 rotas em memória, oriente o usuário a abrir a tela de **APIs Dinâmicas** no BI para carregar a tabela em memória, ou utilize os dados capturados nas requisições do Postman.

---

## 4. Padrão Visual dos Timbrados Oficiais da Tek-System

A pasta `assets/timbrados/` disponibiliza os modelos oficiais da Tek-System:

| Arquivo | Descrição |
|---|---|
| `timbrado_default.png` | **Padrão Oficial Corporativo** (Onda dupla azul-marinho e vinho com logo Tek-System superior direito e rodapé coordenado). |
| `timbrado_tek_onda_dupla.png` | Onda dupla limpa (fundo 100% branco para máxima legibilidade de código). |
| `timbrado_tek_onda_dupla_marca_dagua.png` | Onda dupla com marca d'água centralizada estilizada "TEK". |
| `timbrado_tek_onda.png` | Versão minimalista de onda simples. |
| `timbrado_tek_quadrado.png` | Layout moderno com geometrias retangulares. |

### Configuração de Margens no ReportLab:
Para evitar sobreposição com as ondas do cabeçalho e rodapé:
```python
doc = SimpleDocTemplate(
    output_path,
    pagesize=A4,
    leftMargin=18 * mm,
    rightMargin=18 * mm,
    topMargin=38 * mm,     # Respeita o logo e a onda superior (37mm)
    bottomMargin=23 * mm,  # Respeita a linha de rodapé e a onda inferior
)
```

No callback do canvas (`onFirstPage` e `onLaterPages`):
```python
canvas.drawImage(timbrado_path, 0, 0, width=A4[0], height=A4[1], preserveAspectRatio=False, mask="auto")
canvas.setFont("Helvetica", 8)
canvas.setFillColor(colors.HexColor("#475569"))
canvas.drawString(18 * mm, 13 * mm, "Tek-System Informática — Documentação Técnica de Integração API")
canvas.drawRightString(A4[0] - 18 * mm, 13 * mm, f"Página {doc.page}")
canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
canvas.line(18 * mm, 17 * mm, A4[0] - 18 * mm, 17 * mm)
```

### Paleta de Cores Institucional:
- **Azul Marinho Principal**: `#002060` (Banners, cabeçalhos de tabelas e títulos H1)
- **Vinho / Burgundy Tek**: `#800000` (Barras de destaque, subtítulos H2 e separadores)
- **Fundo de Blocos de Código**: `#0F172A` (Borda: `#334155`, Texto: `#F8FAFC`)
- **Caixa de Token Consumidor (Callout)**: Fundo `#EFF6FF`, Borda Esquerda `#1E40AF`
- **Tabelas de Parâmetros**: Cabeçalho `#002060`, linhas alternadas `#FFFFFF` e `#F8FAFC`

---

## 5. Estrutura Padrão da Documentação Gerada

Toda documentação técnica (tanto em Markdown quanto em PDF) deve conter:
1. **Banner Executivo**: Título da integração, sistema de origem e escopo.
2. **Fluxo de Sequência Mermaid**:
   - Integrador solicita token em `POST /auth`.
   - TekServer autentica consumidor e usuário e responde com JWT.
   - Integrador chama `POST /apidyn/...` enviando `Authorization: Bearer <token>`.
3. **Quadro de Conexão e Credenciais**: Tabela de variáveis (`Host`, `Porta`, `Token Consumidor`, `Token Usuário`).
4. **Endpoint 1: Autenticação (`/auth`)**:
   - Método, URL completa, Headers (`Content-Type: application/json`).
   - Body JSON e tabela explicativa dos campos (`Sistema`, `Token`, `consumidor`).
   - Retorno JSON (`token_Acesso`, expiração).
   - Script de pré-requisição / pós-resposta do Postman.
5. **Endpoint 2: Rota Dinâmica (`/apidyn/...`)**:
   - Metadados do ERP (Handler, recurso, grupo).
   - Headers (`Authorization: Bearer {{tek_acess_token}}`).
   - Body JSON de envio com tabela de tipos e descrições campo a campo.
   - Retorno `200 OK` detalhado com status de negócio (ex: número da entrega, chave NF-e).
6. **Exemplos Prontos em cURL**: Comandos funcionais prontos para terminal.
