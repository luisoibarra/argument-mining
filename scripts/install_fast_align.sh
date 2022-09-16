# Install and build fast_align

git clone https://github.com/clab/fast_align ./../aligner/fast_align

echo "Install dependencies"
sudo apt-get install libgoogle-perftools-dev libsparsehash-dev

cd ./../aligner/fast_align

echo "Building..."

mkdir build
cd build
cmake ..
make

echo "Completed"