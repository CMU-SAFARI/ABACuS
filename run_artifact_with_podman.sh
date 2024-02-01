#!/bin/bash
print_colorful_text() {
  local text="$1"
  local color_code="$2"
  echo "\e[${color_code}m${text}\e[0m"
}

if [ "$1" = "--slurm" ]; then
      execution_mode_arg="--slurm"
      echo "Running in your Slurm cluster";
elif ([ "$1" = "--personalcomputer" ]); then
      execution_mode_arg="--personalcomputer"
      echo "Running in personal computer";
else 
      echo "Provide correct execution mode: --slurm or --personalcomputer"
      exit
fi

container="podman"
echo "Using podman"

 
echo "==================  Run a container test to make sure container works =================="

${container} run docker.io/hello-world

echo "====================================================================================="

echo "==================  Building the podman image to run the experiments =================="

${container} build . -t "abacus_artifact" && \

echo "====================================================================================="

echo "==============================  Compiling the simulator ============================="

${container} run --rm -v $PWD:/app/ abacus_artifact /bin/bash -c "cd /app/ && mkdir -p build && sh ./build-docker.sh"

echo "====================================================================================="
echo "=============  Generating the run scripts (this may take a while) ==================="

${container} run --rm -v $PWD:/app/ docker.io/nisabostanci/comet-image:latest /bin/bash -c "python3 /app/genrunsp_docker.py ${PWD} ${execution_mode_arg} ${container}" 


# check if cputraces/ directory is empty
if [ "$(ls -A cputraces/)" ]; then
  echo "==================  cputraces/ directory is not empty =================="
else
  echo "==================  cputraces/ directory is empty =================="
  echo "==================  Downloading the traces into ./cputraces =================="
  wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=18BAvuQybyKT-RRHeAUFOsMAttG4xWlj-' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=18BAvuQybyKT-RRHeAUFOsMAttG4xWlj-" -O cputraces.tar.bz2 && rm -rf /tmp/cookies.txt
echo "==================  Decompressing the traces into ./cputraces =================="

  tar -xvf cputraces.tar.bz2
fi

echo "====================================================================================="
echo "==============================  Launching experiments  =============================="
sh ./run.sh 







