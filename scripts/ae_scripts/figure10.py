MY_MECHANISM_NAME = 'ABACuS'

### READ RESULTS INTO PANDAS DATAFRAME
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt

resultsdir = "../../ae-results"
# list all directories in resultsdir
configs = [d for d in os.listdir(resultsdir) if os.path.isdir(os.path.join(resultsdir, d))]
configs = ['Baseline.yaml', 'MC-Baseline.yaml', 'Hydra-Baseline.yaml', 'REGA125.yaml', 'REGA250.yaml', 'REGA500.yaml', 'REGA1000.yaml', 'Graphene125.yaml', 'Graphene250.yaml', 'Graphene500.yaml', 'Graphene1000.yaml', 'Hydra125.yaml', 'Hydra250.yaml', 'Hydra500.yaml', 'Hydra1000.yaml', 'PARA125.yaml', 'PARA250.yaml', 'PARA500.yaml', 'PARA1000.yaml', 
           'ABACUS125.yaml', 'ABACUS250.yaml', 'ABACUS500.yaml', 'ABACUS1000.yaml']
# print found configs
print('Found configs: {}'.format(configs))
# list all directories under all configs
workloads = []
for c in configs:
    workloads.append([d for d in os.listdir(os.path.join(resultsdir, c)) if os.path.isdir(os.path.join(resultsdir, c, d))])
# find only the intersection of all workloads
# workloads = list(set.intersection(*map(set, workloads)))
# keep only unique workloads
workloads = list(set([item for sublist in workloads for item in sublist]))

# print found workloads
print('Found workloads: {}'.format(workloads))

stats_per_config_workload = []

# for every config + workload directory
for c in configs:
    for w in workloads:
        # find all files in the directory
        if os.path.isdir(os.path.join(resultsdir, c, w)):
            files = [f for f in os.listdir(os.path.join(resultsdir, c, w)) if os.path.isfile(os.path.join(resultsdir, c, w, f))]
            # find the stats file
            stat_files = [f for f in files if f.endswith('.stats')]
            # if there is a stats file
            if stat_files:
                for stat_file in stat_files:
                    # if the stats_file has less than three lines skip it
                    if len(open(os.path.join(resultsdir, c, w, stat_file)).readlines()) < 3:
                        continue
                    
                    # print the name of the stats_file
                    print('Found stats file: {}'.format(os.path.join(os.path.join(resultsdir, c, w, stat_file))))

                    extension = ''
                    # if stats_file file name itself does not start with DDR4, parse it a bit
                    if not stat_file.startswith('DDR4'):
                        # get the config name from the stats_file name
                        extension = '_'.join(stat_file.split('_')[:-1])
                        # prepend underscore to extension
                        extension = '_' + extension

                    # read the stats file, name columns: 'name', 'value', 'description'
                    df = pd.read_csv(os.path.join(resultsdir, c, w, stat_file), header=None).T
                    df.columns = df.iloc[0]
                    df.drop(0,inplace=True)
                    # add a new column called 'config' with the config name
                    df['config'] = c + extension
                    # add a new column called 'workload' with the workload name
                    df['workload'] = w
                    # print the stats file
                    # print('Config: {}, Workload: {}, Stats: {}'.format(c, w, df))
                    # append the stats to the list
                    df.reset_index(inplace=True, drop=True)
                    stats_per_config_workload.append(df)
            else:
                print('Config: {}, Workload: {}, Stats: No stats file found'.format(c, w))

# concatenate all stats into one dataframe
stats = pd.concat(stats_per_config_workload)

# remove workloads that have "gups" in them
stats = stats[~stats['workload'].str.contains('gups')]

# grep_map0 produced 0 cycles for any core except 7, weird bug, ignore for now
# stats = stats[~stats['workload'].str.contains('grep_map0')]

# also remove them from the list
workloads = [w for w in workloads if 'gups' not in w]

# grep_map0 produced 0 cycles for any core except 7, weird bug, ignore for now
# workloads = [w for w in workloads if 'grep_map0' not in w]


# replace all instances of "random_10.trace" in workload names with "gups"
stats['workload'] = stats['workload'].str.replace('random_10.trace', 'gups')

