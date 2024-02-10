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

# normalized ipc for hydra is not correct, so we overwrite it with the correct value
stats.loc[stats['config'].str.contains('Hydra'), 'ramulator.normalized_ipc'] = stats['ramulator.ipc'] / stats['ramulator.hydra_baseline_ipc']

# add the geometric normalized ipc average as a new workload to every config
geometric_mean = stats.groupby(['config','nrh'])['ramulator.normalized_ipc'].apply(lambda x: x.prod()**(1.0/len(x))).reset_index()
geometric_mean['workload'] = 'GeoMean'



stats = pd.concat([stats, geometric_mean])

# order in decreasing nRH (the nRH column) use pd.Categorical on nrh
stats['nrh'] = pd.Categorical(stats['nrh'], categories=[1000, 500, 250, 125], ordered=True)


# order = ['GeoMean', '531.deepsjeng', '502.gcc', '541.leela', '435.gromacs', '481.wrf', '458.sjeng', '445.gobmk', '444.namd', '508.namd', '401.bzip2', '456.hmmer', '403.gcc', '464.h264ref', '526.blender', '447.dealII', '544.nab', '523.xalancbmk', '500.perlbench', '538.imagick', '525.x264', '507.cactuBSSN', '511.povray', '462.libquantum', '473.astar', '510.parest', '482.sphinx3', '505.mcf', '557.xz', '471.omnetpp', '483.xalancbmk', '436.cactusADM', '520.omnetpp', '450.soplex', '470.lbm', '519.lbm', '434.zeusmp', '433.milc', '459.GemsFDTD', '549.fotonik3d', '429.mcf', '437.leslie3d']
order = ['h264_encode', '511.povray', '481.wrf', '541.leela', '538.imagick', '444.namd', '447.dealII', '464.h264ref', '456.hmmer', '403.gcc', '526.blender', '544.nab', '525.x264', '508.namd', 'grep_map0', '531.deepsjeng', '458.sjeng', '435.gromacs', '445.gobmk', '401.bzip2', '507.cactuBSSN', '502.gcc', 'ycsb_abgsave', 'tpch6', '500.perlbench', '523.xalancbmk', 'ycsb_dserver', 'ycsb_cserver', '510.parest', 'ycsb_bserver', 'ycsb_eserver', 'tpcc64', 'ycsb_aserver', '557.xz', '482.sphinx3', 'jp2_decode', '505.mcf', 'wc_8443', 'wc_map0', '436.cactusADM', '471.omnetpp', '473.astar', 'jp2_encode', 'tpch17', '483.xalancbmk', '462.libquantum', 'tpch2', '433.milc', '520.omnetpp', '437.leslie3d', '450.soplex', '459.GemsFDTD', '549.fotonik3d', '434.zeusmp', '519.lbm', '470.lbm', '429.mcf', 'gups', 'h264_decode', 'bfs_ny', 'bfs_cm2003', 'bfs_dblp','GeoMean']

# order = ['GeoMean', '511.povray', '481.wrf', '541.leela', '538.imagick', '444.namd', '447.dealII', '464.h264ref', '456.hmmer', '403.gcc', '526.blender', '544.nab', '525.x264', '508.namd', '531.deepsjeng', '458.sjeng', '435.gromacs', '445.gobmk', '401.bzip2', '507.cactuBSSN', '502.gcc', '500.perlbench', '523.xalancbmk', '510.parest', '557.xz', '482.sphinx3', '505.mcf', '436.cactusADM', '471.omnetpp', '473.astar', '483.xalancbmk', '462.libquantum', '433.milc', '520.omnetpp', '437.leslie3d', '450.soplex', '459.GemsFDTD', '549.fotonik3d', '434.zeusmp', '519.lbm', '470.lbm', '429.mcf']

stats['workload'] = pd.Categorical(stats['workload'], categories=order, ordered=True)

