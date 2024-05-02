MY_MECHANISM_NAME = 'ABACuS'

### READ RESULTS INTO PANDAS DATAFRAME
import pandas as pd
import os
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

resultsdir = "../../ae-results"
# list all directories in resultsdir
configs = [d for d in os.listdir(resultsdir) if os.path.isdir(os.path.join(resultsdir, d))]
configs = ['Baseline.yaml', 'Hydra-Baseline.yaml', 'REGA125.yaml', 'REGA250.yaml', 'REGA500.yaml', 'REGA1000.yaml', 'Graphene125.yaml', 'Graphene250.yaml', 'Graphene500.yaml', 'Graphene1000.yaml', 'Hydra125.yaml', 'Hydra250.yaml', 'Hydra500.yaml', 'Hydra1000.yaml', 'PARA125.yaml', 'PARA250.yaml', 'PARA500.yaml', 'PARA1000.yaml', 
           'ABACUS125.yaml', 'ABACUS250.yaml', 'ABACUS500.yaml', 'ABACUS1000.yaml']
# print found configs
print('Found configs: {}'.format(configs))
# list all directories under all configs
workloads = []
for c in configs:
    workloads.append([d for d in os.listdir(os.path.join(resultsdir, c)) if os.path.isdir(os.path.join(resultsdir, c, d))])
# find only the intersection of all workloads
workloads = list(set.intersection(*map(set, workloads)))
# print found workloads
print('Found workloads: {}'.format(workloads))

stats_per_config_workload = []
workloads = [w for w in workloads if not '-' in w]

# for every config + workload directory
for c in configs:
    for w in workloads:
        # find all files in the directory
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

# find elements where workload does not contain '-'
# these are multi core workloads
stats = stats[~stats['workload'].str.contains('-')]

# remove these two workloads: stream_10.trace and random_10.trace
stats = stats[~stats['workload'].isin(['gups'])]
# also from workloads
workloads = [w for w in workloads if not w in ['gups']]

# make sure config is string
stats['config'] = stats['config'].astype(str)

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

stats.loc[stats['workload'] == 'random_10.trace', 'workload'] = 'gups'

# increasing order of rbmpki
# order = ['511.povray', '481.wrf', '541.leela', '538.imagick', '444.namd', '447.dealII', '464.h264ref', '456.hmmer', '403.gcc', '526.blender', '544.nab', '525.x264', '508.namd', '531.deepsjeng', '458.sjeng', '435.gromacs', '445.gobmk', '401.bzip2', '507.cactuBSSN', '502.gcc', '500.perlbench', '523.xalancbmk', '510.parest', '557.xz', '482.sphinx3', '505.mcf', '436.cactusADM', '471.omnetpp', '473.astar', '483.xalancbmk', '462.libquantum', '433.milc', '520.omnetpp', '437.leslie3d', '450.soplex', '459.GemsFDTD', '549.fotonik3d', '434.zeusmp', '519.lbm', '470.lbm', '429.mcf']
order = ['h264_encode', '511.povray', '481.wrf', '541.leela', '538.imagick', '444.namd', '447.dealII', '464.h264ref', '456.hmmer', '403.gcc', '526.blender', '544.nab', '525.x264', '508.namd', 'grep_map0', '531.deepsjeng', '458.sjeng', '435.gromacs', '445.gobmk', '401.bzip2', '507.cactuBSSN', '502.gcc', 'ycsb_abgsave', 'tpch6', '500.perlbench', '523.xalancbmk', 'ycsb_dserver', 'ycsb_cserver', '510.parest', 'ycsb_bserver', 'ycsb_eserver', 'stream_10.trace', 'tpcc64', 'ycsb_aserver', '557.xz', '482.sphinx3', 'jp2_decode', '505.mcf', 'wc_8443', 'wc_map0', '436.cactusADM', '471.omnetpp', '473.astar', 'jp2_encode', 'tpch17', '483.xalancbmk', '462.libquantum', 'tpch2', '433.milc', '520.omnetpp', '437.leslie3d', '450.soplex', '459.GemsFDTD', '549.fotonik3d', '434.zeusmp', '519.lbm', '470.lbm', '429.mcf', 'gups', 'h264_decode', 'bfs_ny', 'bfs_cm2003', 'bfs_dblp']

# remove all workloads not in order
stats = stats[stats['workload'].isin(order)]
# also from the workload list
workloads = [w for w in workloads if w in order]

# order workloads according to the order
stats['workload'] = pd.Categorical(stats['workload'], categories=order, ordered=True)

stats_copy = stats.copy()

# import MultipleLocator
from matplotlib.ticker import MultipleLocator