# all workloads
HIGH_RBMPKI = ['h264_encode', '511.povray', '481.wrf', '541.leela', '538.imagick', '444.namd', '447.dealII', '464.h264ref', '456.hmmer', '403.gcc', '526.blender', '544.nab', '525.x264', '508.namd', 'grep_map0', '531.deepsjeng', '458.sjeng', '435.gromacs', '445.gobmk', '401.bzip2', '507.cactuBSSN', '502.gcc', 'ycsb_abgsave', 'tpch6', '500.perlbench', '523.xalancbmk', 'ycsb_dserver', 'ycsb_cserver', '510.parest', 'ycsb_bserver', 'ycsb_eserver', 'stream_10.trace', 'tpcc64', 'ycsb_aserver', '557.xz', '482.sphinx3', 'jp2_decode', '505.mcf', 'wc_8443', 'wc_map0', '436.cactusADM', '471.omnetpp', '473.astar', 'jp2_encode', 'tpch17', '483.xalancbmk', '462.libquantum', 'tpch2', '433.milc', '520.omnetpp', '437.leslie3d', '450.soplex', '459.GemsFDTD', '549.fotonik3d', '434.zeusmp', '519.lbm', '470.lbm', '429.mcf', 'gups', 'h264_decode', 'bfs_ny', 'bfs_cm2003', 'bfs_dblp']

# HIGH_RBMPKI = ['519.lbm', '459.GemsFDTD', '450.soplex', 'h264_decode', '520.omnetpp', '433.milc', '434.zeusmp', 'bfs_dblp', '429.mcf', '549.fotonik3d', '470.lbm', 'bfs_ny', 'bfs_cm2003', '437.leslie3d', 'gups']

# HIGH_RBMPKI = ['h264_encode', '511.povray', '481.wrf', '541.leela', '538.imagick', '444.namd', '447.dealII', '464.h264ref', '456.hmmer', '403.gcc', '526.blender', '544.nab', '525.x264', '508.namd', 'grep_map0', '531.deepsjeng', '458.sjeng', '435.gromacs', '445.gobmk', '401.bzip2', '507.cactuBSSN', '502.gcc', 'ycsb_abgsave', 'tpch6', '500.perlbench', '523.xalancbmk', 'ycsb_dserver', 'ycsb_cserver', '510.parest', 'ycsb_bserver', 'ycsb_eserver', 'stream_10.trace', 'tpcc64', 'ycsb_aserver', '557.xz', '482.sphinx3', 'jp2_decode', '505.mcf', 'wc_8443', 'wc_map0', '436.cactusADM', '471.omnetpp', '473.astar', 'jp2_encode', 'tpch17', '483.xalancbmk', '462.libquantum', 'tpch2', '433.milc', '520.omnetpp', '437.leslie3d', '450.soplex', '459.GemsFDTD', '549.fotonik3d', '434.zeusmp', '519.lbm', '470.lbm', '429.mcf', 'random_10.trace', 'h264_decode', 'bfs_ny', 'bfs_cm2003', 'bfs_dblp']

#HIGH_RBMPKI = ['531.deepsjeng', '502.gcc', '541.leela', '435.gromacs', '481.wrf', '458.sjeng', '445.gobmk', '444.namd', '508.namd', '401.bzip2', '456.hmmer', '403.gcc', '464.h264ref', '526.blender', '447.dealII', '544.nab', '523.xalancbmk', '500.perlbench', '538.imagick', '525.x264', '507.cactuBSSN', '511.povray', '462.libquantum', '473.astar', '510.parest', '482.sphinx3', '505.mcf', '557.xz', '471.omnetpp', '483.xalancbmk', '436.cactusADM', '520.omnetpp', '450.soplex', '470.lbm', '519.lbm', '434.zeusmp', '433.milc', '459.GemsFDTD', '549.fotonik3d', '429.mcf', '437.leslie3d']
stats = stats[stats['workload'].str.contains('|'.join(HIGH_RBMPKI))]

# remove h264_decode fro workloads
# stats = stats[~stats['workload'].str.contains('h264_decode')]
# remove h264_decode from HIGH_RBMPKI
# HIGH_RBMPKI.remove('h264_decode')

# keep mc_only_stats only for workloads that contain the strings in HIGH_RBMPKI

# remove "-16DR" from config names
stats['config'] = stats['config'].str.replace('-16DR', '')

# replace 1K with 1000 in config names
stats['config'] = stats['config'].str.replace('1K', '1000')

# replace 'Baseline' with 'Baseline0'
stats['config'] = stats['config'].str.replace('Baseline', 'Baseline0')

# add a new column that stores in integer the number in the config name
stats['nrh'] = stats['config'].str.extract('(\d+)').astype(int)

# remove numbers from config names
stats['config'] = stats['config'].str.replace('\d+', '', regex=True)

# remove yaml from config names
stats['config'] = stats['config'].str.replace('.yaml', '')

# replace SPR with APAR
stats['config'] = stats['config'].str.replace('ABACUS', MY_MECHANISM_NAME)

