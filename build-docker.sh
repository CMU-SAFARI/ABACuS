mkdir -p /app/build
cd /app/build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j
cp ramulator ..
pwd
cd ..
