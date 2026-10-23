# Tek-System API Documenter & Reverse-Engineering Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Google Antigravity](https://img.shields.io/badge/AI_Agent-Google_Antigravity-4285F4.svg)](https://deepmind.google)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://www.python.org/)
[![PowerShell 5.1+](https://img.shields.io/badge/PowerShell-5.1%2B-blue.svg)](https://microsoft.com/powershell)

Skill oficial para o **Google Antigravity** projetada para automatizar a engenharia reversa, descoberta não-intrusiva de parâmetros e contratos de APIs no **Tek-System ERP / BI**, compilando documentações técnicas completas em **Markdown** e **PDF Corporativo Diagramado** com os **timbrados oficiais da Tek-System**.

---

## 🚀 Funcionalidades Principais

- 🔍 **Varredura não-intrusiva no Postman Desktop**:
  Lê diretamente os arquivos LevelDB (`.ldb` e `.log` em IndexedDB e Local Storage) do Postman ativo sem requerer o fechamento do aplicativo, extraindo variáveis de ambiente/coleção (`url`, `consumidor`, `token_usuario`, `tek_acess_token`) e endpoints `/auth` e `/apidyn/...`.

- ⚡ **Inspeção de Memória do TekServer (64-bit)**:
  Varre a memória do processo `TekServer.exe` ou `GeradorRelatorioMC.exe` via Win32 API (`VirtualQueryEx`, `ReadProcessMemory`), decodificando tabelas XML DataSnap (`GR_APIS_DINAMICAS`) para capturar unidades Pascal, métodos, descrições e schemas JSON de envio e retorno.

- 📄 **Timbrados Oficiais da Tek-System Integrados**:
  Incorpora o pacote institucional de timbrados da empresa (cabeçalhos em onda dupla azul-marinho e vinho, logo institucional Tek-System e rodapés coordenados), com margens seguras e paginação contínua.

- 📊 **Documentação Completa de Integração**:
  Gera especificações prontas para envio a parceiros (ex: SSW, Marketplaces, Transportadoras), com diagrama de sequência em Mermaid, tabelas de credenciais, schemas campo a campo e chamadas cURL para terminal.

---

## 📂 Estrutura do Repositório

```text
skill-api-documenter/
├── SKILL.md                          # Instruções da skill, regras e runbook para o agente
├── README.md                         # Documentação do projeto
├── .gitignore
├── assets/
│   └── timbrados/                    # Pacote oficial de timbrados institucionais Tek-System
│       ├── timbrado_default.png      # Onda dupla corporativa azul-marinho/vinho com logo (Padrão)
│       ├── timbrado_tek_onda_dupla.png
│       ├── timbrado_tek_onda_dupla_marca_dagua.png
│       ├── timbrado_tek_onda.png
│       ├── timbrado_tek_onda_marca_dagua.png
│       ├── timbrado_tek_quadrado.png
│       ├── timbrado_tek_quadrado_marca_dagua.png
│       └── timbrado_tek_rodape.png
└── scripts/
    ├── extract_postman.ps1           # Extrator LevelDB do Postman (variáveis e requisições)
    ├── inspect_tekserver.ps1         # Scanner de memória 64-bit para DataSnap XML no TekServer
    └── gerar_pdf_template.py         # Gerador de PDF em ReportLab com timbrados e paginação
```

---

## 🛠️ Scripts Utilitários Inclusos

### 1. Extração do Postman Desktop (`extract_postman.ps1`)
Varre as coleções e abas do Postman para recuperar parâmetros e rotas:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/extract_postman.ps1 -SearchFilter "ssw" -ExportJson "postman_extraido.json"
```

### 2. Inspeção de Memória do TekServer (`inspect_tekserver.ps1`)
Lê em tempo real os metadados cadastrados nas APIs Dinâmicas do BI/TekServer:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/inspect_tekserver.ps1 -SearchKeyword "confirmar_entrega" -ExportJson "apis_tek.json"
```

### 3. Gerador de PDF com Timbrado Oficial (`gerar_pdf_template.py`)
Gera PDFs com o cabeçalho e rodapé oficial da Tek-System:
```bash
python scripts/gerar_pdf_template.py --output "Documentacao_Tecnica.pdf"
```

---

## 📥 Como Instalar no Google Antigravity

### Instalação Global (Recomendada)
Clone este repositório no diretório de skills globais do usuário:

```bash
git clone https://github.com/ThiagoFPires/skill-api-documenter.git "%USERPROFILE%\.agents\skills\tek-api-documenter"
```

### Instalação em um Projeto Específico
Clone dentro da pasta `.agents/skills/` da sua workspace:

```bash
git clone https://github.com/ThiagoFPires/skill-api-documenter.git ".agents/skills/tek-api-documenter"
```

---

## 📦 Pré-requisitos

- **Windows 10 / 11** ou **Windows Server**
- **PowerShell 5.1+**
- **Python 3.8+** com o pacote `reportlab`:
  ```bash
  pip install reportlab
  ```

---

## 💡 Exemplos de Prompts no Antigravity

Após instalar a skill, utilize o assistente em linguagem natural:

- *"Execute a descoberta no meu Postman e documente a rota do SSW que está aberta."*
- *"Inspecione a memória do TekServer para documentar a API de confirmação de entrega de OC em PDF timbrado."*
- *"Gere o PDF da integração da rota do Mercado Livre com o timbrado corporativo da Tek-System."*

---

## 👤 Autor e Contato

- **Thiago Pires**
- GitHub: [@ThiagoFPires](https://github.com/ThiagoFPires)
- E-mail: [contato.thiagofreitasp@gmail.com](mailto:contato.thiagofreitasp@gmail.com)
