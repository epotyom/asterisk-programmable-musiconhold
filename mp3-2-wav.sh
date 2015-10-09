#!/usr/bin/env bash
for i in *.mp3; do mpg123 -q -s --mono -r 8000 -f 8192 -b 2048 -w ${i%%.*}.wav $i; done
