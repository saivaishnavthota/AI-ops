# View Recent Audit Logs
$baseUrl = "http://localhost:7027/api/v1"
$email = "admin@demo.com"
$password = "Demo@123!"

Write-Host "=== AUDIT LOGS VIEWER ===" -ForegroundColor Cyan
Write-Host ""

# Login
$loginBody = @{
    email = $email
    password = $password
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
$token = $loginResponse.access_token
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# Get audit logs
$auditLogs = Invoke-RestMethod -Uri "$baseUrl/audit-logs?page=1&page_size=100" -Method Get -Headers $headers

Write-Host "Total Audit Logs: $($auditLogs.total)" -ForegroundColor Green
Write-Host ""

# Group by action
Write-Host "=== AUDIT LOGS BY ACTION ===" -ForegroundColor Cyan
$actionGroups = $auditLogs.items | Group-Object -Property action | Sort-Object Count -Descending
foreach ($group in $actionGroups) {
    $color = switch ($group.Name) {
        "create" { "Green" }
        "update" { "Yellow" }
        "delete" { "Red" }
        "login" { "Cyan" }
        "logout" { "Magenta" }
        "login_failed" { "DarkRed" }
        "acknowledge" { "Blue" }
        "resolve" { "Green" }
        "close" { "DarkGray" }
        "activate" { "Green" }
        "deactivate" { "Red" }
        "execute" { "Blue" }
        "assign" { "Yellow" }
        default { "White" }
    }
    Write-Host "$($group.Name.PadRight(15)): $($group.Count) entries" -ForegroundColor $color
}

Write-Host ""

# Group by resource type
Write-Host "=== AUDIT LOGS BY RESOURCE TYPE ===" -ForegroundColor Cyan
$resourceGroups = $auditLogs.items | Group-Object -Property resource_type | Sort-Object Count -Descending
foreach ($group in $resourceGroups) {
    Write-Host "$($group.Name.PadRight(15)): $($group.Count) entries" -ForegroundColor White
}

Write-Host ""

# Show recent 20 entries
Write-Host "=== RECENT 20 AUDIT LOG ENTRIES ===" -ForegroundColor Cyan
Write-Host ""

$recentLogs = $auditLogs.items | Select-Object -First 20
foreach ($log in $recentLogs) {
    $color = switch ($log.action) {
        "create" { "Green" }
        "update" { "Yellow" }
        "delete" { "Red" }
        "login" { "Cyan" }
        "logout" { "Magenta" }
        "login_failed" { "DarkRed" }
        "acknowledge" { "Blue" }
        "resolve" { "Green" }
        "close" { "DarkGray" }
        "activate" { "Green" }
        "deactivate" { "Red" }
        "execute" { "Blue" }
        "assign" { "Yellow" }
        default { "White" }
    }
    
    Write-Host "$($log.action.ToUpper().PadRight(15))" -ForegroundColor $color -NoNewline
    Write-Host " $($log.resource_type.PadRight(12))" -NoNewline
    Write-Host " $($log.description)"
}

Write-Host ""
Write-Host "=== END OF AUDIT LOGS ===" -ForegroundColor Cyan
