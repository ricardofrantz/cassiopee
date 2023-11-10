#!/bin/bash
# Script: install
# Description: This script compiles a list of modules for the Cassiopee software package. It first cleans up the build environment, then pre-compiles the KCore module. After sourcing the environment script for Cassiopee, it compiles the rest of the modules. If a module's install script outputs 'FAILED' on its last line, that line is printed in red; otherwise, it is printed in green.
# Usage: Run this script from the directory where it is located. It does not take any command-line arguments.
# Author: Ricardo Frantz Nov-2023 DynFluid Lab Paris

set -u

abort() {
  printf "%s\n" "$@" >&2
  exit 1
}

MODULES='KCore Mpi4py Converter Geom Transform Generator Post Initiator XCore Connector Distributor2 CPlot Dist2Walls RigidMotion Compressor Intersector'

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    export OMP_NUM_THREADS=$(grep -c ^processor /proc/cpuinfo)
elif [[ "$OSTYPE" == "darwin"* ]]; then
    export OMP_NUM_THREADS=$(sysctl -n hw.logicalcpu)
fi
echo "Number of processors (OMP_NUM_THREADS): $OMP_NUM_THREADS"

# Function to compile a module
compile_module() {
    module=$1
    should_clean_build=$2
    cd $CASSIOPEE_SOURCE_ROOT/$module
    echo "Compiling module $module in $PWD"

    if [ "$should_clean_build" = "clean" ] && [ -d "./build/" ]; then
        echo "Removing existing build directory for $PWD/build/"
        rm -rf ./build/
    fi

    if [ ! -x install ]; then
        echo "Changing permissions of install for $module"
        chmod +x install
    fi

    # Redirect the output of the install script to the log file
    actual_log_file="../${module}.log"
    ./install >> "$actual_log_file" 2>&1
    tail -1 "$actual_log_file" | awk '/FAILED/ {print "\033[31m" $0 "\033[39m"; next} {print "\033[32m" $0 "\033[39m"}'
}

# Clean up the build environment
echo "Cleaning up the build environment..."
./clean.sh

echo "Sourced compilers:"
for compiler in mpicc mpicxx mpif90 mpif77; do
    echo " $(which $compiler)"
done

# Compile KCore first, which should fail before sourcing the environment
echo "Pre-compiling module KCore:"
compile_module "KCore" "clean"

# Source the environment script for Cassiopee
. $CASSIOPEE/Dist/env_Cassiopee.sh

# Compile the rest of the modules
total_modules=$(echo $MODULES | wc -w)
current_module=1

for module in $MODULES
do
    echo "Compiling module $current_module/$total_modules >> $module.log"
    if [ "$module" = "KCore" ]; then
        # Compile KCore again after sourcing the environment
        compile_module "KCore" "noclean"
    else 
        compile_module "$module" "clean"
    fi
    current_module=$((current_module+1))
done

chmod +x $CASSIOPEE/Dist/bin/x86_r8/lib/../cassiopee

. $CASSIOPEE/Dist/env_Cassiopee.sh