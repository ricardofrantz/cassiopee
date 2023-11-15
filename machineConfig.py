import os
import socket
import getpass
import shutil

hostname = socket.gethostname()
username = getpass.getuser()

# Get the path to the current conda environment
conda_env_dir = os.environ['CONDA_PREFIX']

# Check if ifort and icpc are available, otherwise use gfortran and gcc
f77compiler = 'ifort' if shutil.which('ifort') else 'gfortran'
f90compiler = 'ifort' if shutil.which('ifort') else 'gfortran'
Cppcompiler = 'icpc' if shutil.which('icpc') else 'gcc'

# Construct the paths

libavcodec_path = os.path.join(conda_env_dir, "include/libavcodec/")
#avcodec_h_path = os.path.join(conda_env_dir, "include/libavcodec/avcodec.h")
# mem_h_path = os.path.join(conda_env_dir, "include/libavutil/mem.h")
imgutils_h_path = os.path.join(conda_env_dir, "include/libavutil/") #/imgutils.h")
# hdf5_h_path = os.path.join(conda_env_dir, "include/hdf5.h")

installDict = {
    hostname: [ username,
    f77compiler, # f77compiler
    f90compiler, # f90compiler
    Cppcompiler, # Cppcompiler
    [], # CppAdditionalOptions
    [], # f77AdditionalOptions
    True, # useOMP
    False, # static
    False, # CPlotOffScreen
    # additionalIncludePaths
    [
     '/usr/include', # for libpng
     # '/usr/include/mpi', # not if intel mpi
     '/usr/include/hdf5/serial', # for hdf5
     #libavcodec_path,
    #  imgutils_h_path,
      #'/include',
    #  '/include/libavutil/',
    #  '/include/libavcodec/',
     ], 
    # additionalLibs
    ['gfortran',
     'gomp', 
     'pthread'],
    # additionalLibPaths
    [
        '/usr/lib/x86_64-linux-gnu/hdf5/serial/',
        #'/usr/lib/x86_64-linux-gnu',
     ], 
    False, # useCuda
    [] # NvccAdditionalOptions
    ]
}
# find / -name libavcodec 2>/dev/null
# find / -name avcodec.h 2>/dev/null
# find / -name mem.h 2>/dev/null
# find / -name imgutils.h 2>/dev/null
# find / -name hdf5.h 2>/dev/null