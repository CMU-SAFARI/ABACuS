# basic requirements:
# - the cache size should be scaled per core
# - make sure we are running all traces
import yaml
import os
import random
import itertools
import random

BASH_HEADER = "#!/bin/bash\n"

# the command line slurm will execute
BATCH_COMMAND_LINE = "./docker_wrapper.sh podman run --rm -v {ramulator_dir}:/app/ abacus_artifact /app/run_scripts/{config_name}{config_extension}-{workload}.sh\""

# the script executed by the command line slurm executes
BASE_COMMAND_LINE = "\
    /app/ramulator "

# nRH sweep all mechanisms
configs = [
  '/app/configs/ABACUS/ABACUS/ABACUS125.yaml',
  '/app/configs/ABACUS/ABACUS/ABACUS250.yaml',
  '/app/configs/ABACUS/ABACUS/ABACUS500.yaml',
  '/app/configs/ABACUS/ABACUS/ABACUS1000.yaml',
  '/app/configs/ABACUS/Others/Baseline.yaml',
  '/app/configs/ABACUS/Others/Hydra-Baseline.yaml',
  '/app/configs/ABACUS/Others/Graphene125.yaml',
  '/app/configs/ABACUS/Others/Graphene250.yaml',
  '/app/configs/ABACUS/Others/Graphene500.yaml',
  '/app/configs/ABACUS/Others/Graphene1000.yaml',
  '/app/configs/ABACUS/Others/Hydra125.yaml',
  '/app/configs/ABACUS/Others/Hydra250.yaml',
  '/app/configs/ABACUS/Others/Hydra500.yaml',
  '/app/configs/ABACUS/Others/Hydra1000.yaml',
  '/app/configs/ABACUS/Others/REGA125.yaml',
  '/app/configs/ABACUS/Others/REGA250.yaml',
  '/app/configs/ABACUS/Others/REGA500.yaml',
  '/app/configs/ABACUS/Others/REGA1000.yaml',
  '/app/configs/ABACUS/Others/PARA125.yaml',
  '/app/configs/ABACUS/Others/PARA250.yaml',
  '/app/configs/ABACUS/Others/PARA500.yaml',
  '/app/configs/ABACUS/Others/PARA1000.yaml',
  '/app/configs/ABACUS/Others/ACT-period-256ms.yaml',
  '/app/configs/ABACUS/Others/MC-Baseline.yaml'
]

traces = [
  "random_10.trace",
  "stream_10.trace",
  "401.bzip2",
  "403.gcc",
  "429.mcf",
  "433.milc",
  "434.zeusmp",
  "435.gromacs",
  "436.cactusADM",
  "437.leslie3d",
  "444.namd",
  "445.gobmk",
  "447.dealII",
  "450.soplex",
  "456.hmmer",
  "458.sjeng",
  "459.GemsFDTD",
  "462.libquantum",
  "464.h264ref",
  "470.lbm",
  "471.omnetpp",
  "473.astar",
  "481.wrf",
  "482.sphinx3",
  "483.xalancbmk",
  "500.perlbench",
  "502.gcc",
  "505.mcf",
  "507.cactuBSSN",
  "508.namd",
  "510.parest",
  "511.povray",
  "519.lbm",
  "520.omnetpp",
  "523.xalancbmk",
  "525.x264",
  "526.blender",
  "531.deepsjeng",
  "538.imagick",
  "541.leela",
  "544.nab",
  "549.fotonik3d",
  "557.xz",
  "bfs_dblp",
  "bfs_cm2003",
  "bfs_ny",
  "grep_map0",
  "h264_decode",
  "h264_encode",
  "jp2_decode",
  "jp2_encode",
  "tpcc64",
  "tpch17",
  "tpch2",
  "tpch6",
  "wc_8443", # wordcount-8443
  "wc_map0", # wordcount-map0
  "ycsb_abgsave",
  "ycsb_aserver",
  "ycsb_bserver",
  "ycsb_cserver",
  "ycsb_dserver",
  "ycsb_eserver"
]

LOW_RBMPKI = ['531.deepsjeng', '502.gcc', '541.leela', '435.gromacs', '481.wrf', '458.sjeng', '445.gobmk', '444.namd', '508.namd', '401.bzip2', '456.hmmer', '403.gcc', '464.h264ref', '526.blender', '447.dealII', '544.nab', '523.xalancbmk', '500.perlbench', '538.imagick', '525.x264', '507.cactuBSSN', '511.povray']
MED_RBMPKI = ['462.libquantum', '473.astar', '510.parest', '482.sphinx3', '505.mcf', '557.xz', '471.omnetpp', '483.xalancbmk', '436.cactusADM']
HIGH_RBMPKI = ['520.omnetpp', '450.soplex', '470.lbm', '519.lbm', '434.zeusmp', '433.milc', '459.GemsFDTD', '549.fotonik3d', '429.mcf', '437.leslie3d']


