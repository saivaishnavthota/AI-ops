#!/usr/bin/env pwsh

Write-Host "=== Testing Enhanced AI Comments ===" -ForegroundColor Green

# Configuration
$baseUrl = "http://localhost:7027/api/v1"
$loginUrl = "$baseUrl/auth/login"
$ticketsUrl = "$baseUrl/tickets"

# Login as operator
$loginData = @{
    email = "operator@demo.com"
    password = "Demo@123!"
} | ConvertTo-Json

Write-Host "`n1. Logging in..." -ForegroundColor Yellow

$loginResponse = Invoke-RestMethod -Uri $loginUrl -Method POST -Body $loginData -ContentType "application/json"
$token = $loginResponse.access_token
$headers = @{ "Authorization" = "Bearer $token" }
Write-Host "Login successful" -ForegroundColor Green

# Test with a high-confidence security ticket
Write-Host "`n2. Creating security incident (should auto-assign)..." -ForegroundColor Yellow

$securityTicket = @{
    subject = "CRITICAL: Unauthorized access detected - immediate security response required"
    description = "Multiple failed login attempts followed by successful breach from suspicious IP 192.168.1.100. Immediate security team investigation and containment required. User accounts may be compromised."
    category = "security"
    priority = "critical"
} | ConvertTo-Json

$createUrl = $ticketsUrl + "?auto_classify=true&auto_route=true"
$ticketResponse = Invoke-RestMethod -Uri $createUrl -Method POST -Body $securityTicket -Headers $headers -ContentType "application/json"

Write-Host "Security ticket created: $($ticketResponse.id)" -ForegroundColor Green

# Wait for AI processing
Write-Host "Waiting for AI processing..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# Get updated ticket to see enhanced comments
$updatedTicket = Invoke-RestMethod -Uri "$ticketsUrl/$($ticketResponse.id)" -Method GET -Headers $headers

Write-Host "`n3. Enhanced AI Comments:" -ForegroundColor Green
Write-Host "Category: $($updatedTicket.category)" -ForegroundColor Cyan
Write-Host "Status: $($updatedTicket.status)" -ForegroundColor Cyan
Write-Host "Assigned to: $($updatedTicket.assignee_name)" -ForegroundColor Cyan

if ($updatedTicket.comments) {
    foreach ($comment in $updatedTicket.comments) {
        if ($comment.user -eq "AI Assistant") {
            Write-Host "`nAI Comment:" -ForegroundColor Magenta
            Write-Host "$($comment.text)" -ForegroundColor White
        }
    }
} else {
    Write-Host "No AI comments found" -ForegroundColor Red
}

# Test with infrastructure ticket (may not auto-assign)
Write-Host "`n4. Creating infrastructure ticket..." -ForegroundColor Yellow

$infraTicket = @{
    subject = "Server performance degradation on production web server"
    description = "Web server response times have increased significantly. CPU usage at 85% and memory usage at 90%. Infrastructure team needs to investigate and optimize."
    category = "infrastructure"
    priority = "high"
} | ConvertTo-Json

$ticketResponse2 = Invoke-RestMethod -Uri $createUrl -Method POST -Body $infraTicket -Headers $headers -ContentType "application/json"

Write-Host "Infrastructure ticket created: $($ticketResponse2.id)" -ForegroundColor Green

# Wait for AI processing
Start-Sleep -Seconds 8

# Get updated ticket
$updatedTicket2 = Invoke-RestMethod -Uri "$ticketsUrl/$($ticketResponse2.id)" -Method GET -Headers $headers

Write-Host "`n5. Infrastructure Ticket Analysis:" -ForegroundColor Green
Write-Host "Category: $($updatedTicket2.category)" -ForegroundColor Cyan
Write-Host "Status: $($updatedTicket2.status)" -ForegroundColor Cyan
Write-Host "Assigned to: $($updatedTicket2.assignee_name)" -ForegroundColor Cyan

if ($updatedTicket2.comments) {
    foreach ($comment in $updatedTicket2.comments) {
        if ($comment.user -eq "AI Assistant") {
            Write-Host "`nAI Comment:" -ForegroundColor Magenta
            Write-Host "$($comment.text)" -ForegroundColor White
        }
    }
}

Write-Host "`n=== Enhanced Comments Test Complete ===" -ForegroundColor Green