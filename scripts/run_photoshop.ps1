param(
    [Parameter(Mandatory = $true)]
    [string]$Job
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$engine = Join-Path $scriptDir 'photoshop\render_suite.jsx'
$jobPath = (Resolve-Path -LiteralPath $Job).Path.Replace('\', '/')
$enginePath = (Resolve-Path -LiteralPath $engine).Path.Replace('\', '/')
$wrapper = Join-Path (Split-Path -Parent $Job) 'run-photoshop-job.jsx'

$content = @"
#target photoshop
var LIVE_POSTER_JOB_PATH = "$jobPath";
$.evalFile(new File("$enginePath"));
"@
[System.IO.File]::WriteAllText($wrapper, $content, [System.Text.UTF8Encoding]::new($false))

$photoshop = New-Object -ComObject Photoshop.Application
$photoshop.DoJavaScriptFile($wrapper)
Write-Output "Photoshop job completed: $Job"
