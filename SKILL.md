---
name: tek-api-documenter
description: >-
  Use esta skill sempre que o usuário solicitar documentar, realizar engenharia reversa ou gerar PDF de integração de APIs do ERP Tek-System / BI (como SSW, marketplaces, e-commerce, ou rotas personalizadas). A skill orienta a extração dos metadados das telas abertas no BI (GeradorRelatorioMC / TekServer) e das collections e abas ativas do Postman, gerando especificações técnicas completas em Markdown e PDFs diagramados.
---

# Tek-System API Documenter & Reverse-Engineering Runbook

Esta skill automatiza a descoberta, extração de contratos e geração de documentação técnica (Markdown e PDF executivo) para qualquer rota ou integração da **Tek-System**.

## 1. Gatilhos de Ativação

Ative este procedimento quando o usuário pedir para:
- Documentar uma rota de API do Tek-System (ex.: `/auth`, `/apidyn/...`).
- Realizar engenharia reversa das requisições abertas no **Postman** e no **BI / TekServer**.
- Gerar documentação técnica com PDF diagramado para clientes/integradores (ex.: SSW, Marketplaces, Transportadoras, Parceiros).

---

## 2. Parâmetros Necessários

Identifique com o usuário ou descubra no ambiente local:
- **Nome da Integração / Parceiro**: (ex.: SSW, Magazine Luiza, Mercado Livre, etc.)
- **Rota / Endpoint Alvo**: (ex.: `/apidyn/ssw/ecommerce_confirmar_entrega_oc`)
- **Rota de Autenticação**: Geralmente `/auth`
- **Servidor / Host e Porta**: (ex.: `http://170.246.146.28:8080` ou parametrizado como `{{url}}`)
- **Token Consumidor**: (ex.: `REC-F65C8928-9278-4B32-9A4F-1062FA97` ou arquivos na Área de Trabalho/Postman)
- **Token do Usuário**: Token do cadastro de usuário do ERP (`{{token_usuario}}`)

---

## 3. Procedimento Passo a Passo para o Agente

### Passo 1: Extração de Dados do Postman Desktop
1. O banco local do Postman fica em:
   `%APPDATA%\Postman\Partitions\fac55237-396e-4760-88a1-2f9754621525\IndexedDB\https_desktop.postman.com_0.indexeddb.leveldb`
2. Abra os arquivos `.log` e `.ldb` mais recentes usando `[System.IO.FileShare]::ReadWrite` para evitar conflito de processo travado.
3. Busque por:
   - Variáveis da collection: `url`, `consumidor`, `token_usuario`, `tek_acess_token`.
   - Configuração da rota `/auth` (body JSON contendo `Sistema`, `Token`, `consumidor`).
   - Scripts de teste (`afterResponse` / `pm.test`) que extraem o JWT retornado em `token_Acesso`.

### Passo 2: Extração de Metadados da API Dinâmica no BI
1. Verifique os processos ativos `TekServer.exe` e `GeradorRelatorioMC.exe`.
2. Quando a tela do BI está aberta no registro da API Dinâmica, o `TekServer.exe` armazena em memória o XML do DataSnap.
3. Faça uma varredura de memória no processo `TekServer.exe` usando `OpenProcess`, `VirtualQueryEx` e `ReadProcessMemory` buscando pelo nome do recurso (ex.: `ecommerce_confirmar_entrega_oc` ou `APIDIN`).
4. Extraia os campos:
   - `DESCRICAO_APIDIN`: Nome legível da funcionalidade.
   - `CODIGOTEKSYSTEM_APIDIN`: Código interno do componente XML.
   - `GRUPO_APIDIN` e `RECURSO_APIDIN`: Composição do path final (`/apidyn/[grupo]/[recurso]`).
   - `METODOHTTP_APIDIN`: Método (`POST`, `GET`, etc.).
   - `DIRECIONAMENTO_APIDIN`: Unit e método Pascal interno (ex.: `TEK_APIECOMMERCES_ENDPOINT_CONFIRMACAO_ENTREGA.Main`).
   - `OBSERVACAO_APIDIN`: Texto contendo os schemas de exemplo de entrada e retorno.

### Passo 3: Geração da Documentação Técnica (Markdown / Artefato)
Elabore uma documentação estruturada contendo:
- **Fluxograma Mermaid**: Sequência visual entre Integrador -> `/auth` -> `/apidyn/...`.
- **Tabela de Conexão**: Variáveis, URLs, Tokens e descrições.
- **Seção Rota 1 (Auth)**: Método, URL, Headers, Body JSON, Schema de Retorno (`token_Acesso`), Script do Postman.
- **Seção Rota 2 (API Dinâmica)**: Metadados do BI, Método, Headers (`Authorization: Bearer`), Body JSON com tabela de campos, Payload de Retorno `200 OK` com tabela explicativa de cada atributo.
- **Exemplos cURL**: Comandos prontos para terminal.

### Passo 4: Compilação do PDF Profissional
1. Crie um script Python utilizando a biblioteca `reportlab`.
2. Configure:
   - Margens e cabeçalho institucional da Tek-System com rodapé e paginação automática (`Página X`).
   - Caixa de destaque (*callout*) para o **Token Consumidor**.
   - Tabelas estilizadas com larguras de coluna ajustadas para evitar quebras inadequadas de texto.
   - Blocos de código com fundo escuro (`#0F172A`) e fonte monospace para JSON e cURL.
   - Uso de `KeepTogether` em cabeçalhos e blocos filhos para evitar páginas órfãs.
3. Execute o script Python e valide a renderização das páginas do PDF gerado.
