# AI Service Desk Testing Script
# Run this in PowerShell to test all AI features

Write-Host "🤖 Testing AI-First Service Desk Features" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# Step 1: Login and get token
Write-Host "`n1. 🔐 Getting authentication token..." -ForegroundColor Yellow
$loginData = @{
    email = "admin@demo.com"
    password = "Demo@123!"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-WebRequest -Uri "http://localhost:7027/api/v1/auth/login" -Method POST -Body $loginData -ContentType "application/json"
    $tokenObj = $loginResponse.Content | ConvertFrom-Json
    $token = $tokenObj.access_token
    Write-Host "✅ Login successful!" -ForegroundColor Green
} catch {
    Write-Host "❌ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 2: Create a test ticket
Write-Host "`n2. 🎫 Creating test ticket..." -ForegroundColor Yellow
$ticketData = @{
    subject = "Password Reset - Urgent Help Needed"
    description = "I forgot my password and cannot log into my account. I've tried multiple times but keep getting locked out. This is urgent as I have an important presentation today. Please help me reset my password immediately."
    priority = "high"
    category = "authentication"
} | ConvertTo-Json

try {
    $createResponse = Invoke-WebRequest -Uri "http://localhost:7027/api/v1/tickets" -Method POST -Headers @{"Authorization"="Bearer $token"} -Body $ticketData -ContentType "application/json"
    $ticketObj = $createResponse.Content | ConvertFrom-Json
    $ticketId = $ticketObj.id
    Write-Host "✅ Ticket created: $ticketId" -ForegroundColor Green
} catch {
    Write-Host "❌ Ticket creation failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 3: Test AI Classification
Write-Host "`n3. 🧠 Testing AI Classification..." -ForegroundColor Yellow
try {
    $classifyResponse = Invoke-WebRequest -Uri "http://localhost:7027/api/v1/tickets/$ticketId/ai-classify" -Method POST -Headers @{"Authorization"="Bearer $token"}
    $classifyResult = $classifyResponse.Content | ConvertFrom-Json
    
    Write-Host "✅ AI Classification Results:" -ForegroundColor Green
    Write-Host "   Intent: $($classifyResult.ai_analysis.intent)" -ForegroundColor Cyan
    Write-Host "   Category: $($classifyResult.ai_analysis.category)" -ForegroundColor Cyan
    Write-Host "   Priority: $($classifyResult.ai_analysis.priority)" -ForegroundColor Cyan
    Write-Host "   Confidence: $([math]::Round($classifyResult.ai_analysis.confidence * 100, 1))%" -ForegroundColor Cyan
    Write-Host "   Keywords: $($classifyResult.ai_analysis.keywords -join ', ')" -ForegroundColor Cyan
    Write-Host "   Suggested Actions: $($classifyResult.ai_analysis.suggested_actions -join ', ')" -ForegroundColor Cyan
    Write-Host "   KB Articles Found: $($classifyResult.kb_articles_found)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ AI Classification failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 4: Test Smart Routing
Write-Host "`n4. 🎯 Testing Smart Routing..." -ForegroundColor Yellow
try {
    $routeResponse = Invoke-WebRequest -Uri "http://localhost:7027/api/v1/tickets/$ticketId/ai-route" -Method POST -Headers @{"Authorization"="Bearer $token"}
    $routeResult = $routeResponse.Content | ConvertFrom-Json
    
    Write-Host "✅ Smart Routing Results:" -ForegroundColor Green
    if ($routeResult.recommended_agent) {
        Write-Host "   Recommended Agent: $($routeResult.recommended_agent.agent_name)" -ForegroundColor Cyan
        Write-Host "   Agent Score: $([math]::Round($routeResult.recommended_agent.score * 100, 1))%" -ForegroundColor Cyan
        Write-Host "   Availability: $($routeResult.recommended_agent.availability)" -ForegroundColor Cyan
        Write-Host "   Current Workload: $($routeResult.recommended_agent.current_workload) tickets" -ForegroundColor Cyan
        Write-Host "   Reasoning: $($routeResult.recommended_agent.reasoning)" -ForegroundColor Cyan
    }
    Write-Host "   Alternative Agents: $($routeResult.alternative_agents.Count)" -ForegroundColor Cyan
    Write-Host "   Escalation Needed: $($routeResult.escalation_needed)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Smart Routing failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 5: Test Trend Analysis
Write-Host "`n5. 📊 Testing Trend Analysis..." -ForegroundColor Yellow
try {
    $trendsResponse = Invoke-WebRequest -Uri "http://localhost:7027/api/v1/tickets/ai-analytics/trends?days_back=30" -Headers @{"Authorization"="Bearer $token"}
    $trendsResult = $trendsResponse.Content | ConvertFrom-Json
    
    Write-Host "✅ Trend Analysis Results:" -ForegroundColor Green
    Write-Host "   Analysis Period: $($trendsResult.analysis_period_days) days" -ForegroundColor Cyan
    Write-Host "   Total Trends: $($trendsResult.total_trends)" -ForegroundColor Cyan
    Write-Host "   High Impact Trends: $($trendsResult.high_impact_trends)" -ForegroundColor Cyan
    
    if ($trendsResult.trends.Count -gt 0) {
        Write-Host "   Sample Trend:" -ForegroundColor Cyan
        $trend = $trendsResult.trends[0]
        Write-Host "     - Type: $($trend.trend_type)" -ForegroundColor White
        Write-Host "     - Category: $($trend.category)" -ForegroundColor White
        Write-Host "     - Description: $($trend.description)" -ForegroundColor White
        Write-Host "     - Impact Score: $($trend.impact_score)/10" -ForegroundColor White
    }
} catch {
    Write-Host "❌ Trend Analysis failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 6: Test Anomaly Detection
Write-Host "`n6. 🚨 Testing Anomaly Detection..." -ForegroundColor Yellow
try {
    $anomaliesResponse = Invoke-WebRequest -Uri "http://localhost:7027/api/v1/tickets/ai-analytics/anomalies?hours_back=24" -Headers @{"Authorization"="Bearer $token"}
    $anomaliesResult = $anomaliesResponse.Content | ConvertFrom-Json
    
    Write-Host "✅ Anomaly Detection Results:" -ForegroundColor Green
    Write-Host "   Analysis Period: $($anomaliesResult.analysis_period_hours) hours" -ForegroundColor Cyan
    Write-Host "   Total Anomalies: $($anomaliesResult.total_anomalies)" -ForegroundColor Cyan
    Write-Host "   Critical Anomalies: $($anomaliesResult.critical_anomalies)" -ForegroundColor Cyan
    
    if ($anomaliesResult.anomalies.Count -gt 0) {
        Write-Host "   Detected Anomalies:" -ForegroundColor Cyan
        foreach ($anomaly in $anomaliesResult.anomalies) {
            Write-Host "     - $($anomaly.anomaly_type): $($anomaly.description)" -ForegroundColor White
        }
    } else {
        Write-Host "   No anomalies detected (system is running normally)" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Anomaly Detection failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 7: Test Knowledge Gap Analysis
Write-Host "`n7. 📚 Testing Knowledge Gap Analysis..." -ForegroundColor Yellow
try {
    $gapsResponse = Invoke-WebRequest -Uri "http://localhost:7027/api/v1/knowledge-base/ai-analytics/gaps?days_back=30" -Headers @{"Authorization"="Bearer $token"}
    $gapsResult = $gapsResponse.Content | ConvertFrom-Json
    
    Write-Host "✅ Knowledge Gap Analysis Results:" -ForegroundColor Green
    Write-Host "   Analysis Period: $($gapsResult.analysis_period_days) days" -ForegroundColor Cyan
    Write-Host "   Total Gaps: $($gapsResult.total_gaps)" -ForegroundColor Cyan
    Write-Host "   High Priority Gaps: $($gapsResult.high_priority_gaps)" -ForegroundColor Cyan
    Write-Host "   Recommended Articles: $($gapsResult.recommended_articles)" -ForegroundColor Cyan
    
    if ($gapsResult.knowledge_gaps.Count -gt 0) {
        Write-Host "   Knowledge Gaps Found:" -ForegroundColor Cyan
        foreach ($gap in $gapsResult.knowledge_gaps) {
            Write-Host "     - $($gap.category): $($gap.ticket_count) tickets, $($gap.kb_articles) articles (Priority: $($gap.priority))" -ForegroundColor White
        }
    }
} catch {
    Write-Host "❌ Knowledge Gap Analysis failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 8: Test Proactive Recommendations
Write-Host "`n8. 💡 Testing Proactive Recommendations..." -ForegroundColor Yellow
try {
    $recsResponse = Invoke-WebRequest -Uri "http://localhost:7027/api/v1/tickets/ai-analytics/recommendations" -Headers @{"Authorization"="Bearer $token"}
    $recsResult = $recsResponse.Content | ConvertFrom-Json
    
    Write-Host "✅ Proactive Recommendations Results:" -ForegroundColor Green
    Write-Host "   Total Recommendations: $($recsResult.total_recommendations)" -ForegroundColor Cyan
    Write-Host "   High Priority: $($recsResult.high_priority_recommendations)" -ForegroundColor Cyan
    
    if ($recsResult.recommendations.Count -gt 0) {
        Write-Host "   Sample Recommendations:" -ForegroundColor Cyan
        foreach ($rec in $recsResult.recommendations | Select-Object -First 3) {
            Write-Host "     - $($rec.title) (Priority: $($rec.priority))" -ForegroundColor White
            Write-Host "       $($rec.description)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "❌ Proactive Recommendations failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 AI Feature Testing Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "All AI features have been tested. Check the results above to see the AI in action!" -ForegroundColor Yellow