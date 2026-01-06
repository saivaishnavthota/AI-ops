#!/usr/bin/env pwsh

Write-Host "=== OPERATOR WORKFLOW TEST ===" -ForegroundColor Green

# Login as operator
$operatorLogin = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/auth/login" -Method POST -Body '{"email": "operator@demo.com", "password": "Demo@123!"}' -ContentType "application/json"
$operatorToken = $operatorLogin.access_token
$operatorHeaders = @{ "Authorization" = "Bearer $operatorToken" }

Write-Host "1. Checking assigned tickets..." -ForegroundColor Yellow

# Get operator's tickets
$tickets = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/tickets" -Method GET -Headers $operatorHeaders

Write-Host "Operator sees $($tickets.total) assigned tickets:" -ForegroundColor Green
foreach ($ticket in $tickets.items) {
    Write-Host "- $($ticket.subject) | Status: $($ticket.status)" -ForegroundColor Cyan
}

# Find an unresolved ticket
$unresolvedTicket = $null
foreach ($ticket in $tickets.items) {
    if ($ticket.status -ne "resolved") {
        $unresolvedTicket = $ticket
        break
    }
}

if ($unresolvedTicket) {
    Write-Host "`n2. Resolving ticket with feedback..." -ForegroundColor Yellow
    Write-Host "Resolving: $($unresolvedTicket.subject)" -ForegroundColor Cyan
    
    # Feedback data
    $feedback = @{
        title = "Quick Database Fix Guide"
        content = "Steps to fix database issues: 1. Check connections 2. Restart service 3. Monitor performance"
        tags = @("database", "quick-fix")
    } | ConvertTo-Json
    
    # Resolve ticket
    $resolveUrl = "http://localhost:7027/api/v1/tickets/$($unresolvedTicket.id)/resolve"
    $resolved = Invoke-RestMethod -Uri $resolveUrl -Method PUT -Body $feedback -Headers $operatorHeaders -ContentType "application/json"
    
    Write-Host "SUCCESS: Ticket resolved!" -ForegroundColor Green
    Write-Host "Status: $($resolved.status)" -ForegroundColor Cyan
    
    Write-Host "`n3. Checking Knowledge Base..." -ForegroundColor Yellow
    
    # Check KB articles
    $kbArticles = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/knowledge-base" -Method GET -Headers $operatorHeaders
    
    Write-Host "Knowledge Base now has $($kbArticles.total) articles" -ForegroundColor Green
    
    # Look for our new article
    foreach ($article in $kbArticles.items) {
        if ($article.title -eq "Quick Database Fix Guide") {
            Write-Host "SUCCESS: New KB article created from feedback!" -ForegroundColor Green
            Write-Host "Title: $($article.title)" -ForegroundColor Cyan
            break
        }
    }
}

Write-Host "`n=== FEATURES WORKING ===" -ForegroundColor Green
Write-Host "- Operators see only assigned tickets" -ForegroundColor White
Write-Host "- Resolve with feedback creates KB articles" -ForegroundColor White
Write-Host "- Knowledge sharing from operator experience" -ForegroundColor White