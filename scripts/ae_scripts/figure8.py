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
configs = ['Baseline.yaml', 'Hydra-Baseline.yaml', 'REGA125.yaml', 'REGA250.yaml', 'REGA500.yaml', 'REGA1000.yaml', 'Graphene125.yaml', 'Graphene250.yaml', 'Graphene500.yaml', 'Graphene1000.yaml', 'Hydra125.yaml', 'Hydra250.yaml', 'Hydra500.yaml', 'Hydra1000.yaml', 'PARA125.yaml', 'PARA250.yaml', 'PARA500.yaml', 'PARA1000.yaml', 'ABACUS125.yaml', 'ABACUS250.yaml', 'ABACUS500.yaml', 'ABACUS1000.yaml']

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
        stat_files = [f for f in files if f.endswith('output.txt')]
        # if there is a stats file
        if stat_files:
            for stat_file in stat_files:
                # if the stats_file has less than three lines skip it
                if len(open(os.path.join(resultsdir, c, w, stat_file)).readlines()) < 3:
                    continue
                
                # print the name of the stats_file
                print('Found stats file: {}'.format(os.path.join(os.path.join(resultsdir, c, w, stat_file))))

                lines = open(os.path.join(resultsdir, c, w, stat_file)).readlines()
                total_energy = 0
                for l in lines:
                    # if line contains nJ, add l.split()[-2] to total_energy
                    if 'Total Idle energy:' in l:
                        continue
                    if 'nJ' in l:
                        total_energy += float(l.split()[-2])
                    if l.startswith('REF CMD energy'):
                        break

                
                # create a df with the config, workload and total_energy
                df = pd.DataFrame({'config': [c], 'workload': [w], 'total_energy': [total_energy]})
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
#order = ['511.povray', '481.wrf', '541.leela', '538.imagick', '444.namd', '447.dealII', '464.h264ref', '456.hmmer', '403.gcc', '526.blender', '544.nab', '525.x264', '508.namd', '531.deepsjeng', '458.sjeng', '435.gromacs', '445.gobmk', '401.bzip2', '507.cactuBSSN', '502.gcc', '500.perlbench', '523.xalancbmk', '510.parest', '557.xz', '482.sphinx3', '505.mcf', '436.cactusADM', '471.omnetpp', '473.astar', '483.xalancbmk', '462.libquantum', '433.milc', '520.omnetpp', '437.leslie3d', '450.soplex', '459.GemsFDTD', '549.fotonik3d', '434.zeusmp', '519.lbm', '470.lbm', '429.mcf']
order = ['h264_encode', '511.povray', '481.wrf', '541.leela', '538.imagick', '444.namd', '447.dealII', '464.h264ref', '456.hmmer', '403.gcc', '526.blender', '544.nab', '525.x264', '508.namd', 'grep_map0', '531.deepsjeng', '458.sjeng', '435.gromacs', '445.gobmk', '401.bzip2', '507.cactuBSSN', '502.gcc', 'ycsb_abgsave', 'tpch6', '500.perlbench', '523.xalancbmk', 'ycsb_dserver', 'ycsb_cserver', '510.parest', 'ycsb_bserver', 'ycsb_eserver', 'stream_10.trace', 'tpcc64', 'ycsb_aserver', '557.xz', '482.sphinx3', 'jp2_decode', '505.mcf', 'wc_8443', 'wc_map0', '436.cactusADM', '471.omnetpp', '473.astar', 'jp2_encode', 'tpch17', '483.xalancbmk', '462.libquantum', 'tpch2', '433.milc', '520.omnetpp', '437.leslie3d', '450.soplex', '459.GemsFDTD', '549.fotonik3d', '434.zeusmp', '519.lbm', '470.lbm', '429.mcf', 'gups', 'h264_decode', 'bfs_ny', 'bfs_cm2003', 'bfs_dblp']


# remove all workloads not in order
stats = stats[stats['workload'].isin(order)]
# also from the workload list
workloads = [w for w in workloads if w in order]


# order workloads according to the order
stats['workload'] = pd.Categorical(stats['workload'], categories=order, ordered=True)

stats_copy = stats.copy()


# use seaborn-deep style
sns.set(font_scale=1.0)
sns.set_style("whitegrid")
sns.set_palette("pastel", n_colors=1)

