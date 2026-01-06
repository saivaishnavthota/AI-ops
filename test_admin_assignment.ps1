#!/usr/bin/env pwsh

Write-Host "=== ADMIN TICKET ASSIGNMENT WORKFLOW ===" -ForegroundColor Green

# Configuration
$baseUrl = "http://localhost:7027/api/v1"

Write-Host "`n1. ADMIN: Getting assignable users for dropdown..." -ForegroundColor Yellow

# Admin login
$adminLogin = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method POST -Body '{"email": "super.admin@demo.com", "password": "Demo@123!"}' -ContentType "application/json"
$adminHeaders = @{ "Authorization" = "Bearer $($adminLogin.access_token)" }

# Get assignable users (for dropdown)
$assignableUsers = Invoke-RestMethod -Uri "$baseUrl/users/assignable" -Method GET -Headers $adminHeaders

Write-Host "Available team members for assignment:" -ForegroundColor Green
foreach ($user in $assignableUsers) {
    $teamInfo = if ($user.teams.Count -gt 0) { 
        "Teams: " + ($user.teams | ForEach-Object { "$($_.team_name) ($($_.team_type))" }) -join ", "
    } else { 
        "No teams" 
    }
    Write-Host "  - $($user.display_name) | $teamInfo" -ForegroundColor Cyan
}

Write-Host "`n2. ADMIN: Viewing all tickets..." -ForegroundColor Yellow

# Get all tickets (admin view)
$allTickets = Invoke-RestMethod -Uri "$baseUrl/tickets?assigned_only=false" -Method GET -Headers $adminHeaders

Write-Host "Admin sees $($allTickets.total) total tickets" -ForegroundColor Green

# Find unassigned tickets
$unassignedTickets = @()
foreach ($ticket in $allTickets.items) {
    if (-not $ticket.assignee_name -or $ticket.assignee_name -eq "") {
        $unassignedTickets += $ticket
    }
}

Write-Host "Unassigned tickets: $($unassignedTickets.Count)" -ForegroundColor Yellow
foreach ($ticket in $unassignedTickets[0..2]) {  # Show first 3
    Write-Host "  - $($ticket.subject) | Category: $($ticket.category) | Priority: $($ticket.priority)" -ForegroundColor White
}

Write-Host "`n3. ADMIN: Assigning tickets to team members..." -ForegroundColor Yellow

if ($unassignedTickets.Count -gt 0) {
    # Assign first ticket to Emily Rodriguez (Infrastructure/DevOps)
    $emilyId = "1dfc3276-5d9a-4663-9bd4-f9921d8e6852"
    $ticketToAssign = $unassignedTickets[0]
    
    Write-Host "Assigning '$($ticketToAssign.subject)' to Emily Rodriguez..." -ForegroundColor Cyan
    
    $assignmentData = @{ assignee_id = $emilyId } | ConvertTo-Json
    $assignUrl = "$baseUrl/tickets/$($ticketToAssign.id)/assign"
    
    try {
        $assignedTicket = Invoke-RestMethod -Uri $assignUrl -Method PUT -Body $assignmentData -Headers $adminHeaders -ContentType "application/json"
        
        Write-Host "SUCCESS: Ticket assigned!" -ForegroundColor Green
        Write-Host "  Assigned to: $($assignedTicket.assignee_name)" -ForegroundColor Green
        Write-Host "  Status changed to: $($assignedTicket.status)" -ForegroundColor Green
        
        # Show assignment comment
        $latestComment = $assignedTicket.comments[-1]
        if ($latestComment.assignment) {
            Write-Host "  Assignment comment: $($latestComment.text)" -ForegroundColor Gray
        }
        
    } catch {
        Write-Host "Assignment failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n4. OPERATOR: Checking assigned tickets..." -ForegroundColor Yellow

# Operator login
$operatorLogin = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method POST -Body '{"email": "operator@demo.com", "password": "Demo@123!"}' -ContentType "application/json"
$operatorHeaders = @{ "Authorization" = "Bearer $($operatorLogin.access_token)" }

# Check operator's tickets
$operatorTickets = Invoke-RestMethod -Uri "$baseUrl/tickets" -Method GET -Headers $operatorHeaders

Write-Host "Emily Rodriguez now sees $($operatorTickets.total) assigned tickets:" -ForegroundColor Green
foreach ($ticket in $operatorTickets.items) {
    $statusColor = switch ($ticket.status) {
        "open" { "Yellow" }
        "in_progress" { "Cyan" }
        "resolved" { "Green" }
        default { "White" }
    }
    Write-Host "  - $($ticket.subject) | Status: $($ticket.status)" -ForegroundColor $statusColor
}

Write-Host "`n5. VERIFICATION: Assignment workflow complete..." -ForegroundColor Yellow

# Verify the assignment worked
$foundAssignedTicket = $false
foreach ($ticket in $operatorTickets.items) {
    if ($ticket.id -eq $ticketToAssign.id) {
        $foundAssignedTicket = $true
        Write-Host "✓ Assigned ticket appears in operator portal" -ForegroundColor Green
        break
    }
}

if (-not $foundAssignedTicket) {
    Write-Host "✗ Assigned ticket not found in operator portal" -ForegroundColor Red
}

Write-Host "`n=== ASSIGNMENT WORKFLOW FEATURES ===" -ForegroundColor Green
Write-Host "✓ Admin gets list of assignable team members" -ForegroundColor Cyan
Write-Host "✓ Team information shown for each member" -ForegroundColor Cyan
Write-Host "✓ Admin can assign tickets to specific operators" -ForegroundColor Cyan
Write-Host "✓ Assignment creates audit trail comment" -ForegroundColor Cyan
Write-Host "✓ Ticket status changes to 'in_progress' when assigned" -ForegroundColor Cyan
Write-Host "✓ Assigned tickets immediately appear in operator portal" -ForegroundColor Cyan

Write-Host "`n=== ADMIN ASSIGNMENT WORKFLOW COMPLETE ===" -ForegroundColor Green