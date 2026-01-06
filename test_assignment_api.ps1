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

# Test 2: Get all users
Write-Host "`n2. Testing /users endpoint:" -ForegroundColor Yellow
$allUsers = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/users" -Headers @{"Authorization" = "Bearer $token"} -Method GET

Write-Host "All Users (operators and admins only):" -ForegroundColor Cyan
foreach ($user in $allUsers.items) {
    if ($user.role -in @("operator", "admin")) {
        Write-Host "  - $($user.full_name) ($($user.email)) - $($user.role)" -ForegroundColor White
    }
}

# Test 3: Get tickets to see current assignments
Write-Host "`n3. Testing current ticket assignments:" -ForegroundColor Yellow
$tickets = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/tickets" -Headers @{"Authorization" = "Bearer $token"} -Method GET

Write-Host "Current Ticket Assignments:" -ForegroundColor Cyan
foreach ($ticket in $tickets.items) {
    if ($ticket.assignee_name) {
        Write-Host "  - Ticket: $($ticket.subject)" -ForegroundColor White
        Write-Host "    Assigned to: $($ticket.assignee_name)" -ForegroundColor Green
    }
}

# Test 4: Test assignment API
Write-Host "`n4. Testing ticket assignment:" -ForegroundColor Yellow
$testTicket = $tickets.items | Where-Object { $_.assignee_name -ne $null } | Select-Object -First 1

if ($testTicket) {
    Write-Host "Testing assignment of ticket: $($testTicket.subject)" -ForegroundColor Cyan
    
    # Find Emily Rodriguez
    $emily = $assignableUsers | Where-Object { $_.name -eq "Emily Rodriguez" }
    
    if ($emily) {
        Write-Host "Assigning to Emily Rodriguez (ID: $($emily.id))" -ForegroundColor Cyan
        
        $assignmentData = @{assignee_id = $emily.id} | ConvertTo-Json
        
        try {
            $assignResult = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/tickets/$($testTicket.id)/assign" -Headers @{"Authorization" = "Bearer $token"} -Method PUT -Body $assignmentData -ContentType "application/json"
            
            Write-Host "✓ Assignment successful!" -ForegroundColor Green
            Write-Host "  Ticket now assigned to: $($assignResult.assignee_name)" -ForegroundColor Green
        }
        catch {
            Write-Host "✗ Assignment failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Green
Write-Host "If you see correct names above, the backend is working properly." -ForegroundColor Yellow
Write-Host "The issue is in the frontend - try clearing browser cache or hard refresh (Ctrl+Shift+R)" -ForegroundColor Yellow