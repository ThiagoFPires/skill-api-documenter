# Tek-System API Documenter — Antigravity Skill

Skill oficial para o **Google Antigravity** projetada para automatizar a engenharia reversa, extração de contratos e geração de documentações técnicas de integração (em Markdown e PDF corporativo diagramado) para APIs e endpoints do **Tek-System ERP / BI** (como SSW, marketplaces, e-commerce, transportadoras e rotas customizadas).

---

## 🚀 O que esta Skill faz?

1. **Varredura no Postman Desktop**: Inspeciona as collections e abas ativas para extrair parâmetros de envio, variáveis de ambiente/collection (`{{url}}`, `{{consumidor}}`, `{{token_usuario}}`, `{{tek_acess_token}}`) e scripts de teste de captura de token.
2. **Inspeção de Memória do BI / TekServer**: Acessa os metadados cadastrais da tela de APIs Dinâmicas no BI (`GeradorRelatorioMC.exe` / `TekServer.exe`), capturando nome da unit, direcionamento interno, payloads de envio e exemplos de retorno JSON.
3. **Geração de Documentação Completa**:
   - Diagrama de fluxo de sequência em **Mermaid**.
   - Tabela explicativa de credenciais e variáveis.
   - Especificação das rotas (`/auth` e rotas dinâmicas `/apidyn/...`).
   - Contratos JSON com descrição campo a campo.
   - Comandos práticos em **cURL**.
4. **Compilação de PDF Executivo**: Gera um documento PDF profissional com paginação automática, cabeçalho institucional, blocos de código formatados e destaque para tokens de autenticação.

---

## 📂 Estrutura da Skill

```text
skill-api-documenter/
├── SKILL.md                          # Instruções da skill, gatilhos e procedimentos para a IA
├── scripts/
│   └── gerar_pdf_template.py         # Template em Python (ReportLab) para compilação do PDF
├── .gitignore
└── README.md
```

---

## 📥 Como Instalar

### Opção 1: Instalação Global no Antigravity (Recomendado)
Clone ou copie a pasta desta skill para o seu diretório global de skills do usuário:

```bash
git clone https://github.com/ThiagoFPires/skill-api-documenter.git "%USERPROFILE%\.agents\skills\tek-api-documenter"
```

### Opção 2: Instalação em um Repositório de Projeto
Caso queira compartilhar a skill com a equipe em um repositório Git, clone-a na pasta `.agents/skills/`:

```bash
git clone https://github.com/ThiagoFPires/skill-api-documenter.git ".agents/skills/tek-api-documenter"
```

---

## 🔧 Pré-requisitos

Para que o assistente gere os arquivos PDF diagramados, é necessário ter o Python e o pacote `reportlab` instalados:

```bash
pip install reportlab
```

---

## 💡 Como Usar

Com a skill instalada, basta abrir o Antigravity e solicitar a documentação de forma natural. Exemplos:

- *"Documente a rota de confirmação de entrega do SSW que está aberta no meu Postman e no BI."*
- *"Gere o PDF de integração da rota do Mercado Livre acessando o TekServer."*
- *"Use a skill tek-api-documenter para mapear os endpoints abertos na máquina."*

---

## 👤 Autor

- **Thiago Pires**
- GitHub: [@ThiagoFPires](https://github.com/ThiagoFPires)
- Contato: contato.thiagofreitasp@gmail.com
