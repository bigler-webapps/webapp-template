#!/usr/bin/env python3
import argparse
import os
import sys
import yaml # pip install PyYAML

def get_secret(key, default=None, required=False):
    """Retrieves a secret from env vars (CI) or returns default."""
    val = os.environ.get(key, default)
    if required and not val:
        print(f"❌ Error: Secret '{key}' is required but not set in environment.")
        sys.exit(1)
    return val

def write_env_file(path, lines):
    """Helper to write the list of lines to the .env file."""
    try:
        with open(path, "w") as f:
            f.write("\n".join(lines))
            f.write("\n")
        print(f"✅ Successfully wrote {path}")
    except Exception as e:
        print(f"❌ Error writing file: {e}")
        sys.exit(1)

def generate_env(env_name, config_path="project.yaml", output_path=".env"):
    print(f"⚙️  Generating .env for environment: {env_name}")
    
    if not os.path.exists(config_path):
        print(f"❌ Error: Config file '{config_path}' not found.")
        sys.exit(1)

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    project_type = config.get("project_type", "django")

    # 1. Validate Environment exists in YAML
    if env_name not in config.get("environments", {}):
        if env_name == "local" and project_type == "infrastructure":
            print("ℹ️  Infrastructure app does not require local .env generation. Exiting.")
            sys.exit(0)
            
        print(f"❌ Error: Environment '{env_name}' not found in {config_path}")
        sys.exit(1)

    env_config = config["environments"][env_name]
    env_overrides = env_config.get("env_overrides", {})
    env_content = []

    # ==========================================
    # MODE A: INFRASTRUCTURE
    # ==========================================
    if project_type == "infrastructure":
        print("🏗️  Generating Infrastructure .env")
        # [Infrastructure logic omitted for brevity - logic remains identical]
        domain_map = env_config.get("domains", {})
        for var_name, domain in domain_map.items():
            env_content.append(f"{var_name}={domain}")

        infra_secrets = ["TRAEFIK_DASHBOARD_AUTH", "ACME_EMAIL", "WG_SERVERURL", "WG_PEERS"]
        for secret in infra_secrets:
            if secret in env_overrides:
                val = env_overrides[secret]
            else:
                val = get_secret(secret, required=False)
            
            if val:
                if secret == "TRAEFIK_DASHBOARD_AUTH": val = val.replace("$", "$$")
                env_content.append(f"{secret}={val}")

        env_content.append(f"CONTAINER_NAME_PREFIX={config.get('container_prefix', 'infra')}")
        write_env_file(output_path, env_content)
        return

    # ==========================================
    # MODE B: STANDARD DJANGO APP
    # ==========================================
    domains = env_config.get("domains", [])
    use_traefik = env_config.get("use_traefik", False)
    is_local = (env_name == "local")
    local_defaults = env_config.get("defaults", {})

    def resolve(key, required_in_prod=True):
        if key in env_overrides: return env_overrides[key]
        if is_local: return local_defaults.get(key, "")
        return get_secret(key, required=required_in_prod)

    # --- Database ---
    env_content.append(f"# --- Database ---")
    env_content.append(f"DB_USER={resolve('DB_USER')}")
    env_content.append(f"DB_PASSWORD={resolve('DB_PASSWORD')}")
    env_content.append(f"DB_NAME={resolve('DB_NAME')}")
    env_content.append(f"DB_HOST={resolve('DB_HOST')}")
    env_content.append(f"DB_PORT={resolve('DB_PORT')}")

    # --- Django ---
    env_content.append(f"\n# --- Django ---")
    env_content.append(f"DJANGO_SECRET_KEY={resolve('DJANGO_SECRET_KEY', required_in_prod=True)}")
    env_content.append(f"ENV_TYPE={env_name}")
    debug_val = resolve('DEBUG', required_in_prod=False)
    env_content.append(f"DEBUG={debug_val or 'False'}")

    # --- Mail ---
    env_content.append(f"\n# --- Mail ---")
    if is_local:
        env_content.append("EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend")
    else:
        env_content.append(f"EMAIL_HOST={resolve('EMAIL_HOST', required_in_prod=False)}")
        env_content.append(f"EMAIL_PORT={resolve('EMAIL_PORT', required_in_prod=False)}")
        env_content.append(f"EMAIL_USE_TLS={resolve('EMAIL_USE_TLS', required_in_prod=False)}")
        env_content.append(f"EMAIL_USER={resolve('EMAIL_USER', required_in_prod=False)}")
        env_content.append(f"EMAIL_PASSWORD={resolve('EMAIL_PASSWORD', required_in_prod=False)}")
        env_content.append(f"DEFAULT_FROM_EMAIL={resolve('EMAIL_USER', required_in_prod=False)}")

    ex_key = resolve("EXCHANGERATE_HOST_KEY", required_in_prod=False)
    if ex_key:
        env_content.append(f"EXCHANGERATE_HOST_KEY={ex_key}")

    # --- Infrastructure ---
    env_content.append(f"\n# --- Infrastructure ---")
    ctr_prefix = config.get("container_prefix", "app")
    if env_name == "staging":
        ctr_prefix += "_stage"
    
    env_content.append(f"CONTAINER_NAME_PREFIX={ctr_prefix}")
    env_content.append(f"ROUTER_NAME={config.get('project_name')}-{env_name}")

    # --- VOLUMES (New Section) ---
    vol_config = env_config.get("volumes", {})
    
    def get_vol_name(key, default_name):
        val = vol_config.get(key)
        # Handle dict format (e.g., {external: true, name: 'foo'})
        if isinstance(val, dict):
            return val.get("name", default_name)
        # Handle simple string format or None
        return val if val else default_name

    db_vol = get_vol_name("postgres_data", f"{ctr_prefix}_postgres_data")
    media_vol = get_vol_name("media_volume", f"{ctr_prefix}_media_volume")

    env_content.append(f"DB_VOLUME_NAME={db_vol}")
    env_content.append(f"MEDIA_VOLUME_NAME={media_vol}")

    # --- Network ---
    main_domain = domains[0] if domains else "localhost"
    env_content.append(f"DJANGO_ALLOWED_HOSTS={','.join(domains)}")
    protocol = "https" if use_traefik else "http"
    csrf_urls = [f"{protocol}://{d}" for d in domains]
    if is_local:
        csrf_urls.extend(["http://localhost:3000", "http://127.0.0.1:3000"])
        
    env_content.append(f"CSRF_TRUSTED_URLS={','.join(csrf_urls)}")
    env_content.append(f"PUBLIC_ORIGIN={protocol}://{main_domain}")

    if use_traefik:
        rules = [f"Host(`{d}`)" for d in domains]
        env_content.append(f"TRAEFIK_ROUTER_RULE={' || '.join(rules)}")
    else:
        env_content.append("TRAEFIK_ROUTER_RULE=Host(`localhost`)")

    root_mod = config.get("root_module", "project_template_app")
    env_content.append(f"DJANGO_ROOT_MODULE={root_mod}")

    # --- Auth / Social Secrets ---
    env_content.append(f"\n# --- Social Auth ---")
    # Google
    env_content.append(f"GOOGLE_CLIENT_ID={resolve('GOOGLE_CLIENT_ID', required_in_prod=False)}")
    env_content.append(f"GOOGLE_SECRET={resolve('GOOGLE_SECRET', required_in_prod=False)}")
    # Microsoft
    env_content.append(f"MICROSOFT_CLIENT_ID={resolve('MICROSOFT_CLIENT_ID', required_in_prod=False)}")
    env_content.append(f"MICROSOFT_SECRET={resolve('MICROSOFT_SECRET', required_in_prod=False)}")
    env_content.append(f"MICROSOFT_TENANT_ID={resolve('MICROSOFT_TENANT_ID', required_in_prod=False)}")

    write_env_file(output_path, env_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True, help="Environment (production, staging, local)")
    parser.add_argument("--output", default=".env", help="Output file path")
    args = parser.parse_args()
    
    generate_env(args.env, output_path=args.output)