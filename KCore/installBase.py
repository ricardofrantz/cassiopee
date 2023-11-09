import os
import sys

# Get the path from an environment variable
cassiopee_path = os.getenv('cassiopee_src_path')

if cassiopee_path is not None:
    # Add the path to sys.path
    sys.path.insert(0, cassiopee_path)

from machineConfig import installDict