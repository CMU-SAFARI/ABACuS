# plot cumulative_bank_usage_stats
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import numpy as np
import glob

# one counter per DRAM row, in each counter, there are as many entries as there are ranks + banks, which is 32
def find_distribution_bank_usage_stat(filepath, analysis_threshold):

  counters = {}

  bank_usage_stats = []

  actual_lines = []
  with open(filepath, "r") as f:
      for line in f:
          actual_lines = line.split(' ')
          break
        
  for i in range (len(actual_lines)):
    # if line is empty, skip
    if actual_lines[i] == "":
      continue
    
    line = actual_lines[i]

    tokens = line.split(":")
    ra = int(tokens[1])
    bg = int(tokens[2])
    ba = int(tokens[3])
    row = int(tokens[4])
    
    secondary_index = ra << 4 | bg << 2 | ba
    
    if row not in counters:
      init_array = []
      for i in range(32):
        init_array.append(0)
      counters[row] = init_array
      counters[row][secondary_index] += 1
    else:
      counters[row][secondary_index] += 1
      if counters[row][secondary_index] == analysis_threshold:
        # append all counter values except secondary_index to bank_usage_stats
        for j in range(len(counters[row])):
          if j != secondary_index:
            bank_usage_stats.append(counters[row][j])
               
        # remove this row from the counters
        del counters[row]
        
    # print the progress of lines so far as fraction of total lines
    if i % 1000000 == 0:
      print("Progress:", str(i / len(actual_lines)))
  
  return bank_usage_stats

# all workloads are in activate-periods directory
# under each workload directory, there is an activate_periods.txt file

MED_RBMPKI = ['510.parest', '462.libquantum', 'tpch2', 'wc_8443', 'ycsb_aserver', '473.astar', 'stream_10.trace', 'jp2_decode', '436.cactusADM', '557.xz', 'ycsb_cserver', 'ycsb_eserver', '471.omnetpp', '483.xalancbmk', '505.mcf', 'wc_map0', 'jp2_encode', 'tpch17', 'ycsb_bserver', 'tpcc64', '482.sphinx3']
HIGH_RBMPKI = ['519.lbm', '459.GemsFDTD', '450.soplex', 'h264_decode', '520.omnetpp', '433.milc', '434.zeusmp', 'random_10.trace', 'bfs_dblp', '429.mcf', '549.fotonik3d', '470.lbm', 'bfs_ny', 'bfs_cm2003', '437.leslie3d']
MEDHIGH_RBMPKI = MED_RBMPKI + HIGH_RBMPKI

os.system("cp -r ../../ae-results/ACT-period-256ms.yaml activate_periods")

# iterate over all workloads
for workload in MEDHIGH_RBMPKI:
  df = pd.DataFrame(columns=['workload', 'cumulative_bank_usage_stat', 'analysis_threshold'])
  # iterate over all analysis_thresholds
  for analysis_threshold in [2, 125, 250, 500]:
    all_bank_usage_stats = find_distribution_bank_usage_stat("activate_periods/" + workload + "/activate_periods.txt", analysis_threshold)
    workload_array = [workload for i in range(len(all_bank_usage_stats))]
    analysis_threshold_array = [analysis_threshold for i in range(len(all_bank_usage_stats))]
    # add these to df fast
    df = pd.concat([df, pd.DataFrame({'workload': workload_array, 'analysis_threshold': analysis_threshold_array, 'bank_usage_stat': all_bank_usage_stats})])    
    print("workload:", workload, "analysis_threshold:", analysis_threshold)  
  # save df as csv
  df.to_csv("distr_bank_usage_stat_" + workload + ".csv")

# empty dataframe with the same columns
dfn = pd.DataFrame(columns=['workload', 'cumulative_bank_usage_stat', 'analysis_threshold', 'bank_usage_stat'])

