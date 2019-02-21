#!/bin/bash

cd -- $(dirname "$BASH_SOURCE")
NAME=$(basename "$PWD")

[ -d "$NAME-env" ] || python3 -m venv "$NAME-env"
. "$NAME-env/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt
