MY_MECHANISM_NAME = 'ABACuS'

### READ RESULTS INTO PANDAS DATAFRAME
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt

resultsdir = "../../ae-results"
# list all directories in resultsdir
configs = [d for d in os.listdir(resultsdir) if os.path.isdir(os.path.join(resultsdir, d))]
configs = ['Baseline.yaml', 'MC-Baseline.yaml', 'Hydra-Baseline.yaml', 'REGA125.yaml', 'REGA250.yaml', 'REGA500.yaml', 'REGA1000.yaml', 'Graphene125.yaml', 'Graphene250.yaml', 'Graphene500.yaml', 'Graphene1000.yaml', 'Hydra125.yaml', 'Hydra250.yaml', 'Hydra500.yaml', 'Hydra1000.yaml', 'PARA125.yaml', 'PARA250.yaml', 'PARA500.yaml', 'PARA1000.yaml', 'ABACUS125.yaml', 'ABACUS250.yaml', 'ABACUS500.yaml', 'ABACUS1000.yaml']

# print found configs
print('Found configs: {}'.format(configs))
# list all directories under all configs
workloads = []
for c in configs:
    workloads.append([d for d in os.listdir(os.path.join(resultsdir, c)) if os.path.isdir(os.path.join(resultsdir, c, d))])
# find only the intersection of all workloads
# workloads = list(set.intersection(*map(set, workloads)))
workloads = list(set([item for sublist in workloads for item in sublist]))
# print found workloads
print('Found workloads: {}'.format(workloads))

stats_per_config_workload = []

# remove workloads with fewer than 7 dashes
workloads = [w for w in workloads if w.count('-') >= 7]

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

                    # if df has this column total_dram_energy0_channel
                    if 'ramulator.total_dram_energy0_channel' in df.columns:
                        total_energy = df['ramulator.total_dram_energy0_channel'].values[1]
                    else:
                        total_energy = 0

                    # create a df with the config, workload and total_energy
                    df = pd.DataFrame({'config': [c], 'workload': [w], 'total_energy': [total_energy]})
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
HIGH_RBMPKI = ['h264_encode', '511.povray', '481.wrf', '541.leela', '538.imagick', '444.namd', '447.dealII', '464.h264ref', '456.hmmer', '403.gcc', '526.blender', '544.nab', '525.x264', '508.namd', 'grep_map0', '531.deepsjeng', '458.sjeng', '435.gromacs', '445.gobmk', '401.bzip2', '507.cactuBSSN', '502.gcc', 'ycsb_abgsave', 'tpch6', '500.perlbench', '523.xalancbmk', 'ycsb_dserver', 'ycsb_cserver', '510.parest', 'ycsb_bserver', 'ycsb_eserver', 'stream_10.trace', 'tpcc64', 'ycsb_aserver', '557.xz', '482.sphinx3', 'jp2_decode', '505.mcf', 'wc_8443', 'wc_map0', '436.cactusADM', '471.omnetpp', '473.astar', 'jp2_encode', 'tpch17', '483.xalancbmk', '462.libquantum', 'tpch2', '433.milc', '520.omnetpp', '437.leslie3d', '450.soplex', '459.GemsFDTD', '549.fotonik3d', '434.zeusmp', '519.lbm', '470.lbm', '429.mcf', 'gups', 'h264_decode', 'bfs_ny', 'bfs_cm2003', 'bfs_dblp']
stats = stats[stats['workload'].str.contains('|'.join(HIGH_RBMPKI))]
# remove h264_decode fro workloads
# stats = stats[~stats['workload'].str.contains('h264_decode')]
# remove h264_decode from HIGH_RBMPKI
# HIGH_RBMPKI.remove('h264_decode')

# remove from mc_only_stats the workloads that contain less than 7 dashes
stats = stats[stats['workload'].str.count('-') >= 7]

# print number of unique workloads
print('Unique workloads: {}'.format(stats['workload'].nunique()))

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

# remove normalized_energy below 1
stats = stats[stats['normalized_energy'] >= 0.9]
# remove 429.mcf
# stats = stats[~stats['workload'].str.contains('bfs_ny')]
# stats = stats[~stats['workload'].str.contains('bfs_cm2003')]

# normalized ipc for hydra is not correct, so we overwrite it with the correct value
stats.loc[stats['config'].str.contains('Hydra'), 'normalized_energy'] = stats['total_energy'] / stats['ramulator.hydra_baseline_energy']

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
ax = sns.boxplot(x="nrh", y="normalized_energy", hue="config", data=stats_no_baseline, showmeans=True, meanprops={"marker":"o","markerfacecolor":"white", "markeredgecolor":"black"})#, showfliers = False)
ax.set_xlabel('RowHammer Threshold ($N_{RH}$)')
ax.set_ylabel('Normalized Energy Distribution')
# draw a red line at y = 1.0, label it as baseline IPC
ax.axhline(y=1.0, color='r', linestyle='--')
# write above the red line 'baseline IPC'
ax.text(0.02, 0.02, 'Baseline DRAM energy', color='#e74c3c', transform=ax.transAxes, fontsize=15)
# extend the y axis to 1.2
ax.set_ylim(0.6, 4.0)
# color the 5th y tick red
ax.get_yticklabels()[1].set_color('#e74c3c')
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
fig.savefig('figure12_abacus_energy_comparison_multi_core.pdf', bbox_inches='tight')
# export data to csv
stats_no_baseline.to_csv('abacus_energy_comparison_multi_core.csv', index=False)

# print mean DRAM energy for ABAcus at each nRH
print(stats_no_baseline[stats_no_baseline['config'] == 'ABACuS'].groupby('nrh')['normalized_energy'].mean())
print(stats_no_baseline[stats_no_baseline['config'] == 'ABACuS'].groupby('nrh')['normalized_energy'].max())

print(1-stats_no_baseline[(stats_no_baseline['config'] == 'ABACuS') & (stats_no_baseline['nrh'] == 125)]['normalized_energy'].mean()/stats_no_baseline[(stats_no_baseline['config'] == 'Hydra') & (stats_no_baseline['nrh'] == 125)]['normalized_energy'].mean())
print(1-stats_no_baseline[(stats_no_baseline['config'] == 'ABACuS') & (stats_no_baseline['nrh'] == 125)]['normalized_energy'].mean()/stats_no_baseline[(stats_no_baseline['config'] == 'REGA') & (stats_no_baseline['nrh'] == 125)]['normalized_energy'].mean())
print(1-stats_no_baseline[(stats_no_baseline['config'] == 'ABACuS') & (stats_no_baseline['nrh'] == 125)]['normalized_energy'].mean()/stats_no_baseline[(stats_no_baseline['config'] == 'PARA') & (stats_no_baseline['nrh'] == 125)]['normalized_energy'].mean())

print(1-stats_no_baseline[(stats_no_baseline['config'] == 'Graphene') & (stats_no_baseline['nrh'] == 125)]['normalized_energy'].mean()/stats_no_baseline[(stats_no_baseline['config'] == 'ABACuS') & (stats_no_baseline['nrh'] == 125)]['normalized_energy'].mean())


# print the number of unique workloads
print('Unique workloads: {}'.format(stats_no_baseline['workload'].nunique()))