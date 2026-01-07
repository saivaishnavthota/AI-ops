# Test Login Audit Logging
Write-Host "Testing Login Audit Logging" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:7027/api/v1"

# Step 1: Login to create audit log
Write-Host "Step 1: Logging in to create audit log entry..." -ForegroundColor Yellow
$loginBody = @{
    email = "admin@demo.com"
    password = "Demo@123!"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.access_token
    Write-Host "Login successful!" -ForegroundColor Green
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
Start-Sleep -Seconds 2

# Step 2: Check audit logs for login entry
Write-Host "Step 2: Checking audit logs for login entry..." -ForegroundColor Yellow
try {
    $logsResponse = Invoke-RestMethod -Uri "$baseUrl/audit-logs?page=1&page_size=5" -Method Get -Headers $headers
    
    Write-Host "Recent audit logs:" -ForegroundColor Cyan
    Write-Host ""
    
    $loginFound = $false
    foreach ($log in $logsResponse.items) {
        if ($log.action -eq "login") {
            $loginFound = $true
            Write-Host "  LOGIN ENTRY FOUND!" -ForegroundColor Green
            Write-Host "  Action: $($log.action)" -ForegroundColor White
            Write-Host "  User: $($log.user_name) ($($log.user_email))" -ForegroundColor White
            Write-Host "  Status: $($log.status)" -ForegroundColor White
            Write-Host "  IP: $($log.ip_address)" -ForegroundColor White
            Write-Host "  Time: $($log.created_at)" -ForegroundColor White
            Write-Host "  Description: $($log.description)" -ForegroundColor White
            Write-Host ""
            break
        }
    }
    
    if (-not $loginFound) {
        Write-Host "  No login entry found in recent logs" -ForegroundColor Yellow
        Write-Host "  Showing all recent entries:" -ForegroundColor Gray
        foreach ($log in $logsResponse.items) {
            Write-Host "    - $($log.action) by $($log.user_name) at $($log.created_at)" -ForegroundColor Gray
        }
    }
}
catch {
    Write-Host "Failed to fetch audit logs: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Step 3: Test failed login
Write-Host "Step 3: Testing failed login audit logging..." -ForegroundColor Yellow
$badLoginBody = @{
    email = "admin@demo.com"
    password = "WrongPassword123!"
} | ConvertTo-Json

try {
    $badLoginResponse = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method Post -Body $badLoginBody -ContentType "application/json"
    Write-Host "Unexpected: Bad login succeeded" -ForegroundColor Red
}
catch {
    Write-Host "Failed login attempt (expected)" -ForegroundColor Green
}

Write-Host ""
Start-Sleep -Seconds 2

# Step 4: Check for failed login entry
Write-Host "Step 4: Checking for failed login entry..." -ForegroundColor Yellow
try {
    $logsResponse = Invoke-RestMethod -Uri "$baseUrl/audit-logs?page=1&page_size=5" -Method Get -Headers $headers
    
    $failedLoginFound = $false
    foreach ($log in $logsResponse.items) {
        if ($log.action -eq "login_failed") {
            $failedLoginFound = $true
            Write-Host "  FAILED LOGIN ENTRY FOUND!" -ForegroundColor Green
            Write-Host "  Action: $($log.action)" -ForegroundColor White
            Write-Host "  Email: $($log.resource_id)" -ForegroundColor White
            Write-Host "  Status: $($log.status)" -ForegroundColor White
            Write-Host "  IP: $($log.ip_address)" -ForegroundColor White
            Write-Host "  Error: $($log.error_message)" -ForegroundColor White
            Write-Host ""
            break
        }
    }
    
    if (-not $failedLoginFound) {
        Write-Host "  No failed login entry found" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Failed to fetch audit logs: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================" -ForegroundColor Cyan
Write-Host "Test completed!" -ForegroundColor Cyan
Write-Host ""
Write-Host "To view in UI:" -ForegroundColor Yellow
Write-Host "1. Open http://localhost:7026" -ForegroundColor White
Write-Host "2. Login with admin@demo.com / Demo@123!" -ForegroundColor White
Write-Host "3. Go to Settings > Audit Log" -ForegroundColor White
Write-Host "4. Look for login and login_failed entries" -ForegroundColor White
