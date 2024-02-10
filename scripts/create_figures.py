#### Create figures 2, 3, 7, 8, 9, 10, 11, 12 ####

import os

# cd into ae_scripts
os.chdir('scripts/ae_scripts')

# if "distr_bank_usage_first_plot.csv" does not exist, run preprocess_activation_histograms.py
if not os.path.exists('distr_bank_usage_first_plot.csv'):
    os.system('python3 preprocess_activation_histograms.py')

# run figure2.py
os.system('python3 figure2.py')

# run figure3.py
os.system('python3 figure3.py')

# run figure7.py
os.system('python3 figure7.py')

# run figure8.py
os.system('python3 figure8.py')

# run figure9.py
os.system('python3 figure9.py')

# run figure10.py
os.system('python3 figure10.py')

# run figure11.py
os.system('python3 figure11.py')

# run figure12.py
os.system('python3 figure12.py')

