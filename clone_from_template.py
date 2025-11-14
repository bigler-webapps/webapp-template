#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
from pathlib import Path
import getpass

# -------------------------------------------------------------------
# Template-specific constants
# -------------------------------------------------------------------

# Django project/package name in the TEMPLATE backend
# -> backend/project_template_app/settings.py, urls.py, ...
TEMPLATE_DJANGO_NAME = "project_template_app"

# Default ports used in the template (adjust if your template uses others)
TEMPLATE_WEB_PORT = "8125"
TEMPLATE_DB_PORT = "5435"

# Directories that should not be copied/processed deeply
IGNORE_DIRS = {
    ".git",
    "node_modules",
    "build",
    "dist",
    "__pycache__",
    "staticfiles",
    ".venv",
}

# File extensions that should be processed for text replacement
TEXT_FILE_EXTS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".yml",
    ".yaml",
    ".env",
    ".toml",
    ".md",
    ".html",
    ".css",
    ".scss",
    ".txt",
}

# File names without extension that we still want to process
TEXT_FILE_NAMES = {
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.override.yml",
    ".env",
    "migrate.cmd",
}

# Django apps whose migrations should be copied back from the container
MIGRATION_APPS = [
    "users",
    # "structure",
    # "calculate",
    # "live_sync",
    # "utils",
]


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def run_command(cmd, cwd=None, env=None, description=None):
    """Runs a subprocess command and raises on error."""
    desc = description or (cmd if isinstance(cmd, str) else " ".join(cmd))
    print(f"\n>> {desc}")
    print("   ", cmd if isinstance(cmd, str) else " ".join(cmd))

    # simple wrapper; no shell=True by default
    result = subprocess.run(cmd, cwd=cwd, env=env)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed ({desc}) with exit code {result.returncode}")
    return result


def copy_template(template_path: Path, target_path: Path) -> None:
    """Copies the whole template directory to the new app directory."""
    if target_path.exists():
        raise RuntimeError(f"Target path already exists: {target_path}")

    print(f">> Copying template from {template_path} -> {target_path}")
    shutil.copytree(
        template_path,
        target_path,
        ignore=shutil.ignore_patterns(*[f"{d}" for d in IGNORE_DIRS]),
    )


def rename_django_package(target_path: Path, new_name: str) -> None:
    """Renames the Django project package directory in backend."""
    backend_dir = target_path / "backend"
    old_pkg_dir = backend_dir / TEMPLATE_DJANGO_NAME
    new_pkg_name = f"{new_name}_app"
    new_pkg_dir = backend_dir / new_pkg_name

    if old_pkg_dir.exists():
        print(f">> Renaming Django package {old_pkg_dir.name} -> {new_pkg_name}")
        old_pkg_dir.rename(new_pkg_dir)
    else:
        print(f">> Django package {TEMPLATE_DJANGO_NAME} not found, skipping rename.")


def should_process_file(path: Path) -> bool:
    """Returns True if file should be opened and processed for text replacements."""
    if path.is_dir():
        return False
    if path.suffix in TEXT_FILE_EXTS:
        return True
    if path.name in TEXT_FILE_NAMES:
        return True
    return False


def replace_in_file(path: Path, replacements: list[tuple[str, str]]) -> None:
    """Replaces all given string pairs in the file if needed."""
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Skips non-text files
        return

    original_text = text
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new)

    if text != original_text:
        path.write_text(text, encoding="utf-8")


