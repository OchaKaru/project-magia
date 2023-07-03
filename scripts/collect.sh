#! /bin/bash

pip install -r ./scripts/util/required
cd modeltraining/
clear
echo "Starting Data Collection"
python3 datacollector.py