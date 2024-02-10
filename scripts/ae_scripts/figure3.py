# plot cumulative_bank_usage_stats
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import numpy as np

df = pd.read_csv("distr_bank_usage.csv")

MED_RBMPKI = ['510.parest', '462.libquantum', 'tpch2', 'wc_8443', 'ycsb_aserver', '473.astar', 'stream_10.trace', 'jp2_decode', '436.cactusADM', '557.xz', 'ycsb_cserver', 'ycsb_eserver', '471.omnetpp', '483.xalancbmk', '505.mcf', 'wc_map0', 'jp2_encode', 'tpch17', 'ycsb_bserver', 'tpcc64', '482.sphinx3']
HIGH_RBMPKI = ['519.lbm', '459.GemsFDTD', '450.soplex', 'h264_decode', '520.omnetpp', '433.milc', '434.zeusmp', 'bfs_dblp', '429.mcf', '549.fotonik3d', 'random_10.trace', '470.lbm', 'bfs_ny', 'bfs_cm2003', '437.leslie3d']
MEDHIGH_RBMPKI = MED_RBMPKI + HIGH_RBMPKI
RH_ESTIMATE = ['ds', 'ds-p1' , 'ds-p8', 'ds-p32', 'ms' , 'ms-p1', 'ms-p8', 'ms-p32']

MEDHIGH_RBMPKI = MED_RBMPKI + HIGH_RBMPKI + RH_ESTIMATE

# remove where workload is stream_10.trace and random_10.trace from MEDHIGH_RBMPKI
MEDHIGH_RBMPKI.remove('stream_10.trace')
# MEDHIGH_RBMPKI.remove('random_10.trace')
# MEDHIGH_RBMPKI.remove('gups')
# get rid of workloads not in MEDHIGH_RBMPKI
dfn = df[df['workload'].isin(MEDHIGH_RBMPKI)].copy()
# remove where workload is stream_10.trace and random_10.trace
dfn = dfn[dfn['workload'] != 'stream_10.trace']
# dfn = dfn[dfn['workload'] != 'random_10.trace']
dfn = dfn[dfn['workload'] != 'gups']

# rename random_10.trace to gups
dfn['workload'] = dfn['workload'].replace('random_10.trace', 'gups')

#rename random_10.trace to gups in MEDHIGH_RBMPKI
MEDHIGH_RBMPKI = [x.replace('random_10.trace', 'gups') for x in MEDHIGH_RBMPKI]

order = ['h264_encode', '511.povray', '481.wrf', '541.leela', '538.imagick', '444.namd', '447.dealII', '464.h264ref', '456.hmmer', '403.gcc', '526.blender', '544.nab', '525.x264', '508.namd', 'grep_map0', '531.deepsjeng', '458.sjeng', '435.gromacs', '445.gobmk', '401.bzip2', '507.cactuBSSN', '502.gcc', 'ycsb_abgsave', 'tpch6', '500.perlbench', '523.xalancbmk', 'ycsb_dserver', 'ycsb_cserver', '510.parest', 'ycsb_bserver', 'ycsb_eserver', 'stream_10.trace', 'tpcc64', 'ycsb_aserver', '557.xz', '482.sphinx3', 'jp2_decode', '505.mcf', 'wc_8443', 'wc_map0', '436.cactusADM', '471.omnetpp', '473.astar', 'jp2_encode', 'tpch17', '483.xalancbmk', '462.libquantum', 'tpch2', '433.milc', '520.omnetpp', '437.leslie3d', '450.soplex', '459.GemsFDTD', '549.fotonik3d', '434.zeusmp', '519.lbm', '470.lbm', '429.mcf', 'gups', 'h264_decode', 'bfs_ny', 'bfs_cm2003', 'bfs_dblp', 'ds', 'ds-p1' , 'ds-p8', 'ds-p32', 'ms' , 'ms-p1', 'ms-p8', 'ms-p32']
# remove from order, workloads not in MEDHIGH_RBMPKI
order = [x for x in order if x in MEDHIGH_RBMPKI]
# sort by workload according to order
dfn['workload'] = pd.Categorical(dfn['workload'], order)
dfn = dfn.sort_values('workload')

sns.set_theme(style="whitegrid")
# create side-by-side two subplots
fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, figsize=(7, 4.5), sharex=True)

PROPS = {
    'boxprops':{'edgecolor':'black'},
    'medianprops':{'color':'black'},
    'whiskerprops':{'color':'black'},
    'capprops':{'color':'black'}
}

flierprops = dict(markerfacecolor='black', markeredgecolor='black', markersize=2,
              linestyle='none')

