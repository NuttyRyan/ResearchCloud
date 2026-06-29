from __future__ import annotations

from typing import Literal

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


class ResourceUsage(BaseModel):
    used: float
    limit: float
    unit: str


class ProjectUtilization(BaseModel):
    project_ext_id: str
    project_name: str
    vcpus: ResourceUsage
    memory_gib: ResourceUsage
    storage_gib: ResourceUsage


class CostSummary(BaseModel):
    """Cost usage summary - placeholder until NCM Cost Governance is integrated."""

    available: bool = False
    source: str = "NCM Cost Governance"
    currency: str = "USD"
    month_to_date: float | None = None
    forecast: float | None = None
    note: str = ""


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


# --- Phase 2: file shares ---

SharePermissionAccess = Literal["READ_ONLY", "READ_WRITE", "NO_ACCESS"]


class SharePermission(BaseModel):
    principal: str = Field(min_length=1, description="AD user/group or 'Everyone'")
    access: SharePermissionAccess = "READ_WRITE"


class Share(BaseModel):
    ext_id: str
    name: str
    file_server_ext_id: str
    file_server_name: str
    protocol: Literal["SMB", "NFS"]
    size_gib: int
    state: str
    permissions: list[SharePermission] = []


class ShareCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    protocol: Literal["SMB", "NFS"] = "SMB"
    size_gib: int = Field(default=100, ge=1)
    permissions: list[SharePermission] = []


# --- Phase 2: object buckets ---


class Bucket(BaseModel):
    ext_id: str
    name: str
    object_store_ext_id: str
    object_store_name: str
    versioning: bool
    size_gib: int
    state: str


class BucketCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    versioning: bool = False
    size_gib: int = Field(default=100, ge=1)


# --- Phase 6: virtual machines ---

VmPowerState = Literal["ON", "OFF"]
VmPowerActionType = Literal["ON", "OFF", "RESTART"]


class Vm(BaseModel):
    ext_id: str
    name: str
    project_ext_id: str
    project_name: str
    cluster_ext_id: str
    cluster_name: str
    num_vcpus: int
    memory_gib: int
    os: str
    power_state: VmPowerState
    ip_address: str | None = None


class VmCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    project_ext_id: str = Field(min_length=1)
    cluster_ext_id: str = Field(min_length=1)
    num_vcpus: int = Field(default=2, ge=1, le=128)
    memory_gib: int = Field(default=8, ge=1, le=1024)
    os: str = Field(default="Ubuntu 22.04")


class VmPowerAction(BaseModel):
    action: VmPowerActionType