# use seaborn-deep style
sns.set(font_scale=1.0)
sns.set_style("whitegrid")
sns.set_palette("pastel", n_colors=5)

stats = stats_copy.copy()
# instructions per cycle (IPC) is record_cycles_insts_0 / record_cycs_core_0
stats['ramulator.ipc'] = stats['ramulator.record_insts_core_0'] / stats['ramulator.record_cycs_core_0']


stats['ramulator.rbmpki'] = (stats['ramulator.row_conflicts_channel_0_core'] + stats['ramulator.row_misses_channel_0_core']) /\
                            stats['ramulator.record_insts_core_0'] * 1000

# copy the IPC of the baseline config as to all configs
baseline = stats[stats['config'] == 'Baseline']
baseline = baseline[['workload', 'ramulator.ipc', 'ramulator.read_latency_avg_0', 'ramulator.rbmpki', 'ramulator.window_full_stall_cycles_core_0']]
# baseline
baseline.columns = ['workload', 'ramulator.baseline_ipc', 'ramulator.baseline_read_latency_avg_0', 'ramulator.baseline_rbmpki', 'ramulator.baseline_stall_cycles']
stats = pd.merge(stats, baseline, on='workload')
#hydra baseline
hydra_baseline = stats[stats['config'] == 'Hydra-Baseline']
hydra_baseline = hydra_baseline[['workload', 'ramulator.ipc']]
# hydra_baseline
hydra_baseline.columns = ['workload', 'ramulator.hydra_baseline_ipc']
stats = pd.merge(stats, hydra_baseline, on='workload')

stats['ramulator.normalized_ipc'] = stats['ramulator.ipc'] / stats['ramulator.baseline_ipc']
stats['ramulator.normalized_read_latency'] = stats['ramulator.read_latency_avg_0'] / stats['ramulator.baseline_read_latency_avg_0']
stats['ramulator.normalized_stall_cycles'] = stats['ramulator.window_full_stall_cycles_core_0'] / stats['ramulator.baseline_stall_cycles']
stats['ramulator.normalized_rbmpki'] = stats['ramulator.rbmpki'] / stats['ramulator.baseline_rbmpki']

# # instructions per cycle (IPC) is record_cycles_insts_0 / record_cycs_core_0
# stats['ramulator.ipc'] = stats['ramulator.record_insts_core_0'] / stats['ramulator.record_cycs_core_0']

# # copy the IPC of the baseline config as to all configs
# baseline = stats[stats['config'] == 'Baseline']
# baseline = baseline[['workload', 'ramulator.ipc']]
# # baseline
# baseline.columns = ['workload', 'ramulator.baseline_ipc']
# stats = pd.merge(stats, baseline, on='workload')

# #hydra baseline
# hydra_baseline = stats[stats['config'] == 'Hydra-Baseline']
# hydra_baseline = hydra_baseline[['workload', 'ramulator.ipc']]
# # hydra_baseline
# hydra_baseline.columns = ['workload', 'ramulator.hydra_baseline_ipc']
# stats = pd.merge(stats, hydra_baseline, on='workload')

# stats['ramulator.normalized_ipc'] = stats['ramulator.ipc'] / stats['ramulator.baseline_ipc']

# normalized ipc for hydra is not correct, so we overwrite it with the correct value
stats.loc[stats['config'].str.contains('Hydra'), 'ramulator.normalized_ipc'] = stats['ramulator.ipc'] / stats['ramulator.hydra_baseline_ipc']


# new dataframe that does not have the baseline configs
stats_no_baseline = stats[~stats['config'].str.contains('Baseline')]

# new dataframe that does not have the baseline configs
print(stats_no_baseline['config'].unique())

# order nRH from high to low
stats_no_baseline['nrh'] = pd.Categorical(stats_no_baseline['nrh'], categories=[1000, 500, 250, 125], ordered=True)

# order config in this order: abacus, Graphene, Hydra, REGA, PARA
stats_no_baseline['config'] = pd.Categorical(stats_no_baseline['config'], categories=['ABACuS', 'Graphene', 'Hydra', 'REGA', 'PARA'], ordered=True)

#boxplot of normalized IPC
fig, ax = plt.subplots(figsize=(10, 4))
# show mean values as well
ax = sns.boxplot(x="nrh", y="ramulator.normalized_ipc", hue="config", data=stats_no_baseline, showmeans=True, meanprops={"marker":"o","markerfacecolor":"white", "markeredgecolor":"black"})
ax.set_xlabel('RowHammer Threshold ($N_{RH}$)')
ax.set_ylabel('Normalized IPC Distribution')
# draw a red line at y = 1.0, label it as baseline IPC
ax.axhline(y=1.0, color='r', linestyle='--')
# write above the red line 'baseline IPC'
ax.text(0.02, 0.92, 'Baseline IPC', color='#e74c3c', transform=ax.transAxes, fontsize=15)
# extend the y axis to 1.2
ax.set_ylim(0.2, 1.1)
# y axis tick every 0.1 increment
ax.yaxis.set_major_locator(MultipleLocator(0.1))
# color the 5th y tick red
ax.get_yticklabels()[9].set_color('#e74c3c')
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
plt.show()

