import yaml
import os
import warnings
import logging

from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATHS = {
    "AdminConfig": Path(__file__).parent/ "test_config.yaml",
    "SubscriptionFeature": Path(__file__).parent/  "subscription_features.yaml",
    # Add more config paths here as needed
}

def load_yaml_config(path: str):
    """Load YAML config from path if file exists and is not empty."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Config file {path} does not exist. Correct your `DEFAULT_CONFIG_PATHS` variable.")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return {}
        return yaml.safe_load(content) or {}

DEFAULT_CONFIGS = {}
for key, path in DEFAULT_CONFIG_PATHS.items():
    config_yaml = load_yaml_config(path)
    logger.info(f"Loading config for {key} from {path}")
    if config_yaml:
        if key == "AdminConfig":
            DEFAULT_CONFIGS[key] = {
                "name": "MyAdminConfig",
                "version": 0.1,
                "configuration": config_yaml,
            }
        elif key == "SubscriptionFeature":
            # Store the raw config for SubscriptionFeature
            DEFAULT_CONFIGS[key] = config_yaml
    else:
        warnings.warn(
            f"Config file {path} is empty or does not exist. Using default values."
        )
        # Add more model-specific logic as needed

# Load SubscriptionFeature config as list of dicts if present, else empty list
if "SubscriptionFeature" in DEFAULT_CONFIGS and isinstance(DEFAULT_CONFIGS["SubscriptionFeature"], list):
    DEFAULT_SUBSCRIPTION_FEATURES = DEFAULT_CONFIGS["SubscriptionFeature"]
else:
    DEFAULT_SUBSCRIPTION_FEATURES = []

# At #sym:ensure_defaults, use DEFAULT_SUBSCRIPTION_FEATURES as a list of dicts:
# Example:
# for feature_dict in DEFAULT_SUBSCRIPTION_FEATURES:
#     # Use feature_dict directly as a dictionary