stats = stats_copy.copy()


# copy the IPC of the baseline config as to all configs
baseline = stats[stats['config'] == 'Baseline']
baseline = baseline[['workload', 'total_energy']]
# baseline
baseline.columns = ['workload', 'baseline_energy']
stats = pd.merge(stats, baseline, on='workload')

#hydra baseline
hydra_baseline = stats[stats['config'] == 'Hydra-Baseline']
hydra_baseline = hydra_baseline[['workload', 'total_energy']]
# hydra_baseline
hydra_baseline.columns = ['workload', 'ramulator.hydra_baseline_energy']
stats = pd.merge(stats, hydra_baseline, on='workload')

stats['normalized_energy'] = stats['total_energy'] / stats['baseline_energy']

# normalized ipc for hydra is not correct, so we overwrite it with the correct value
stats.loc[stats['config'].str.contains('Hydra'), 'normalized_energy'] = stats['total_energy'] / stats['ramulator.hydra_baseline_energy']

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

# order and sort nRH high to low
stats['nrh'] = pd.Categorical(stats['nrh'], categories=[1000, 500, 250, 125], ordered=True)
stats = stats.sort_values('nrh')

# remove rows where rbmpki_category is none
stats = stats[stats['rbmpki_category'] != 'none']

order = ['low (<2)', 'medium (<10)', 'high (>10)']
stats['rbmpki_category'] = pd.Categorical(stats['rbmpki_category'], categories=order, ordered=True)

#barplot of normalized IPC, also draw edges around bars
fig, ax = plt.subplots(figsize=(7, 2))
ax = sns.boxplot(x='rbmpki_category', y='normalized_energy', hue='nrh', data=stats[(stats['config'] == 'ABACuS')], showmeans=True, meanprops={"marker":"o","markerfacecolor":"white", "markeredgecolor":"black"})

ax.set_xlabel('Row buffer misses per kilo instructions (RBMPKI)')
ax.set_ylabel('Normalized\nDRAM energy\ndistribution')
ax.axhline(y=1.0, color='#e74c3c', linestyle='--')
# write above the red line 'baseline IPC' using the same pastel red color
ax.text(0.01, 0.15, 'Baseline DRAM energy', color='#e74c3c', transform=ax.transAxes, fontsize=15)
# extend the y axis to 1.2
# ax.set_ylim(0.8, 1.05)
# color the 5th y tick red
ax.get_yticklabels()[1].set_color('#e74c3c')
# rotate x axis ticks
ax.set_xticklabels(ax.get_xticklabels())
# make axis tick font bigger
ax.tick_params(axis='both', which='major', labelsize=11)
ax.tick_params(axis='y', which='major', labelsize=12)

# have four y axis ticks
# ax.set_yticks([0.8, 0.85, 0.9, 0.95, 1.0, 1.05])

# # make x and y axis labels bigger
ax.xaxis.label.set_size(16)
# ax.yaxis.label.set_fontweight('bold')
ax.yaxis.label.set_size(16)
# ax.xaxis.label.set_fontweight('bold')
ax.add_patch(plt.Circle((2.303, 1.30), 0.05, color='blue', fill=False, clip_on=False))
ax.add_patch(plt.Circle((2.103, 1.71), 0.05, color='blue', fill=False, clip_on=False))
ax.add_patch(plt.Circle((1.903, 1.81), 0.05, color='blue', fill=False, clip_on=False))
ax.add_patch(plt.Circle((1.7, 2.01), 0.05, color='blue', fill=False, clip_on=False))
# write the minimum value of abacus at nrh = 1000
ax.text(1.55, 1.5, 'gups', color='blue', fontsize=12, bbox=dict(facecolor='white', edgecolor='blue', boxstyle='round,pad=0.2', alpha = 0.95))

# # put the legend on top of the plot
# ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=4, fancybox=True, shadow=True, fontsize=10)
# # prepend "nRH" to legend names
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles, ['$N_{RH}$ = ' + label for label in labels], loc='upper center', bbox_to_anchor=(0.15, 1.0), ncol=1, fancybox=True, shadow=True, fontsize=10)

# remove legend
ax.legend_.remove()

