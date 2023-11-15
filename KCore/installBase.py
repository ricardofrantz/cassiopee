import os
import sys
import socket

# Get the path from an environment variable
cassiopee_path = os.getenv('CASSIOPEE_SOURCE_ROOT')

if cassiopee_path is not None:
    # Add the path to sys.path
    sys.path.insert(0, cassiopee_path)

from machineConfig import installDict

print('installDict = ', installDict[socket.gethostname()])
