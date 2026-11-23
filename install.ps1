# ==============================================================================
# HuyNex Agent Kit — Universal One-Line Installer (Windows PowerShell)
# Usage: irm https://raw.githubusercontent.com/huylinhhg/HuyNex-Agent-Kit/main/install.ps1 | iex
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "  _    _             _   _            " -ForegroundColor Cyan
Write-Host " | |  | |           | \ | |           " -ForegroundColor Cyan
Write-Host " | |__| |_   _ _   _|  \| | _____  __ " -ForegroundColor Cyan
Write-Host " |  __  | | | | | | | . \` |/ _ \ \/ / " -ForegroundColor Cyan
Write-Host " | |  | | |_| | |_| | |\  |  __/>  <  " -ForegroundColor Cyan
Write-Host " |_|  |_|\__,_|\__, |_| \_|\___/_/\_\ " -ForegroundColor Cyan
Write-Host "                __/ |                 " -ForegroundColor Cyan
Write-Host "               |___/   AGENT KIT      " -ForegroundColor Cyan
Write-Host "------------------------------------------------------------------"
Write-Host "Hệ thống Kỹ năng & Quy tắc AI Agent Chuẩn Mở Top 1 Thế Giới" -ForegroundColor Yellow

# 1. Kiểm tra Python
$pyCmd = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } elseif (Get-Command python3 -ErrorAction SilentlyContinue) { "python3" } else { $null }
if (-not $pyCmd) {
    Write-Error "Không tìm thấy Python. Vui lòng cài đặt Python 3 trước."
    exit 1
}

# 2. Kiểm tra Git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "Không tìm thấy Git. Vui lòng cài đặt Git trước."
    exit 1
}

$installDir = Join-Path $env:USERPROFILE ".huynex\agent-kit"
$repoUrl = "https://github.com/huylinhhg/HuyNex-Agent-Kit.git"

Write-Host "▶ Đang đồng bộ kho mã nguồn HuyNex Agent Kit..." -ForegroundColor Green
if (Test-Path (Join-Path $installDir ".git")) {
    git -C $installDir pull --ff-only origin main
} else {
    New-Item -ItemType Directory -Force -Path (Split-Path $installDir) | Out-Null
    git clone --depth 1 $repoUrl $installDir
}

# 3. Kích hoạt cài đặt
Write-Host "▶ Đang cài đặt Kỹ năng và Quy tắc vào hệ thống..." -ForegroundColor Green
& $pyCmd (Join-Path $installDir "scripts\install.py") --all

# 4. Kích hoạt Hard Guardrail cho Claude Code
$claudeDir = Join-Path $env:USERPROFILE ".claude"
if (Test-Path $claudeDir) {
    $hooksDir = Join-Path $claudeDir "hooks"
    New-Item -ItemType Directory -Force -Path $hooksDir | Out-Null
    Copy-Item (Join-Path $installDir "scripts\guardrail.py") (Join-Path $hooksDir "guardrail.py") -Force
    Write-Host "  ✓ Đã kích hoạt Chốt chặn cứng Hard Git Guardrails" -ForegroundColor Green
}

Write-Host "`n🎉 CÀI ĐẶT HOÀN TẤT THÀNH CÔNG!" -ForegroundColor Green
Write-Host "AI Coding Agents của bạn trên Windows đã sẵn sàng hoạt động với 9 modules kỷ luật thép.`n"