ax.annotate('$N_{RH}=1000$ (leftmost box)\n$N_{RH}=500$\n$N_{RH}=250$\n$N_{RH}=125$ (rightmost box)', xy=(0.05, 0.90), xycoords='axes fraction',
            size=10, ha='left', va='top',
            bbox=dict(boxstyle='round', fc='w', ec='k'))



# plt.tight_layout()
# save figure
fig.savefig('figure8_abacus_energy_single_core_small.pdf', bbox_inches='tight')
# export data to csv
stats.to_csv('abacus_energy_single_core_small.csv', index=False)


# ABACuS average normalized energy at 1K nRH
print(stats[(stats['nrh'] == 1000) & (stats['config'] == 'ABACuS')]['normalized_energy'].mean())
# ABACuS max. normalized energy at 1K nRH
print(stats[(stats['nrh'] == 1000) & (stats['config'] == 'ABACuS')]['normalized_energy'].max())
# ABACuS average normalized energy at 125 nRH
print(stats[(stats['nrh'] == 125) & (stats['config'] == 'ABACuS')]['normalized_energy'].mean())
# ABACuS max. normalized energy at 125 nRH
print(stats[(stats['nrh'] == 125) & (stats['config'] == 'ABACuS')]['normalized_energy'].max())

# use seaborn-deep style
sns.set(font_scale=1.0)
sns.set_style("whitegrid")
sns.set_palette("pastel", n_colors=5)

stats = stats_copy.copy()

# copy the IPC of the baseline config as to all configs
baseline = stats[stats['config'] == 'Baseline']
baseline = baseline[['workload', 'total_energy']]
# baseline
baseline.columns = ['workload', 'baseline_energy']
stats = pd.merge(stats, baseline, on='workload')

#hydra baseline
hydra_baseline = stats[stats['config'] == 'Hydra-Baseline']
hydra_baseline = hydra_baseline[['workload', 'total_energy']]
# hydra_baseline
hydra_baseline.columns = ['workload', 'ramulator.hydra_baseline_energy']
stats = pd.merge(stats, hydra_baseline, on='workload')

stats['normalized_energy'] = stats['total_energy'] / stats['baseline_energy']

# normalized ipc for hydra is not correct, so we overwrite it with the correct value
stats.loc[stats['config'].str.contains('Hydra'), 'normalized_energy'] = stats['total_energy'] / stats['ramulator.hydra_baseline_energy']

# add the geometric normalized ipc average as a new workload to every config
geometric_mean = stats.groupby(['config','nrh'])['normalized_energy'].apply(lambda x: x.prod()**(1.0/len(x))).reset_index()
geometric_mean['workload'] = 'GeoMean'

stats = pd.concat([stats, geometric_mean])
# order in decreasing nRH (the nRH column) use pd.Categorical on nrh
stats['nrh'] = pd.Categorical(stats['nrh'], categories=[1000, 500, 250, 125], ordered=True)


#order = ['GeoMean', '531.deepsjeng', '502.gcc', '541.leela', '435.gromacs', '481.wrf', '458.sjeng', '445.gobmk', '444.namd', '508.namd', '401.bzip2', '456.hmmer', '403.gcc', '464.h264ref', '526.blender', '447.dealII', '544.nab', '523.xalancbmk', '500.perlbench', '538.imagick', '525.x264', '507.cactuBSSN', '511.povray', '462.libquantum', '473.astar', '510.parest', '482.sphinx3', '505.mcf', '557.xz', '471.omnetpp', '483.xalancbmk', '436.cactusADM', '520.omnetpp', '450.soplex', '470.lbm', '519.lbm', '434.zeusmp', '433.milc', '459.GemsFDTD', '549.fotonik3d', '429.mcf', '437.leslie3d']
order = ['h264_encode', '511.povray', '481.wrf', '541.leela', '538.imagick', '444.namd', '447.dealII', '464.h264ref', '456.hmmer', '403.gcc', '526.blender', '544.nab', '525.x264', '508.namd', 'grep_map0', '531.deepsjeng', '458.sjeng', '435.gromacs', '445.gobmk', '401.bzip2', '507.cactuBSSN', '502.gcc', 'ycsb_abgsave', 'tpch6', '500.perlbench', '523.xalancbmk', 'ycsb_dserver', 'ycsb_cserver', '510.parest', 'ycsb_bserver', 'ycsb_eserver', 'tpcc64', 'ycsb_aserver', '557.xz', '482.sphinx3', 'jp2_decode', '505.mcf', 'wc_8443', 'wc_map0', '436.cactusADM', '471.omnetpp', '473.astar', 'jp2_encode', 'tpch17', '483.xalancbmk', '462.libquantum', 'tpch2', '433.milc', '520.omnetpp', '437.leslie3d', '450.soplex', '459.GemsFDTD', '549.fotonik3d', '434.zeusmp', '519.lbm', '470.lbm', '429.mcf', 'gups', 'h264_decode', 'bfs_ny', 'bfs_cm2003', 'bfs_dblp','GeoMean']

