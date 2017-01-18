#!/bin/sh

set -e

command -v python 2>&1 >/dev/null && { PYTHON=python; }
command -v python3 2>&1 >/dev/null && { PYTHON=python3; }
command -v python3.4 2>&1 >/dev/null && { PYTHON=python3.4; }
command -v python3.5 2>&1 >/dev/null && { PYTHON=python3.5; }
command -v python3.6 2>&1 >/dev/null && { PYTHON=python3.6; }
command -v coverage 2>&1 >/dev/null && { coverage erase; PYTHON="coverage run -a"; }

for TEST in tests/test_*.py
do
  PYTHONPATH=. $PYTHON $TEST
done
