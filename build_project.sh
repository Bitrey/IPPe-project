#!/bin/bash

# pack parser.py and tests/* into a .tgz, excluding tests/*.out.xml
cp docs/parser/docs.pdf parser-docs.pdf
tar --exclude='tests/*.out.xml' -czf xamella00.tgz parser.py tests parser-docs.pdf run_tests.sh
rm parser-docs.pdf
