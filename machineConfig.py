installDict = {
###############################################################################
'pop-os': [ 'cobra',
'ifort', # f77compiler
'ifort', # f90compiler
'icpc', # Cppcompiler
[], # CppAdditionalOptions
[], # f77AdditionalOptions
True, # useOMP
False, # static
False, # CPlotOffScreen
['/usr/include', '/usr/include/hdf5/serial'], # additionalIncludePaths
['gfortran', 'gomp', 'pthread'], # additionalLibs
['/usr/lib/x86_64-linux-gnu/hdf5/serial/'], # additionalLibPaths
False, # useCuda
[] # NvccAdditionalOptions
],
###############################################################################
# 'pop-os': [ 'cobra',
# 'gfortran', # f77compiler
# 'gfortran', # f90compiler
# 'gcc', # Cppcompiler
# [], # CppAdditionalOptions
# [], # f77AdditionalOptions
# True, # useOMP
# False, # static
# False, # CPlotOffScreen
# ['/usr/include/mpi', '/usr/include/hdf5/serial'], # additionalIncludePaths
# ['gfortran', 'gomp', 'pthread'], # additionalLibs
# ['/usr/lib/x86_64-linux-gnu','/usr/lib/x86_64-linux-gnu/hdf5/serial/'], # additionalLibPaths
# False, # useCuda
# [] # NvccAdditionalOptions
# ]
###############################################################################
# 'Rs-MacBook-Pro.local': [ 'r',
# 'gfortran', # f77compiler
# 'gfortran', # f90compiler
# 'gcc', # Cppcompiler
# [], # CppAdditionalOptions
# [], # f77AdditionalOptions
# True, # useOMP
# False, # static
# False, # CPlotOffScreen
# ['/usr/include/mpi', '/usr/include/hdf5/serial'], # additionalIncludePaths
# ['gfortran', 'gomp', 'pthread'], # additionalLibs
# ['/usr/lib/x86_64-linux-gnu','/usr/lib/x86_64-linux-gnu/hdf5/serial/'], # additionalLibPaths
# False, # useCuda
# [] # NvccAdditionalOptions
# ]
###############################################################################
}
