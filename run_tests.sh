#!/bin/bash

for file in ./tests/*.ippecode; do
    ./parser.py "$file" "${file}.out.xml"
    echo "Processed ${file}"
done
