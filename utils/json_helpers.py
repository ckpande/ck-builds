# json_helpers.py
# Chandrakant Pande - ckpande

import json
import os


def load_json(path, default=None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path, data, indent=2):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent)
        return True
    except OSError:
        return False


if __name__ == "__main__":
    test_path = "test.json"
    test_data = {"name": "Chandrakant", "role": "developer"}
    ok = save_json(test_path, test_data)
    print(f"save_json: {ok}")
    loaded = load_json(test_path)
    print(f"load (exists): {loaded}")
    missing = load_json("missing.json", default={})
    print(f"load (missing): {missing}")
    os.remove(test_path)
