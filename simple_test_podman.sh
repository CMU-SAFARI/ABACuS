#!/bin/bash
echo "==================  Building the podman image to run the experiments =================="

podman build . -t "abacus_artifact" && \

echo "====================================================================================="

echo "==============================  Compiling the simulator ============================="

podman run --rm -v $PWD:/app/ abacus_artifact "cd /app/ && mkdir -p build && sh ./build-docker.sh"

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

echo "==============================  Running the simple test ============================="

podman run --rm -v $PWD:/app/ abacus_artifact "./ramulator --config configs/ABACUS/Others/Simple.yaml"