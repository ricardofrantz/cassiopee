# cassiopee

This document provides instructions on how to install Cassiopee and its dependencies.

## Installing Intel OneAPI v2023+

```bash
# Download the Intel GPG key and add it to your keyring
wget -O- https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB \
| gpg --dearmor | sudo tee /usr/share/keyrings/oneapi-archive-keyring.gpg > /dev/null
# Add the Intel OneAPI repository to your sources list
echo "deb [signed-by=/usr/share/keyrings/oneapi-archive-keyring.gpg] https://apt.repos.intel.com/oneapi all main" | sudo tee /etc/apt/sources.list.d/oneAPI.list
```

then
```bash
# Update your package lists for upgrades and new package installations
sudo apt update
# Install the Intel OneAPI HPC Toolkit
sudo apt install intel-hpckit
```

## Installation conda

```bash
# This script removes any directory in the home directory that contains 'conda3' in its name, 
# deletes the base directory of the current conda installation, and removes conda configuration files
rm -rf ~/*conda3*
rm -rf $(conda info --base)
rm -f "${HOME}/.condarc"
rm -fr "${HOME}/.conda"
```

### Installing Miniforge (faster)

```bash
wget "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
```

Please note that, as of now, we need to use setuptools up to version 58.0.4 due to the deprecation of certain functions that have not yet been updated in Cassiopee.

Here are the steps to set up the environment:

```bash
# Deactivate any currently active conda environment
conda deactivate

# Remove the 'dnami' environment if it exists
conda remove --name dnami --all

# Create a new conda environment named 'dnami'
conda create --name dnami

# Activate the 'dnami' environment
conda activate dnami 

# Install the necessary packages in the 'dnami' environment
conda install python python-devtools setuptools=58.0.4 scons scipy sympy matplotlib

# Ensure the 'dnami' environment is activated
conda activate dnami
```
## Installation apt

```bash
# Update your package lists for upgrades and new package installations
sudo apt update

# Remove all unused packages
sudo apt -y autoremove

# Install the necessary packages
sudo apt install -y build-essential python3-dev python3-numpy scons gfortran xorg-dev libhdf5-dev libglfw3-dev libgl1-mesa-dev libglu1-mesa-dev
```

## Installation cassiopee

source dnami setEnv.sh
```bash
git clone https://github.com/ricardofrantz/cassiopee.git
cd cassiopee
./install
```