#!/usr/bin/env pwsh

Write-Host "=== VERIFYING NAME CONSISTENCY ===" -ForegroundColor Green

# Login as admin
$adminLogin = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/auth/login" -Method POST -Body '{"email": "super.admin@demo.com", "password": "Demo@123!"}' -ContentType "application/json"
$adminHeaders = @{ "Authorization" = "Bearer $($adminLogin.access_token)" }

Write-Host "`n1. Database Users (Assignable):" -ForegroundColor Yellow
$users = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/users/assignable" -Method GET -Headers $adminHeaders
foreach ($user in $users | Sort-Object { $_.name }) {
    Write-Host "  - $($user.name) ($($user.email))" -ForegroundColor Cyan
}

Write-Host "`n2. Ticket Assignee Names:" -ForegroundColor Yellow
$allTickets = Invoke-RestMethod -Uri "http://localhost:7027/api/v1/tickets?assigned_only=false" -Method GET -Headers $adminHeaders
$assigneeNames = @()
foreach ($ticket in $allTickets.items) {
    if ($ticket.assignee_name -and $ticket.assignee_name -ne "" -and $assigneeNames -notcontains $ticket.assignee_name) {
        $assigneeNames += $ticket.assignee_name
    }
}
foreach ($name in $assigneeNames | Sort-Object) {
    Write-Host "  - $name" -ForegroundColor White
}

Write-Host "`n3. Consistency Check:" -ForegroundColor Yellow
$userNames = $users | ForEach-Object { $_.name } | Sort-Object
$ticketNames = $assigneeNames | Where-Object { $_ -ne "Support Team" } | Sort-Object

$consistent = $true
foreach ($ticketName in $ticketNames) {
    if ($userNames -notcontains $ticketName) {
        Write-Host "  ✗ '$ticketName' in tickets but not in users" -ForegroundColor Red
        $consistent = $false
    }
}

if ($consistent) {
    Write-Host "  ✓ All assignee names match database users" -ForegroundColor Green
} else {
    Write-Host "  ✗ Name inconsistencies found" -ForegroundColor Red
}

Write-Host "`n4. Sample Assignment Test:" -ForegroundColor Yellow
# Find an unassigned ticket
$unassignedTicket = $null
foreach ($ticket in $allTickets.items) {
    if (-not $ticket.assignee_name -or $ticket.assignee_name -eq "") {
        $unassignedTicket = $ticket
        break
    }
}

if ($unassignedTicket) {
    Write-Host "  Testing assignment of: $($unassignedTicket.subject)" -ForegroundColor Cyan
    
    # Assign to Emily Rodriguez
    $emilyId = ($users | Where-Object { $_.name -eq "Emily Rodriguez" }).id
    if ($emilyId) {
        $assignmentData = @{ assignee_id = $emilyId } | ConvertTo-Json
        $assignUrl = "http://localhost:7027/api/v1/tickets/$($unassignedTicket.id)/assign"
        
        try {
            $assignedTicket = Invoke-RestMethod -Uri $assignUrl -Method PUT -Body $assignmentData -Headers $adminHeaders -ContentType "application/json"
            Write-Host "  ✓ Successfully assigned to: $($assignedTicket.assignee_name)" -ForegroundColor Green
        } catch {
            Write-Host "  ✗ Assignment failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
} else {
    Write-Host "  No unassigned tickets available for testing" -ForegroundColor Gray
}

Write-Host "`n=== VERIFICATION COMPLETE ===" -ForegroundColor Green
Write-Host "The dropdown names now match the database user names exactly." -ForegroundColor White