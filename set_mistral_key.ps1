# PowerShell script to securely set your Mistral API key
# Usage: .\set_mistral_key.ps1 YOUR_ACTUAL_API_KEY

param(
    [Parameter(Mandatory=$true)]
    [string]$ApiKey
)

if (-not $ApiKey) {
    Write-Host "Usage: .\set_mistral_key.ps1 <your-mistral-api-key>" -ForegroundColor Red
    Write-Host "Example: .\set_mistral_key.ps1 a8zh3krcxy8FHvP2RmzxJDO5YWcwVg0I" -ForegroundColor Yellow
    exit 1
}

# Check if .env file exists
if (Test-Path ".env") {
    # Read the .env file content
    $content = Get-Content ".env" -Raw
    
    # Replace the placeholder with the actual key
    $updatedContent = $content -replace "MISTRAL_API_KEY=your-mistral-api-key-here", "MISTRAL_API_KEY=$ApiKey"
    
    # Write back to .env file
    Set-Content ".env" $updatedContent -NoNewline
    
    Write-Host "✅ Mistral API key updated in .env file" -ForegroundColor Green
    Write-Host "🔒 Your API key is now securely stored in the .env file" -ForegroundColor Blue
    Write-Host "⚠️  Remember: Never commit .env files to version control!" -ForegroundColor Yellow
} else {
    Write-Host "❌ .env file not found. Please copy .env.example to .env first." -ForegroundColor Red
    exit 1
}