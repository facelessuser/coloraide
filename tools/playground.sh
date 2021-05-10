#!/bin/bash
rm docs/src/markdown/playground/*
python3 -m build --wheel -o docs/src/markdown/playground/
wheel=(docs/src/markdown/playground/*.whl)
filename="docs/src/markdown/.snippets/playground.py.txt"
sed -i.bak "s/^wheel = .*$/wheel = '${wheel##*/}'/" $filename
rm docs/src/markdown/.snippets/playground.py.txt.bak
