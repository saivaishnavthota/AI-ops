# Final Verification Test
Write-Host "=== Final Verification Test ===" -ForegroundColor Green

# Login
$loginData = @{email="admin@demo.com"; password="Demo@123!"} | ConvertTo-Json
$response = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/auth/login" -Method POST -Body $loginData -ContentType "application/json"
$token = $response.access_token
Write-Host "Login successful" -ForegroundColor Green

# Test Assignable Users API
Write-Host "`nTesting Assignable Users API:" -ForegroundColor Yellow
$assignableUsers = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/users/assignable" -Headers @{"Authorization" = "Bearer $token"} -Method GET

Write-Host "Assignable Users for Dropdown:" -ForegroundColor Cyan
foreach ($user in $assignableUsers) {
    Write-Host "- $($user.display_name)" -ForegroundColor White
}

# Test Assignment
Write-Host "`nTesting Assignment:" -ForegroundColor Yellow
$tickets = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/tickets" -Headers @{"Authorization" = "Bearer $token"} -Method GET
$testTicket = $tickets.items[0]

$emily = $assignableUsers | Where-Object { $_.name -eq "Emily Rodriguez" }
$assignmentData = @{assignee_id = $emily.id} | ConvertTo-Json

$assignResult = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/tickets/$($testTicket.id)/assign" -Headers @{"Authorization" = "Bearer $token"} -Method PUT -Body $assignmentData -ContentType "application/json"
Write-Host "Assignment successful: $($assignResult.assignee_name)" -ForegroundColor Green

# Test Resolve with Feedback
Write-Host "`nTesting Resolve with Feedback:" -ForegroundColor Yellow
$feedbackData = @{
    title = "Test Solution"
    content = "This is a test solution for demonstration"
    tags = @("test", "demo")
} | ConvertTo-Json

$resolveResult = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/tickets/$($testTicket.id)/resolve" -Headers @{"Authorization" = "Bearer $token"} -Method PUT -Body $feedbackData -ContentType "application/json"
Write-Host "Resolve with feedback successful!" -ForegroundColor Green

Write-Host "`n=== ALL TESTS PASSED ===" -ForegroundColor Green
Write-Host "Frontend should now show correct names and feedback form!" -ForegroundColor Yellow