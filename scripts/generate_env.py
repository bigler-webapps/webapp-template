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
        # Special check: If infra never runs locally, exit gracefully
        if env_name == "local" and project_type == "infrastructure":
            print("ℹ️  Infrastructure app does not require local .env generation. Exiting.")
            sys.exit(0)
            
        print(f"❌ Error: Environment '{env_name}' not found in {config_path}")
        sys.exit(1)

    env_config = config["environments"][env_name]
    env_content = []

    # ==========================================
    # MODE A: INFRASTRUCTURE
    # ==========================================
    if project_type == "infrastructure":
        print("🏗️  Generating Infrastructure .env")

        # 1. Load Domains
        domain_map = env_config.get("domains", {})
        for var_name, domain in domain_map.items():
            env_content.append(f"{var_name}={domain}")

        # 2. Load Secrets
        infra_secrets = [
            "TRAEFIK_DASHBOARD_AUTH", 
            "ACME_EMAIL", 
            "WG_SERVERURL", 
            "WG_PEERS"
        ]
        
        for secret in infra_secrets:
            val = get_secret(secret, required=False) 
            if val:
                # --- FIX: Escape $ for Docker Compose ---
                if secret == "TRAEFIK_DASHBOARD_AUTH":
                    val = val.replace("$", "$$")
                # ----------------------------------------
                env_content.append(f"{secret}={val}")

        # 3. Base Identifiers
        env_content.append(f"CONTAINER_NAME_PREFIX={config.get('container_prefix', 'infra')}")
        
        # Write and Exit
        write_env_file(output_path, env_content)
        return

    # ==========================================
    # MODE B: STANDARD DJANGO APP
    # ==========================================
    # Logic for standard apps...
    domains = env_config.get("domains", [])
    use_traefik = env_config.get("use_traefik", False)
    
    is_local = (env_name == "local")
    local_defaults = env_config.get("defaults", {})

    def resolve(key, required_in_prod=True):
        if is_local:
            return local_defaults.get(key, "")
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
        env_content.append(f"EMAIL_HOST={get_secret('EMAIL_HOST')}")
        env_content.append(f"EMAIL_PORT={get_secret('EMAIL_PORT')}")
        env_content.append(f"EMAIL_USE_TLS={get_secret('EMAIL_USE_TLS')}")
        env_content.append(f"EMAIL_USER={get_secret('EMAIL_USER')}")
        env_content.append(f"EMAIL_PASSWORD={get_secret('EMAIL_PASSWORD')}")
        env_content.append(f"DEFAULT_FROM_EMAIL={get_secret('EMAIL_USER')}")

    # --- Infrastructure ---
    env_content.append(f"\n# --- Infrastructure & Traefik ---")
    ctr_prefix = config.get("container_prefix", "app")
    if env_name == "staging":
        ctr_prefix += "_stage"
    
    env_content.append(f"CONTAINER_NAME_PREFIX={ctr_prefix}")
    env_content.append(f"ROUTER_NAME={config.get('project_name')}-{env_name}")

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

    write_env_file(output_path, env_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True, help="Environment (production, staging, local)")
    parser.add_argument("--output", default=".env", help="Output file path")
    args = parser.parse_args()
    
    generate_env(args.env, output_path=args.output)