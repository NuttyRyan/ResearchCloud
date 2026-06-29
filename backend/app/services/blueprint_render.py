from __future__ import annotations

import re

from app.schemas.catalog import AppSpec


def platform_for(os_name: str) -> str:
    """Return 'windows' or 'linux' based on the OS name."""

    return "windows" if "windows" in os_name.lower() else "linux"


def _slug(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_]+", "_", name).strip("_").lower()
    return slug or "app"


def _class_name(name: str) -> str:
    parts = re.split(r"[^a-zA-Z0-9]+", name)
    cleaned = "".join(p.capitalize() for p in parts if p)
    if not cleaned or not cleaned[0].isalpha():
        cleaned = f"Bp{cleaned}"
    return cleaned


def _linux_app_block(app: AppSpec) -> str:
    slug = _slug(app.name)
    if app.method == "URL":
        if not app.url:
            return f'echo "Skipping {app.name}: no URL provided"'
        return (
            f'echo "==> Installing {app.name} from {app.url}"\n'
            f'curl -fsSL "{app.url}" -o "/tmp/install_{slug}.sh"\n'
            f'chmod +x "/tmp/install_{slug}.sh"\n'
            f'bash "/tmp/install_{slug}.sh"'
        )
    return f'echo "==> Installing {app.name}"\n{app.script.strip()}'


def _windows_app_block(app: AppSpec) -> str:
    slug = _slug(app.name)
    if app.method == "URL":
        if not app.url:
            return f'Write-Host "Skipping {app.name}: no URL provided"'
        return (
            f'Write-Host "==> Installing {app.name} from {app.url}"\n'
            f'Invoke-WebRequest -Uri "{app.url}" -OutFile "$env:TEMP\\install_{slug}.ps1"\n'
            f'& "$env:TEMP\\install_{slug}.ps1"'
        )
    return f'Write-Host "==> Installing {app.name}"\n{app.script.strip()}'


def generate_install_script(os_name: str, apps: list[AppSpec]) -> str:
    """Render a bash or PowerShell install script for the given OS and apps."""

    if platform_for(os_name) == "windows":
        header = (
            "# ResearchCloud generated install script (PowerShell)\n"
            f"# Target OS: {os_name}\n"
            "$ErrorActionPreference = 'Stop'\n"
        )
        body = "\n\n".join(_windows_app_block(a) for a in apps)
        footer = '\nWrite-Host "All applications installed."'
        return header + ("\n" + body if body else "") + footer

    header = (
        "#!/usr/bin/env bash\n"
        "# ResearchCloud generated install script (bash)\n"
        f"# Target OS: {os_name}\n"
        "set -euo pipefail\n"
    )
    body = "\n\n".join(_linux_app_block(a) for a in apps)
    footer = '\necho "All applications installed."'
    return header + ("\n" + body if body else "") + footer


def generate_calm_dsl(
    name: str, os_name: str, num_vcpus: int, memory_gib: int, install_script: str
) -> str:
    """Render a NCM Self-Service (Calm) DSL blueprint scaffold.

    This is a generated starting point - refine and validate with `calm compile bp`.
    """

    cls = _class_name(name)
    is_windows = platform_for(os_name) == "windows"
    task = "CalmTask.Exec.powershell" if is_windows else "CalmTask.Exec.ssh"
    cred = "WINDOWS_CRED" if is_windows else "LINUX_CRED"

    return f'''"""ResearchCloud-generated NCM Self-Service (Calm) DSL blueprint: {name}.

Generated starting point - review credentials/image refs and validate with:
    calm compile bp --file {_slug(name)}_blueprint.py
"""
from calm.dsl.builtins import (
    Service,
    Package,
    Substrate,
    Deployment,
    Profile,
    Blueprint,
    CalmTask,
    action,
    ref,
)

INSTALL_SCRIPT = r"""
{install_script}
"""


class {cls}Service(Service):
    """Application service for {name}."""


class {cls}Package(Package):
    services = [ref({cls}Service)]

    @action
    def __install__():  # noqa: N807
        {task}(name="InstallApps", script=INSTALL_SCRIPT, cred=ref({cred}))


class {cls}Substrate(Substrate):
    os_type = "{"Windows" if is_windows else "Linux"}"
    provider_type = "AHV_VM"
    # TODO: point at a real AHV VM spec (image, NIC, sizing below as guidance).
    # vCPUs: {num_vcpus}, Memory: {memory_gib} GiB


class {cls}Deployment(Deployment):
    packages = [ref({cls}Package)]
    substrate = ref({cls}Substrate)


class DefaultProfile(Profile):
    deployments = [ref({cls}Deployment)]


class {cls}Blueprint(Blueprint):
    """{name}"""

    profiles = [ref(DefaultProfile)]
    services = [ref({cls}Service)]
    packages = [ref({cls}Package)]
    substrates = [ref({cls}Substrate)]
'''
