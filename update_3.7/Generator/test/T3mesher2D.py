# - T3mesher2D (array) -
import Generator as G
import Converter as C
import Geom as D

a = D.circle((0,0,0), 1, N=50)
a = C.convertArray2Tetra(a)
a = G.close(a)
b = G.T3mesher2D(a, triangulateOnly=0, grading=1.2, metricInterpType=0) # linear metric interpolation
C.convertArrays2File([a,b], 'outL.plt')

b = G.T3mesher2D(a, triangulateOnly=0, grading=1.2, metricInterpType=1) # geometric metric interpolation
C.convertArrays2File([a,b], 'outG.plt')
