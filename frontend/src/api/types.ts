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