#barplot of normalized IPC, also draw edges around bars
fig, ax = plt.subplots(figsize=(13, 4))
ax = sns.barplot(x='workload', y='ramulator.normalized_ipc', hue='nrh', data=stats[(stats['config'] == 'ABACuS')], edgecolor='black', linewidth=0.5)


ax.set_xlabel('Workload')
ax.set_ylabel('Normalized IPC')
# move ylabel down
ax.yaxis.set_label_coords(-0.045,0.45)
# draw a red line at y = 1.0, label it as baseline IPC
ax.axhline(y=1.0, color='r', linestyle='--')
# write above the red line 'baseline IPC' using the same pastel red color
ax.text(0.01, 0.7, 'Baseline IPC', color='#e74c3c', transform=ax.transAxes, fontsize=15)
# extend the y axis to 1.2
ax.set_ylim(0.6, 1.2)
# color the 5th y tick red
ax.get_yticklabels()[2].set_color('#e74c3c')
# rotate x axis ticks
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
# make axis tick font bigger
ax.tick_params(axis='both', which='major', labelsize=11)
ax.tick_params(axis='y', which='major', labelsize=12)

# # draw vertical lines to separate the rowhammer threshold values
ax.axvline(x=26.52, color='grey', linestyle='-', alpha=0.5)
# put text before the line saying "LOW RBMPKI"
ax.text(0.33, 0.7, 'LOW RBMPKI', color='grey', transform=ax.transAxes, fontsize=12)
# put arrow to the left above text
ax.annotate('', xy=(19.5, 1.08), xytext=(25.5, 1.08), arrowprops=dict(facecolor='grey', shrink=0.01, width=3, headwidth=10, alpha=0.5))
ax.axvline(x=46.52, color='grey', linestyle='-', alpha=0.5)
ax.text(0.65, 0.7, 'MED. RBMPKI', color='grey', transform=ax.transAxes, fontsize=12)
ax.annotate('', xy=(39.5, 1.08), xytext=(45.5, 1.08), arrowprops=dict(facecolor='grey', shrink=0.01, width=3, headwidth=10, alpha=0.5))
ax.axvline(x=61.52, color='grey', linestyle='-', alpha=0.5)
ax.text(0.875, 0.7, 'HIGH RBMPKI', color='grey', transform=ax.transAxes, fontsize=12)
ax.annotate('', xy=(53.5, 1.08), xytext=(60.5, 1.08), arrowprops=dict(facecolor='grey', shrink=0.01, width=3, headwidth=10, alpha=0.5))

# make x and y axis labels bigger
ax.xaxis.label.set_size(16)
#ax.yaxis.label.set_fontweight('bold')
ax.yaxis.label.set_size(16)
#ax.xaxis.label.set_fontweight('bold')

# put the legend on top of the plot
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=4, fancybox=True, shadow=True, fontsize=12)
# prepend "nRH" to legend names
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles, ['$N_{RH}$ = ' + label for label in labels], loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=4, fancybox=True, shadow=True, fontsize=12)

# highlight the geometric mean ax label
ax.get_xticklabels()[62].set_fontweight('bold')

plt.tight_layout()
stats.to_csv('abacus_performance_single_core.csv', index=False)

# numbers to put in paper

# ABACuS at 1000 nRH normalized_ipc for geomean workload
print(stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 1000) & (stats['workload'] == 'GeoMean')]['ramulator.normalized_ipc'])
# ABACuS at 1000 nRH minimum normalized_ipc
print(stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 1000)]['ramulator.normalized_ipc'].min())
# ABACuS at 1000 nRH preventive_refreshes_channel_0_core average
print(stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 1000)]['ramulator.preventive_refreshes_channel_0_core'].mean())
# ABACuS at 1000 nRH normalized_read_latency average
print(stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 1000)]['ramulator.normalized_read_latency'].mean())

