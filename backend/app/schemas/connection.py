from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConnectionBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    host: str = Field(min_length=1, max_length=255)
    port: int = Field(default=9440, ge=1, le=65535)
    username: str = Field(min_length=1, max_length=150)
    verify_ssl: bool = False


class ConnectionCreate(ConnectionBase):
    secret: str = Field(min_length=1, description="Password or API key (stored encrypted)")


class ConnectionUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=150)
    host: str | None = Field(default=None, max_length=255)
    port: int | None = Field(default=None, ge=1, le=65535)
    username: str | None = Field(default=None, max_length=150)
    secret: str | None = Field(default=None)
    verify_ssl: bool | None = None


class ConnectionOut(ConnectionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ConnectionTestResult(BaseModel):
    ok: bool
    message: str
    prism_central_version: str | None = None
    cluster_count: int | None = None
    mode: str = "mock"
