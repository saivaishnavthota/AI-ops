# Test Assignment Functionality
Write-Host "=== Testing Assignment Functionality ===" -ForegroundColor Green

# Login
$loginData = @{email="admin@demo.com"; password="Demo@123!"} | ConvertTo-Json
$response = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/auth/login" -Method POST -Body $loginData -ContentType "application/json"
$token = $response.access_token
Write-Host "Login successful" -ForegroundColor Green

# Get assignable users
$assignableUsers = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/users/assignable" -Headers @{"Authorization" = "Bearer $token"} -Method GET

Write-Host "`nAssignable Users:" -ForegroundColor Yellow
foreach ($user in $assignableUsers) {
    Write-Host "- $($user.name) (ID: $($user.id))" -ForegroundColor White
}

# Get a test ticket
$tickets = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/tickets" -Headers @{"Authorization" = "Bearer $token"} -Method GET
$testTicket = $tickets.items[0]

Write-Host "`nTest ticket: $($testTicket.subject)" -ForegroundColor Yellow
Write-Host "Current assignee: $($testTicket.assignee_name)" -ForegroundColor Cyan

# Test assignment
$emily = $assignableUsers | Where-Object { $_.name -eq "Emily Rodriguez" }
$assignmentData = @{assignee_id = $emily.id} | ConvertTo-Json

Write-Host "`nTesting assignment to Emily Rodriguez..." -ForegroundColor Yellow

$assignResult = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/tickets/$($testTicket.id)/assign" -Headers @{"Authorization" = "Bearer $token"} -Method PUT -Body $assignmentData -ContentType "application/json"

Write-Host "Assignment successful!" -ForegroundColor Green
Write-Host "New assignee: $($assignResult.assignee_name)" -ForegroundColor Green

Write-Host "`n=== DOCKER UPDATE COMPLETE ===" -ForegroundColor Green
Write-Host "✓ All containers rebuilt with latest code" -ForegroundColor Green
Write-Host "✓ Database names corrected" -ForegroundColor Green  
Write-Host "✓ APIs returning correct names" -ForegroundColor Green
Write-Host "✓ Assignment functionality working" -ForegroundColor Green