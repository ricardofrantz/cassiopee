import sys
import os

os.system('tar -xovf fast.tar')

#modules= ['KCore','Converter','Connector','CPlot','Dist2Walls','Distributor2','Generator','Geom','Initiator','Transform','Post','Envs','Compressor','RigidMotion']
modules= ['KCore','Converter','Connector','CPlot','Dist2Walls','Distributor2','Generator','Geom','Initiator','Post','Transform','Envs','Compressor','RigidMotion','XCore','Apps']
for module in modules:
   command0='cd Modules; gzip -d '+ module +'.tar.gz; tar -xovf ' + module +'.tar'
   os.system(command0)

Thirdparty= ['mpi4py','scons','paradigma','scotch']
for module in Thirdparty:
  command0='cd Modules/ThirdParty;  gzip -d '+ module +'.tar.gz; tar -xovf ' +module+'.tar'
  os.system(command0)

pmodules= ['FastC','FastS','FastP','FastLBM','Fast']
#pmodules= ['Fast','FastLBM']
for module in pmodules:
   command0='cd PModules; gzip -d '+ module +'.tar.gz; tar -xovf ' + module +'.tar'
   os.system(command0)