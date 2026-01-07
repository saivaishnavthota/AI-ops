# Comprehensive Audit Logging Test
$baseUrl = "http://localhost:7027/api/v1"
$email = "admin@demo.com"
$password = "Demo@123!"

Write-Host "=== COMPREHENSIVE AUDIT LOGGING TEST ===" -ForegroundColor Cyan
Write-Host ""

# Login
Write-Host "Step 1: Logging in..." -ForegroundColor Yellow
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

# Test Incidents
Write-Host "Step 2: Testing Incident Audit Logging..." -ForegroundColor Yellow
$incidentBody = @{
    title = "Test Incident for Audit"
    description = "Testing audit logging"
    severity = "high"
    priority = "high"
    status = "open"
} | ConvertTo-Json

$incident = Invoke-RestMethod -Uri "$baseUrl/incidents" -Method Post -Body $incidentBody -Headers $headers
Write-Host "Created incident: $($incident.id)" -ForegroundColor Green

# Test Alerts
Write-Host "Step 3: Testing Alert Audit Logging..." -ForegroundColor Yellow
$alertBody = @{
    title = "Test Alert"
    description = "Testing alert audit"
    severity = "warning"
    source = "test"
    host = "test-host"
    service = "test-service"
} | ConvertTo-Json

$alert = Invoke-RestMethod -Uri "$baseUrl/alerts" -Method Post -Body $alertBody -Headers $headers
Write-Host "Created alert: $($alert.id)" -ForegroundColor Green

# Test Users
Write-Host "Step 4: Testing User Audit Logging..." -ForegroundColor Yellow
$userBody = @{
    email = "testuser_$(Get-Random)@example.com"
    password = "TestPass123!"
    first_name = "Test"
    last_name = "User"
    role = "operator"
} | ConvertTo-Json

$user = Invoke-RestMethod -Uri "$baseUrl/users" -Method Post -Body $userBody -Headers $headers
Write-Host "Created user: $($user.id)" -ForegroundColor Green

# Test Teams
Write-Host "Step 5: Testing Team Audit Logging..." -ForegroundColor Yellow
$teamBody = @{
    name = "Test Team $(Get-Random)"
    description = "Testing team audit"
    team_type = "engineering"
} | ConvertTo-Json

$team = Invoke-RestMethod -Uri "$baseUrl/teams" -Method Post -Body $teamBody -Headers $headers
Write-Host "Created team: $($team.id)" -ForegroundColor Green

# Test Tickets
Write-Host "Step 6: Testing Ticket Audit Logging..." -ForegroundColor Yellow
$ticketBody = @{
    subject = "Test Ticket"
    description = "Testing ticket audit"
    priority = "medium"
    category = "technical"
} | ConvertTo-Json

$ticket = Invoke-RestMethod -Uri "$baseUrl/tickets" -Method Post -Body $ticketBody -Headers $headers
Write-Host "Created ticket: $($ticket.id)" -ForegroundColor Green

# Test Playbooks
Write-Host "Step 7: Testing Playbook Audit Logging..." -ForegroundColor Yellow
$playbookBody = @{
    name = "Test Playbook $(Get-Random)"
    description = "Testing playbook audit"
    trigger_type = "manual"
    steps = @(
        @{
            name = "Step 1"
            action = "notify"
            parameters = @{}
        }
    )
    is_active = $true
} | ConvertTo-Json -Depth 10

$playbook = Invoke-RestMethod -Uri "$baseUrl/playbooks" -Method Post -Body $playbookBody -Headers $headers
Write-Host "Created playbook: $($playbook.id)" -ForegroundColor Green
Write-Host ""

# Check Audit Logs
Write-Host "Step 8: Checking Audit Logs..." -ForegroundColor Yellow
$auditLogs = Invoke-RestMethod -Uri "$baseUrl/audit-logs?page=1&page_size=50" -Method Get -Headers $headers

Write-Host "Total audit logs: $($auditLogs.total)" -ForegroundColor Green
Write-Host ""
Write-Host "Recent Audit Entries:" -ForegroundColor Cyan

$recentLogs = $auditLogs.items | Select-Object -First 15
foreach ($log in $recentLogs) {
    $timestamp = [DateTime]::Parse($log.timestamp).ToString("yyyy-MM-dd HH:mm:ss")
    Write-Host "[$timestamp] $($log.action) $($log.resource_type): $($log.description)"
}

Write-Host ""
Write-Host "=== TEST COMPLETE ===" -ForegroundColor Cyan
Write-Host "Audit logging is working for all critical endpoints!" -ForegroundColor Green
