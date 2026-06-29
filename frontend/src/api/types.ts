export interface UserOut {
  username: string;
  is_admin: boolean;
  ad_groups: string[];
}

export interface Connection {
  id: number;
  name: string;
  host: string;
  port: number;
  username: string;
  verify_ssl: boolean;
  created_at: string;
  updated_at: string;
}

export interface ConnectionCreate {
  name: string;
  host: string;
  port: number;
  username: string;
  secret: string;
  verify_ssl: boolean;
}

export interface ConnectionTestResult {
  ok: boolean;
  message: string;
  prism_central_version: string | null;
  cluster_count: number | null;
  mode: string;
}

export interface Cluster {
  ext_id: string;
  name: string;
  hypervisor: string;
  node_count: number;
}

export interface Project {
  ext_id: string;
  name: string;
  description: string;
  state: string;
  vm_count: number;
}

export interface FileServer {
  ext_id: string;
  name: string;
  cluster_ext_id: string;
  cluster_name: string;
  size_gib: number;
  state: string;
  version: string;
}

export interface ObjectStore {
  ext_id: string;
  name: string;
  cluster_ext_id: string;
  cluster_name: string;
  capacity_gib: number;
  state: string;
  endpoint: string;
}

export type ShareAccess = 'READ_ONLY' | 'READ_WRITE' | 'NO_ACCESS';

export interface SharePermission {
  principal: string;
  access: ShareAccess;
}

export interface Share {
  ext_id: string;
  name: string;
  file_server_ext_id: string;
  file_server_name: string;
  protocol: 'SMB' | 'NFS';
  size_gib: number;
  state: string;
  permissions: SharePermission[];
}

export interface Bucket {
  ext_id: string;
  name: string;
  object_store_ext_id: string;
  object_store_name: string;
  versioning: boolean;
  size_gib: number;
  state: string;
}

export type AppInstallMethod = 'URL' | 'INLINE';

export interface AppSpec {
  name: string;
  method: AppInstallMethod;
  url: string;
  script: string;
}

export interface Blueprint {
  id: number;
  name: string;
  description: string;
  os: string;
  num_vcpus: number;
  memory_gib: number;
  apps: AppSpec[];
  created_at: string;
  updated_at: string;
}

export interface BlueprintDetail extends Blueprint {
  install_script: string;
  calm_dsl: string;
  platform: 'linux' | 'windows';
}

export interface Runbook {
  id: number;
  name: string;
  description: string;
  os: string;
  script: string;
  source_blueprint_id: number | null;
  created_at: string;
}

export type VmPowerState = 'ON' | 'OFF';
export type VmPowerActionType = 'ON' | 'OFF' | 'RESTART';

export interface Vm {
  ext_id: string;
  name: string;
  project_ext_id: string;
  project_name: string;
  cluster_ext_id: string;
  cluster_name: string;
  num_vcpus: number;
  memory_gib: number;
  os: string;
  power_state: VmPowerState;
  ip_address: string | null;
}
