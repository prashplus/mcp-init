# MCP Tutorial Launcher for Windows
# PowerShell script to easily run different MCP demonstration modes

Write-Host "=" -NoNewline
Write-Host ("=" * 58)
Write-Host "  MCP (Model Context Protocol) Tutorial"
Write-Host "=" -NoNewline  
Write-Host ("=" * 58)
Write-Host ""

function Show-Menu {
    Write-Host "Choose a demonstration mode:"
    Write-Host "1. Basic MCP Demo (server + client)"
    Write-Host "2. Interactive MCP Client"
    Write-Host "3. Ollama + MCP Integration Demo"
    Write-Host "4. Interactive Ollama Chat with MCP"
    Write-Host "5. Exit"
    Write-Host ""
}

function Start-MCPDemo {
    param([string]$Mode)
    
    try {
        switch ($Mode) {
            "1" {
                Write-Host "`nRunning basic MCP demo..." -ForegroundColor Green
                Set-Location client
                python client.py
                Set-Location ..
            }
            "2" {
                Write-Host "`nStarting interactive MCP client..." -ForegroundColor Green
                Write-Host "(Type 'help' for commands, 'quit' to exit)" -ForegroundColor Yellow
                Set-Location client
                python client.py interactive
                Set-Location ..
            }
            "3" {
                Write-Host "`nRunning Ollama + MCP integration demo..." -ForegroundColor Green
                Set-Location client
                python ollama_integration.py
                Set-Location ..
            }
            "4" {
                Write-Host "`nStarting interactive Ollama chat with MCP..." -ForegroundColor Green
                Write-Host "(Type 'quit' to exit, 'model <name>' to change model)" -ForegroundColor Yellow
                Set-Location client
                python ollama_integration.py chat
                Set-Location ..
            }
        }
    }
    catch {
        Write-Host "Error: $_" -ForegroundColor Red
    }
}

# Main loop
do {
    Show-Menu
    $choice = Read-Host "Enter your choice (1-5)"
    
    if ($choice -match "^[1-4]$") {
        Start-MCPDemo -Mode $choice
        Write-Host ""
    }
    elseif ($choice -eq "5") {
        Write-Host "Goodbye!" -ForegroundColor Green
        break
    }
    else {
        Write-Host "Invalid choice. Please enter 1-5." -ForegroundColor Red
        Write-Host ""
    }
} while ($true)
