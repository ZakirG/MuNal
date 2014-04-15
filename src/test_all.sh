#test all, output probabilities of test songs' genres, percent success
#!/bin/bash

sh create_testing_data.sh

python data_analysis.py load