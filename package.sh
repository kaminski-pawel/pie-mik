#!/bin/bash

# LAMBDA_SOURCE_CODE_DIRS=("B")
LAMBDA_SOURCE_CODE_DIRS=("A" "B")
DIR_ROOT="$PWD"
RUNTIME=python3.10

cd $DIR_ROOT
# rm -r dist/*
mkdir -p dist

for path in ${LAMBDA_SOURCE_CODE_DIRS[@]}; do
    echo "Preparing virtual environment for ${path}"
    if [ ! -d "src/$path/.venv" ]; then
        python -m venv "src/$path/.venv"
    fi
    if [ ! -f "src/$path/.venv/bin/activate" ]; then
        echo "Error: src/$path/.venv/bin/activate does not exist."
        exit 1
    fi

    source "src/$path/.venv/bin/activate"
    python -m pip install -r "src/$path/requirements.txt"
    deactivate
    echo "Preparing .zip package for ${path}"
    cd "src/$path/.venv/lib/$RUNTIME/site-packages/"
    zip -r9 "../../../../${path}.zip" .
    cd ../../../../
    zip -g "${path}.zip" lambda_function.py
    cp -r "${path}.zip" "$DIR_ROOT/dist"
    rm -rf "${path}.zip"
    cd "$DIR_ROOT"

done
