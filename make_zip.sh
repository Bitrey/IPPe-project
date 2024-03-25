#!/bin/bash

# pack parser.py and tests/* into a .tgz, excluding tests/*.out.xml
tar --exclude='tests/*.out.xml' -czf parser.tgz parser.py tests
