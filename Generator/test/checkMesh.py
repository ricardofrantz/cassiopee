# - checkMesh (array) -
import Generator as G

a = G.cart((0,0,0), (1,1,1), (10,10,10))
infos = G.checkMesh(a)
print(infos)
#> {'vmin': 1.0, 'vmax': 1.0, 'vmean': 1.0, 'rmin': 0.0, 'rmax': 0.0, 'rmean': 0.0, 'omin': 0.0, 'omax': 0.0, 'omean': 0.0}
