#!/usr/bin/env pwsh

# Test Team-Based Smart Assignment
Write-Host "=== Testing Team-Based Smart Assignment ===" -ForegroundColor Green

# Configuration
$baseUrl = "http://localhost:7027/api/v1"
$loginUrl = "$baseUrl/auth/login"
$ticketsUrl = "$baseUrl/tickets"
$teamsUrl = "$baseUrl/teams"

# Login credentials (admin user)
$loginData = @{
    email = "super.admin@demo.com"
    password = "Demo@123!"
} | ConvertTo-Json

Write-Host "1. Logging in as admin..." -ForegroundColor Yellow

try {
    $loginResponse = Invoke-RestMethod -Uri $loginUrl -Method POST -Body $loginData -ContentType "application/json"
    $token = $loginResponse.access_token
    $headers = @{ "Authorization" = "Bearer $token" }
    Write-Host "Login successful" -ForegroundColor Green
} catch {
    Write-Host "Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Check teams structure
Write-Host "`n2. Checking teams structure..." -ForegroundColor Yellow

try {
    $teamsResponse = Invoke-RestMethod -Uri $teamsUrl -Method GET -Headers $headers
    Write-Host "Found $($teamsResponse.total) teams:" -ForegroundColor Green
    
    foreach ($team in $teamsResponse.items) {
        Write-Host "  - $($team.name) (Type: $($team.team_type), Members: $($team.member_count))" -ForegroundColor Cyan
    }
} catch {
    Write-Host "Failed to get teams: $($_.Exception.Message)" -ForegroundColor Red
}

# Test infrastructure ticket
Write-Host "`n3. Testing Infrastructure ticket..." -ForegroundColor Yellow

$infraTicket = @{
    subject = "Server infrastructure issue - disk space critical"
    description = "Production server running out of disk space, need immediate attention"
    category = "infrastructure"
    priority = "urgent"
} | ConvertTo-Json

try {
    $createUrl = $ticketsUrl + "?auto_classify=true" + "&" + "auto_route=true"
    $ticketResponse = Invoke-RestMethod -Uri $createUrl -Method POST -Body $infraTicket -Headers $headers -ContentType "application/json"
    
    Write-Host "Infrastructure ticket created: $($ticketResponse.id)" -ForegroundColor Green
    
    # Wait for background processing
    Start-Sleep -Seconds 5
    
    # Get updated ticket
    $getTicketUrl = "$ticketsUrl/$($ticketResponse.id)"
    $updatedTicket = Invoke-RestMethod -Uri $getTicketUrl -Method GET -Headers $headers
    
    Write-Host "Category: $($updatedTicket.category)" -ForegroundColor Cyan
    Write-Host "Status: $($updatedTicket.status)" -ForegroundColor Cyan
    Write-Host "Assigned to: $($updatedTicket.assignee_name)" -ForegroundColor Cyan
    
    if ($updatedTicket.comments) {
        Write-Host "AI Comments:" -ForegroundColor Magenta
        foreach ($comment in $updatedTicket.comments) {
            if ($comment.user -eq "AI Assistant") {
                Write-Host "  - $($comment.text)" -ForegroundColor Magenta
            }
        }
    }
    
} catch {
    Write-Host "Infrastructure ticket test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test security ticket
Write-Host "`n4. Testing Security ticket..." -ForegroundColor Yellow

$securityTicket = @{
    subject = "Security breach detected"
    description = "Suspicious login attempts detected from unknown IP addresses"
    category = "security"
    priority = "urgent"
} | ConvertTo-Json

try {
    $createUrl = $ticketsUrl + "?auto_classify=true" + "&" + "auto_route=true"
    $ticketResponse = Invoke-RestMethod -Uri $createUrl -Method POST -Body $securityTicket -Headers $headers -ContentType "application/json"
    
    Write-Host "Security ticket created: $($ticketResponse.id)" -ForegroundColor Green
    
    # Wait for background processing
    Start-Sleep -Seconds 5
    
    # Get updated ticket
    $getTicketUrl = "$ticketsUrl/$($ticketResponse.id)"
    $updatedTicket = Invoke-RestMethod -Uri $getTicketUrl -Method GET -Headers $headers
    
    Write-Host "Category: $($updatedTicket.category)" -ForegroundColor Cyan
    Write-Host "Status: $($updatedTicket.status)" -ForegroundColor Cyan
    Write-Host "Assigned to: $($updatedTicket.assignee_name)" -ForegroundColor Cyan
    
    if ($updatedTicket.comments) {
        Write-Host "AI Comments:" -ForegroundColor Magenta
        foreach ($comment in $updatedTicket.comments) {
            if ($comment.user -eq "AI Assistant") {
                Write-Host "  - $($comment.text)" -ForegroundColor Magenta
            }
        }
    }
    
} catch {
    Write-Host "Security ticket test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test manual AI routing
Write-Host "`n5. Testing manual AI routing..." -ForegroundColor Yellow

$manualTicket = @{
    subject = "Application deployment failure"
    description = "Latest application deployment failed, rollback needed"
    category = "application"
    priority = "high"
} | ConvertTo-Json

try {
    # Create ticket without auto-routing
    $manualCreateUrl = $ticketsUrl + "?auto_classify=true" + "&" + "auto_route=false"
    $manualResponse = Invoke-RestMethod -Uri $manualCreateUrl -Method POST -Body $manualTicket -Headers $headers -ContentType "application/json"
    
    Write-Host "Manual ticket created: $($manualResponse.id)" -ForegroundColor Green
    
    # Test AI routing endpoint
    $routingUrl = "$ticketsUrl/$($manualResponse.id)/ai-route"
    $routingResponse = Invoke-RestMethod -Uri $routingUrl -Method POST -Headers $headers
    
    Write-Host "AI Routing Analysis:" -ForegroundColor Green
    if ($routingResponse.recommended_agent) {
        Write-Host "  Recommended Agent: $($routingResponse.recommended_agent.agent_name)" -ForegroundColor Cyan
        Write-Host "  Score: $($routingResponse.recommended_agent.score)" -ForegroundColor Cyan
        Write-Host "  Reasoning: $($routingResponse.recommended_agent.reasoning)" -ForegroundColor Cyan
        Write-Host "  Availability: $($routingResponse.recommended_agent.availability)" -ForegroundColor Cyan
        Write-Host "  Current Workload: $($routingResponse.recommended_agent.current_workload)" -ForegroundColor Cyan
    }
    Write-Host "  Team Recommendation: $($routingResponse.team_recommendation)" -ForegroundColor Cyan
    Write-Host "  Confidence: $($routingResponse.confidence)" -ForegroundColor Cyan
    Write-Host "  Escalation Needed: $($routingResponse.escalation_needed)" -ForegroundColor Cyan
    
} catch {
    Write-Host "Manual routing test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Team-Based Smart Assignment Test Complete ===" -ForegroundColor Green