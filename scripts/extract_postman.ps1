<#
.SYNOPSIS
    Extrai variáveis, requisições, payloads e scripts de autenticação das collections do Postman Desktop.
.DESCRIPTION
    Realiza varredura não-intrusiva nos bancos LevelDB (IndexedDB e Local Storage) do Postman
    Desktop em %APPDATA%\Postman, sem necessitar que o Postman seja fechado.
.PARAMETER SearchFilter
    Filtro de busca opcional por texto na URL ou nome da requisição (ex: "ssw", "auth", "confirmar_entrega").
.PARAMETER ExportJson
    Caminho para salvar o resultado estruturado em arquivo JSON.
.PARAMETER Quiet
    Se informado, não imprime mensagens detalhadas no console, apenas retorna os dados.
.EXAMPLE
    .\extract_postman.ps1 -SearchFilter "ssw" -ExportJson "postman_extraido.json"
#>

[CmdletBinding()]
param (
    [string]$SearchFilter = "",
    [string]$ExportJson = "",
    [switch]$Quiet
)

function Write-Info([string]$msg) {
    if (-not $Quiet) {
        Write-Host "[Postman-Extractor] $msg" -ForegroundColor Cyan
    }
}

function Write-Success([string]$msg) {
    if (-not $Quiet) {
        Write-Host "[Postman-Extractor] $msg" -ForegroundColor Green
    }
}

function Write-WarnMsg([string]$msg) {
    if (-not $Quiet) {
        Write-Host "[Postman-Extractor] AVISO: $msg" -ForegroundColor Yellow
    }
}

$postmanBasePath = Join-Path $env:APPDATA "Postman"
if (-not (Test-Path $postmanBasePath)) {
    Write-WarnMsg "Diretório de dados do Postman não encontrado em: $postmanBasePath"
    return
}

Write-Info "Procurando bancos de dados LevelDB do Postman..."

# Localiza diretórios IndexedDB e Local Storage
$candidateDirs = Get-ChildItem -Path $postmanBasePath -Recurse -Directory -ErrorAction SilentlyContinue | Where-Object {
    $_.FullName -match "indexeddb\.leveldb" -or ($_.FullName -match "Local Storage" -and $_.Name -eq "leveldb")
}

if (-not $candidateDirs) {
    Write-WarnMsg "Nenhum diretório LevelDB encontrado no Postman."
    return
}

$extractedVariables = @{}
$extractedEndpoints = [System.Collections.Generic.List[PSCustomObject]]::new()
$discoveredHosts = [System.Collections.Generic.HashSet[string]]::new()

