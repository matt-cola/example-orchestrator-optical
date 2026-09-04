#!/bin/bash

# Exit on errors or unset variables
set -eu

# Tell uv not to ever download python, but use whatever version is set in
# https://github.com/workfloworchestrator/orchestrator-core/blob/main/Dockerfile
export UV_PYTHON_DOWNLOADS=never

cd /home/orchestrator

# Sync the app dependencies into the image's preinstalled venv (this aligns
# orchestrator-core with the version pinned in pyproject.toml)
echo "▶ uv sync"
uv sync --frozen
source .venv/bin/activate

# Install the orchestrator-optical module under test, editable, so module
# edits reload with uvicorn --reload
echo "▶ install orchestrator-optical (editable)"
uv pip install -e /home/orchestrator/orchestrator-optical

# Refresh the app translations with the module's shipped strings: core
# deep-merges TRANSLATIONS_DIR over its own defaults, so this single file
# carries all the shipped workflow display strings
cp /home/orchestrator/orchestrator-optical/src/orchestrator/optical/translations/en-GB.json \
    /home/orchestrator/translations/en-GB.json

setup() {
    echo "▶ db upgrade heads"
    python main.py db upgrade heads

    echo "▶ index subscriptions"
    python main.py index subscriptions

    echo "▶ index products"
    python main.py index products

    echo "▶ index processes"
    python main.py index processes

    echo "▶ index workflows"
    python main.py index workflows
}

if [ -f "${CORE_OVERRIDE:-/home/orchestrator/orchestrator-core}/pyproject.toml" ]; then
    echo "⏭️ Use editable install of orchestrator-core"
    uv pip install -e "${CORE_OVERRIDE:-/home/orchestrator/orchestrator-core}"

    setup

    uvicorn --host 0.0.0.0 --port 8080 ${UVICORN_ARGS:-} wsgi:app --reload --proxy-headers \
        --reload-dir "$CORE_OVERRIDE" \
        --reload-dir products \
        --reload-dir translations \
        --reload-dir workflows
else
    setup

    echo "⏭️ Use orchestrator-core as specified in pyproject.toml $(uv pip freeze | grep orchestrator-core)"
    uvicorn --host 0.0.0.0 --port 8080 ${UVICORN_ARGS:-} wsgi:app --reload --proxy-headers \
        --reload-dir /home/orchestrator/orchestrator-optical/src \
        --reload-dir products \
        --reload-dir translations \
        --reload-dir workflows
fi
