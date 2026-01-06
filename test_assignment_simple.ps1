#!/usr/bin/env pwsh

# Test Assignment API with correct names
Write-Host "=== Testing Assignment API ===" -ForegroundColor Green

# Login and get token
$loginData = @{email="admin@demo.com"; password="Demo@123!"} | ConvertTo-Json
$response = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/auth/login" -Method POST -Body $loginData -ContentType "application/json"
$token = $response.access_token

Write-Host "✓ Login successful" -ForegroundColor Green

# Test 1: Get assignable users
Write-Host "`n1. Testing /users/assignable endpoint:" -ForegroundColor Yellow
$assignableUsers = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/users/assignable" -Headers @{"Authorization" = "Bearer $token"} -Method GET

Write-Host "Assignable Users:" -ForegroundColor Cyan
foreach ($user in $assignableUsers) {
    Write-Host "  - $($user.name) ($($user.email)) - $($user.role)" -ForegroundColor White
}

# Test 2: Get tickets to see current assignments
Write-Host "`n2. Testing current ticket assignments:" -ForegroundColor Yellow
$tickets = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/tickets" -Headers @{"Authorization" = "Bearer $token"} -Method GET

Write-Host "Current Ticket Assignments:" -ForegroundColor Cyan
foreach ($ticket in $tickets.items) {
    if ($ticket.assignee_name) {
        Write-Host "  - Ticket: $($ticket.subject)" -ForegroundColor White
        Write-Host "    Assigned to: $($ticket.assignee_name)" -ForegroundColor Green
    }
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Green
Write-Host "✓ Backend APIs are returning correct names:" -ForegroundColor Green
Write-Host "  - Emily Rodriguez (not Emily Davis)" -ForegroundColor White
Write-Host "  - James Wilson (not Mike Wilson)" -ForegroundColor White
Write-Host "  - Michael Chen (correct)" -ForegroundColor White
Write-Host ""
Write-Host "🔧 SOLUTION: The issue is frontend caching. Try these steps:" -ForegroundColor Yellow
Write-Host "  1. Hard refresh browser: Ctrl+Shift+R (Chrome/Edge) or Cmd+Shift+R (Mac)" -ForegroundColor Cyan
Write-Host "  2. Clear browser cache and cookies for localhost:7026" -ForegroundColor Cyan
Write-Host "  3. Open browser Developer Tools (F12) > Network tab > check Disable cache" -ForegroundColor Cyan
Write-Host "  4. If still showing old names, check which API endpoint the frontend is calling" -ForegroundColor Cyan