stats_copy = stats.copy()

# remove from mc_only_stats the workloads that contain less than 7 dashes
mc_only_stats = stats[stats['workload'].str.count('-') >= 7]
# remove from mc_only_stats workloads that contain stream_10.trace or random_10.trace
mc_only_stats = mc_only_stats[~mc_only_stats['workload'].str.contains('stream_10.trace')]
mc_only_stats = mc_only_stats[~mc_only_stats['workload'].str.contains('random_10.trace')]
sc_only_stats = stats[~stats['workload'].str.contains('-')].copy()

# expand the workload column into four columns by splitting using '-'
mc_only_stats[['wl0', 'wl1', 'wl2', 'wl3', 'wl4', 'wl5', 'wl6', 'wl7']] = mc_only_stats['workload'].str.split('-', expand=True)
sc_only_stats['ramulator.ipc'] = sc_only_stats['ramulator.record_insts_core_0'] / sc_only_stats['ramulator.record_cycs_core_0']

# for each ramulator.record_insts_core_i column, if ramulator.record_cycs_core_i is 0, set it to 1 (This is to prevent division by zero)
for i in range(0, 8):
    mc_only_stats.loc[mc_only_stats['ramulator.record_cycs_core_{}'.format(i)] == 0, 'ramulator.record_cycs_core_{}'.format(i)] = 1

# for each ramulator.record_insts_core_i column, divide it by ramulator.record_cycs_core_i column and add it as ipci column
for i in range(0, 8):
    mc_only_stats['ipc{}'.format(i)] = mc_only_stats['ramulator.record_insts_core_{}'.format(i)] / mc_only_stats['ramulator.record_cycs_core_{}'.format(i)]

# write to csv mc_only_stats but only the config, workload and ipci columns
mc_only_stats[['config', 'wl0', 'wl1', 'wl2', 'wl3', 'wl4', 'wl5', 'wl6', 'wl7', 'ipc0', 'ipc1', 'ipc2', 'ipc3', 'ipc4', 'ipc5', 'ipc6', 'ipc7', 'nrh']].to_csv('mc_only_stats.csv', index=False)

# use seaborn-deep style
sns.set(font_scale=1.0)
sns.set_style("whitegrid")
sns.set_palette("pastel", n_colors=5)

stats_parsed = pd.read_csv('mc_only_stats.csv')

stats_parsed['workload'] = stats_parsed['wl0']

# copy the IPC of the baseline config as to all configs
baseline = sc_only_stats[sc_only_stats['config'] == 'MC-Baseline']
baseline = baseline[['workload', 'ramulator.ipc']]

# baseline
baseline.columns = ['workload', 'ramulator.baseline_ipc']
stats_parsed = pd.merge(stats_parsed, baseline, on='workload')

# for all ipc columns, divide by the baseline ipc
for i in range(0, 8):
    stats_parsed['normalized_ipc{}'.format(i)] = stats_parsed['ipc{}'.format(i)] / stats_parsed['ramulator.baseline_ipc']

stats_parsed['weighted_speedup'] = stats_parsed['normalized_ipc0'] + stats_parsed['normalized_ipc1'] + stats_parsed['normalized_ipc2'] + stats_parsed['normalized_ipc3'] + stats_parsed['normalized_ipc4'] + stats_parsed['normalized_ipc5'] + stats_parsed['normalized_ipc6'] + stats_parsed['normalized_ipc7']

baselinepp = stats_parsed[stats_parsed['config'] == 'Baseline']
baselinepp = baselinepp[['workload', 'weighted_speedup']]
# baseline
baselinepp.columns = ['workload', 'baseline_weighted_speedup']
stats_parsed = pd.merge(stats_parsed, baselinepp, on='workload')

stats_parsed['normalized_weighted_speedup'] = stats_parsed['weighted_speedup'] / stats_parsed['baseline_weighted_speedup']

# for normalized_weighted_speedups above 1.0, make them 1.0
# stats_parsed.loc[stats_parsed['normalized_weighted_speedup'] > 1.0, 'normalized_weighted_speedup'] = 1.0

stats_parsed = stats_parsed[~stats_parsed['config'].str.contains('Baseline')]

# print(stats_parsed['workload'].unique())

# order nRH from high to low
stats_parsed['nrh'] = pd.Categorical(stats_parsed['nrh'], categories=[1000, 500, 250, 125], ordered=True)

# order config in this order: abacus, Graphene, Hydra, REGA, PARA
stats_parsed['config'] = pd.Categorical(stats_parsed['config'], categories=['ABACuS', 'Graphene', 'Hydra', 'REGA', 'PARA'], ordered=True)

