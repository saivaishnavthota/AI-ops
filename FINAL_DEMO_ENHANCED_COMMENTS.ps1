#!/usr/bin/env pwsh

Write-Host "=== ENHANCED AI COMMENTS & TEAM-BASED ROUTING DEMO ===" -ForegroundColor Green

# Configuration
$baseUrl = "http://localhost:7027/api/v1"
$loginUrl = "$baseUrl/auth/login"
$ticketsUrl = "$baseUrl/tickets"

# Login
$loginData = @{
    email = "operator@demo.com"
    password = "Demo@123!"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri $loginUrl -Method POST -Body $loginData -ContentType "application/json"
$token = $loginResponse.access_token
$headers = @{ "Authorization" = "Bearer $token" }
Write-Host "✓ Logged in successfully" -ForegroundColor Green

Write-Host "`n=== DEMONSTRATION SCENARIOS ===" -ForegroundColor Yellow

# Scenario 1: Auto-Assignment Success (Security)
Write-Host "`n1. HIGH-CONFIDENCE SECURITY INCIDENT (Should Auto-Assign)" -ForegroundColor Cyan

$securityTicket = @{
    subject = "CRITICAL: Active security breach - unauthorized access detected"
    description = "Security monitoring detected unauthorized access to production systems. Multiple failed login attempts followed by successful breach. Security operations team required for immediate incident response."
    category = "security"
    priority = "critical"
} | ConvertTo-Json

$ticketResponse = Invoke-RestMethod -Uri ($ticketsUrl + "?auto_classify=true" + "&auto_route=true") -Method POST -Body $securityTicket -Headers $headers -ContentType "application/json"
Write-Host "   Ticket ID: $($ticketResponse.id)" -ForegroundColor Gray

Start-Sleep -Seconds 6

$ticket = Invoke-RestMethod -Uri "$ticketsUrl/$($ticketResponse.id)" -Method GET -Headers $headers

Write-Host "   Category: $($ticket.category)" -ForegroundColor White
Write-Host "   Status: $($ticket.status)" -ForegroundColor White
Write-Host "   Assigned to: $($ticket.assignee_name)" -ForegroundColor $(if ($ticket.assignee_name) { "Green" } else { "Red" })

if ($ticket.comments) {
    foreach ($comment in $ticket.comments) {
        if ($comment.user -eq "AI Assistant") {
            Write-Host "`n   AI ANALYSIS:" -ForegroundColor Magenta
            Write-Host "   $($comment.text)" -ForegroundColor White
        }
    }
}

# Scenario 2: Manual Routing Recommended (Infrastructure)
Write-Host "`n2. INFRASTRUCTURE ISSUE (Manual Routing Recommended)" -ForegroundColor Cyan

$infraTicket = @{
    subject = "Server performance degradation on web cluster"
    description = "Web servers showing increased response times and CPU usage. Infrastructure team should investigate hardware and optimize performance."
    category = "infrastructure"
    priority = "medium"
} | ConvertTo-Json

$ticketResponse2 = Invoke-RestMethod -Uri ($ticketsUrl + "?auto_classify=true" + "&auto_route=true") -Method POST -Body $infraTicket -Headers $headers -ContentType "application/json"
Write-Host "   Ticket ID: $($ticketResponse2.id)" -ForegroundColor Gray

Start-Sleep -Seconds 6

$ticket2 = Invoke-RestMethod -Uri "$ticketsUrl/$($ticketResponse2.id)" -Method GET -Headers $headers

Write-Host "   Category: $($ticket2.category)" -ForegroundColor White
Write-Host "   Status: $($ticket2.status)" -ForegroundColor White
Write-Host "   Assigned to: $($ticket2.assignee_name)" -ForegroundColor $(if ($ticket2.assignee_name) { "Green" } else { "Yellow" })

if ($ticket2.comments) {
    foreach ($comment in $ticket2.comments) {
        if ($comment.user -eq "AI Assistant") {
            Write-Host "`n   AI ANALYSIS:" -ForegroundColor Magenta
            Write-Host "   $($comment.text)" -ForegroundColor White
        }
    }
}

# Scenario 3: Database Issue
Write-Host "`n3. DATABASE EMERGENCY (Team-Specific Routing)" -ForegroundColor Cyan

$dbTicket = @{
    subject = "Database connection pool exhausted - service disruption"
    description = "All database connections are in use, new requests failing. Database administration team needs to investigate connection leaks and increase pool size."
    category = "database"
    priority = "high"
} | ConvertTo-Json

$ticketResponse3 = Invoke-RestMethod -Uri ($ticketsUrl + "?auto_classify=true" + "&auto_route=true") -Method POST -Body $dbTicket -Headers $headers -ContentType "application/json"
Write-Host "   Ticket ID: $($ticketResponse3.id)" -ForegroundColor Gray

Start-Sleep -Seconds 6

$ticket3 = Invoke-RestMethod -Uri "$ticketsUrl/$($ticketResponse3.id)" -Method GET -Headers $headers

Write-Host "   Category: $($ticket3.category)" -ForegroundColor White
Write-Host "   Status: $($ticket3.status)" -ForegroundColor White
Write-Host "   Assigned to: $($ticket3.assignee_name)" -ForegroundColor $(if ($ticket3.assignee_name) { "Green" } else { "Yellow" })

if ($ticket3.comments) {
    foreach ($comment in $ticket3.comments) {
        if ($comment.user -eq "AI Assistant") {
            Write-Host "`n   AI ANALYSIS:" -ForegroundColor Magenta
            Write-Host "   $($comment.text)" -ForegroundColor White
        }
    }
}

Write-Host "`n=== ENHANCED FEATURES DEMONSTRATED ===" -ForegroundColor Green
Write-Host "✓ Detailed AI Classification (Category, Intent, Keywords)" -ForegroundColor Cyan
Write-Host "✓ Team-Based Agent Recommendations" -ForegroundColor Cyan
Write-Host "✓ Confidence-Based Auto-Assignment (80% threshold)" -ForegroundColor Cyan
Write-Host "✓ Agent Scoring with Team Specialization" -ForegroundColor Cyan
Write-Host "✓ Workload Balancing and Availability Status" -ForegroundColor Cyan
Write-Host "✓ Comprehensive AI Comments with All Details" -ForegroundColor Cyan

Write-Host "`n=== DEMO COMPLETE ===" -ForegroundColor Green
Write-Host "The AI system now provides:" -ForegroundColor White
Write-Host "- Clear category classification" -ForegroundColor White
Write-Host "- Specific team member assignments" -ForegroundColor White
Write-Host "- Detailed reasoning and confidence scores" -ForegroundColor White
Write-Host "- Team specialization matching" -ForegroundColor White