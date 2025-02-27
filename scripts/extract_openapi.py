import argparse
import json
import sys

import yaml
from uvicorn.importer import import_from_string

parser = argparse.ArgumentParser(prog="extract_openapi.py")
parser.add_argument("app", help='App import string. Eg. "main:app"', default="main:app")
parser.add_argument("--app-dir", help="Directory containing the app", default=None)
parser.add_argument(
    "--out", help="Output file ending in .json or .yaml", default="openapi.yaml"
)
parser.add_argument(
    "--pretty", help="Pretty-print JSON output", action="store_true"
)  # Added option for pretty-printing JSON

if __name__ == "__main__":
    args = parser.parse_args()

    if args.app_dir is not None:
        print(f"Adding {args.app_dir} to sys.path")
        sys.path.insert(0, args.app_dir)

    print(f"Importing app from {args.app}")
    app = import_from_string(args.app)
    openapi = app.openapi()
    version = openapi.get("openapi", "unknown version")

    print(f"Writing OpenAPI spec v{version} to {args.out}")
    with open(args.out, "w") as f:
        if args.out.endswith(".json"):
            json.dump(openapi, f, indent=2 if args.pretty else None)  # Supports pretty-print
        else:
            yaml.dump(openapi, f, sort_keys=False)

    print(f"OpenAPI spec written to {args.out} successfully!")
