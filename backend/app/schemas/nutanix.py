from __future__ import annotations

from pydantic import BaseModel, Field


class Cluster(BaseModel):
    ext_id: str
    name: str
    hypervisor: str
    node_count: int


class Project(BaseModel):
    ext_id: str
    name: str
    description: str = ""
    state: str = "ACTIVE"
    vm_count: int = 0


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str = ""


class FileServer(BaseModel):
    ext_id: str
    name: str
    cluster_ext_id: str
    cluster_name: str
    size_gib: int
    state: str
    version: str


class FileServerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    cluster_ext_id: str = Field(min_length=1)
    size_gib: int = Field(default=1024, ge=1024)


class ObjectStore(BaseModel):
    ext_id: str
    name: str
    cluster_ext_id: str
    cluster_name: str
    capacity_gib: int
    state: str
    endpoint: str


class ObjectStoreCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    cluster_ext_id: str = Field(min_length=1)
    capacity_gib: int = Field(default=2048, ge=1024)
