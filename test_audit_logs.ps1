# Test Audit Logs API
Write-Host "Testing Audit Logs API" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:7027/api/v1"

# Step 1: Login
Write-Host "Step 1: Logging in..." -ForegroundColor Yellow
$loginBody = @{
    email = "admin@demo.com"
    password = "Demo@123!"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.access_token
    Write-Host "Logged in successfully" -ForegroundColor Green
}
catch {
    Write-Host "Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

Write-Host ""

# Step 2: Get Audit Logs
Write-Host "Step 2: Fetching audit logs..." -ForegroundColor Yellow
try {
    $logsResponse = Invoke-RestMethod -Uri "$baseUrl/audit-logs?page=1&page_size=10" -Method Get -Headers $headers
    
    Write-Host "Total audit logs: $($logsResponse.total)" -ForegroundColor Green
    Write-Host "Current page: $($logsResponse.page)" -ForegroundColor Green
    Write-Host "Logs on this page: $($logsResponse.items.Count)" -ForegroundColor Green
    Write-Host ""
    
    if ($logsResponse.items.Count -gt 0) {
        Write-Host "Recent Audit Logs:" -ForegroundColor Cyan
        foreach ($log in $logsResponse.items | Select-Object -First 5) {
            Write-Host ""
            Write-Host "  Action: $($log.action)" -ForegroundColor White
            Write-Host "  User: $($log.user_name) ($($log.user_email))" -ForegroundColor Gray
            Write-Host "  Resource: $($log.resource_type)" -ForegroundColor Gray
            Write-Host "  Status: $($log.status)" -ForegroundColor Gray
            Write-Host "  Time: $($log.created_at)" -ForegroundColor Gray
            Write-Host "  Description: $($log.description)" -ForegroundColor Gray
        }
    }
    else {
        Write-Host "No audit logs found" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Failed to fetch audit logs: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Step 3: Get Audit Log Stats
Write-Host "Step 3: Fetching audit log statistics..." -ForegroundColor Yellow
try {
    $statsResponse = Invoke-RestMethod -Uri "$baseUrl/audit-logs/stats" -Method Get -Headers $headers
    
    Write-Host "Statistics:" -ForegroundColor Cyan
    Write-Host "  Total Actions: $($statsResponse.total_actions)" -ForegroundColor White
    Write-Host "  Actions Today: $($statsResponse.actions_today)" -ForegroundColor White
    Write-Host "  Actions This Week: $($statsResponse.actions_this_week)" -ForegroundColor White
    Write-Host ""
    
    if ($statsResponse.by_action) {
        Write-Host "  Top Actions:" -ForegroundColor Cyan
        $statsResponse.by_action.PSObject.Properties | Sort-Object Value -Descending | Select-Object -First 5 | ForEach-Object {
            Write-Host "    $($_.Name): $($_.Value)" -ForegroundColor Gray
        }
    }
}
catch {
    Write-Host "Failed to fetch stats: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "======================" -ForegroundColor Cyan
Write-Host "Test completed!" -ForegroundColor Cyan
