/*    
    Copyright 2013-2023 Onera.

    This file is part of Cassiopee.

    Cassiopee is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Cassiopee is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Cassiopee.  If not, see <http://www.gnu.org/licenses/>.
*/
#ifndef _OCC_OCC_H_
#define _OCC_OCC_H_

#include "kcore.h"

namespace K_OCC
{
  PyObject* convertCAD2Arrays0(PyObject* self, PyObject* args); // with OCC internal
  PyObject* convertCAD2Arrays1(PyObject* self, PyObject* args); // with T3Mesher
  PyObject* convertCAD2Arrays2(PyObject* self, PyObject* args); // with T3Mesher
  PyObject* readCAD(PyObject* self, PyObject* args);
  PyObject* getNbFaces(PyObject* self, PyObject* args);
  PyObject* getNbEdges(PyObject* self, PyObject* args);
  PyObject* meshGlobalEdges(PyObject* self, PyObject* args);
  PyObject* meshGlobalEdges2(PyObject* self, PyObject* args);
  PyObject* meshEdgesByFace(PyObject* self, PyObject* args);
  PyObject* identifyLoopsInEdges(PyObject* self, PyObject* args);
  PyObject* evalEdge(PyObject* self, PyObject* args);
  PyObject* evalFace(PyObject* self, PyObject* args);
  PyObject* projectOnFaces(PyObject* self, PyObject* args);
  PyObject* projectOnEdges(PyObject* self, PyObject* args);
  PyObject* linkNodes2CAD(PyObject* self, PyObject* args);
  PyObject* updateFcadidFromNcadid(PyObject* self, PyObject* args);
  PyObject* updateNcadidFromFcadid(PyObject* self, PyObject* args);
  PyObject* getNodalParameters(PyObject* self, PyObject* args);
  PyObject* trimesh(PyObject* self, PyObject* args);
}

#endif
