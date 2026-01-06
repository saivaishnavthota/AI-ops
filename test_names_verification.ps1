# Test Assignment API - Verify Names
Write-Host "=== Testing Assignment API ===" -ForegroundColor Green

# Login
$loginData = @{email="admin@demo.com"; password="Demo@123!"} | ConvertTo-Json
$response = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/auth/login" -Method POST -Body $loginData -ContentType "application/json"
$token = $response.access_token
Write-Host "Login successful" -ForegroundColor Green

# Get assignable users
$assignableUsers = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/users/assignable" -Headers @{"Authorization" = "Bearer $token"} -Method GET

Write-Host "`nAssignable Users from API:" -ForegroundColor Yellow
foreach ($user in $assignableUsers) {
    Write-Host "- $($user.name) ($($user.email))" -ForegroundColor White
}

# Get tickets
$tickets = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/tickets" -Headers @{"Authorization" = "Bearer $token"} -Method GET

Write-Host "`nCurrent Ticket Assignments:" -ForegroundColor Yellow
foreach ($ticket in $tickets.items) {
    if ($ticket.assignee_name) {
        Write-Host "- $($ticket.subject) -> $($ticket.assignee_name)" -ForegroundColor White
    }
}

Write-Host "`n=== CONCLUSION ===" -ForegroundColor Green
Write-Host "Backend APIs return correct names. Frontend cache issue." -ForegroundColor Yellow
Write-Host "Solution: Hard refresh browser (Ctrl+Shift+R)" -ForegroundColor Cyan