# above stats for nrh = 125
print(stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 125) & (stats['workload'] == 'GeoMean')]['ramulator.normalized_ipc'])
print(stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 125)]['ramulator.normalized_ipc'].min())
print(stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 125)]['ramulator.preventive_refreshes_channel_0_core'].mean())
print(stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 125)]['ramulator.normalized_read_latency'].mean())

# REGA at 125 nrh normalized_ipc for geomean workload
print(stats[(stats['config'] == 'REGA') & (stats['nrh'] == 125) & (stats['workload'] == 'GeoMean')]['ramulator.normalized_ipc'])

# PARA at 125 nrh normalized_ipc for geomean workload
print(stats[(stats['config'] == 'PARA') & (stats['nrh'] == 125) & (stats['workload'] == 'GeoMean')]['ramulator.normalized_ipc'])

# PARA at 1000 nrh normalized_ipc for geomean workload
print(stats[(stats['config'] == 'PARA') & (stats['nrh'] == 1000) & (stats['workload'] == 'GeoMean')]['ramulator.normalized_ipc'])

# Hydra at 125 nrh normalized_ipc for geomean workload divided by Abacus at 125 nrh normalized_ipc for geomean workload
print(stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 125) & (stats['workload'] == 'GeoMean')]['ramulator.normalized_ipc'].values[0]/ stats[(stats['config'] == 'Hydra') & (stats['nrh'] == 125) & (stats['workload'] == 'GeoMean')]['ramulator.normalized_ipc'].values[0])
print(stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 250) & (stats['workload'] == 'GeoMean')]['ramulator.normalized_ipc'].values[0]/ stats[(stats['config'] == 'Hydra') & (stats['nrh'] == 250) & (stats['workload'] == 'GeoMean')]['ramulator.normalized_ipc'].values[0])
print(stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 500) & (stats['workload'] == 'GeoMean')]['ramulator.normalized_ipc'].values[0]/ stats[(stats['config'] == 'Hydra') & (stats['nrh'] == 500) & (stats['workload'] == 'GeoMean')]['ramulator.normalized_ipc'].values[0])
print(stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 1000) & (stats['workload'] == 'GeoMean')]['ramulator.normalized_ipc'].values[0]/ stats[(stats['config'] == 'Hydra') & (stats['nrh'] == 1000) & (stats['workload'] == 'GeoMean')]['ramulator.normalized_ipc'].values[0])


# Hydra normalized RBMPKI at nrh = 125 for geomean
print('hydravsabacus rbmpki: ', stats[(stats['config'] == 'Hydra') & (stats['nrh'] == 125)]['ramulator.normalized_rbmpki'].mean()- stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 125)]['ramulator.normalized_rbmpki'].mean())
# Hydra at 125 nRH normalized_read_latency average
print('hydravsabacus latency: ', stats[(stats['config'] == 'Hydra') & (stats['nrh'] == 125)]['ramulator.normalized_read_latency'].mean() - stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 125)]['ramulator.normalized_read_latency'].mean())

# mean number of preventive refreshes for ABACuS at 125 nrh
print(stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 125)]['ramulator.preventive_refreshes_channel_0_core'].mean())
print(stats[(stats['config'] == 'Graphene') & (stats['nrh'] == 125)]['ramulator.preventive_refreshes_channel_0_core'].mean())

# mean normalized_stall_cycles for ABACuS at 125 nrh
print(stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 125)]['ramulator.normalized_stall_cycles'].mean())
print(stats[(stats['config'] == 'Graphene') & (stats['nrh'] == 125)]['ramulator.normalized_stall_cycles'].mean())

