<#
.SYNOPSIS
    Realiza varredura de memória no TekServer / GeradorRelatorioMC para extrair metadados e contratos de APIs Dinâmicas.
.DESCRIPTION
    Utiliza as APIs Win32 (VirtualQueryEx e ReadProcessMemory) em arquitetura 64-bit para localizar
    em tempo de execução as definições XML do DataSnap (tabela GR_APIS_DINAMICAS) carregadas pelo ERP/BI da Tek-System.
.PARAMETER ProcessName
    Nome do processo a inspecionar (padrão: "TekServer"). Também suporta "GeradorRelatorioMC".
.PARAMETER SearchKeyword
    Palavra-chave opcional para filtrar os resultados (ex: "ssw", "confirmar_entrega", "ecommerce").
.PARAMETER ExportJson
    Caminho para salvar o resultado em formato JSON estruturado.
.PARAMETER ExportXml
    Caminho para salvar os blocos XML brutos extraídos da memória.
.PARAMETER Quiet
    Se informado, suprime as mensagens visuais no console.
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\inspect_tekserver.ps1 -SearchKeyword "confirmar_entrega" -ExportJson "apis_tek.json"
#>

[CmdletBinding()]
param (
    [string]$ProcessName = "TekServer",
    [string]$SearchKeyword = "",
    [string]$ExportJson = "",
    [string]$ExportXml = "",
    [switch]$Quiet
)

function Write-Info([string]$msg) {
    if (-not $Quiet) {
        Write-Host "[TekServer-Inspector] $msg" -ForegroundColor Cyan
    }
}

function Write-Success([string]$msg) {
    if (-not $Quiet) {
        Write-Host "[TekServer-Inspector] $msg" -ForegroundColor Green
    }
}

function Write-WarnMsg([string]$msg) {
    if (-not $Quiet) {
        Write-Host "[TekServer-Inspector] AVISO: $msg" -ForegroundColor Yellow
    }
}

# Compila o scanner Win32 em C#
$csharpSource = @"
using System;
using System.Runtime.InteropServices;
using System.Text;
using System.Collections.Generic;

public class TekMemEngine {
    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern IntPtr OpenProcess(uint dwDesiredAccess, bool bInheritHandle, int dwProcessId);

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern bool ReadProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, int dwSize, out int lpNumberOfBytesRead);

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern IntPtr VirtualQueryEx(IntPtr hProcess, IntPtr lpAddress, out MEMORY_BASIC_INFORMATION64 lpBuffer, IntPtr dwLength);

    [DllImport("kernel32.dll")]
    public static extern bool CloseHandle(IntPtr hObject);

    [StructLayout(LayoutKind.Sequential)]
    public struct MEMORY_BASIC_INFORMATION64 {
        public ulong BaseAddress;
        public ulong AllocationBase;
        public uint AllocationProtect;
        public uint __alignment1;
        public ulong RegionSize;
        public uint State;
        public uint Protect;
        public uint Type;
        public uint __alignment2;
    }

    public static List<string> ScanForApiXml(int pid) {
        var results = new List<string>();
        IntPtr hProc = OpenProcess(0x0410, false, pid); // PROCESS_QUERY_INFORMATION | PROCESS_VM_READ
        if (hProc == IntPtr.Zero) return results;

        ulong addr = 0;
        MEMORY_BASIC_INFORMATION64 mbi;
        IntPtr mbiSize = new IntPtr(Marshal.SizeOf(typeof(MEMORY_BASIC_INFORMATION64)));

        while (VirtualQueryEx(hProc, new IntPtr((long)addr), out mbi, mbiSize) != IntPtr.Zero) {
            ulong regionSize = mbi.RegionSize;
            if (mbi.State == 0x1000 && (mbi.Protect == 0x04 || mbi.Protect == 0x02 || mbi.Protect == 0x20 || mbi.Protect == 0x40)) {
                if (regionSize > 0 && regionSize < 60 * 1024 * 1024) {
                    byte[] buf = new byte[regionSize];
                    int bytesRead;
                    if (ReadProcessMemory(hProc, new IntPtr((long)mbi.BaseAddress), buf, (int)regionSize, out bytesRead)) {
                        string s = Encoding.ASCII.GetString(buf, 0, bytesRead);
                        int idx = s.IndexOf("<ROW AUTOINC_APIDIN=", StringComparison.OrdinalIgnoreCase);
                        while (idx >= 0) {
                            int endIdx = s.IndexOf("</ROW>", idx, StringComparison.OrdinalIgnoreCase);
                            if (endIdx < 0) {
                                endIdx = s.IndexOf("/>", idx, StringComparison.OrdinalIgnoreCase);
                                if (endIdx >= 0) endIdx += 2;
                            } else {
                                endIdx += 6;
                            }

                            if (endIdx > idx) {
                                string rowXml = s.Substring(idx, endIdx - idx);
                                if (!results.Contains(rowXml)) {
                                    results.Add(rowXml);
                                }
                            }
                            idx = s.IndexOf("<ROW AUTOINC_APIDIN=", idx + 20, StringComparison.OrdinalIgnoreCase);
                        }
                    }
                }
            }
            ulong next = mbi.BaseAddress + regionSize;
            if (next <= addr) break;
            addr = next;
        }
        CloseHandle(hProc);
        return results;
    }
}
"@

