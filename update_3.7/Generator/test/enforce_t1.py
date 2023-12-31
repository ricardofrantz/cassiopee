# - enforceX, enforceY, ... monotonic (array) -
import Generator as G
import KCore.test as test

a = G.cart((0,0,0), (1,1,1), (20,20,10))
b = G.enforceX(a, 5., 0.2, 10, 5)
b = G.enforceX(b, 15., 0.2, 10, 5)
b = G.enforceY(b, 10., 0.1, 5, 5)
b = G.enforcePlusY(b, 0.01, 20, 5)
test.testA([a,b])
