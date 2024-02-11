#!/bin/bash

print_colorful_text() {
  local text="$1"
  local color_code="$2"
  echo -e "\e[${color_code}m${text}\e[0m"
}

echo "==================  Compiling the simulator =================="
sh ./build.sh

for i in {5..1}; do
  echo -ne "$i seconds to start the experiments...\r"
  sleep 1
done

echo "==================  Generating run scripts =================="
python3 ./slurm_without_podman.py -wd $PWD -od $PWD/ae-results -td $PWD/cputraces


# check if cputraces/ directory is empty
if [ "$(ls -A cputraces/)" ]; then
  echo "==================  cputraces/ directory is not empty =================="
else
  echo "==================  cputraces/ directory is empty =================="
  echo "==================  Downloading the traces into ./cputraces =================="
  python3 download_traces.py

  tar -xvf cputraces.tar.bz2 --no-same-owner
fi

echo "==================  Launching experiments =================="
sh ./run.sh
