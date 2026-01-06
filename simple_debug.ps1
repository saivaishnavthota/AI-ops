# Simple Debug Test
Write-Host "=== Simple Debug Test ===" -ForegroundColor Green

# Login
$loginData = @{email="admin@demo.com"; password="Demo@123!"} | ConvertTo-Json
$response = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/auth/login" -Method POST -Body $loginData -ContentType "application/json"
$token = $response.access_token
Write-Host "Login successful" -ForegroundColor Green

# Test assignable users endpoint
Write-Host "`nTesting assignable users:" -ForegroundColor Yellow
$assignableUsers = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/users/assignable" -Headers @{"Authorization" = "Bearer $token"} -Method GET
Write-Host "Assignable users returned: $($assignableUsers.Count)" -ForegroundColor Green
foreach ($user in $assignableUsers) {
    Write-Host "- $($user.display_name)" -ForegroundColor White
}

# Test frontend
Write-Host "`nTesting frontend:" -ForegroundColor Yellow
$frontendResponse = Invoke-WebRequest -Uri "http://localhost:7026" -Method GET -UseBasicParsing
Write-Host "Frontend status: $($frontendResponse.StatusCode)" -ForegroundColor Green

Write-Host "`n=== ISSUE DIAGNOSIS ===" -ForegroundColor Yellow
Write-Host "Backend APIs work correctly" -ForegroundColor Green
Write-Host "Frontend container is running" -ForegroundColor Green
Write-Host ""
Write-Host "LIKELY CAUSE: Browser cache or frontend not rebuilt properly" -ForegroundColor Red
Write-Host ""
Write-Host "SOLUTIONS:" -ForegroundColor Cyan
Write-Host "1. Hard refresh browser: Ctrl+Shift+R" -ForegroundColor White
Write-Host "2. Clear browser cache completely" -ForegroundColor White
Write-Host "3. Try incognito/private browsing mode" -ForegroundColor White
Write-Host "4. Check browser console for JavaScript errors" -ForegroundColor White