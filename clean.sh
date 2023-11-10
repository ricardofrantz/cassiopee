#!/bin/bash

set -u

MODULES='KCore Mpi4py Converter Geom Transform Generator Post Initiator XCore Connector Distributor2 CPlot Dist2Walls RigidMotion Compressor Intersector'

rm *.log
rm -rf "$CASSIOPEE"
rm -rf __pycache__
for module in $MODULES
do
    rm -rf "$module"/build
    rm -rf "$module"/__pycache__
done