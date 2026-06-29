from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

AppInstallMethod = Literal["URL", "INLINE"]


class AppSpec(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    method: AppInstallMethod = "URL"
    # For URL installs: a script/installer URL to download and run.
    url: str = ""
    # For INLINE installs: a raw shell/PowerShell snippet.
    script: str = ""


class BlueprintBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str = ""
    os: str = Field(default="Ubuntu 22.04", max_length=100)
    num_vcpus: int = Field(default=2, ge=1, le=128)
    memory_gib: int = Field(default=8, ge=1, le=1024)
    apps: list[AppSpec] = []


class BlueprintCreate(BlueprintBase):
    pass


class BlueprintOut(BlueprintBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class BlueprintDetail(BlueprintOut):
    # Generated artifacts (computed on read).
    install_script: str
    calm_dsl: str
    platform: Literal["linux", "windows"]


class RunbookCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str = ""
    os: str = Field(default="Ubuntu 22.04", max_length=100)
    script: str = Field(min_length=1)


class RunbookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    os: str
    script: str
    source_blueprint_id: int | None
    created_at: datetime