foreach ($dir in $candidateDirs) {
    $dbFiles = Get-ChildItem -Path $dir.FullName -File -ErrorAction SilentlyContinue | Where-Object {
        $_.Extension -in '.ldb', '.log'
    } | Sort-Object LastWriteTime -Descending

    foreach ($file in $dbFiles) {
        try {
            $stream = [System.IO.File]::Open($file.FullName, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
            $bytes = New-Object byte[] $stream.Length
            [void]$stream.Read($bytes, 0, $bytes.Length)
            $stream.Close()
            $text = [System.Text.Encoding]::ASCII.GetString($bytes)

            # 1. Extração de Variáveis (url, consumidor, token_usuario, tek_acess_token)
            # Padrão: key" ... value" ou "key":"...", "value":"..."
            $varMatches = [regex]::Matches($text, '(?:"key"|key)[^A-Za-z0-9_-]{1,10}([A-Za-z0-9_]+)[^A-Za-z0-9_-]{1,10}(?:"value"|value)[^A-Za-z0-9_-]{1,10}"?([^"\r\n\x00-\x1F]{1,120})"?')
            foreach ($m in $varMatches) {
                $k = $m.Groups[1].Value.Trim()
                $v = $m.Groups[2].Value.Trim()
                if ($k -match "^(url|consumidor|token_usuario|tek_acess_token|token|base_url|baseUrl|host|port)$") {
                    if ($v.Length -gt 0 -and $v -notmatch "^\{\{.*\}\}$" -and $v -notmatch "^(disabledF|secretF)" -and -not $extractedVariables.ContainsKey($k)) {
                        $extractedVariables[$k] = $v
                    }
                }
            }

            # 2. Extração de URLs e Métodos
            # Busca URLs com padrões http://, https:// ou {{url}}
            $urlMatches = [regex]::Matches($text, '(?:"url"|url)[^A-Za-z0-9_{}]{1,15}((?:https?://|\{\{url\}\})[A-Za-z0-9_{}:/\.\-\?&=%]+)')
            foreach ($m in $urlMatches) {
                $rawUrl = $m.Groups[1].Value.Trim()

                # Limpeza de prefixos ou sufixos residuais da serialização do Chromium
                $rawUrl = $rawUrl -replace "^[a-zA-Z0-9_]{1,3}https?://", "http://"
                $rawUrl = $rawUrl -replace "^[a-zA-Z0-9_]{1,3}\{\{url\}\}", "{{url}}"

                if ($rawUrl -match "^(https?://[^/\s]+)") {
                    [void]$discoveredHosts.Add($matches[1])
                }

                if ($SearchFilter -and ($rawUrl -notmatch [regex]::Escape($SearchFilter) -and $rawUrl -notmatch "auth")) {
                    continue
                }

                # Procura método HTTP próximo (GET, POST, PUT, DELETE)
                $method = "POST"
                $subIdx = [Math]::Max(0, $m.Index - 250)
                $context = $text.Substring($subIdx, [Math]::Min(500, $text.Length - $subIdx))
                if ($context -match '"(GET|POST|PUT|DELETE|PATCH)"') {
                    $method = $matches[1]
                } elseif ($context -match 'descriptor"[\s\x00-\x1F]*"?(GET|POST|PUT|DELETE|PATCH)"?') {
                    $method = $matches[1]
                }

                # Identifica se já registramos esta rota para evitar duplicações
                $alreadyExists = $extractedEndpoints | Where-Object { $_.Url -eq $rawUrl -and $_.Method -eq $method }
                if (-not $alreadyExists) {
                    $extractedEndpoints.Add([PSCustomObject]@{
                        Method = $method
                        Url    = $rawUrl
                        SourceFile = $file.Name
                    })
                }
            }

            # 3. Busca específica por Token Consumidor (ex: REC-...)
            $recMatch = [regex]::Match($text, 'REC-[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4,12}')
            if ($recMatch.Success) {
                $extractedVariables["consumidor"] = $recMatch.Value
            }

        } catch {
            # Arquivo travado exclusivamente ou erro transitório
        }
    }
}

# Organiza os resultados

# Fallback para token consumidor na Área de Trabalho
$desktopPath = [Environment]::GetFolderPath('Desktop')
$tokenFiles = Get-ChildItem -Path $desktopPath -Filter "*token*.txt" -ErrorAction SilentlyContinue
foreach ($tf in $tokenFiles) {
    try {
        $tfContent = [System.IO.File]::ReadAllText($tf.FullName)
        $recM = [regex]::Match($tfContent, 'REC-[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4,12}')
        if ($recM.Success -and (-not $extractedVariables.ContainsKey('consumidor') -or $extractedVariables['consumidor'] -notmatch '^REC-')) {
            $extractedVariables['consumidor'] = $recM.Value
            Write-Info "Token consumidor recuperado de arquivo na Área de Trabalho ($($tf.Name)): $($recM.Value)"
        }
    } catch { }
}

$result = [PSCustomObject]@{
    Variables = $extractedVariables
    DiscoveredHosts = @($discoveredHosts)
    Endpoints = @($extractedEndpoints | Sort-Object Method, Url)
}

if (-not $Quiet) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor DarkGray
    Write-Host "          RESULTADOS DA EXTRAÇÃO DO POSTMAN DESKTOP         " -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "--- Variáveis Identificadas ---" -ForegroundColor Yellow
    if ($extractedVariables.Count -gt 0) {
        $extractedVariables.GetEnumerator() | Sort-Object Name | ForEach-Object {
            Write-Host "  $($_.Key) = $($_.Value)" -ForegroundColor White
        }
    } else {
        Write-Host "  Nenhuma variável de collection encontrada diretamente." -ForegroundColor Gray
    }

    Write-Host ""
    Write-Host "--- Hosts / Servidores Descobertos ---" -ForegroundColor Yellow
    if ($discoveredHosts.Count -gt 0) {
        $discoveredHosts | ForEach-Object {
            Write-Host "  $($_)" -ForegroundColor White
        }
    } else {
        Write-Host "  Nenhum host absoluto detectado." -ForegroundColor Gray
    }

    Write-Host ""
    Write-Host "--- Endpoints Localizados ($($result.Endpoints.Count)) ---" -ForegroundColor Yellow
    if ($result.Endpoints.Count -gt 0) {
        $result.Endpoints | ForEach-Object {
            $mColor = switch ($_.Method) {
                "GET"  { "Green" }
                "POST" { "Yellow" }
                "PUT"  { "Cyan" }
                default { "Magenta" }
            }
            Write-Host "  [$($_.Method)] " -ForegroundColor $mColor -NoNewline
            Write-Host "$($_.Url) " -ForegroundColor White -NoNewline
            Write-Host "($($_.SourceFile))" -ForegroundColor DarkGray
        }
    } else {
        Write-Host "  Nenhum endpoint correspondente aos filtros foi encontrado." -ForegroundColor Gray
    }
    Write-Host ""
}

if ($ExportJson) {
    $json = $result | ConvertTo-Json -Depth 5
    $fullExportPath = [System.IO.Path]::GetFullPath($ExportJson)
    [System.IO.File]::WriteAllText($fullExportPath, $json, [System.Text.Encoding]::UTF8)
    Write-Success "Dados exportados com sucesso para: $fullExportPath"
}

return $result