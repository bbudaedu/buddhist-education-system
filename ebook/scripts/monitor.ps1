# Website Monitoring CLI Wrapper
# Usage: ./monitor.ps1 [command] [options]

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

python website_monitoring_cli.py @args
