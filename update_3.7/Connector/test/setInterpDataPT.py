# - setInterpData (pyTree) -
import Converter.PyTree as C
import Generator.PyTree as G
import Connector.PyTree as X

a = G.cylinder((0,0,0),1.,3.,360,0,1,(200,30,2)); a[0] = 'cylindre1'
a = C.addBC2Zone(a, 'wall1', 'BCWall', 'jmin')
a = C.addBC2Zone(a, 'ov1', 'BCOverlap', 'jmax')
b = G.cylinder((4,0,0),1.,3.,360,0,1,(200,30,2)); b[0] = 'cylindre2'
b = C.addBC2Zone(b, 'wall1', 'BCWall', 'jmin')
b = C.addBC2Zone(b, 'ov1', 'BCOverlap', 'jmax')
c = G.cart((-5.,-7.5,0), (15./200,15./200,1), (200,200,2))
t = C.newPyTree(['Corps1', 'Corps2', 'Bgrd'])
t[2][1][2].append(a); t[2][2][2].append(b); t[2][3][2].append(c)
t = X.connectMatch(t, dim=2)
t = C.fillEmptyBCWith(t, 'nref', 'BCFarfield', dim=2)
t = X.applyBCOverlaps(t, depth=1)
t[2][2:] = X.setInterpData(t[2][1], t[2][2:], loc='centers', storage='inverse')
C.convertPyTree2File(t, "out.cgns")