# order = ['GeoMean', '511.povray', '481.wrf', '541.leela', '538.imagick', '444.namd', '447.dealII', '464.h264ref', '456.hmmer', '403.gcc', '526.blender', '544.nab', '525.x264', '508.namd', '531.deepsjeng', '458.sjeng', '435.gromacs', '445.gobmk', '401.bzip2', '507.cactuBSSN', '502.gcc', '500.perlbench', '523.xalancbmk', '510.parest', '557.xz', '482.sphinx3', '505.mcf', '436.cactusADM', '471.omnetpp', '473.astar', '483.xalancbmk', '462.libquantum', '433.milc', '520.omnetpp', '437.leslie3d', '450.soplex', '459.GemsFDTD', '549.fotonik3d', '434.zeusmp', '519.lbm', '470.lbm', '429.mcf']

stats['workload'] = pd.Categorical(stats['workload'], categories=order, ordered=True)
#barplot of normalized IPC, also draw edges around bars

fig, ax = plt.subplots(figsize=(13, 4))
ax = sns.barplot(x='workload', y='normalized_energy', hue='nrh', data=stats[(stats['config'] == 'ABACuS')], edgecolor='black', linewidth=0.5)

ax.set_xlabel('Workload')
ax.set_ylabel('Normalized DRAM Energy')
# move ylabel down
ax.yaxis.set_label_coords(-0.045,0.3)
# draw a red line at y = 1.0, label it as baseline IPC
ax.axhline(y=0.999, color='r', linestyle='--')
# write above the red line 'baseline IPC' using the same pastel red color, also draw a box around it
#ax.text(0.5, 0.99, 'baseline DRAM Energy', color='r', transform=ax.transAxes, bbox=dict(facecolor='white', edgecolor='r', boxstyle='round,pad=0.2'))
ax.text(0.01, 0.2, 'Baseline DRAM energy', color='#e74c3c', transform=ax.transAxes, fontsize=15, bbox=dict(facecolor='white', edgecolor='r', boxstyle='round,pad=0.2', alpha = 0.95))

# extend the y axis to 1.2
ax.set_ylim(0.90, 1.2)
# color the 5th y tick red
ax.get_yticklabels()[1].set_color('#e74c3c')
# rotate x axis ticks
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
# make axis tick font bigger
ax.tick_params(axis='both', which='major', labelsize=11)
ax.tick_params(axis='y', which='major', labelsize=12)

# # draw vertical lines to separate the rowhammer threshold values
ax.axvline(x=26.5, color='grey', linestyle='-', alpha=0.5)
# put text before the line saying "LOW RBMPKI"
ax.text(0.33, 0.2, 'LOW RBMPKI', color='grey', transform=ax.transAxes, fontsize=12, bbox=dict(facecolor='white', edgecolor='grey', boxstyle='round,pad=0.2', alpha = 0.95))
# put arrow to the left above text
ax.annotate('', xy=(19.5, 0.93), xytext=(25.5, 0.93), arrowprops=dict(facecolor='grey', shrink=0.01, width=3, headwidth=10, alpha=0.99))
ax.axvline(x=46.5, color='grey', linestyle='-', alpha=0.5)
ax.text(0.65, 0.2, 'MED. RBMPKI', color='grey', transform=ax.transAxes, fontsize=12, bbox=dict(facecolor='white', edgecolor='grey', boxstyle='round,pad=0.2', alpha = 0.99))
ax.annotate('', xy=(39.5, 0.93), xytext=(45.5, 0.93), arrowprops=dict(facecolor='grey', shrink=0.01, width=3, headwidth=10, alpha=0.95))
ax.axvline(x=61.5, color='grey', linestyle='-', alpha=0.5)
ax.text(0.875, 0.2, 'HIGH RBMPKI', color='grey', transform=ax.transAxes, fontsize=12, bbox=dict(facecolor='white', edgecolor='grey', boxstyle='round,pad=0.2', alpha = 0.99))
ax.annotate('', xy=(54.5, 0.93), xytext=(60.5, 0.93), arrowprops=dict(facecolor='grey', shrink=0.01, width=3, headwidth=10, alpha=0.95))

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