evaluation_paragraph = """
ABACuS average slowdown at 1K nRH {avg_slowdown_1k}
ABACuS max slowdown at 1K nRH {max_slowdown_1k}
ABACuS average memory latency increase at 1K nRH {avg_mem_lat_1k}

ABACuS average slowdown at 125 nRH {avg_slowdown_125}
ABACuS max slowdown at 125 nRH {max_slowdown_125}
ABACuS average memory latency increase at 125 nRH {avg_mem_lat_125}
""".format(
    avg_slowdown_1k=1-(stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 1000)]['ramulator.normalized_ipc'].mean()),
    max_slowdown_1k=1-(stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 1000)]['ramulator.normalized_ipc'].min()),
    avg_mem_lat_1k=stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 1000)]['ramulator.normalized_read_latency'].mean(),
    avg_slowdown_125=1-(stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 125)]['ramulator.normalized_ipc'].mean()),
    max_slowdown_125=1-(stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 125)]['ramulator.normalized_ipc'].min()),
    avg_mem_lat_125=stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 125)]['ramulator.normalized_read_latency'].mean(),
)

print(evaluation_paragraph)


# Graphene at 125 nrh normalized_ipc for geomean workload divided by Abacus at 125 nrh normalized_ipc for geomean workload
# print(stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 125) & (stats['workload'] == 'GeoMean')]['ramulator.normalized_ipc'].values[0]/ stats[(stats['config'] == 'Graphene') & (stats['nrh'] == 125) & (stats['workload'] == 'GeoMean')]['ramulator.normalized_ipc'].values[0])

# use seaborn-deep style
sns.set(font_scale=1.0)
sns.set_style("whitegrid")
sns.set_palette("pastel", n_colors=1)

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

# order and sort nRH high to low
stats['nrh'] = pd.Categorical(stats['nrh'], categories=[1000, 500, 250, 125], ordered=True)
stats = stats.sort_values('nrh')

stats['ramulator.normalized_ipc'] = stats['ramulator.ipc'] / stats['ramulator.baseline_ipc']
stats['ramulator.normalized_read_latency'] = stats['ramulator.read_latency_avg_0'] / stats['ramulator.baseline_read_latency_avg_0']
stats['ramulator.normalized_stall_cycles'] = stats['ramulator.window_full_stall_cycles_core_0'] / stats['ramulator.baseline_stall_cycles']
stats['ramulator.normalized_rbmpki'] = stats['ramulator.rbmpki'] / stats['ramulator.baseline_rbmpki']

# normalized ipc for hydra is not correct, so we overwrite it with the correct value
stats.loc[stats['config'].str.contains('Hydra'), 'ramulator.normalized_ipc'] = stats['ramulator.ipc'] / stats['ramulator.hydra_baseline_ipc']

# add the geometric normalized ipc average as a new workload to every config
# geometric_mean = stats.groupby(['config','nrh'])['ramulator.normalized_ipc'].apply(lambda x: x.prod()**(1.0/len(x))).reset_index()
# geometric_mean['workload'] = 'GeoMean'

# stats = pd.concat([stats, geometric_mean])

# # order = ['GeoMean', '531.deepsjeng', '502.gcc', '541.leela', '435.gromacs', '481.wrf', '458.sjeng', '445.gobmk', '444.namd', '508.namd', '401.bzip2', '456.hmmer', '403.gcc', '464.h264ref', '526.blender', '447.dealII', '544.nab', '523.xalancbmk', '500.perlbench', '538.imagick', '525.x264', '507.cactuBSSN', '511.povray', '462.libquantum', '473.astar', '510.parest', '482.sphinx3', '505.mcf', '557.xz', '471.omnetpp', '483.xalancbmk', '436.cactusADM', '520.omnetpp', '450.soplex', '470.lbm', '519.lbm', '434.zeusmp', '433.milc', '459.GemsFDTD', '549.fotonik3d', '429.mcf', '437.leslie3d']
# order = ['GeoMean', 'h264_encode', '511.povray', '481.wrf', '541.leela', '538.imagick', '444.namd', '447.dealII', '464.h264ref', '456.hmmer', '403.gcc', '526.blender', '544.nab', '525.x264', '508.namd', 'grep_map0', '531.deepsjeng', '458.sjeng', '435.gromacs', '445.gobmk', '401.bzip2', '507.cactuBSSN', '502.gcc', 'ycsb_abgsave', 'tpch6', '500.perlbench', '523.xalancbmk', 'ycsb_dserver', 'ycsb_cserver', '510.parest', 'ycsb_bserver', 'ycsb_eserver', 'tpcc64', 'ycsb_aserver', '557.xz', '482.sphinx3', 'jp2_decode', '505.mcf', 'wc_8443', 'wc_map0', '436.cactusADM', '471.omnetpp', '473.astar', 'jp2_encode', 'tpch17', '483.xalancbmk', '462.libquantum', 'tpch2', '433.milc', '520.omnetpp', '437.leslie3d', '450.soplex', '459.GemsFDTD', '549.fotonik3d', '434.zeusmp', '519.lbm', '470.lbm', '429.mcf', 'gups', 'h264_decode', 'bfs_ny', 'bfs_cm2003', 'bfs_dblp']

