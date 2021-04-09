#!/bin/bash
rm docs/src/markdown/playground/*
python3 -m build --wheel -o docs/src/markdown/playground/
wheel=(docs/src/markdown/playground/*.whl)
echo "wheel = './${wheel##*/}'" > docs/src/markdown/_snippets/package.txt
