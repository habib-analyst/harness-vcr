#!/bin/bash
# G0 gate: unit tests must be green before any head-to-head run.
set -e
cd "$(dirname "$0")"
python3 -m pytest tests/ -q
