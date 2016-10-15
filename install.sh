#!/bin/sh

BINLOC=/usr/bin/halibot
SRCLOC=/usr/local/share/halibot

cp -v run-scripts/halibot $BINLOC

mkdir -p $SRCLOC
cp -v main.py $SRCLOC
cp -rv halibot $SRCLOC/halibot
cp -rv packages $SRCLOC/packages