# save figure
fig.savefig('figure9_abacus_performance_comparison_single_core.pdf', bbox_inches='tight')

# list mean normalized_ipc at 1000 nRH for all configs
# print(stats_no_baseline.groupby(['config','nrh'])['ramulator.normalized_ipc'].mean())

# Average normalized IPC for REGA at nRH = 125
print(1-stats_no_baseline[(stats_no_baseline['config'] == 'REGA') & (stats_no_baseline['nrh'] == 125)]['ramulator.normalized_ipc'].mean())
# Same for PARA at 1000 and 125
print(1-stats_no_baseline[(stats_no_baseline['config'] == 'PARA') & (stats_no_baseline['nrh'] == 1000)]['ramulator.normalized_ipc'].mean())
print(1-stats_no_baseline[(stats_no_baseline['config'] == 'PARA') & (stats_no_baseline['nrh'] == 125)]['ramulator.normalized_ipc'].mean())
# Average normalized IPC for ABACuS divided by Hydra at each nRH
print(1/stats_no_baseline[(stats_no_baseline['config'] == 'Hydra') & (stats_no_baseline['nrh'] == 1000)]['ramulator.normalized_ipc'].mean()/stats_no_baseline[(stats_no_baseline['config'] == 'ABACuS') & (stats_no_baseline['nrh'] == 1000)]['ramulator.normalized_ipc'].mean())
print(1/stats_no_baseline[(stats_no_baseline['config'] == 'Hydra') & (stats_no_baseline['nrh'] == 500)]['ramulator.normalized_ipc'].mean()/stats_no_baseline[(stats_no_baseline['config'] == 'ABACuS') & (stats_no_baseline['nrh'] == 500)]['ramulator.normalized_ipc'].mean())
print(1/stats_no_baseline[(stats_no_baseline['config'] == 'Hydra') & (stats_no_baseline['nrh'] == 250)]['ramulator.normalized_ipc'].mean()/stats_no_baseline[(stats_no_baseline['config'] == 'ABACuS') & (stats_no_baseline['nrh'] == 250)]['ramulator.normalized_ipc'].mean())
print(1/stats_no_baseline[(stats_no_baseline['config'] == 'Hydra') & (stats_no_baseline['nrh'] == 125)]['ramulator.normalized_ipc'].mean()/stats_no_baseline[(stats_no_baseline['config'] == 'ABACuS') & (stats_no_baseline['nrh'] == 125)]['ramulator.normalized_ipc'].mean())

# average rbmpki of Hydra at nRH 125 divided by ABACuS at nRH 125
print(1/(stats_no_baseline[(stats_no_baseline['config'] == 'ABACuS') & (stats_no_baseline['nrh'] == 125)]['ramulator.normalized_rbmpki'].mean()/stats_no_baseline[(stats_no_baseline['config'] == 'Hydra') & (stats_no_baseline['nrh'] == 125)]['ramulator.normalized_rbmpki'].mean()))
# same for memory latency
print(1/(stats_no_baseline[(stats_no_baseline['config'] == 'ABACuS') & (stats_no_baseline['nrh'] == 125)]['ramulator.normalized_read_latency'].mean()/stats_no_baseline[(stats_no_baseline['config'] == 'Hydra') & (stats_no_baseline['nrh'] == 125)]['ramulator.normalized_read_latency'].mean()))

# mean number of preventive refreshes for ABACuS at 125 nrh divided by graphene
print(stats_no_baseline[(stats_no_baseline['config'] == 'ABACuS') & (stats_no_baseline['nrh'] == 125)]['ramulator.preventive_refreshes_channel_0_core'].mean()/stats_no_baseline[(stats_no_baseline['config'] == 'Graphene') & (stats_no_baseline['nrh'] == 125)]['ramulator.preventive_refreshes_channel_0_core'].mean())
# mean number of stall cycles for the same
print(1/(stats_no_baseline[(stats_no_baseline['config'] == 'ABACuS') & (stats_no_baseline['nrh'] == 125)]['ramulator.normalized_stall_cycles'].mean()/stats_no_baseline[(stats_no_baseline['config'] == 'Graphene') & (stats_no_baseline['nrh'] == 125)]['ramulator.normalized_stall_cycles'].mean()))
