# Simple AI Testing Script
Write-Host "Testing AI Features..." -ForegroundColor Green

# Login
$loginData = @{email="admin@demo.com"; password="Demo@123!"} | ConvertTo-Json
$response = Invoke-WebRequest -Uri "http://localhost:7027/api/v1/auth/login" -Method POST -Body $loginData -ContentType "application/json"
$token = ($response.Content | ConvertFrom-Json).access_token
Write-Host "Login successful!" -ForegroundColor Green

# Create test ticket
$ticketData = @{
    subject = "Password Reset Urgent"
    description = "I forgot my password and cannot log into my account. Please help me reset it urgently."
    priority = "high"
    category = "authentication"
} | ConvertTo-Json

$createResponse = Invoke-WebRequest -Uri "http://localhost:7027/api/v1/tickets" -Method POST -Headers @{"Authorization"="Bearer $token"} -Body $ticketData -ContentType "application/json"
$ticketId = ($createResponse.Content | ConvertFrom-Json).id
Write-Host "Ticket created: $ticketId" -ForegroundColor Green

# Test AI Classification
Write-Host "Testing AI Classification..." -ForegroundColor Yellow
$classifyResponse = Invoke-WebRequest -Uri "http://localhost:7027/api/v1/tickets/$ticketId/ai-classify" -Method POST -Headers @{"Authorization"="Bearer $token"}
$classifyResult = $classifyResponse.Content | ConvertFrom-Json
Write-Host "AI Intent: $($classifyResult.ai_analysis.intent)" -ForegroundColor Cyan
Write-Host "AI Category: $($classifyResult.ai_analysis.category)" -ForegroundColor Cyan
Write-Host "AI Confidence: $($classifyResult.ai_analysis.confidence)" -ForegroundColor Cyan

# Test Smart Routing
Write-Host "Testing Smart Routing..." -ForegroundColor Yellow
$routeResponse = Invoke-WebRequest -Uri "http://localhost:7027/api/v1/tickets/$ticketId/ai-route" -Method POST -Headers @{"Authorization"="Bearer $token"}
$routeResult = $routeResponse.Content | ConvertFrom-Json
Write-Host "Recommended Agent: $($routeResult.recommended_agent.agent_name)" -ForegroundColor Cyan
Write-Host "Agent Score: $($routeResult.recommended_agent.score)" -ForegroundColor Cyan

# Test Analytics
Write-Host "Testing Analytics..." -ForegroundColor Yellow
$trendsResponse = Invoke-WebRequest -Uri "http://localhost:7027/api/v1/tickets/ai-analytics/trends" -Headers @{"Authorization"="Bearer $token"}
$trendsResult = $trendsResponse.Content | ConvertFrom-Json
Write-Host "Trends Found: $($trendsResult.total_trends)" -ForegroundColor Cyan

$gapsResponse = Invoke-WebRequest -Uri "http://localhost:7027/api/v1/knowledge-base/ai-analytics/gaps" -Headers @{"Authorization"="Bearer $token"}
$gapsResult = $gapsResponse.Content | ConvertFrom-Json
Write-Host "Knowledge Gaps: $($gapsResult.total_gaps)" -ForegroundColor Cyan

Write-Host "AI Testing Complete!" -ForegroundColor Green