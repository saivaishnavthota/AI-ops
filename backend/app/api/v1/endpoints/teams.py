from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, func, select, update, delete
from typing import Optional
from uuid import UUID

from app.api.v1.deps import CurrentUser, DBSession
from app.models import Team, TeamMember, User
from app.schemas.team import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamListResponse,
    TeamMemberCreate,
    TeamMemberUpdate,
)

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("", response_model=TeamListResponse)
async def list_teams(
    db: DBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """List all teams for the organization."""
    # Simple query first to test
    result = await db.execute(
        select(Team)
        .where(Team.organization_id == current_user.organization_id)
        .order_by(desc(Team.created_at))
        .offset(skip)
        .limit(limit)
    )
    teams = result.scalars().all()
    
    # Get total count
    count_result = await db.execute(
        select(func.count(Team.id))
        .where(Team.organization_id == current_user.organization_id)
    )
    total = count_result.scalar()
    
    # Build response with member counts
    items = []
    for team in teams:
        # Get member count for this team
        member_count_result = await db.execute(
            select(func.count(TeamMember.id)).where(TeamMember.team_id == team.id)
        )
        member_count = member_count_result.scalar() or 0
        print(f"DEBUG: Team {team.name} (ID: {team.id}) has {member_count} members")
        
        team_dict = {
            "id": str(team.id),
            "organization_id": str(team.organization_id),
            "name": team.name,
            "description": team.description,
            "team_type": team.team_type,
            "settings": team.settings or {},
            "is_active": team.is_active,
            "created_at": team.created_at,
            "updated_at": team.updated_at,
            "member_count": member_count,
        }
        items.append(team_dict)
    
    # Calculate pagination fields
    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit  # Ceiling division
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": limit,
        "pages": pages,
    }


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_in: TeamCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    """Create a new team."""
    team = Team(
        organization_id=current_user.organization_id,
        **team_in.dict(),
    )
    db.add(team)
    await db.commit()
    await db.refresh(team)
    
    team_dict = {
        "id": str(team.id),
        "organization_id": str(team.organization_id),
        "name": team.name,
        "description": team.description,
        "team_type": team.team_type,
        "settings": team.settings or {},  # Add settings field
        "is_active": team.is_active,
        "created_at": team.created_at,
        "updated_at": team.updated_at,
        "member_count": 0,
    }
    return team_dict


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """Get a specific team."""
    result = await db.execute(
        select(Team).where(
            Team.id == team_id,
            Team.organization_id == current_user.organization_id,
        )
    )
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    
    # Get member count
    member_count_result = await db.execute(
        select(func.count(TeamMember.id)).where(TeamMember.team_id == team.id)
    )
    member_count = member_count_result.scalar()
    
    # Get on-call member
    on_call_result = await db.execute(
        select(User.full_name)
        .select_from(TeamMember)
        .join(User)
        .where(
            TeamMember.team_id == team.id,
            TeamMember.is_on_call == True,
        )
    )
    on_call_person = on_call_result.scalar_one_or_none()
    
    team_dict = {
        "id": str(team.id),
        "organization_id": str(team.organization_id),
        "name": team.name,
        "description": team.description,
        "team_type": team.team_type,
        "settings": team.settings or {},  # Add settings field
        "is_active": team.is_active,
        "created_at": team.created_at,
        "updated_at": team.updated_at,
        "member_count": member_count,
    }
    return team_dict


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: UUID,
    team_in: TeamUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    """Update a team."""
    result = await db.execute(
        select(Team).where(
            Team.id == team_id,
            Team.organization_id == current_user.organization_id,
        )
    )
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    
    update_data = team_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(team, field, value)
    
    await db.commit()
    await db.refresh(team)
    
    # Get member count
    member_count_result = await db.execute(
        select(func.count(TeamMember.id)).where(TeamMember.team_id == team.id)
    )
    member_count = member_count_result.scalar()
    
    team_dict = {
        "id": str(team.id),
        "organization_id": str(team.organization_id),
        "name": team.name,
        "description": team.description,
        "team_type": team.team_type,
        "settings": team.settings or {},  # Add settings field
        "is_active": team.is_active,
        "created_at": team.created_at,
        "updated_at": team.updated_at,
        "member_count": member_count,
    }
    return team_dict


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """Delete a team."""
    result = await db.execute(
        select(Team).where(
            Team.id == team_id,
            Team.organization_id == current_user.organization_id,
        )
    )
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    
    await db.execute(delete(Team).where(Team.id == team_id))
    await db.commit()


@router.get("/{team_id}/members")
async def list_team_members(
    team_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """List all members of a team."""
    result = await db.execute(
        select(Team).where(
            Team.id == team_id,
            Team.organization_id == current_user.organization_id,
        )
    )
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    
    members_result = await db.execute(
        select(TeamMember, User)
        .select_from(TeamMember)
        .join(User)
        .where(TeamMember.team_id == team_id)
    )
    members = members_result.all()
    
    items = []
    for member, user in members:
        items.append({
            "id": str(member.id),
            "user_id": str(user.id),
            "name": user.full_name,
            "email": user.email,
            "role": member.role,
            "is_on_call": member.is_on_call,
        })
    
    return {"items": items}


@router.post("/{team_id}/members", status_code=status.HTTP_201_CREATED)
async def add_team_member(
    team_id: UUID,
    member_in: TeamMemberCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    """Add a member to a team."""
    result = await db.execute(
        select(Team).where(
            Team.id == team_id,
            Team.organization_id == current_user.organization_id,
        )
    )
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    
    # Check if user exists
    user_result = await db.execute(
        select(User).where(
            User.id == member_in.user_id,
            User.organization_id == current_user.organization_id,
        )
    )
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if already a member
    existing_result = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == member_in.user_id,
        )
    )
    existing = existing_result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this team",
        )
    
    member = TeamMember(
        team_id=team_id,
        **member_in.dict(),
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    
    return {
        "id": str(member.id),
        "user_id": str(user.id),
        "name": user.full_name,
        "email": user.email,
        "role": member.role,
        "is_on_call": member.is_on_call,
    }


@router.put("/{team_id}/members/{member_id}")
async def update_team_member(
    team_id: UUID,
    member_id: UUID,
    member_in: TeamMemberUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    """Update a team member."""
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.id == member_id,
            TeamMember.team_id == team_id,
        )
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found",
        )
    
    update_data = member_in.dict(exclude_unset=True)
    
    # If setting on-call, remove on-call from other members
    if update_data.get("is_on_call"):
        await db.execute(
            update(TeamMember)
            .where(
                TeamMember.team_id == team_id,
                TeamMember.id != member_id,
            )
            .values(is_on_call=False)
        )
    
    for field, value in update_data.items():
        setattr(member, field, value)
    
    await db.commit()
    await db.refresh(member)
    
    user_result = await db.execute(select(User).where(User.id == member.user_id))
    user = user_result.scalar_one()
    
    return {
        "id": str(member.id),
        "user_id": str(user.id),
        "name": user.full_name,
        "email": user.email,
        "role": member.role,
        "is_on_call": member.is_on_call,
    }


@router.delete("/{team_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_member(
    team_id: UUID,
    member_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """Remove a member from a team."""
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.id == member_id,
            TeamMember.team_id == team_id,
        )
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found",
        )
    
    await db.execute(delete(TeamMember).where(TeamMember.id == member_id))
    await db.commit()