# draw a small orange arrow to the middle of the plot
ax.annotate('', xy=(54.5, 1.18), xytext=(56.5, 1.18), arrowprops=dict(facecolor='blue', shrink=0.01, width=3, headwidth=10, alpha=0.99))
# put text above the arrow
ax.text(0.835, 0.9, '2.01', color='blue', transform=ax.transAxes, fontsize=12, bbox=dict(facecolor='white', edgecolor='blue', boxstyle='round,pad=0.2', alpha = 0.99))

# draw a small orange arrow to the middle of the plot
ax.annotate('', xy=(54.5, 1.11), xytext=(56.8, 1.15), arrowprops=dict(facecolor='#e67e22', shrink=0.01, width=3, headwidth=10, alpha=0.99))
# put text above the arrow
ax.text(0.835, 0.6, '1.81', color='orange', transform=ax.transAxes, fontsize=12, bbox=dict(facecolor='white', edgecolor='orange', boxstyle='round,pad=0.2', alpha = 0.99))

# draw a small orange arrow to the middle of the plot
ax.annotate('', xy=(58.5, 1.115), xytext=(57.0, 1.15), arrowprops=dict(facecolor='green', shrink=0.01, width=3, headwidth=10, alpha=0.99))
# put text above the arrow
ax.text(0.935, 0.6, '1.71', color='green', transform=ax.transAxes, fontsize=12, bbox=dict(facecolor='white', edgecolor='green', boxstyle='round,pad=0.2', alpha = 0.99))

# draw a small orange arrow to the middle of the plot
ax.annotate('', xy=(59.5, 1.18), xytext=(57.3, 1.18), arrowprops=dict(facecolor='red', shrink=0.01, width=3, headwidth=10, alpha=0.99))
# put text above the arrow
ax.text(0.955, 0.9, '1.30', color='red', transform=ax.transAxes, fontsize=12, bbox=dict(facecolor='white', edgecolor='red', boxstyle='round,pad=0.2', alpha = 0.99))


plt.tight_layout()

# export data to csv
stats.to_csv('abacus_energy_single_core.csv', index=False)



# numbers to put in paper

# ABACuS at 1000 nRH normalized_energy for the geomean workload
print(stats[(stats['workload'] == 'GeoMean') & (stats['nrh'] == 1000) & (stats['config'] == 'ABACuS')]['normalized_energy'])
# ABACuS at 1000 nRH maximum normalized_energy
print(stats[(stats['nrh'] == 1000) & (stats['config'] == 'ABACuS')]['normalized_energy'].max())

# the above for nrh = 125
print(stats[(stats['workload'] == 'GeoMean') & (stats['nrh'] == 125) & (stats['config'] == 'ABACuS')]['normalized_energy'])
print(stats[(stats['nrh'] == 125) & (stats['config'] == 'ABACuS')]['normalized_energy'].max())


evaluation_paragraph = """
ABACuS average normalized energy at 1K nRH {avg_energy_1k}
ABACuS max normalized energy at 1K nRH {max_energy_1k}

ABACuS average normalized energy at 125 nRH {avg_energy_125}
ABACuS max normalized energy at 125 nRH {max_energy_125}
""".format(
    avg_energy_1k=stats[(stats['nrh'] == 1000) & (stats['config'] == 'ABACuS')]['normalized_energy'].mean(),
    max_energy_1k=stats[(stats['nrh'] == 1000) & (stats['config'] == 'ABACuS')]['normalized_energy'].max(),
    avg_energy_125=stats[(stats['nrh'] == 125) & (stats['config'] == 'ABACuS')]['normalized_energy'].mean(),
    max_energy_125=stats[(stats['nrh'] == 125) & (stats['config'] == 'ABACuS')]['normalized_energy'].max(),
)

print(evaluation_paragraph)