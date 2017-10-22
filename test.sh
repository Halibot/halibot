#!/bin/sh

set -e

command -v python 2>&1 >/dev/null && { PYTHON=python; }
command -v python3 2>&1 >/dev/null && { PYTHON=python3; }
command -v coverage 2>&1 >/dev/null && { coverage erase; PYTHON="coverage run -a --source=. --omit=main.py"; }

for TEST in tests/test_*.py
do
  PYTHONPATH=. $PYTHON $TEST
done