low_rbmpki = ['h264_encode', '511.povray', '481.wrf', '541.leela', '538.imagick', '444.namd', '447.dealII', '464.h264ref', '456.hmmer', '403.gcc', '526.blender', '544.nab', '525.x264', '508.namd', 'grep_map0', '531.deepsjeng', '458.sjeng', '435.gromacs', '445.gobmk', '401.bzip2', '507.cactuBSSN', '502.gcc', 'ycsb_abgsave', 'tpch6', '500.perlbench', '523.xalancbmk', 'ycsb_dserver']
med_rbmpki = ['ycsb_cserver', '510.parest', 'ycsb_bserver', 'ycsb_eserver', 'tpcc64', 'ycsb_aserver', '557.xz', '482.sphinx3', 'jp2_decode', '505.mcf', 'wc_8443', 'wc_map0', '436.cactusADM', '471.omnetpp', '473.astar', 'jp2_encode', 'tpch17', '483.xalancbmk', '462.libquantum', 'tpch2']
high_rbmpki = ['433.milc', '520.omnetpp', '437.leslie3d', '450.soplex', '459.GemsFDTD', '549.fotonik3d', '434.zeusmp', '519.lbm', '470.lbm', '429.mcf', 'gups', 'h264_decode', 'bfs_ny', 'bfs_cm2003', 'bfs_dblp']

# add new column called rbmpki_category, set category if workload matches one of the above lists
stats['rbmpki_category'] = np.where(stats['workload'].isin(low_rbmpki), 'low (<2)', np.where(stats['workload'].isin(med_rbmpki), 'medium (<10)', np.where(stats['workload'].isin(high_rbmpki), 'high (>10)', 'none')))

# geometric_mean = stats.groupby(['config','nrh','rbmpki_category'])['ramulator.normalized_ipc'].apply(lambda x: x.prod()**(1.0/len(x))).reset_index()
# geometric_mean['workload'] = 'GeoMean'
# stats = pd.concat([stats, geometric_mean])

# remove rows where rbmpki_category is none
stats = stats[stats['rbmpki_category'] != 'none']

order = ['low (<2)', 'medium (<10)', 'high (>10)']
stats['rbmpki_category'] = pd.Categorical(stats['rbmpki_category'], categories=order, ordered=True)

#barplot of normalized IPC, also draw edges around bars
fig, ax = plt.subplots(figsize=(7, 2))
ax = sns.boxplot(x='rbmpki_category', y='ramulator.normalized_ipc', hue='nrh', data=stats[(stats['config'] == 'ABACuS')], showmeans=True, meanprops={"marker":"o","markerfacecolor":"white", "markeredgecolor":"black"})

