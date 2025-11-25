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

def generate_env(env_name, config_path="project.yaml", output_path=".env"):
    print(f"⚙️  Generating .env for environment: {env_name}")
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    if env_name not in config["environments"]:
        print(f"❌ Error: Environment '{env_name}' not found in {config_path}")
        sys.exit(1)

    env_config = config["environments"][env_name]
    domains = env_config.get("domains", [])
    use_traefik = env_config.get("use_traefik", False)
    
    # --- 1. Base Variables ---
    # In CI, secrets come from Env Vars. In Local, we use defaults from YAML.
    is_local = (env_name == "local")
    local_defaults = env_config.get("defaults", {})

    # Helper to get value based on mode
    def resolve(key, required_in_prod=True):
        if is_local:
            return local_defaults.get(key, "")
        return get_secret(key, required=required_in_prod)

    env_content = []
    
    # DB
    env_content.append(f"# --- Database ---")
    env_content.append(f"DB_USER={resolve('DB_USER')}")
    env_content.append(f"DB_PASSWORD={resolve('DB_PASSWORD')}")
    env_content.append(f"DB_NAME={resolve('DB_NAME')}")
    env_content.append(f"DB_HOST={resolve('DB_HOST')}")
    env_content.append(f"DB_PORT={resolve('DB_PORT')}")

    # App
    env_content.append(f"\n# --- Django ---")
    # For local, we generate a dummy key if not present
    env_content.append(f"DJANGO_SECRET_KEY={resolve('DJANGO_SECRET_KEY', required_in_prod=True) or 'dev-insecure-key'}")
    env_content.append(f"ENV_TYPE={env_name}")
    env_content.append(f"DEBUG={resolve('DEBUG') or 'False'}")

    # Mail
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

    # --- 2. Calculated Networking (The Logic moved from Bash) ---
    env_content.append(f"\n# --- Infrastructure & Traefik ---")
    
    # Container Naming
    ctr_prefix = config.get("container_prefix", "app")
    if env_name == "staging":
        ctr_prefix += "_stage"
    
    env_content.append(f"CONTAINER_NAME_PREFIX={ctr_prefix}")
    env_content.append(f"ROUTER_NAME={config.get('project_name')}-{env_name}")

    # Domain Calculations
    main_domain = domains[0] if domains else "localhost"
    
    # 1. DJANGO_ALLOWED_HOSTS (comma separated)
    env_content.append(f"DJANGO_ALLOWED_HOSTS={','.join(domains)}")
    
    # 2. CSRF_TRUSTED_ORIGINS (needs https:// or http://)
    protocol = "https" if use_traefik else "http"
    csrf_urls = [f"{protocol}://{d}" for d in domains]
    # Add local ports for dev if needed
    if is_local:
        csrf_urls.append("http://localhost:3000")
        csrf_urls.append("http://127.0.0.1:3000")
        
    env_content.append(f"CSRF_TRUSTED_URLS={','.join(csrf_urls)}")
    env_content.append(f"PUBLIC_ORIGIN={protocol}://{main_domain}")

    # 3. Traefik Rule
    if use_traefik:
        # Generates: Host(`a.com`) || Host(`b.com`)
        rules = [f"Host(`{d}`)" for d in domains]
        traefik_rule = " || ".join(rules)
        env_content.append(f"TRAEFIK_ROUTER_RULE={traefik_rule}")
    else:
        # Dummy value for local to prevent docker-compose variable errors
        env_content.append("TRAEFIK_ROUTER_RULE=Host(`localhost`)")

    # --- Write File ---
    with open(output_path, "w") as f:
        f.write("\n".join(env_content))
        f.write("\n")
    
    print(f"✅ Successfully wrote {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True, help="Environment (production, staging, local)")
    parser.add_argument("--output", default=".env", help="Output file path")
    args = parser.parse_args()
    
    generate_env(args.env, output_path=args.output)


#python scripts/generate_env.py --env local