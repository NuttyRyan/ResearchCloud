from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.catalog import Blueprint, Runbook
from app.schemas.catalog import (
    AppSpec,
    BlueprintCreate,
    BlueprintDetail,
    RunbookCreate,
)
from app.services.blueprint_render import (
    generate_calm_dsl,
    generate_install_script,
    platform_for,
)


def list_blueprints(db: Session) -> list[Blueprint]:
    return list(db.scalars(select(Blueprint).order_by(Blueprint.id)))


def get_blueprint(db: Session, blueprint_id: int) -> Blueprint | None:
    return db.get(Blueprint, blueprint_id)


def get_blueprint_by_name(db: Session, name: str) -> Blueprint | None:
    return db.scalar(select(Blueprint).where(Blueprint.name == name))


def create_blueprint(db: Session, payload: BlueprintCreate) -> Blueprint:
    blueprint = Blueprint(
        name=payload.name,
        description=payload.description,
        os=payload.os,
        num_vcpus=payload.num_vcpus,
        memory_gib=payload.memory_gib,
        apps=[a.model_dump() for a in payload.apps],
    )
    db.add(blueprint)
    db.commit()
    db.refresh(blueprint)
    return blueprint


def delete_blueprint(db: Session, blueprint: Blueprint) -> None:
    db.delete(blueprint)
    db.commit()


def render_install_script(blueprint: Blueprint) -> str:
    apps = [AppSpec(**a) for a in (blueprint.apps or [])]
    return generate_install_script(blueprint.os, apps)


def build_detail(blueprint: Blueprint) -> BlueprintDetail:
    script = render_install_script(blueprint)
    dsl = generate_calm_dsl(
        blueprint.name,
        blueprint.os,
        blueprint.num_vcpus,
        blueprint.memory_gib,
        script,
    )
    return BlueprintDetail(
        id=blueprint.id,
        name=blueprint.name,
        description=blueprint.description,
        os=blueprint.os,
        num_vcpus=blueprint.num_vcpus,
        memory_gib=blueprint.memory_gib,
        apps=[AppSpec(**a) for a in (blueprint.apps or [])],
        created_at=blueprint.created_at,
        updated_at=blueprint.updated_at,
        install_script=script,
        calm_dsl=dsl,
        platform=platform_for(blueprint.os),  # type: ignore[arg-type]
    )


# --- runbooks ---


def list_runbooks(db: Session) -> list[Runbook]:
    return list(db.scalars(select(Runbook).order_by(Runbook.id)))


def get_runbook(db: Session, runbook_id: int) -> Runbook | None:
    return db.get(Runbook, runbook_id)


def get_runbook_by_name(db: Session, name: str) -> Runbook | None:
    return db.scalar(select(Runbook).where(Runbook.name == name))


def create_runbook(db: Session, payload: RunbookCreate) -> Runbook:
    runbook = Runbook(
        name=payload.name,
        description=payload.description,
        os=payload.os,
        script=payload.script,
    )
    db.add(runbook)
    db.commit()
    db.refresh(runbook)
    return runbook


def create_runbook_from_blueprint(
    db: Session, blueprint: Blueprint, name: str, description: str
) -> Runbook:
    runbook = Runbook(
        name=name,
        description=description or f"Generated from blueprint '{blueprint.name}'",
        os=blueprint.os,
        script=render_install_script(blueprint),
        source_blueprint_id=blueprint.id,
    )
    db.add(runbook)
    db.commit()
    db.refresh(runbook)
    return runbook


def delete_runbook(db: Session, runbook: Runbook) -> None:
    db.delete(runbook)
    db.commit()
