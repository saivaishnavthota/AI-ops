# Show Resolved Tickets in Audit Log
$baseUrl = "http://localhost:7027/api/v1"
$email = "admin@demo.com"
$password = "Demo@123!"

Write-Host "=== RESOLVED TICKETS IN AUDIT LOG ===" -ForegroundColor Cyan
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

# Get all audit logs
Write-Host "Fetching audit logs..." -ForegroundColor Yellow
$auditLogs = Invoke-RestMethod -Uri "$baseUrl/audit-logs?page=1&page_size=100" -Method Get -Headers $headers
Write-Host "Total audit logs: $($auditLogs.total)" -ForegroundColor Green
Write-Host ""

# Filter for resolved tickets
$resolvedTickets = $auditLogs.items | Where-Object { 
    $_.resource_type -eq "ticket" -and $_.action -eq "resolve"
}

Write-Host "=== RESOLVED TICKETS ===" -ForegroundColor Cyan
Write-Host "Found $($resolvedTickets.Count) resolved ticket entries" -ForegroundColor Green
Write-Host ""

if ($resolvedTickets.Count -eq 0) {
    Write-Host "No resolved tickets found in current audit log page." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Creating and resolving a ticket to demonstrate..." -ForegroundColor Yellow
    Write-Host ""
    
    # Create a ticket
    Write-Host "Creating a test ticket..." -ForegroundColor Yellow
    $ticketBody = @{
        subject = "Test Ticket for Resolution Demo"
        description = "This ticket will be resolved to demonstrate audit logging"
        priority = "high"
        category = "technical"
    } | ConvertTo-Json
    
    $ticket = Invoke-RestMethod -Uri "$baseUrl/tickets" -Method Post -Body $ticketBody -Headers $headers
    $ticketId = $ticket.id
    Write-Host "Created ticket: $ticketId" -ForegroundColor Green
    Write-Host "  Subject: $($ticket.subject)" -ForegroundColor White
    Write-Host ""
    
    # Resolve the ticket
    Write-Host "Resolving the ticket..." -ForegroundColor Yellow
    $resolveBody = @{
        title = "Solution for Test Ticket"
        content = "This is the resolution for the test ticket"
        tags = @("resolved", "test")
    } | ConvertTo-Json
    
    $resolvedTicket = Invoke-RestMethod -Uri "$baseUrl/tickets/$ticketId/resolve" -Method Put -Body $resolveBody -Headers $headers
    Write-Host "Ticket resolved successfully!" -ForegroundColor Green
    Write-Host "  Status: $($resolvedTicket.status)" -ForegroundColor White
    Write-Host ""
    
    # Wait for audit log
    Start-Sleep -Seconds 2
    
    # Fetch audit logs again
    Write-Host "Fetching updated audit logs..." -ForegroundColor Yellow
    $auditLogs = Invoke-RestMethod -Uri "$baseUrl/audit-logs?page=1&page_size=100" -Method Get -Headers $headers
    $resolvedTickets = $auditLogs.items | Where-Object { 
        $_.resource_type -eq "ticket" -and $_.action -eq "resolve"
    }
    Write-Host ""
}

# Display resolved tickets
if ($resolvedTickets.Count -gt 0) {
    Write-Host "=== RESOLVED TICKET AUDIT ENTRIES ===" -ForegroundColor Cyan
    Write-Host ""
    
    $counter = 1
    foreach ($log in $resolvedTickets) {
        Write-Host "Entry #$counter" -ForegroundColor Yellow
        Write-Host "  Resource Type: $($log.resource_type)" -ForegroundColor White
        Write-Host "  Action: $($log.action)" -ForegroundColor Green
        Write-Host "  Resource ID: $($log.resource_id)" -ForegroundColor White
        Write-Host "  Resource Name: $($log.resource_name)" -ForegroundColor Cyan
        Write-Host "  Description: $($log.description)" -ForegroundColor White
        Write-Host "  User Email: $($log.user_email)" -ForegroundColor White
        Write-Host "  IP Address: $($log.ip_address)" -ForegroundColor White
        Write-Host "  Status: $($log.status)" -ForegroundColor Green
        Write-Host "  Timestamp: $($log.timestamp)" -ForegroundColor White
        Write-Host ""
        $counter++
    }
    
    Write-Host "=== SUMMARY ===" -ForegroundColor Cyan
    Write-Host "Total resolved tickets in audit log: $($resolvedTickets.Count)" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== ALL TICKET ACTIONS IN AUDIT LOG ===" -ForegroundColor Cyan
Write-Host ""

# Show all ticket-related actions
$ticketActions = $auditLogs.items | Where-Object { $_.resource_type -eq "ticket" } | Group-Object -Property action

Write-Host "Ticket Actions Summary:" -ForegroundColor Yellow
foreach ($group in $ticketActions) {
    $color = switch ($group.Name) {
        "create" { "Green" }
        "update" { "Yellow" }
        "delete" { "Red" }
        "resolve" { "Magenta" }
        "assign" { "Cyan" }
        default { "White" }
    }
    Write-Host "  $($group.Name): $($group.Count) entries" -ForegroundColor $color
}

Write-Host ""
Write-Host "Recent Ticket Actions:" -ForegroundColor Yellow
$recentTicketActions = $auditLogs.items | Where-Object { $_.resource_type -eq "ticket" } | Select-Object -First 10

foreach ($log in $recentTicketActions) {
    $color = switch ($log.action) {
        "create" { "Green" }
        "update" { "Yellow" }
        "delete" { "Red" }
        "resolve" { "Magenta" }
        "assign" { "Cyan" }
        default { "White" }
    }
    Write-Host "  [$($log.action.ToUpper())]" -ForegroundColor $color -NoNewline
    Write-Host " $($log.description)"
}

Write-Host ""
Write-Host "=== END ===" -ForegroundColor Cyan