def process_files(target_path: Path, new_name: str, web_port: str, db_port: str) -> None:
    """
    Walks through the copied project and applies replacements.

    Naming conventions in the template:
    - Django package: project_template_app
    - Service/container/human project name: project_template
    - Placeholder: PROJECT_NAME
    """
    new_django_name = f"{new_name}_app"

    replacements = [
        # Django project/package name: project_template_app -> {new_name}_app
        ("project_template_app", new_django_name),

        # Container-/Service-Name:
        # django_backend_project_template_app -> django_backend_{new_name}
        ("django_backend_project_template_app", f"django_backend_{new_name}"),

        # Projekt-Slug / Image-Namen o.Ä.
        ("project_template", new_name),

        # Expliziter Platzhalter:
        ("PROJECT_NAME", new_name),

        # Ports
        (TEMPLATE_WEB_PORT, web_port),
        (TEMPLATE_DB_PORT, db_port),
    ]

    print(">> Applying text replacements (name, ports, etc.)")
    for root, dirs, files in os.walk(target_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file_name in files:
            file_path = Path(root) / file_name
            if should_process_file(file_path):
                replace_in_file(file_path, replacements)


def run_pnpm_install(target_path: Path) -> None:
    """
    Runs pnpm install in the frontend directory.

    Strategy:
    - Remove pnpm-lock.yaml in the cloned project, so resolution is fresh.
    - Run 'pnpm install --no-frozen-lockfile'.
    """
    frontend_dir = target_path / "frontend"
    if not frontend_dir.exists():
        print(">> No frontend directory found, skipping pnpm install.")
        return

    lockfile_path = frontend_dir / "pnpm-lock.yaml"
    if lockfile_path.exists():
        print(">> Removing pnpm-lock.yaml in cloned frontend to force fresh resolution")
        lockfile_path.unlink()

    # On Windows we often want shell=True to behave like manual cmd usage
    print("\n>> Running pnpm install in frontend")
    if os.name == "nt":
        cmd = "pnpm install --no-frozen-lockfile"
        result = subprocess.run(cmd, cwd=frontend_dir, shell=True)
    else:
        cmd = ["pnpm", "install", "--no-frozen-lockfile"]
        result = subprocess.run(cmd, cwd=frontend_dir)

    if result.returncode != 0:
        raise RuntimeError(f"pnpm install failed with exit code {result.returncode}")


def run_docker_compose_build_and_up(target_path: Path) -> None:
    """Builds and starts the docker-compose stack."""
    run_command(
        ["docker-compose", "build"],
        cwd=target_path,
        description="docker-compose build",
    )
    run_command(
        ["docker-compose", "up", "-d"],
        cwd=target_path,
        description="docker-compose up -d",
    )


def get_container_id(target_path: Path, service_name: str) -> str:
    """Returns the container id for a docker-compose service."""
    result = subprocess.run(
        ["docker-compose", "ps", "-q", service_name],
        cwd=target_path,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Failed to get container id for service {service_name}: {result.stderr}"
        )
    container_id = result.stdout.strip()
    if not container_id:
        raise RuntimeError(f"No running container found for service {service_name}")
    return container_id


def back_copy_migrations(target_path: Path, service_name: str, apps: list[str]) -> None:
    """Copies migration files from the running container back to the host."""
    container_id = get_container_id(target_path, service_name)
    backend_host_dir = target_path / "backend"

    print(">> Copying migration files from container to host")
    for app in apps:
        src = f"{container_id}:/app/backend/{app}/migrations/."
        dest_dir = backend_host_dir / app / "migrations"
        dest_dir.mkdir(parents=True, exist_ok=True)

        run_command(
            ["docker", "cp", src, str(dest_dir)],
            cwd=target_path,
            description=f"docker cp migrations for app '{app}'",
        )


def run_django_migrations(target_path: Path, service_name: str) -> None:
    """Runs makemigrations and migrate inside the Django container, then copies migrations back to the host."""
    run_command(
        ["docker-compose", "exec", service_name, "python", "manage.py", "makemigrations"],
        cwd=target_path,
        description="Django makemigrations",
    )
    run_command(
        ["docker-compose", "exec", service_name, "python", "manage.py", "migrate"],
        cwd=target_path,
        description="Django migrate",
    )

    if MIGRATION_APPS:
        back_copy_migrations(target_path, service_name, MIGRATION_APPS)


def create_superuser(
    target_path: Path,
    service_name: str,
    settings_module: str,
    email: str,
    username: str,
    password: str,
) -> None:
    """Creates or updates a superuser inside the Django container."""
    python_code = (
        "import os, django; "
        f"os.environ.setdefault('DJANGO_SETTINGS_MODULE', {settings_module!r}); "
        "django.setup(); "
        "from django.contrib.auth import get_user_model; "
        "User = get_user_model(); "
        f"email = {email!r}; "
        f"username = {username!r}; "
        f"password = {password!r}; "
        "u, created = User.objects.get_or_create("
        "    username=username, defaults={'email': email}"
        "); "
        "u.is_superuser = True; "
        "u.is_staff = True; "
        "u.set_password(password); "
        "u.email = email; "
        "u.save(); "
        "print('Superuser created' if created else 'Superuser updated'); "
        "print('Username:', username); "
        "print('Email:', email)"
    )

    run_command(
        ["docker-compose", "exec", service_name, "python", "-c", python_code],
        cwd=target_path,
        description="Create or update Django superuser",
    )


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main() -> None:
    """Parses CLI arguments and orchestrates cloning and bootstrapping."""
    parser = argparse.ArgumentParser(
        description=(
            "Clone a Django/React project from a template, rename it, "
            "install dependencies, run Docker and initialise Django."
        )
    )
    parser.add_argument(
        "--template",
        required=True,
        help="Path to the template app directory (e.g. template_app).",
    )
    parser.add_argument(
        "--name",
        required=True,
        help="New project name (e.g. innoservice).",
    )
    parser.add_argument(
        "--web-port",
        default=TEMPLATE_WEB_PORT,
        help=f"New web port mapping (host port, default: {TEMPLATE_WEB_PORT}).",
    )
    parser.add_argument(
        "--db-port",
        default=TEMPLATE_DB_PORT,
        help=f"New database host port (default: {TEMPLATE_DB_PORT}).",
    )
    parser.add_argument(
        "--superuser-email",
        default="micha.bigler2@gmail.com",
        help="Email address for the initial Django superuser.",
    )

    args = parser.parse_args()

    template_path = Path(args.template).resolve()
    if not template_path.exists():
        raise RuntimeError(f"Template path does not exist: {template_path}")

    parent_dir = template_path.parent
    target_path = parent_dir / args.name

    print(f"Creating new app at: {target_path}")
    copy_template(template_path, target_path)

    print("Renaming Django package...")
    rename_django_package(target_path, args.name)

    print("Processing files (name and ports)...")
    process_files(target_path, args.name, args.web_port, args.db_port)

    # Install frontend dependencies
    try:
        run_pnpm_install(target_path)
    except Exception as exc:
        print(f"Warning: pnpm install failed: {exc}")

    # Build and start docker-compose
    run_docker_compose_build_and_up(target_path)

    # Service name in docker-compose is assumed to be <name>_app
    service_name = f"{args.name}_app"
    settings_module = f"{args.name}_app.settings"

    # Run migrations inside container
    run_django_migrations(target_path, service_name)

    # Ask for superuser password
    print("\nNow creating an initial Django superuser.")
    print(f"Email will be: {args.superuser_email}")
    pw1 = getpass.getpass("Superuser password: ")
    pw2 = getpass.getpass("Repeat password: ")
    if pw1 != pw2:
        raise RuntimeError("Passwords do not match.")

    username = args.superuser_email

    create_superuser(
        target_path=target_path,
        service_name=service_name,
        settings_module=settings_module,
        email=args.superuser_email,
        username=username,
        password=pw1,
    )

    print("\nAll done.")
    print(f"- New app directory: {target_path}")
    print(f"- Docker is running (docker-compose up -d in that folder)")
    print(f"- Superuser: {username} / <your password>")


if __name__ == "__main__":
    main()
