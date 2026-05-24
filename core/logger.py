import json
import os
import time

def log_result(success, attempts, file_name, details=""):
    result = {
        "success": success,
        "attempts": attempts,
        "file": file_name,
        "timestamp": time.time(),
        "details": details
    }

    file_path = "results.json"

    # Load existing results
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
                if not isinstance(data, list):
                    data = []
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Append new result
    data.append(result)

    # Save back
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Warning: Failed to write results.json: {e}")