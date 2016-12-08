#!/bin/bash
# Tests all our functionalities. 
# Output probabilities of test songs' genres, percent success
sh create_testing_data.sh
python data_analysis.py load