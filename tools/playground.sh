#!/bin/bash
rm docs/src/markdown/playground/*
python3 -m build --wheel -o docs/src/markdown/playground/
wheel=(docs/src/markdown/playground/*.whl)
input="tools/playground_pyodide.py"
output="docs/src/markdown/.snippets/playground.txt"
sed "s/^wheel = .*$/wheel = '${wheel##*/}'/;s/\\\\n/\\\\\\\\n/g;s/\`/\\\\\`/g" $input > $output
