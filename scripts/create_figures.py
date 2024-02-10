#### Create figures 2, 3, 7, 8, 9, 10, 11, 12 ####

import os

# cd into ae_scripts
os.chdir('scripts/ae_scripts')

# if "distr_bank_usage_first_plot.csv" does not exist, run preprocess_activation_histograms.py
if not os.path.exists('distr_bank_usage_first_plot.csv'):
    print("Preprocessing activation histograms. This will take a while, but hopefully I will do it only once.")
    os.system('python3 preprocess_activation_histograms.py')

print("Creating figure2.")
# run figure2.py
os.system('python3 figure2.py')
print("Created figure2.")

print("Creating figure3.")
# run figure3.py
os.system('python3 figure3.py')
print("Created figure3.")

print("Creating figure7.")
# run figure7.py
os.system('python3 figure7.py')
print("Created figure7.")

print("Creating figure8.")
# run figure8.py
os.system('python3 figure8.py')
print("Created figure8.")

print("Creating figure9.")
# run figure9.py
os.system('python3 figure9.py')
print("Created figure9.")

print("Creating figure10.")
# run figure10.py
os.system('python3 figure10.py')
print("Created figure10.")

print("Creating figure11.")
# run figure11.py
os.system('python3 figure11.py')
print("Created figure11.")

print("Creating figure12.")
# run figure12.py
os.system('python3 figure12.py')
print("Created figure12.")