if (-not ([System.Management.Automation.PSTypeName]'TekMemEngine').Type) {
    Add-Type -TypeDefinition $csharpSource -ErrorAction Stop
}

# Localiza os processos candidatos
$targets = Get-Process | Where-Object { $_.ProcessName -match "^($ProcessName|GeradorRelatorioMC)$" }

if (-not $targets) {
    Write-WarnMsg "Nenhum processo '$ProcessName' ou 'GeradorRelatorioMC' está em execução no momento."
    Write-Info "Dica: Abra o TekServer.exe ou a tela do BI (GeradorRelatorioMC.exe) com o cadastro da API aberto."
    return
}

$rawXmlList = [System.Collections.Generic.List[string]]::new()

foreach ($proc in $targets) {
    Write-Info "Inspecionando processo $($proc.ProcessName) (PID: $($proc.Id))..."
    try {
        $extracted = [TekMemEngine]::ScanForApiXml($proc.Id)
        if ($extracted -and $extracted.Count -gt 0) {
            Write-Success "Encontradas $($extracted.Count) definições XML em $($proc.ProcessName) (PID: $($proc.Id))"
            foreach ($item in $extracted) {
                if (-not $rawXmlList.Contains($item)) {
                    $rawXmlList.Add($item)
                }
            }
        }
    } catch {
        Write-WarnMsg "Erro ao escanear processo $($proc.Id): $_"
    }
}

if ($rawXmlList.Count -eq 0) {
    Write-WarnMsg "Nenhuma tabela DataSnap XML de APIs Dinâmicas encontrada na memória ativa."
    Write-Info "Explicação Técnica: Os metadados XML são carregados na memória do TekServer / BI quando:"
    Write-Info "  1. A tela de 'APIs Dinâmicas' está aberta no GeradorRelatorioMC;"
    Write-Info "  2. Ou uma requisição recente foi atendida pelo TekServer.exe."
    Write-Info "Para capturar, abra o registro no BI e execute este script novamente."
    return
}

# Decodificador de entidades HTML e extrator de atributos
function Decode-Html([string]$str) {
    if (-not $str) { return "" }
    $q = [char]34
    $s = $str.Replace("&quot;", $q).Replace("&amp;", "&").Replace("&lt;", "<").Replace("&gt;", ">")
    $s = $s.Replace("&#xA;", "`n").Replace("&#xD;", "`r")
    return $s
}

$parsedApis = [System.Collections.Generic.List[PSCustomObject]]::new()

