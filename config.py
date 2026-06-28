import yaml


def load_config(path: str) -> dict:
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f)  # safe_load only loads basic Python types (strings, numbers, lists, dicts) and won't execute arbitrary code embedded in the YAML
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Config file is malformed or has incorrect indentation: {e}")