#boxplot of normalized IPC
fig, ax = plt.subplots(figsize=(10, 4))

# show mean values do not plot outliers
ax = sns.boxplot(x="nrh", y="normalized_weighted_speedup", hue="config", data=stats_parsed, showmeans=True, meanprops={"marker":"o","markerfacecolor":"white", "markeredgecolor":"black"})#, showfliers=False)

ax.set_xlabel('RowHammer Threshold ($N_{RH}$)')
ax.set_ylabel('Normalized Weighted Speedup')
# draw a red line at y = 1.0, label it as baseline IPC
ax.axhline(y=1.0, color='r', linestyle='--')
# write above the red line 'baseline IPC'
ax.text(0.02, 0.94, 'Baseline weighted speedup', color='#e74c3c', transform=ax.transAxes, fontsize=15)
# extend the y axis to 1.2
ax.set_ylim(0, 1.1)
# color the 5th y tick red
ax.get_yticklabels()[5].set_color('#e74c3c')
# make axis tick font bigger
ax.tick_params(axis='both', which='major', labelsize=14)
# draw vertical lines to separate the rowhammer threshold values
ax.axvline(x=0.5, color='grey', linestyle='-', alpha=0.5)
ax.axvline(x=1.5, color='grey', linestyle='-', alpha=0.5)
ax.axvline(x=2.5, color='grey', linestyle='-', alpha=0.5)
# make x and y axis labels bigger
ax.xaxis.label.set_size(16)
ax.yaxis.label.set_size(16)

# put the legend on top of the plot
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.2), ncol=5, fancybox=True, shadow=True, fontsize=12)

plt.tight_layout()

# save figure
fig.savefig('figure10_abacus_performance_comparison_multi_core.pdf', bbox_inches='tight')
# export csv to file
stats_parsed.to_csv('abacus_performance_comparison_multi_core.csv', index=False)


# average normalized ws across all workloads for ABACuS at 1K nRH (print in one line)
print(1-(stats_parsed[(stats_parsed['config'] == 'ABACuS') & (stats_parsed['nrh'] == 1000)]['normalized_weighted_speedup'].mean()))
# same for other 3 thresholds
print(1-(stats_parsed[(stats_parsed['config'] == 'ABACuS') & (stats_parsed['nrh'] == 500)]['normalized_weighted_speedup'].mean()))
print(1-(stats_parsed[(stats_parsed['config'] == 'ABACuS') & (stats_parsed['nrh'] == 250)]['normalized_weighted_speedup'].mean()))
print(1-(stats_parsed[(stats_parsed['config'] == 'ABACuS') & (stats_parsed['nrh'] == 125)]['normalized_weighted_speedup'].mean()))

#Hydra's average normalized ws across all workloads at 1K nRH (print in one line) divided by ABACuS's
print(-(stats_parsed[(stats_parsed['config'] == 'Hydra') & (stats_parsed['nrh'] == 1000)]['normalized_weighted_speedup'].mean())+(stats_parsed[(stats_parsed['config'] == 'ABACuS') & (stats_parsed['nrh'] == 1000)]['normalized_weighted_speedup'].mean()))

print(1/(stats_parsed[(stats_parsed['config'] == 'ABACuS') & (stats_parsed['nrh'] == 125)]['normalized_weighted_speedup'].mean()))
# Just Hydra's overhead at nRH 125
print(1-(stats_parsed[(stats_parsed['config'] == 'Hydra') & (stats_parsed['nrh'] == 125)]['normalized_weighted_speedup'].mean()))
# REGA's
print(1-(stats_parsed[(stats_parsed['config'] == 'REGA') & (stats_parsed['nrh'] == 125)]['normalized_weighted_speedup'].mean()))
# PARA's
print(1-(stats_parsed[(stats_parsed['config'] == 'PARA') & (stats_parsed['nrh'] == 125)]['normalized_weighted_speedup'].mean()))

# Graphene's at nRH 1000
print(1-(stats_parsed[(stats_parsed['config'] == 'Graphene') & (stats_parsed['nrh'] == 1000)]['normalized_weighted_speedup'].mean()))

print(1-(stats_parsed[(stats_parsed['config'] == 'ABACuS') & (stats_parsed['nrh'] == 1000)]['normalized_weighted_speedup'].min()))

# Hydra max overhead at 125
print(1-(stats_parsed[(stats_parsed['config'] == 'Hydra') & (stats_parsed['nrh'] == 125)]['normalized_weighted_speedup'].min()))
