#!/bin/sh

# TODO detect if this should rather be python3 or similar
PYTHON=python

for TEST in tests/test_*.py
do
  PYTHONPATH=. $PYTHON $TEST
done
