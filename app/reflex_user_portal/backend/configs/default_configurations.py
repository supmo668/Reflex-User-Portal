import yaml
import os
import warnings
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Default configuration paths for different models
DEFAULT_CONFIG_PATHS = {
    "AdminConfig": Path(__file__).parent / "admin_config.yaml",
    "SubscriptionFeature": Path(__file__).parent / "subscription_features.yaml",
    # Add more models and their config paths as needed ...
    "User": Path(__file__).parent / "initial_users.yaml",
}

def load_yaml_config(path: str):
    """Load YAML config from path if file exists and is not empty, always as a list."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Config file {path} does not exist. Correct your `DEFAULT_CONFIG_PATHS` variable.")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return []
        data = yaml.safe_load(content)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
        else:
            return []

def build_default_configs():
    configs = {}
    for model_key, path in DEFAULT_CONFIG_PATHS.items():
        try:
            config_list = load_yaml_config(path)
            logger.info(f"Loading config for {model_key} from {path}")
            configs[model_key] = config_list
        except Exception as e:
            warnings.warn(f"Failed to load config for {model_key}: {e}")
            configs[model_key] = []
    return configs

DEFAULT_CONFIGS = build_default_configs()

# Convenience: list of subscription features
DEFAULT_SUBSCRIPTION_FEATURES = DEFAULT_CONFIGS.get("SubscriptionFeature", [])