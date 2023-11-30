import os, socket, getpass, shutil, subprocess
hostname = socket.gethostname()
username = getpass.getuser()

# Check if ifort and icpc are available, otherwise use gfortran and gcc
f77compiler = 'ifort' if shutil.which('ifort') else 'gfortran'
f90compiler = 'ifort' if shutil.which('ifort') else 'gfortran'
Cppcompiler = 'icpc' if shutil.which('icpc') else 'gcc'
#Cppcompiler = 'icpx' if shutil.which('icpx') else 'gcc' # new intel compiler # NOT WORKING YET

include_path = []
lib_path = []

# Get the active conda environment
active_conda_env = os.environ.get('CONDA_DEFAULT_ENV') # return conda env name
active_conda_env_path = os.environ.get('CONDA_PREFIX') # return conda env path
if active_conda_env is not None:
    print('Detected active conda environment:', active_conda_env)
    # output = subprocess.check_output("conda list", shell=True)
    include_path.append('/usr/include/x86_64-linux-gnu')  # default include path
    lib_path.append('/usr/lib/x86_64-linux-gnu')  # default lib path

    include_path.append(os.path.join(active_conda_env_path, "include"))
    lib_path.append(os.path.join(active_conda_env_path, "lib"))
else:
    print('No active conda environment') 
    #custom include and lib paths #
    include_path.append('/usr/include')  # default include path
    include_path.append('/usr/include/x86_64-linux-gnu')  # default include path
    include_path.append('/usr/include/hdf5/serial') # hdf5 include path
    lib_path.append('/usr/lib/x86_64-linux-gnu')  # default lib path
    lib_path.append('/usr/lib/x86_64-linux-gnu/hdf5/serial') # hdf5 lib path

# compiler_path = subprocess.getoutput(f'which mpiicc')
# if 'no mpiicc in' not in compiler_path:
#     mpi_path = os.path.dirname(compiler_path)
#     mpi_path_components = mpi_path.split(os.sep)
#     first_five_folders = os.sep.join(mpi_path_components[:6])
#     include_path.append(first_five_folders + '/include')
# else:
#     include_path.append('/usr/include/mpi')  # default include path
#     lib_path.append('/usr/include/mpi')  # default include path


## DO NOT EDIT BELOW THIS LINE ##

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
    include_path,
    # additionalLibs
    ['gfortran',
     'gomp', 
     'pthread'],
    # additionalLibPaths
    lib_path,
    False, # useCuda
    [] # NvccAdditionalOptions
    ]
}