# Add RH_ESTIMATE workloads to the dataframe
for i in range (0, 32):
  dfn = pd.concat([dfn, pd.DataFrame([['ds', 0, 125]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
dfn = pd.concat([dfn, pd.DataFrame([['ds-p1', 124, 125]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
for i in range (0, 31):
  dfn = pd.concat([dfn, pd.DataFrame([['ds-p1', 0, 125]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
for i in range (0, 8):
  dfn = pd.concat([dfn, pd.DataFrame([['ds-p8', 124, 125]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
for i in range (0, 24):
  dfn = pd.concat([dfn, pd.DataFrame([['ds-p8', 0, 125]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])  
for i in range (0, 32):
  dfn = pd.concat([dfn, pd.DataFrame([['ds-p32', 124, 125]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])

for i in range (0, 32):
  dfn = pd.concat([dfn, pd.DataFrame([['ms', 0, 125]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
dfn = pd.concat([dfn, pd.DataFrame([['ms-p1', 124, 125]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
for i in range (0, 31):
  dfn = pd.concat([dfn, pd.DataFrame([['ms-p1', 0, 125]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
for i in range (0, 8):
  dfn = pd.concat([dfn, pd.DataFrame([['ms-p8', 124, 125]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
for i in range (0, 24):
  dfn = pd.concat([dfn, pd.DataFrame([['ms-p8', 0, 125]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])  
for i in range (0, 32):
  dfn = pd.concat([dfn, pd.DataFrame([['ms-p32', 124, 125]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])

# Add RH_ESTIMATE workloads to the dataframe
for i in range (0, 32):
  dfn = pd.concat([dfn, pd.DataFrame([['ds', 0, 250]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
dfn = pd.concat([dfn, pd.DataFrame([['ds-p1', 249, 250]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
for i in range (0, 31):
  dfn = pd.concat([dfn, pd.DataFrame([['ds-p1', 0, 250]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
for i in range (0, 8):
  dfn = pd.concat([dfn, pd.DataFrame([['ds-p8', 249, 250]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
for i in range (0, 24):
  dfn = pd.concat([dfn, pd.DataFrame([['ds-p8', 0, 250]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])  
for i in range (0, 32):
  dfn = pd.concat([dfn, pd.DataFrame([['ds-p32', 249, 250]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])

for i in range (0, 32):
  dfn = pd.concat([dfn, pd.DataFrame([['ms', 0, 250]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
dfn = pd.concat([dfn, pd.DataFrame([['ms-p1', 249, 250]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
for i in range (0, 31):
  dfn = pd.concat([dfn, pd.DataFrame([['ms-p1', 0, 250]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
for i in range (0, 8):
  dfn = pd.concat([dfn, pd.DataFrame([['ms-p8', 249, 250]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
for i in range (0, 24):
  dfn = pd.concat([dfn, pd.DataFrame([['ms-p8', 0, 250]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])  
for i in range (0, 32):
  dfn = pd.concat([dfn, pd.DataFrame([['ms-p32', 249, 250]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])

# Add RH_ESTIMATE workloads to the dataframe
for i in range (0, 32):
  dfn = pd.concat([dfn, pd.DataFrame([['ds', 0, 500]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
dfn = pd.concat([dfn, pd.DataFrame([['ds-p1', 499, 500]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
for i in range (0, 31):
  dfn = pd.concat([dfn, pd.DataFrame([['ds-p1', 0, 500]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
for i in range (0, 8):
  dfn = pd.concat([dfn, pd.DataFrame([['ds-p8', 499, 500]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
for i in range (0, 24):
  dfn = pd.concat([dfn, pd.DataFrame([['ds-p8', 0, 500]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])  
for i in range (0, 32):
  dfn = pd.concat([dfn, pd.DataFrame([['ds-p32', 499, 500]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])

for i in range (0, 32):
  dfn = pd.concat([dfn, pd.DataFrame([['ms', 0, 500]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
dfn = pd.concat([dfn, pd.DataFrame([['ms-p1', 499, 500]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
for i in range (0, 31):
  dfn = pd.concat([dfn, pd.DataFrame([['ms-p1', 0, 500]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
for i in range (0, 8):
  dfn = pd.concat([dfn, pd.DataFrame([['ms-p8', 499, 500]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
for i in range (0, 24):
  dfn = pd.concat([dfn, pd.DataFrame([['ms-p8', 0, 500]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])  
for i in range (0, 32):
  dfn = pd.concat([dfn, pd.DataFrame([['ms-p32', 499, 500]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])  
  
# read all csvs into one dataframe
# read one file at a time, store it in temporary dataframe
# sample 1/10 of the data randomly to put in the final datafrmae
df = pd.DataFrame()
for filename in glob.glob("distr_bank_usage_stat_*.csv"):
    df_tmp = pd.read_csv(filename, index_col=None, header=0)
    # sample 1/10 of the data
    df_tmp = df_tmp.sample(frac=0.1, random_state=1)
    # add to final dataframe using concat
    df = pd.concat([df, df_tmp])    
    print("Done reading " + filename)

# merge dfn to df
df = pd.concat([df, dfn])

df.to_csv("distr_bank_usage.csv", index=False)

# read all csvs into one dataframe
# read one file at a time, store it in temporary dataframe
# sample 1/10 of the data randomly to put in the final datafrmae
df = pd.DataFrame()
new_df_arr = []
for filename in glob.glob("distr_bank_usage_stat_*.csv"):
    print(filename)
    df_tmp = pd.read_csv(filename, index_col=0, header=0)
    df_tmp = df_tmp[df_tmp['analysis_threshold'] == 2]
    # select bank_usage_stat as series
    sum_series = df_tmp['bank_usage_stat']
    # sum of every 31 elements
    sum_series = sum_series.groupby(np.arange(len(sum_series))//31).sum()
    # reconstruct a df from the series
    df_new = pd.DataFrame({'bank_usage_stat': sum_series})
    df_new['workload'] = df_tmp['workload'][0]
    df_new['analysis_threshold'] = df_tmp['analysis_threshold'][0]
    new_df_arr.append(df_new)
    # print size in MB of df_new
    print(df_new.memory_usage().sum() / 1024**2)

# concat new_df_arr
df = pd.concat(new_df_arr)
# merge dfn to df
df = pd.concat([df, dfn])

df.to_csv("distr_bank_usage_first_plot.csv", index=False)
