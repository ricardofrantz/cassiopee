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
This script removes any directory in the home directory that contains 'conda3' in its name, deletes the base directory of the current conda installation, and removes conda configuration files.
```bash
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

Here are the steps to set up the environment to deactivate any currently active environment, remove the 'dnami' environment if it exists, create a new conda environment and activate it. 

```bash
conda config --set auto_activate_base false
conda deactivate
conda remove --name dnami --all
conda create --name dnami
conda activate dnami 
conda install setuptools=58.0 scons sympy matplotlib slepc4py libpng ffmpeg # python-devtools 
```

## Installation on Ubuntu apt
Update your package lists for upgrades and new package installations
This ensures you have the latest versions of all packages
Remove all unused packages and keep your system clean
Install the necessary packages
build-essential: contains references to all the packages needed to compile a Debian package. It generally includes the gcc/g++ compilers and libraries and some other utilities.
python3-dev: contains the header files you need to build Python extensions.
python3-numpy: is the fundamental package for array computing with Python.
scons: is a software construction tool.
gfortran: the GNU Fortran compiler.
xorg-dev: X.Org X Window System development libraries. They are needed for GUI applications.
libhdf5-dev: contains the header files and static libraries for developing programs that will use Hierarchical Data Format 5 (HDF5).
libglfw3-dev: is the development files for GLFW 3 library, which is a free, open source, multi-platform library for creating windows with OpenGL contexts.
libgl1-mesa-dev, libglu1-mesa-dev: are the development files for the Mesa 3D graphics library.
default-jdk
bison

```bash
sudo apt update
sudo apt -y autoremove
sudo apt install -y build-essential python3-dev python3-numpy scons gfortran xorg-dev libhdf5-dev libglfw3-dev libgl1-mesa-dev libglu1-mesa-dev default-jdk bison
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
This is the directory where the Cassiopee source code will be stored
This is the directory where Cassiopee will be installed
Also add an alias

```bash
export CASSIOPEE_SOURCE_ROOT="$HOME/cassiopee"
export CASSIOPEE=$CASSIOPEE_SOURCE_ROOT/3.6
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
git clone --depth 1 https://github.com/ricardofrantz/cassiopee.git
cd cassiopee
```

Finally, you can install Cassiopee by running the installation script:
```bash
./install.sh
```

This will compile and install Cassiopee in the directory specified by the `CASSIOPEE` environment variable.

Once Cassiopee is installed, you can run it directly from the terminal:

```bash
cassiopee
```
or
```bash
c
```
## Installing tapenade
```bash
git clone --depth 1 https://gitlab.inria.fr/tapenade/tapenade.git
cd tapenade
javac -version
./gradlew clean
./gradlew
```

## Installing fully automatic
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/ricardofrantz/cassiopee/main/cassiopee.sh)"
```
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/ricardofrantz/cassiopee/main/tapenade.sh)"
```
