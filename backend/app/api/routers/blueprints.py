from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.deps import DbSession, get_current_user
from app.models.catalog import Blueprint, Runbook
from app.schemas.catalog import (
    BlueprintCreate,
    BlueprintDetail,
    BlueprintOut,
    RunbookCreate,
    RunbookOut,
)
from app.services import blueprint_service

router = APIRouter(tags=["self-service"], dependencies=[Depends(get_current_user)])


def _get_blueprint_or_404(blueprint_id: int, db: DbSession) -> Blueprint:
    bp = blueprint_service.get_blueprint(db, blueprint_id)
    if bp is None:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    return bp


def _get_runbook_or_404(runbook_id: int, db: DbSession) -> Runbook:
    rb = blueprint_service.get_runbook(db, runbook_id)
    if rb is None:
        raise HTTPException(status_code=404, detail="Runbook not found")
    return rb


# --- blueprints ---


@router.get("/api/blueprints", response_model=list[BlueprintOut])
def list_blueprints(db: DbSession) -> list[Blueprint]:
    return blueprint_service.list_blueprints(db)


@router.post(
    "/api/blueprints", response_model=BlueprintDetail, status_code=status.HTTP_201_CREATED
)
def create_blueprint(payload: BlueprintCreate, db: DbSession) -> BlueprintDetail:
    if blueprint_service.get_blueprint_by_name(db, payload.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Blueprint '{payload.name}' already exists",
        )
    bp = blueprint_service.create_blueprint(db, payload)
    return blueprint_service.build_detail(bp)


@router.get("/api/blueprints/{blueprint_id}", response_model=BlueprintDetail)
def get_blueprint(blueprint: Blueprint = Depends(_get_blueprint_or_404)) -> BlueprintDetail:
    return blueprint_service.build_detail(blueprint)


@router.delete("/api/blueprints/{blueprint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blueprint(
    db: DbSession, blueprint: Blueprint = Depends(_get_blueprint_or_404)
) -> None:
    blueprint_service.delete_blueprint(db, blueprint)


class RunbookFromBlueprint(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str = ""


@router.post(
    "/api/blueprints/{blueprint_id}/runbook",
    response_model=RunbookOut,
    status_code=status.HTTP_201_CREATED,
)
def create_runbook_from_blueprint(
    payload: RunbookFromBlueprint,
    db: DbSession,
    blueprint: Blueprint = Depends(_get_blueprint_or_404),
) -> Runbook:
    if blueprint_service.get_runbook_by_name(db, payload.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Runbook '{payload.name}' already exists",
        )
    return blueprint_service.create_runbook_from_blueprint(
        db, blueprint, payload.name, payload.description
    )


# --- runbooks ---


@router.get("/api/runbooks", response_model=list[RunbookOut])
def list_runbooks(db: DbSession) -> list[Runbook]:
    return blueprint_service.list_runbooks(db)


@router.post("/api/runbooks", response_model=RunbookOut, status_code=status.HTTP_201_CREATED)
def create_runbook(payload: RunbookCreate, db: DbSession) -> Runbook:
    if blueprint_service.get_runbook_by_name(db, payload.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Runbook '{payload.name}' already exists",
        )
    return blueprint_service.create_runbook(db, payload)


@router.get("/api/runbooks/{runbook_id}", response_model=RunbookOut)
def get_runbook(runbook: Runbook = Depends(_get_runbook_or_404)) -> Runbook:
    return runbook


@router.delete("/api/runbooks/{runbook_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_runbook(
    db: DbSession, runbook: Runbook = Depends(_get_runbook_or_404)
) -> None:
    blueprint_service.delete_runbook(db, runbook)
