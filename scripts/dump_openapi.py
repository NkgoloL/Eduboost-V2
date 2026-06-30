import json
import yaml
from app.api_v2 import app

def dump_openapi():
    openapi_schema = app.openapi()
    
    # Save as JSON
    with open("openapi.json", "w") as f:
        json.dump(openapi_schema, f, indent=2)
    
    # Save as YAML
    with open("openapi.yaml", "w") as f:
        yaml.dump(openapi_schema, f, sort_keys=False)

if __name__ == "__main__":
    dump_openapi()
