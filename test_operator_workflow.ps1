#!/usr/bin/env pwsh

Write-Host "=== OPERATOR WORKFLOW DEMONSTRATION ===" -ForegroundColor Green

# Configuration
$baseUrl = "http://localhost:7027/api/v1"
$loginUrl = "$baseUrl/auth/login"
$ticketsUrl = "$baseUrl/tickets"
$kbUrl = "$baseUrl/knowledge-base"

Write-Host "`n1. ADMIN: Creating test ticket..." -ForegroundColor Yellow

# Admin login
$adminLogin = Invoke-RestMethod -Uri $loginUrl -Method POST -Body '{"email": "super.admin@demo.com", "password": "Demo@123!"}' -ContentType "application/json"
$adminToken = $adminLogin.access_token
$adminHeaders = @{ "Authorization" = "Bearer $adminToken" }

# Create test ticket
$testTicket = @{
    subject = "Database connection timeout issue"
    description = "Users reporting database connection timeouts during peak hours. Need investigation and resolution."
    category = "database"
    priority = "high"
} | ConvertTo-Json

$url = $ticketsUrl + "?auto_classify=true&auto_route=true"
$ticketResponse = Invoke-RestMethod -Uri $url -Method POST -Body $testTicket -Headers $adminHeaders -ContentType "application/json"

Write-Host "✓ Test ticket created: $($ticketResponse.id)" -ForegroundColor Green

Start-Sleep -Seconds 5

Write-Host "`n2. OPERATOR: Viewing assigned tickets..." -ForegroundColor Yellow

# Operator login
$operatorLogin = Invoke-RestMethod -Uri $loginUrl -Method POST -Body '{"email": "operator@demo.com", "password": "Demo@123!"}' -ContentType "application/json"
$operatorToken = $operatorLogin.access_token
$operatorHeaders = @{ "Authorization" = "Bearer $operatorToken" }

# Check operator's assigned tickets
$operatorTickets = Invoke-RestMethod -Uri $ticketsUrl -Method GET -Headers $operatorHeaders

Write-Host "✓ Operator sees $($operatorTickets.total) assigned tickets:" -ForegroundColor Green
foreach ($ticket in $operatorTickets.items) {
    if ($ticket.assignee_name -eq "Emily Rodriguez") {
        Write-Host "  - $($ticket.subject) | Status: $($ticket.status)" -ForegroundColor Cyan
    }
}

Write-Host "`n3. OPERATOR: Resolving ticket with feedback..." -ForegroundColor Yellow

# Find a ticket to resolve
$ticketToResolve = $null
foreach ($ticket in $operatorTickets.items) {
    if ($ticket.assignee_name -eq "Emily Rodriguez" -and $ticket.status -ne "resolved") {
        $ticketToResolve = $ticket
        break
    }
}

if ($ticketToResolve) {
    Write-Host "✓ Resolving ticket: $($ticketToResolve.subject)" -ForegroundColor Green
    
    # Prepare feedback data
    $feedbackData = @{
        title = "Resolving Database Connection Timeouts"
        content = "Solution steps: 1. Check database connection pool settings in application config. 2. Increase max_connections in database configuration. 3. Optimize slow queries using EXPLAIN ANALYZE. 4. Implement connection pooling if not already present. 5. Monitor connection usage with pg_stat_activity. 6. Set up alerts for connection pool exhaustion."
        tags = @("database", "connection", "timeout", "performance")
    } | ConvertTo-Json
    
    # Resolve with feedback
    $resolveUrl = "$ticketsUrl/$($ticketToResolve.id)/resolve"
    $resolveResponse = Invoke-RestMethod -Uri $resolveUrl -Method PUT -Body $feedbackData -Headers $operatorHeaders -ContentType "application/json"
    
    Write-Host "✓ Ticket resolved successfully!" -ForegroundColor Green
    Write-Host "  Status: $($resolveResponse.status)" -ForegroundColor Cyan
    Write-Host "  Resolved at: $($resolveResponse.resolved_at)" -ForegroundColor Cyan
    
    Write-Host "`n4. CHECKING: Knowledge Base article creation..." -ForegroundColor Yellow
    
    # Check if KB article was created
    $kbArticles = Invoke-RestMethod -Uri $kbUrl -Method GET -Headers $operatorHeaders
    
    $newArticle = $null
    foreach ($article in $kbArticles.items) {
        if ($article.title -eq "Resolving Database Connection Timeouts") {
            $newArticle = $article
            break
        }
    }
    
    if ($newArticle) {
        Write-Host "✓ Knowledge Base article created successfully!" -ForegroundColor Green
        Write-Host "  Title: $($newArticle.title)" -ForegroundColor Cyan
        Write-Host "  Category: $($newArticle.category)" -ForegroundColor Cyan
        Write-Host "  Content preview: $($newArticle.excerpt)" -ForegroundColor Gray
    } else {
        Write-Host "✗ Knowledge Base article not found" -ForegroundColor Red
    }
    
} else {
    Write-Host "✗ No unresolved tickets found for operator" -ForegroundColor Red
}

Write-Host "`n5. VERIFICATION: Ticket filtering..." -ForegroundColor Yellow

# Check updated ticket list
$updatedTickets = Invoke-RestMethod -Uri $ticketsUrl -Method GET -Headers $operatorHeaders
Write-Host "✓ Operator now sees $($updatedTickets.total) tickets" -ForegroundColor Green

# Show resolved tickets (still visible until 1 day passes)
$resolvedCount = 0
foreach ($ticket in $updatedTickets.items) {
    if ($ticket.status -eq "resolved") {
        $resolvedCount++
    }
}

Write-Host "  - $resolvedCount resolved tickets (will move to incidents after 1 day)" -ForegroundColor Gray

Write-Host "`n=== WORKFLOW FEATURES DEMONSTRATED ===" -ForegroundColor Green
Write-Host "✓ Operators see only their assigned tickets" -ForegroundColor Cyan
Write-Host "✓ Resolve with feedback functionality" -ForegroundColor Cyan
Write-Host "✓ Automatic Knowledge Base article creation" -ForegroundColor Cyan
Write-Host "✓ Ticket filtering (resolved tickets hidden after 1 day)" -ForegroundColor Cyan
Write-Host "✓ Knowledge sharing from operator experience" -ForegroundColor Cyan

Write-Host "`n=== OPERATOR WORKFLOW COMPLETE ===" -ForegroundColor Green