foreach ($xml in $rawXmlList) {
    $getAttr = {
        param([string]$attrName)
        $q = [char]34
        $pattern = $attrName + "=" + $q + "([^" + $q + "]*)" + $q
        $m = [regex]::Match($xml, $pattern)
        if ($m.Success) { return $m.Groups[1].Value } else { return "" }
    }

    $path = & $getAttr "Path"
    $descricao = & $getAttr "DESCRICAO_APIDIN"
    $metodo = & $getAttr "METODOHTTP_APIDIN"
    $grupo = & $getAttr "GRUPO_APIDIN"
    $recurso = & $getAttr "RECURSO_APIDIN"
    $direcionamento = & $getAttr "DIRECIONAMENTO_APIDIN"
    $observacaoRaw = & $getAttr "OBSERVACAO_APIDIN"
    $publica = & $getAttr "PUBLICA_APIDIN"
    $requerAuth = & $getAttr "REQUER_AUTENTICACAO_APIDIN"
    $autoInc = & $getAttr "AUTOINC_APIDIN"
    $tipoRetorno = & $getAttr "TIPO_CONTEUDO_RETORNO_APIDIN"

    if (-not $path -and $grupo -and $recurso) {
        $path = "/apidyn/$grupo/$recurso"
    }

    # Aplica filtro se fornecido
    if ($SearchKeyword) {
        $contentToTest = "$path $descricao $recurso $grupo $direcionamento"
        if ($contentToTest -notmatch [regex]::Escape($SearchKeyword)) {
            continue
        }
    }

    $observacaoDecoded = Decode-Html $observacaoRaw

    # Tenta separar schemas de exemplo contidos na observação
    $inputJson = ""
    $outputJson = ""

    if ($observacaoDecoded -match '(?s)Exemplo.*?Body.*?:\s*(\{.*?\})\s*Exemplo de Retorno.*?:\s*(\{.*\})') {
        $inputJson = $matches[1].Trim()
        $outputJson = $matches[2].Trim()
    } elseif ($observacaoDecoded -match '(?s)(\{.*?\})') {
        $inputJson = $matches[1].Trim()
    }

    $parsedApis.Add([PSCustomObject]@{
        Id                  = $autoInc
        Descricao           = $descricao
        Metodo              = $metodo
        Path                = $path
        Grupo               = $grupo
        Recurso             = $recurso
        Direcionamento      = $direcionamento
        Publica             = ($publica -eq "S")
        RequerAutenticacao  = ($requerAuth -eq "S")
        TipoConteudoRetorno = $tipoRetorno
        Observacao          = $observacaoDecoded
        SchemaEnvio         = $inputJson
        SchemaRetorno       = $outputJson
    })
}

if (-not $Quiet) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor DarkGray
    Write-Host "       APIS DINÂMICAS EXTRAÍDAS DA MEMÓRIA DO TEKSERVER      " -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "Total de rotas encontradas: $($parsedApis.Count)" -ForegroundColor Yellow
    Write-Host ""

    foreach ($api in $parsedApis) {
        Write-Host "------------------------------------------------------------" -ForegroundColor DarkGray
        Write-Host "  Endpoint:  " -ForegroundColor Gray -NoNewline
        Write-Host "[$($api.Metodo)] $($api.Path)" -ForegroundColor Cyan
        Write-Host "  Descrição: " -ForegroundColor Gray -NoNewline
        Write-Host "$($api.Descricao)" -ForegroundColor White
        Write-Host "  Handler:   " -ForegroundColor Gray -NoNewline
        Write-Host "$($api.Direcionamento)" -ForegroundColor Magenta
        Write-Host "  Auth Req:  " -ForegroundColor Gray -NoNewline
        Write-Host "$($api.RequerAutenticacao)" -ForegroundColor Yellow
        if ($api.SchemaEnvio) {
            Write-Host "  Payload Envio Detectado: Sim" -ForegroundColor Green
        }
        if ($api.SchemaRetorno) {
            Write-Host "  Payload Retorno Detectado: Sim" -ForegroundColor Green
        }
    }
    Write-Host "------------------------------------------------------------" -ForegroundColor DarkGray
    Write-Host ""
}

if ($ExportJson) {
    $fullJsonPath = [System.IO.Path]::GetFullPath($ExportJson)
    $json = $parsedApis | ConvertTo-Json -Depth 6
    [System.IO.File]::WriteAllText($fullJsonPath, $json, [System.Text.Encoding]::UTF8)
    Write-Success "Metadados de APIs exportados para: $fullJsonPath"
}

if ($ExportXml) {
    $fullXmlPath = [System.IO.Path]::GetFullPath($ExportXml)
    $xmlContent = "<APIS_DINAMICAS>`n" + ($rawXmlList -join "`n") + "`n</APIS_DINAMICAS>"
    [System.IO.File]::WriteAllText($fullXmlPath, $xmlContent, [System.Text.Encoding]::UTF8)
    Write-Success "XML bruto das APIs exportado para: $fullXmlPath"
}

return $parsedApis