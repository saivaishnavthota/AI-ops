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
    email = "admin@acme.com"
    password = "admin123"
} | ConvertTo-Json

Write-Host "1. Logging in as admin..." -ForegroundColor Yellow

try {
    $loginResponse = Invoke-RestMethod -Uri $loginUrl -Method POST -Body $loginData -ContentType "application/json"
    $token = $loginResponse.access_token
    $headers = @{ "Authorization" = "Bearer $token" }
    Write-Host "✓ Login successful" -ForegroundColor Green
} catch {
    Write-Host "✗ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# First, let's check the teams data to understand team structure
Write-Host "`n2. Checking teams structure..." -ForegroundColor Yellow

try {
    $teamsResponse = Invoke-RestMethod -Uri $teamsUrl -Method GET -Headers $headers
    Write-Host "✓ Found $($teamsResponse.total) teams:" -ForegroundColor Green
    
    foreach ($team in $teamsResponse.items) {
        Write-Host "  - $($team.name) (Type: $($team.team_type), Members: $($team.member_count))" -ForegroundColor Cyan
    }
} catch {
    Write-Host "✗ Failed to get teams: $($_.Exception.Message)" -ForegroundColor Red
}

# Test different ticket categories to see team-based routing
$testTickets = @(
    @{
        subject = "Server infrastructure issue - disk space critical"
        description = "Production server running out of disk space, need immediate attention"
        category = "infrastructure"
        priority = "urgent"
    },
    @{
        subject = "Application deployment failure"
        description = "Latest application deployment failed, rollback needed"
        category = "application" 
        priority = "high"
    },
    @{
        subject = "Security breach detected"
        description = "Suspicious login attempts detected from unknown IP addresses"
        category = "security"
        priority = "urgent"
    },
    @{
        subject = "Database performance issues"
        description = "Database queries running slowly, affecting application performance"
        category = "database"
        priority = "high"
    },
    @{
        subject = "Network connectivity problems"
        description = "Users unable to connect to internal network resources"
        category = "network"
        priority = "normal"
    }
)

Write-Host "`n3. Testing team-based smart assignment..." -ForegroundColor Yellow

$testResults = @()

foreach ($ticketData in $testTickets) {
    Write-Host "`n   Testing: $($ticketData.subject)" -ForegroundColor Cyan
    
    try {
        # Create ticket with auto-routing enabled
        $createUrl = "$ticketsUrl?auto_classify=true&auto_route=true"
        $ticketJson = $ticketData | ConvertTo-Json
        
        $ticketResponse = Invoke-RestMethod -Uri $createUrl -Method POST -Body $ticketJson -Headers $headers -ContentType "application/json"
        
        Write-Host "   ✓ Ticket created: $($ticketResponse.id)" -ForegroundColor Green
        
        # Wait a moment for background processing
        Start-Sleep -Seconds 3
        
        # Get updated ticket to see AI enhancements
        $getTicketUrl = "$ticketsUrl/$($ticketResponse.id)"
        $updatedTicket = Invoke-RestMethod -Uri $getTicketUrl -Method GET -Headers $headers
        
        # Analyze the results
        $result = @{
            TicketId = $updatedTicket.id
            Subject = $updatedTicket.subject
            Category = $updatedTicket.category
            Priority = $updatedTicket.priority
            AssignedTo = $updatedTicket.assignee_name
            Status = $updatedTicket.status
            Comments = $updatedTicket.comments.Count
            AIEnhanced = $false
            TeamRouted = $false
        }
        
        # Check for AI comments
        if ($updatedTicket.comments) {
            foreach ($comment in $updatedTicket.comments) {
                if ($comment.user -eq "AI Assistant") {
                    $result.AIEnhanced = $true
                    if ($comment.text -like "*assigned to*") {
                        $result.TeamRouted = $true
                    }
                    Write-Host "   AI Comment: $($comment.text)" -ForegroundColor Magenta
                }
            }
        }
        
        if ($result.AssignedTo) {
            Write-Host "   ✓ Auto-assigned to: $($result.AssignedTo)" -ForegroundColor Green
        } else {
            Write-Host "   ○ Not auto-assigned (manual routing recommended)" -ForegroundColor Yellow
        }
        
        $testResults += $result
        
    } catch {
        Write-Host "   ✗ Failed to create/process ticket: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test manual AI routing for comparison
Write-Host "`n4. Testing manual AI routing..." -ForegroundColor Yellow

try {
    # Create a ticket without auto-routing
    $manualTicket = @{
        subject = "Email server configuration issue"
        description = "Users reporting email delivery delays and connection timeouts"
        category = "email"
        priority = "normal"
    } | ConvertTo-Json
    
    $manualCreateUrl = "$ticketsUrl?auto_classify=true&auto_route=false"
    $manualResponse = Invoke-RestMethod -Uri $manualCreateUrl -Method POST -Body $manualTicket -Headers $headers -ContentType "application/json"
    
    Write-Host "   ✓ Manual ticket created: $($manualResponse.id)" -ForegroundColor Green
    
    # Now test AI routing endpoint
    $routingUrl = "$ticketsUrl/$($manualResponse.id)/ai-route"
    $routingResponse = Invoke-RestMethod -Uri $routingUrl -Method POST -Headers $headers
    
    Write-Host "   ✓ AI Routing Analysis:" -ForegroundColor Green
    Write-Host "     Recommended Agent: $($routingResponse.recommended_agent.agent_name)" -ForegroundColor Cyan
    Write-Host "     Score: $($routingResponse.recommended_agent.score)" -ForegroundColor Cyan
    Write-Host "     Reasoning: $($routingResponse.recommended_agent.reasoning)" -ForegroundColor Cyan
    Write-Host "     Team Recommendation: $($routingResponse.team_recommendation)" -ForegroundColor Cyan
    Write-Host "     Confidence: $($routingResponse.confidence)" -ForegroundColor Cyan
    
} catch {
    Write-Host "   ✗ Manual routing test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Summary
Write-Host "`n=== Test Results Summary ===" -ForegroundColor Green
Write-Host "Total tickets tested: $($testResults.Count)" -ForegroundColor White

$aiEnhanced = ($testResults | Where-Object { $_.AIEnhanced }).Count
$autoAssigned = ($testResults | Where-Object { $_.AssignedTo -ne $null }).Count
$teamRouted = ($testResults | Where-Object { $_.TeamRouted }).Count

Write-Host "AI Enhanced: $aiEnhanced/$($testResults.Count)" -ForegroundColor Cyan
Write-Host "Auto-assigned: $autoAssigned/$($testResults.Count)" -ForegroundColor Cyan
Write-Host "Team-based routing: $teamRouted/$($testResults.Count)" -ForegroundColor Cyan

Write-Host "`nDetailed Results:" -ForegroundColor White
foreach ($result in $testResults) {
    $status = if ($result.AssignedTo) { "ASSIGNED to $($result.AssignedTo)" } else { "PENDING" }
    Write-Host "  $($result.Category): $status" -ForegroundColor $(if ($result.AssignedTo) { "Green" } else { "Yellow" })
}

Write-Host "`n=== Team-Based Smart Assignment Test Complete ===" -ForegroundColor Green