import type {
  AppSpec,
  Blueprint,
  BlueprintDetail,
  Bucket,
  Cluster,
  Connection,
  ConnectionCreate,
  ConnectionTestResult,
  CostSummary,
  FileServer,
  ObjectStore,
  Project,
  ProjectUtilization,
  Runbook,
  Share,
  SharePermission,
  UserOut,
  Vm,
  VmPowerActionType,
} from './types';

const TOKEN_KEY = 'rc_token';

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null): void {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers);
  const token = getToken();
  if (token) headers.set('Authorization', `Bearer ${token}`);
  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const resp = await fetch(`/api${path}`, { ...options, headers });
  if (resp.status === 204) return undefined as T;

  const text = await resp.text();
  const data = text ? JSON.parse(text) : undefined;
  if (!resp.ok) {
    const detail = data?.detail ?? resp.statusText;
    const message = Array.isArray(detail)
      ? detail.map((d: { msg?: string }) => d.msg ?? JSON.stringify(d)).join(', ')
      : String(detail);
    throw new ApiError(resp.status, message);
  }
  return data as T;
}

export const api = {
  async login(username: string, password: string): Promise<string> {
    const body = new URLSearchParams({ username, password });
    const resp = await fetch('/api/auth/login', { method: 'POST', body });
    if (!resp.ok) {
      throw new ApiError(resp.status, 'Incorrect username or password');
    }
    const data = (await resp.json()) as { access_token: string };
    return data.access_token;
  },

  me: () => request<UserOut>('/auth/me'),

  health: () => request<{ status: string; mode: string }>('/health'),

  listConnections: () => request<Connection[]>('/connections'),
  createConnection: (payload: ConnectionCreate) =>
    request<Connection>('/connections', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  deleteConnection: (id: number) =>
    request<void>(`/connections/${id}`, { method: 'DELETE' }),
  testConnection: (id: number) =>
    request<ConnectionTestResult>(`/connections/${id}/test`, { method: 'POST' }),

  listClusters: (cid: number) =>
    request<Cluster[]>(`/connections/${cid}/clusters`),

  listProjects: (cid: number) => request<Project[]>(`/connections/${cid}/projects`),
  getProjectUtilization: (cid: number) =>
    request<ProjectUtilization[]>(`/connections/${cid}/projects/utilization`),
  getCostSummary: (cid: number) =>
    request<CostSummary>(`/connections/${cid}/cost/summary`),
  createProject: (cid: number, payload: { name: string; description: string }) =>
    request<Project>(`/connections/${cid}/projects`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  listFileServers: (cid: number) =>
    request<FileServer[]>(`/connections/${cid}/files`),
  createFileServer: (
    cid: number,
    payload: { name: string; cluster_ext_id: string; size_gib: number },
  ) =>
    request<FileServer>(`/connections/${cid}/files`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  listObjectStores: (cid: number) =>
    request<ObjectStore[]>(`/connections/${cid}/objects`),
  createObjectStore: (
    cid: number,
    payload: { name: string; cluster_ext_id: string; capacity_gib: number },
  ) =>
    request<ObjectStore>(`/connections/${cid}/objects`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  listShares: (cid: number, fsExtId: string) =>
    request<Share[]>(`/connections/${cid}/files/${fsExtId}/shares`),
  createShare: (
    cid: number,
    fsExtId: string,
    payload: {
      name: string;
      protocol: 'SMB' | 'NFS';
      size_gib: number;
      permissions: SharePermission[];
    },
  ) =>
    request<Share>(`/connections/${cid}/files/${fsExtId}/shares`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  listBuckets: (cid: number, osExtId: string) =>
    request<Bucket[]>(`/connections/${cid}/objects/${osExtId}/buckets`),
  createBucket: (
    cid: number,
    osExtId: string,
    payload: { name: string; versioning: boolean; size_gib: number },
  ) =>
    request<Bucket>(`/connections/${cid}/objects/${osExtId}/buckets`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  listVms: (cid: number, projectExtId?: string) => {
    const qs = projectExtId ? `?project=${encodeURIComponent(projectExtId)}` : '';
    return request<Vm[]>(`/connections/${cid}/vms${qs}`);
  },
  createVm: (
    cid: number,
    payload: {
      name: string;
      project_ext_id: string;
      cluster_ext_id: string;
      num_vcpus: number;
      memory_gib: number;
      os: string;
    },
  ) =>
    request<Vm>(`/connections/${cid}/vms`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  setVmPower: (cid: number, vmExtId: string, action: VmPowerActionType) =>
    request<Vm>(`/connections/${cid}/vms/${vmExtId}/power`, {
      method: 'POST',
      body: JSON.stringify({ action }),
    }),
  deleteVm: (cid: number, vmExtId: string) =>
    request<void>(`/connections/${cid}/vms/${vmExtId}`, { method: 'DELETE' }),

  // Self-service: blueprints & runbooks (app-level, not connection-scoped).
  listBlueprints: () => request<Blueprint[]>('/blueprints'),
  getBlueprint: (id: number) => request<BlueprintDetail>(`/blueprints/${id}`),
  createBlueprint: (payload: {
    name: string;
    description: string;
    os: string;
    num_vcpus: number;
    memory_gib: number;
    apps: AppSpec[];
  }) =>
    request<BlueprintDetail>('/blueprints', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  deleteBlueprint: (id: number) =>
    request<void>(`/blueprints/${id}`, { method: 'DELETE' }),
  createRunbookFromBlueprint: (
    id: number,
    payload: { name: string; description: string },
  ) =>
    request<Runbook>(`/blueprints/${id}/runbook`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  listRunbooks: () => request<Runbook[]>('/runbooks'),
  getRunbook: (id: number) => request<Runbook>(`/runbooks/${id}`),
  createRunbook: (payload: {
    name: string;
    description: string;
    os: string;
    script: string;
  }) =>
    request<Runbook>('/runbooks', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  deleteRunbook: (id: number) =>
    request<void>(`/runbooks/${id}`, { method: 'DELETE' }),
};
