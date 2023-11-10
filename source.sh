dnami(){
echo 'Loading dNami variables...'

export CASSIOPEE_SOURCE_ROOT="$HOME/cassiopee"
echo "CASSIOPEE_SOURCE_ROOT is set to $CASSIOPEE_SOURCE_ROOT"

export CASSIOPEE=$CASSIOPEE_SOURCE_ROOT/3.6
echo "CASSIOPEE is set to $CASSIOPEE"

echo "Sourcing env_Cassiopee.sh..."
. $CASSIOPEE/Dist/env_Cassiopee.sh

export DNAMI_SOURCE_ROOT="$HOME/dNamiDynFluid"
echo "DNAMI_SOURCE_ROOT is set to $DNAMI_SOURCE_ROOT"

export PATH=$DNAMI_SOURCE_ROOT/bin:$PATH
echo "PATH is set to $PATH"

export SRCdNami=$DNAMI_SOURCE_ROOT/dNami
echo "SRCdNami is set to $SRCdNami"

export SRCdNamiLin=$DNAMI_SOURCE_ROOT/dNamiLin
echo "SRCdNamiLin is set to $SRCdNamiLin"

export PYTHONPATH=$PYTHONPATH:$SRCdNamiLin/src_py
echo "PYTHONPATH is set to $PYTHONPATH"

export PYTHONEXE=python3
echo "PYTHONEXE is set to $PYTHONEXE"

export OMP_NUM_THREADS=1
echo "OMP_NUM_THREADS is set to $OMP_NUM_THREADS"

export MESA_GL_VERSION_OVERRIDE=3.0
echo "MESA_GL_VERSION_OVERRIDE is set to $MESA_GL_VERSION_OVERRIDE"

echo "Deactivating any active conda environment..."
conda deactivate

echo "Activating dnami conda environment..."
conda activate dnami

echo "Sourcing Intel OneAPI..."
source /opt/intel/oneapi/mpi/latest/env/vars.sh
source /opt/intel/oneapi/compiler/latest/env/vars.sh
#source /opt/intel/oneapi/setvars.sh --force

alias c='cassiopee'
}