# @returns SBATCH command used to invoke the ramulator script
def generateExecutionSetup(ramulator_dir, output_dir, trace_dir, config, workload_name_list):

  CMD = BASE_COMMAND_LINE.format(
    ramulator_dir = ramulator_dir,
  )

  ramulator_config=None
  with open(config) as f:    
    ramulator_config = yaml.load(f, Loader=yaml.FullLoader)
  bare_config = config.split('/')[-1]

  workload_name_list_dir = [(trace_dir + "/" + x) for x in workload_name_list]
  ramulator_config["processor"]["trace"] = workload_name_list_dir

  if "cache" in ramulator_config["processor"]:
    if ramulator_config["processor"]["cache"]:
      if "L3" in ramulator_config["processor"]["cache"]:
        ramulator_config["processor"]["cache"]["L3"]["capacity"] = str(int(len(workload_name_list_dir) * 2)) + "MB"

  if "MC-Baseline.yaml" not in config:
    ramulator_config["processor"]["warmup_insts"] = int(100000000/len(workload_name_list_dir))
    if len(workload_name_list_dir) > 1:
      ramulator_config["processor"]["warmup_insts"] = 0
    ramulator_config["processor"]["expected_limit_insts"] = int(200000000/len(workload_name_list_dir))

  BATCH_CMD = BATCH_COMMAND_LINE.format(
    ramulator_dir = ramulator_dir,
    config_extension = '',
    config_name = bare_config,
    workload = '{workload}'
  )
  
  prog_list = ""

  length = len(workload_name_list)

  for j in range(length-1):
    prog_list += workload_name_list[j] + '-'
  
  prog_list += workload_name_list[length-1]

  stats_prefix = output_dir + '/' + bare_config + '/' + prog_list + '/'
  ramulator_config["stats"]["prefix"] = stats_prefix
  activate_dump_file_name = output_dir + '/' + bare_config + '/' + prog_list + '/activate_commands.txt'
  period_dump_file_name = output_dir + '/' + bare_config + '/' + prog_list + '/activate_periods.txt'
  ramulator_config["memory"]["controller"]["activation_count_dump_file"] = activate_dump_file_name
  if "refresh_based_defense" in ramulator_config["post_warmup_settings"]["memory"]["controller"]:
    ramulator_config["post_warmup_settings"]["memory"]["controller"]["refresh_based_defense"]["activation_period_file_name"] = period_dump_file_name

  # Finalize CMD
  CMD += "\"" + yaml.dump(ramulator_config) + "\"" + " 1> " + output_dir + '/' + bare_config + '/' + prog_list + '/output.txt 2> ' + output_dir + '/' + bare_config + '/' + prog_list + '/error.txt'

  BATCH_CMD = BATCH_CMD.format(
    workload = prog_list
  )            

  os.system('mkdir -p ' + output_dir + '/' + bare_config + '/' + prog_list)

  f = open(ramulator_dir + '/run_scripts/' + bare_config + '-' + prog_list + '.sh', 'w')
  f.write(BASH_HEADER)
  f.write(CMD)
  f.close()
  
  return BATCH_CMD

ramulator_dir = '/app'
output_dir = '/app/ae-results'
trace_dir = '/app/cputraces'

# remove scripts
os.system('rm -r ' + ramulator_dir + '/run_scripts')

os.system('mkdir -p ' + output_dir)
os.system('mkdir -p ' + ramulator_dir + '/run_scripts')

all_sbatch_commands = []
all_sbatch_commands.append(BASH_HEADER)

for config in configs:
  os.system('mkdir -p ' + output_dir + '/' + config.split('/')[-1])

  ###################### single core traces ######################
  for trace in traces:
    print(trace)
    all_sbatch_commands.append(generateExecutionSetup(ramulator_dir, output_dir, trace_dir, config, [trace]))
  
  ###################### 8-core traces ######################
  if config != '/app/configs/ABACUS/Others/ACT-period-256ms.yaml':
    for workload in traces:
      print([workload] * 8)
      all_sbatch_commands.append(generateExecutionSetup(ramulator_dir, output_dir, trace_dir, config, [workload] * 8))
  
with open('run.sh', 'w') as f:
  f.write('\n'.join(all_sbatch_commands))

os.system('chmod uog+x run.sh')
