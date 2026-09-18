$ErrorActionPreference = 'Stop'
$skillDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$fontSource = Join-Path $skillDir 'assets\fonts'
$fontTarget = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Fonts'
$registryPath = 'HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts'

New-Item -ItemType Directory -Force -Path $fontTarget | Out-Null
New-Item -Path $registryPath -Force | Out-Null

Get-ChildItem -LiteralPath $fontSource -File | Where-Object { $_.Extension -in '.ttf', '.otf' } | ForEach-Object {
    $destination = Join-Path $fontTarget $_.Name
    Copy-Item -LiteralPath $_.FullName -Destination $destination -Force
    $kind = if ($_.Extension -ieq '.otf') { 'OpenType' } else { 'TrueType' }
    New-ItemProperty -Path $registryPath -Name "$($_.BaseName) ($kind)" -Value $_.Name -PropertyType String -Force | Out-Null
    Write-Output "Installed $($_.Name)"
}

Write-Output 'Font files installed for the current user. Restart Photoshop before rendering.'