ax.set_xlabel('Row buffer misses per kilo instructions (RBMPKI)')
ax.set_ylabel('Normalized IPC\ndistribution')
ax.axhline(y=1.0, color='#e74c3c', linestyle='--')
# write above the red line 'baseline IPC' using the same pastel red color
ax.text(0.01, 0.85, 'Baseline IPC', color='#e74c3c', transform=ax.transAxes, fontsize=15)
# extend the y axis to 1.2
ax.set_ylim(0.6, 1.1)
# rotate x axis ticks
ax.set_xticklabels(ax.get_xticklabels())
# make axis tick font bigger
ax.tick_params(axis='both', which='major', labelsize=11)
ax.tick_params(axis='y', which='major', labelsize=12)

# have four y axis ticks
ax.set_yticks([0.6, 0.7, 0.8, 0.9, 1.0, 1.1])

# color the 5th y tick red
ax.get_yticklabels()[4].set_color('#e74c3c')
# # make x and y axis labels bigger
ax.xaxis.label.set_size(16)
# ax.yaxis.label.set_fontweight('bold')
ax.yaxis.label.set_size(16)
# ax.xaxis.label.set_fontweight('bold')

# draw a circle around the minimum value of abacus at nrh = 1000
# get the minimum value of abacus at nrh = 1000
ax.add_patch(plt.Circle((2.3, 0.87), 0.03, color='blue', fill=False, clip_on=False))
ax.add_patch(plt.Circle((2.1, 0.75), 0.03, color='blue', fill=False, clip_on=False))
ax.add_patch(plt.Circle((1.9, 0.725), 0.03, color='blue', fill=False, clip_on=False))
ax.add_patch(plt.Circle((1.7, 0.677), 0.03, color='blue', fill=False, clip_on=False))
# write the minimum value of abacus at nrh = 1000
ax.text(1.59, 0.8, 'gups', color='blue', fontsize=12, bbox=dict(facecolor='white', edgecolor='blue', boxstyle='round,pad=0.2', alpha = 0.95))
# draw an arrow from text to circle
# ax.annotate("", xy=(-0.32, 0.88), xytext=(-0.2, 0.47), arrowprops=dict(arrowstyle="->", color='blue', lw=1))


# # put the legend on top of the plot
# ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=4, fancybox=True, shadow=True, fontsize=10)
# # prepend "nRH" to legend names
handles, labels = ax.get_legend_handles_labels()
newlabels = ['$N_{RH}$ = ' + label for label in labels]
newlabels[0] += ' (leftmost box)'
newlabels[3] += ' (rightmost box)'
ax.legend(handles, newlabels, loc='upper center', bbox_to_anchor=(0.235, 0.74), ncol=1, fancybox=True, shadow=True, fontsize=10)

# remove legend
ax.legend_.remove()

ax.annotate('$N_{RH}=1000$ (leftmost box)\n$N_{RH}=500$\n$N_{RH}=250$\n$N_{RH}=125$ (rightmost box)', xy=(0.05, 0.60), xycoords='axes fraction',
            size=10, ha='left', va='top',
            bbox=dict(boxstyle='round', fc='w', ec='k'))


# plt.tight_layout()
# plt.show()

# save figure
fig.savefig('figure7_abacus_performance_single_core_small.pdf', bbox_inches='tight')
# export data to csv
stats.to_csv('abacus_performance_single_core_small.csv', index=False)

# ABACuS average normalized IPC at nRH = 1000
print(1-stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 1000)]['ramulator.normalized_ipc'].mean())
# ABACuS min. normalized IPC at nRH = 1000
print(1-stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 1000)]['ramulator.normalized_ipc'].min())
# ABACuS average normalized memory latency at nRH = 1000
print(stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 1000)]['ramulator.normalized_read_latency'].mean())

# ABACuS average normalized IPC at nRH = 125
print(1-stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 125)]['ramulator.normalized_ipc'].mean())
# ABACuS min. normalized IPC at nRH = 125
print(1-stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 125)]['ramulator.normalized_ipc'].min())
# ABACuS average normalized memory latency at nRH = 125
print(stats[(stats['config'] == 'ABACuS') & (stats['nrh'] == 125)]['ramulator.normalized_read_latency'].mean())