# barplot workload on x axis, cumulative_bank_usage_stat on y axis, only for analysis_threshold = 4, only for workloads with high RBMPKI
sns.boxplot(ax=ax3, x="workload", y="bank_usage_stat", data=dfn[(dfn['analysis_threshold'] == 125) & (dfn['workload'].isin(MEDHIGH_RBMPKI))], palette="pastel", showmeans=True, meanprops={"marker":"o","markerfacecolor":"white", "markeredgecolor":"black", "markersize":"3"}, flierprops=flierprops,**PROPS)
# rotate x axis labels

# rename x axis
ax3.set_xlabel("Workload")

# rename y axis
ax3.set_ylabel("Average Counter Value")

# plot the same but for analysis_threshold = 32
sns.boxplot(ax=ax2, x="workload", y="bank_usage_stat", data=dfn[(dfn['analysis_threshold'] == 250) & (dfn['workload'].isin(MEDHIGH_RBMPKI))], palette="pastel", showmeans=True, meanprops={"marker":"o","markerfacecolor":"white", "markeredgecolor":"black", "markersize":"3"},flierprops=flierprops, **PROPS)
# rotate x axis labels
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=90)
ax2.set_xlabel("")
ax2.set_ylabel("Average Counter Value")


# plot the same but for analysis_threshold = 32
sns.boxplot(ax=ax1, x="workload", y="bank_usage_stat", data=dfn[(dfn['analysis_threshold'] == 500) & (dfn['workload'].isin(MEDHIGH_RBMPKI))], palette="pastel", showmeans=True, meanprops={"marker":"o","markerfacecolor":"white", "markeredgecolor":"black", "markersize":"3"},flierprops=flierprops, **PROPS)
# rotate x axis labels
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)
ax1.set_xlabel("")
ax1.set_ylabel("Sibling row activation count")

ax3.set_xlabel("Workload")
ax3.set_xticklabels(ax3.get_xticklabels(), rotation=90)

# set x axis tick labels using workload names
ax3.set_xticklabels(order)


# show y until 4 for ax1
ax3.set_ylim([0, 140])
# y ticks in increments of 1 for ax1
ax3.set_yticks(np.arange(0, 125, 32).tolist() + [125])
# draw a red line at 4
ax3.axhline(y=125, color='r', linestyle='-')
ax2.set_ylim([0, 280])
# y ticks in increments of 1 for ax1
ax2.set_yticks(np.arange(0, 249, 64).tolist() + [250])
# draw a red line at (analysis_threshold-1)
ax2.axhline(y=250, color='r', linestyle='-')
# show y until 4 for ax1
ax1.set_ylim([0, 560])
# y ticks in increments of 1 for ax1
ax1.set_yticks(np.arange(0, 500, 128).tolist() + [500])
# draw a red line at (analysis_threshold-1)
ax1.axhline(y=500, color='r', linestyle='-')

# show y until 4 for ax1

# move y axis labels down
ax1.yaxis.set_label_coords(-0.12,-0.8)
ax2.yaxis.set_label_coords(-0.09,0.3)
ax3.yaxis.set_label_coords(-0.09,0.3)

# make x axis tick labels smaller
ax1.tick_params(axis='x', labelsize=10)
ax2.tick_params(axis='x', labelsize=10)
ax3.tick_params(axis='x', labelsize=10)

# remove ax2-3 y axis labels
ax2.set_ylabel('')
ax3.set_ylabel('')


# title each ax
ax3.set_title("RowHammer Threshold $(N_{RH})$ = 125")
ax2.set_title("RowHammer Threshold $(N_{RH})$ = 250")
ax1.set_title("RowHammer Threshold $(N_{RH})$ = 500")

# draw verticel line between leslie3d and ds
ax1.axvline(x=34.5, color='black', linestyle='--')
ax2.axvline(x=34.5, color='black', linestyle='--')
ax3.axvline(x=34.5, color='black', linestyle='--')
# continue the line below drawing area
# add text to the right of the vertical line
ax3.text(38.7, -140, 'RowHammer\nAttacks', fontsize=9, va='center', ha='center', color='brown')

# color the last 8 x axis tick labels blue
for tick in ax1.get_xticklabels()[-8:]:
  tick.set_color('brown')
# color the last 8 x axis tick labels blue
for tick in ax2.get_xticklabels()[-8:]:
  tick.set_color('brown')
# color the last 8 x axis tick labels blue
for tick in ax3.get_xticklabels()[-8:]:
  tick.set_color('brown')

# reduce gap between subplots
plt.subplots_adjust(hspace=0.3)

# save as pdf tight layout
plt.savefig("figure3_distr_counter_values.pdf", bbox_inches='tight')