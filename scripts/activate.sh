#!/bin/bash

export SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export HOME_DIR="$(pwd)"

echo "Activating this virtual environment..."
source "$HOME_DIR/neutron-env/bin/activate"