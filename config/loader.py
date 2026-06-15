import os
import yaml
from dotenv import load_dotenv

def load_config(config_path="config/config.yaml"):
    """
    Load configuration from YAML file and override secrets with environment variables.

    Expected config.yaml structure:
    ai:
      model: str
      temperature: float
      api_base: str
      api_key_env: str  # name of environment variable containing the API key
    calendar:
      token_env: str
      database_id_env: str
    platform:
      token_env: str
    system_prompts:
      default: str

    Returns:
        dict: Configuration dictionary with resolved values.
    """
    # Load environment variables from .env file (if not already loaded)
    load_dotenv()

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Resolve API key and other secrets from environment variables
    if 'ai' in config and 'api_key_env' in config['ai']:
        env_var = config['ai']['api_key_env']
        config['ai']['api_key'] = os.getenv(env_var)
        # Optionally remove the env var name from config if not needed elsewhere
        # del config['ai']['api_key_env']

    if 'calendar' in config:
        if 'token_env' in config['calendar']:
            env_var = config['calendar']['token_env']
            config['calendar']['token'] = os.getenv(env_var)
            # del config['calendar']['token_env']
        if 'database_id_env' in config['calendar']:
            env_var = config['calendar']['database_id_env']
            config['calendar']['database_id'] = os.getenv(env_var)
            # del config['calendar']['database_id_env']

    if 'platform' in config and 'token_env' in config['platform']:
        env_var = config['platform']['token_env']
        config['platform']['token'] = os.getenv(env_var)
        # del config['platform']['token_env']

    # Note: We keep the _env fields in config for reference, but we also add resolved fields.
    # Alternatively, we could remove them. We'll keep them for clarity.

    return config