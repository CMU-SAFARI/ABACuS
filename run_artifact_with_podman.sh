#!/bin/bash
print_colorful_text() {
  local text="$1"
  local color_code="$2"
  echo "\e[${color_code}m${text}\e[0m"
}

if [ "$1" = "--slurm" ]; then
      echo "Running in your Slurm cluster";
elif ([ "$1" = "--personalcomputer" ]); then
      echo "Running in your personal computer";
else 
      echo "Provide correct execution mode: --slurm or --personalcomputer"
      exit
fi

echo "==================  Building the podman image to run the experiments =================="

podman build . -t "abacus_artifact" && \

echo "====================================================================================="

echo "==============================  Compiling the simulator ============================="

podman run --rm -v $PWD:/app/ abacus_artifact "cd /app/ && mkdir -p build && sh ./build-docker.sh"

echo "====================================================================================="
echo "=============  Generating the run scripts (this may take a while) ==================="

if  [ "$1" = "--slurm" ]; then
  podman run --rm -v $PWD:/app/ abacus_artifact "python3 /app/slurm_with_podman.py" 
else 
  podman run --rm -v $PWD:/app/ abacus_artifact "python3 /app/personal_computer_with_podman.py" 
fi

# check if cputraces/ directory is empty
if [ "$(ls -A cputraces/)" ]; then
  echo "==================  cputraces/ directory is not empty =================="
else
  echo "==================  cputraces/ directory is empty =================="
  echo "==================  Downloading the traces into ./cputraces =================="
  podman run --rm -v $PWD:/app/ abacus_artifact "python3 /app/download_traces.py"
  echo "==================  Decompressing the traces into ./cputraces =================="
  podman run --rm -v $PWD:/app/ abacus_artifact "tar -xvf cputraces.tar.bz2 --no-same-owner"
fi

echo "====================================================================================="
echo "==============================  Launching experiments  =============================="
# sh ./run.sh 







