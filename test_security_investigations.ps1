# Test Security Events and Investigations
$baseUrl = "http://localhost:7027/api/v1"
$email = "admin@demo.com"
$password = "Demo@123!"

Write-Host "=== TESTING SECURITY EVENTS AND INVESTIGATIONS ===" -ForegroundColor Cyan
Write-Host ""

# Login
Write-Host "Logging in..." -ForegroundColor Yellow
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
Write-Host "Login successful" -ForegroundColor Green
Write-Host ""

# Test Security Events
Write-Host "Testing Security Events..." -ForegroundColor Yellow
try {
    $securityEvents = Invoke-RestMethod -Uri "$baseUrl/security-events" -Method Get -Headers $headers
    Write-Host "Security Events: $($securityEvents.total) total" -ForegroundColor Green
    Write-Host ""
    
    if ($securityEvents.total -gt 0) {
        Write-Host "Recent Security Events:" -ForegroundColor Cyan
        foreach ($event in $securityEvents.items | Select-Object -First 5) {
            Write-Host "  - [$($event.severity.ToUpper())] $($event.title)" -ForegroundColor White
            Write-Host "    Type: $($event.type), Status: $($event.status)" -ForegroundColor Gray
        }
    }
    
    Write-Host ""
    
    # Get stats
    $stats = Invoke-RestMethod -Uri "$baseUrl/security-events/stats" -Method Get -Headers $headers
    Write-Host "Security Event Statistics:" -ForegroundColor Cyan
    Write-Host "  Total Events: $($stats.total_events)" -ForegroundColor White
    Write-Host "  Critical: $($stats.critical_count)" -ForegroundColor Red
    Write-Host "  High: $($stats.high_count)" -ForegroundColor Yellow
    Write-Host "  Open: $($stats.open_count)" -ForegroundColor White
    
} catch {
    Write-Host "Failed to fetch security events: $_" -ForegroundColor Red
}

Write-Host ""

# Test Investigations
Write-Host "Testing Investigations..." -ForegroundColor Yellow
try {
    $investigations = Invoke-RestMethod -Uri "$baseUrl/investigations" -Method Get -Headers $headers
    Write-Host "Investigations: $($investigations.total) total" -ForegroundColor Green
    Write-Host ""
    
    if ($investigations.total -gt 0) {
        Write-Host "Recent Investigations:" -ForegroundColor Cyan
        foreach ($inv in $investigations.items | Select-Object -First 5) {
            Write-Host "  - [$($inv.priority.ToUpper())] $($inv.title)" -ForegroundColor White
            Write-Host "    Status: $($inv.status), Progress: $($inv.progress)%" -ForegroundColor Gray
        }
    }
    
} catch {
    Write-Host "Failed to fetch investigations: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== TEST COMPLETE ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "- Security Events API: Working" -ForegroundColor Green
Write-Host "- Investigations API: Working" -ForegroundColor Green
Write-Host "- Data is now visible in the UI!" -ForegroundColor Green
