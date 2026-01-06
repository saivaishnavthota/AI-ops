#!/usr/bin/env pwsh

Write-Host "=== Team-Based Smart Assignment Demo ===" -ForegroundColor Green

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

# Test cases for different team specializations
$testCases = @(
    @{
        name = "Infrastructure Issue"
        subject = "Critical server disk space - production impact"
        description = "Production server disk at 95% capacity, immediate infrastructure team response needed"
        category = "infrastructure"
        priority = "urgent"
    },
    @{
        name = "Security Incident"
        subject = "Suspicious login activity - potential breach"
        description = "Multiple failed login attempts from foreign IPs, security team investigation required"
        category = "security"
        priority = "high"
    },
    @{
        name = "Application Issue"
        subject = "Application deployment failure - rollback needed"
        description = "Latest deployment causing errors, DevOps team rollback required"
        category = "application"
        priority = "high"
    }
)

Write-Host "`n2. Testing Team-Based Auto-Assignment..." -ForegroundColor Yellow

$results = @()

foreach ($testCase in $testCases) {
    Write-Host "`n   $($testCase.name):" -ForegroundColor Cyan
    
    # Create ticket with auto-routing
    $ticketData = @{
        subject = $testCase.subject
        description = $testCase.description
        category = $testCase.category
        priority = $testCase.priority
    } | ConvertTo-Json
    
    $createUrl = $ticketsUrl + "?auto_classify=true&auto_route=true"
    $ticketResponse = Invoke-RestMethod -Uri $createUrl -Method POST -Body $ticketData -Headers $headers -ContentType "application/json"
    
    Write-Host "   Ticket created: $($ticketResponse.id)" -ForegroundColor Gray
    
    # Wait for AI processing
    Start-Sleep -Seconds 5
    
    # Get updated ticket
    $updatedTicket = Invoke-RestMethod -Uri "$ticketsUrl/$($ticketResponse.id)" -Method GET -Headers $headers
    
    # Check results
    if ($updatedTicket.assignee_name) {
        Write-Host "   SUCCESS: Auto-assigned to $($updatedTicket.assignee_name)" -ForegroundColor Green
        $results += "ASSIGNED"
    } else {
        Write-Host "   PENDING: Not auto-assigned (manual routing recommended)" -ForegroundColor Yellow
        $results += "PENDING"
    }
    
    # Show AI comments
    if ($updatedTicket.comments) {
        foreach ($comment in $updatedTicket.comments) {
            if ($comment.user -eq "AI Assistant") {
                Write-Host "   AI: $($comment.text)" -ForegroundColor Magenta
            }
        }
    }
    
    # Test manual routing for comparison
    Write-Host "   Manual routing analysis:" -ForegroundColor Gray
    $routingResponse = Invoke-RestMethod -Uri "$ticketsUrl/$($ticketResponse.id)/ai-route" -Method POST -Headers $headers
    
    if ($routingResponse.recommended_agent) {
        Write-Host "   Recommended: $($routingResponse.recommended_agent.agent_name) (Score: $($routingResponse.recommended_agent.score.ToString('F2')))" -ForegroundColor Gray
        Write-Host "   Team: $($routingResponse.team_recommendation)" -ForegroundColor Gray
    }
}

# Summary
Write-Host "`n=== Results Summary ===" -ForegroundColor Green
$assigned = ($results | Where-Object { $_ -eq "ASSIGNED" }).Count
$total = $results.Count

Write-Host "Auto-assigned: $assigned/$total tickets" -ForegroundColor Cyan
Write-Host "Team specialization routing: ACTIVE" -ForegroundColor Cyan
Write-Host "AI confidence threshold: 85%" -ForegroundColor Cyan

Write-Host "`n=== Key Features Demonstrated ===" -ForegroundColor Green
Write-Host "- Category-to-team mapping (Infrastructure -> Infrastructure Team)" -ForegroundColor White
Write-Host "- Team specialization scoring with role bonuses" -ForegroundColor White
Write-Host "- Confidence-based auto-assignment" -ForegroundColor White
Write-Host "- Workload balancing across team members" -ForegroundColor White
Write-Host "- AI classification with background processing" -ForegroundColor White

Write-Host "`n=== Demo Complete ===" -ForegroundColor Green