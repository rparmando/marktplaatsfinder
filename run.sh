#!/bin/bash
cd /Users/armando/marktplaatsfinder/marktplaatsfinder
echo "--- $(date) ---" >> logs/run.log
/usr/bin/python3 main.py >> logs/run.log 2>&1
