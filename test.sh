#!/bin/sh

command -v python 2>&1 >/dev/null && { PYTHON=python; }
command -v python3 2>&1 >/dev/null && { PYTHON=python3; }
command -v coverage 2>&1 >/dev/null && { PYTHON="coverage run"; }

for TEST in tests/test_*.py
do
  PYTHONPATH=. $PYTHON $TEST
done
