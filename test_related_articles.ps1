# Test script for Related KB Articles feature
Write-Host "Testing Related KB Articles Feature" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:7027/api/v1"

# Step 1: Login
Write-Host "Step 1: Logging in..." -ForegroundColor Yellow
$loginBody = @{
    email = "admin@demo.com"
    password = "Demo@123!"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
$token = $loginResponse.access_token
Write-Host "Logged in successfully" -ForegroundColor Green
Write-Host ""

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# Step 2: Get list of tickets
Write-Host "Step 2: Fetching tickets..." -ForegroundColor Yellow
$ticketsResponse = Invoke-RestMethod -Uri "$baseUrl/tickets?limit=5" -Method Get -Headers $headers
$tickets = $ticketsResponse.items

if ($tickets.Count -eq 0) {
    Write-Host "No tickets found. Creating a test ticket..." -ForegroundColor Red
    
    $newTicket = @{
        subject = "Cannot access production dashboard"
        description = "Getting 403 error when trying to access the main dashboard"
        priority = "high"
        category = "Access Issue"
    } | ConvertTo-Json
    
    $ticketResponse = Invoke-RestMethod -Uri "$baseUrl/tickets" -Method Post -Body $newTicket -Headers $headers
    $testTicket = $ticketResponse
    Write-Host "Created test ticket" -ForegroundColor Green
}
else {
    $testTicket = $tickets[0]
    Write-Host "Found $($tickets.Count) tickets" -ForegroundColor Green
}

Write-Host ""
Write-Host "Ticket Details:" -ForegroundColor Cyan
Write-Host "  ID: $($testTicket.id)"
Write-Host "  Subject: $($testTicket.subject)"
Write-Host "  Category: $($testTicket.category)"
Write-Host ""

# Step 3: Get related KB articles
Write-Host "Step 3: Fetching related KB articles..." -ForegroundColor Yellow
try {
    $url = "$baseUrl/tickets/$($testTicket.id)/related-articles?limit=5"
    $relatedArticles = Invoke-RestMethod -Uri $url -Method Get -Headers $headers
    
    if ($relatedArticles.Count -eq 0) {
        Write-Host "No related articles found" -ForegroundColor Yellow
    }
    else {
        Write-Host "Found $($relatedArticles.Count) related articles!" -ForegroundColor Green
        Write-Host ""
        
        foreach ($article in $relatedArticles) {
            Write-Host "  $($article.title)" -ForegroundColor White
            Write-Host "     Category: $($article.category)" -ForegroundColor Gray
            Write-Host "     Views: $($article.views)" -ForegroundColor Gray
        }
    }
}
catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Test completed!" -ForegroundColor Cyan
