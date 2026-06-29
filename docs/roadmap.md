# ResearchCloud Roadmap

ResearchCloud is delivered in phases. Phase 1 establishes the foundation and a runnable
vertical slice; later phases build out the full feature set from the product vision.

## Phase 1 - Foundation + vertical slice (delivered)

- [x] Monorepo scaffold (frontend, backend, deploy, infra) with lint/test/build tooling
- [x] Prism Central connection management (CRUD + test, credentials encrypted at rest)
- [x] `NutanixClient` abstraction with mock + live (v4 REST) providers
- [x] Create & manage Nutanix Projects
- [x] Deploy Nutanix Files
- [x] Deploy Nutanix Objects
- [x] Nutanix-themed UI (purple `#7855fa`, charcoal, rounded typography)
- [x] Docker images + Helm chart for Nutanix NKP (HA)

## Phase 2 - Storage + provisioning depth

- [ ] Create file shares (select Files cluster, set permissions)
- [ ] Create buckets in object stores
- [ ] Wire Terraform / Calm DSL provisioners for real create paths

## Phase 3 - Self-Service + consoles

- [ ] Self-Service blueprint builder (OS, applications)
- [ ] Dynamic install from a URL -> generated bash / PowerShell scripts
- [ ] Runbooks (repeatable, selectable by other users) generated as Calm DSL
- [ ] VNC console for VMs in a user's project (WebSocket proxy to Prism)

## Phase 4 - Identity + network security

- [ ] User management linked to Active Directory groups & Projects (IAM / LDAP)
- [ ] Flow microsegmentation management UI (`microseg` v4 namespace)

## Notes on Nutanix APIs

- v4 REST APIs are GA and the recommended integration surface; legacy v1-v3 deprecate
  in Q4 2026.
- Full Projects support in v4 is expected mid-2026, so Projects currently use the v3 API
  in the live client.
- Calm DSL / NCM Self-Service DSL is Python-based and actively maintained, which informs
  the choice of a Python backend.
