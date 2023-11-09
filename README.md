# cassiopee

This document provides instructions on how to install Cassiopee and its dependencies.

## (Optional) Installing Intel OneAPI v2023+

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

### (Optional) Removing old conda installation
```bash
# This script removes any directory in the home directory that contains 'conda3' in its name, 
# deletes the base directory of the current conda installation, and removes conda configuration files
rm -rf ~/*conda3*
rm -rf $(conda info --base)
rm -f "${HOME}/.condarc"
rm -fr "${HOME}/.conda"
```

### Installing Miniforge

Miniforge is a minimal conda installer. It is recommended over Anaconda or Miniconda for managing conda environments. This is because Miniforge is a smaller, more lightweight solution that is focused on providing conda and Python, making it faster and easier to install. It also supports more platforms compared to Anaconda and Miniconda and *conda-forge* comes as the default channel.

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

## Installation on Ubuntu apt

```bash
# Update your package lists for upgrades and new package installations
# This ensures you have the latest versions of all packages
sudo apt update

# Remove all unused packages
# This helps to keep your system clean
sudo apt -y autoremove

# Install the necessary packages
# build-essential: contains references to all the packages needed to compile a Debian package. It generally includes the gcc/g++ compilers and libraries and some other utilities.
# python3-dev: contains the header files you need to build Python extensions.
# python3-numpy: is the fundamental package for array computing with Python.
# scons: is a software construction tool.
# gfortran: the GNU Fortran compiler.
# xorg-dev: X.Org X Window System development libraries. They are needed for GUI applications.
# libhdf5-dev: contains the header files and static libraries for developing programs that will use Hierarchical Data Format 5 (HDF5).
# libglfw3-dev: is the development files for GLFW 3 library, which is a free, open source, multi-platform library for creating windows with OpenGL contexts.
# libgl1-mesa-dev, libglu1-mesa-dev: are the development files for the Mesa 3D graphics library.
sudo apt install -y build-essential python3-dev python3-numpy scons gfortran xorg-dev libhdf5-dev libglfw3-dev libgl1-mesa-dev libglu1-mesa-dev
```

## Installation on macOS

Install Command Line Tools for `XCode`:

```bash
xcode-select --install
```
Install Homebrew:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
and then
```bash
brew update
brew install gcc openmpi numpy scons hdf5 glfw 
```
Install XQuartz
1. Visit [XQuartz website](https://www.xquartz.org).
2. Download the latest `.dmg` file.
3. Open the `.dmg` file and run `XQuartz.pkg`.

## Installation cassiopee

The following instructions will guide you through the process of installing Cassiopee.

First, you need to set up some environment variables. Add the following lines to your `.bashrc` or `.bash_profile` file:

```bash
# This is the directory where the Cassiopee source code will be stored
export cassiopee_src_path=$HOME/cassiopee

# This is the directory where Cassiopee will be installed
export CASSIOPEE=$HOME/cassiopee/3.6

# Also add an alias
alias c='cassiopee'
```

After adding these lines, you need to reload your `.bashrc` or `.bash_profile` file. You can do this by closing and reopening your terminal, or by running the `source` command:

```bash
source ~/.bashrc
# or
source ~/.bash_profile
```

Next, you need to clone the Cassiopee repository and navigate into it:

```bash
# Clone the Cassiopee repository
git clone https://github.com/ricardofrantz/cassiopee.git

# Navigate into the cassiopee directory
cd cassiopee
```

Finally, you can install Cassiopee by running the `install` script:

```bash
# Run the install script
./install
```

This will compile and install Cassiopee in the directory specified by the `CASSIOPEE` environment variable.

Once Cassiopee is installed, you can run it directly from the terminal:

```bash
cassiopee
```