# plot cumulative_bank_usage_stats
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import numpy as np

df = pd.read_csv("distr_bank_usage_first_plot.csv")

MED_RBMPKI = ['510.parest', '462.libquantum', 'tpch2', 'wc_8443', 'ycsb_aserver', '473.astar', 'stream_10.trace', 'jp2_decode', '436.cactusADM', '557.xz', 'ycsb_cserver', 'ycsb_eserver', '471.omnetpp', '483.xalancbmk', '505.mcf', 'wc_map0', 'jp2_encode', 'tpch17', 'ycsb_bserver', 'tpcc64', '482.sphinx3']
HIGH_RBMPKI = ['519.lbm', '459.GemsFDTD', '450.soplex', 'h264_decode', '520.omnetpp', '433.milc', '434.zeusmp', 'bfs_dblp', '429.mcf', '549.fotonik3d', 'random_10.trace', 'gups', '470.lbm', 'bfs_ny', 'bfs_cm2003', '437.leslie3d']
RH_ESTIMATE = ['ds', 'ds-p1' , 'ds-p8', 'ds-p32', 'ms' , 'ms-p1', 'ms-p8', 'ms-p32']
# dfx = df.copy()
dfx = df

# Add RH_ESTIMATE workloads to the dataframe
dfx = pd.concat([dfx, pd.DataFrame([['ds', 0, 2]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
dfx = pd.concat([dfx, pd.DataFrame([['ds-p1', 1, 2]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
dfx = pd.concat([dfx, pd.DataFrame([['ds-p8', 8, 2]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
dfx = pd.concat([dfx, pd.DataFrame([['ds-p32', 31, 2]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
dfx = pd.concat([dfx, pd.DataFrame([['ms', 0, 2]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
dfx = pd.concat([dfx, pd.DataFrame([['ms-p1', 1, 2]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
dfx = pd.concat([dfx, pd.DataFrame([['ms-p8', 8, 2]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])
dfx = pd.concat([dfx, pd.DataFrame([['ms-p32', 31, 2]], columns=['workload', 'bank_usage_stat', 'analysis_threshold'])])

MEDHIGH_RBMPKI = MED_RBMPKI + HIGH_RBMPKI + RH_ESTIMATE
# remove where workload is stream_10.trace and random_10.trace from MEDHIGH_RBMPKI
MEDHIGH_RBMPKI.remove('stream_10.trace')
MEDHIGH_RBMPKI.remove('gups')
# MEDHIGH_RBMPKI.remove('random_10.trace')
# get rid of workloads not in MEDHIGH_RBMPKI
dfn = dfx[dfx['workload'].isin(MEDHIGH_RBMPKI)]
# dfn['use_stat'] = dfn['cumulative_bank_usage_stat'] * 32
# remove where workload is stream_10.trace and random_10.trace
dfn = dfn[dfn['workload'] != 'stream_10.trace']
# dfn = dfn[dfn['workload'] != 'random_10.trace']
dfn = dfn[dfn['workload'] != 'gups']

dfn['workload'] = dfn['workload'].replace('random_10.trace', 'gups')

# #rename random_10.trace to gups in MEDHIGH_RBMPKI
MEDHIGH_RBMPKI = [x.replace('random_10.trace', 'gups') for x in MEDHIGH_RBMPKI]
order = ['h264_encode', '511.povray', '481.wrf', '541.leela', '538.imagick', '444.namd', '447.dealII', '464.h264ref', '456.hmmer', '403.gcc', '526.blender', '544.nab', '525.x264', '508.namd', 'grep_map0', '531.deepsjeng', '458.sjeng', '435.gromacs', '445.gobmk', '401.bzip2', '507.cactuBSSN', '502.gcc', 'ycsb_abgsave', 'tpch6', '500.perlbench', '523.xalancbmk', 'ycsb_dserver', 'ycsb_cserver', '510.parest', 'ycsb_bserver', 'ycsb_eserver', 'stream_10.trace', 'tpcc64', 'ycsb_aserver', '557.xz', '482.sphinx3', 'jp2_decode', '505.mcf', 'wc_8443', 'wc_map0', '436.cactusADM', '471.omnetpp', '473.astar', 'jp2_encode', 'tpch17', '483.xalancbmk', '462.libquantum', 'tpch2', '433.milc', '520.omnetpp', '437.leslie3d', '450.soplex', '459.GemsFDTD', '549.fotonik3d', '434.zeusmp', '519.lbm', '470.lbm', '429.mcf', 'gups', 'h264_decode', 'bfs_ny', 'bfs_cm2003', 'bfs_dblp', 'ds', 'ds-p1' , 'ds-p8', 'ds-p32', 'ms' , 'ms-p1', 'ms-p8', 'ms-p32']
# remove from order, workloads not in MEDHIGH_RBMPKI
order = [x for x in order if x in MEDHIGH_RBMPKI]
# sort by workload according to order
dfn['workload'] = pd.Categorical(dfn['workload'], order)
dfn = dfn.sort_values('workload')

sns.set_theme(style="whitegrid")
# create side-by-side two subplots
fig, (ax1) = plt.subplots(ncols=1, figsize=(7, 1.5))

PROPS = {
    'boxprops':{'edgecolor':'black'},
    'medianprops':{'color':'black'},
    'whiskerprops':{'color':'black'},
    'capprops':{'color':'black'}
}


flierprops = dict(markerfacecolor='black', markeredgecolor='black', markersize=2,
              linestyle='none')

# barplot workload on x axis, cumulative_bank_usage_stat on y axis, only for analysis_threshold = 4, only for workloads with high RBMPKI
sns.boxplot(ax=ax1, x="workload", y="bank_usage_stat", data=dfn[(dfn['analysis_threshold'] == 2) & (dfn['workload'].isin(MEDHIGH_RBMPKI))], palette="pastel", showmeans=True, meanprops={"marker":"o","markerfacecolor":"white", "markeredgecolor":"black", "markersize":"3"}, flierprops=flierprops,**PROPS)
# rotate x axis labels
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)
# rename x axis
ax1.set_xlabel("Workload")
# rename y axis
ax1.set_ylabel("Number of\nsibling row activations")


# show y until 4 for ax1
ax1.set_ylim([0, 35.84])
# y ticks in increments of 1 for ax1
ax1.set_yticks(np.arange(0, 32, 8).tolist() + [31]) 
# draw a red line at 4
ax1.axhline(y=31, color='r', linestyle='-')
# move y axis labels down
ax1.yaxis.set_label_coords(-0.08,0.1)

# make x axis tick labels smaller
ax1.tick_params(axis='x', labelsize=10)

# draw verticel line between leslie3d and ds
ax1.axvline(x=34.5, color='black', linestyle='--')
# continue the line below drawing area

# add text to the right of the vertical line
ax1.text(38.7, -30, 'RowHammer\nAttacks', fontsize=9, va='center', ha='center', color='brown')

# color the last 8 x axis tick labels blue
for tick in ax1.get_xticklabels()[-8:]:
  tick.set_color('brown')


# save as pdf tight layout
plt.savefig("figure2_sibling_row_activations.pdf", bbox_inches='tight')

# print average use_stat across workloads
# print("Average use_stat across workloads:", dfn[(dfn['analysis_threshold'] == 2)]['use_stat'].mean())
# # max and min
# print("Max use_stat across workloads:", dfn[(dfn['analysis_threshold'] == 2)]['use_stat'].max())
# print("Min use_stat across workloads:", dfn[(dfn['analysis_threshold'] == 2)]['use_stat'].min())