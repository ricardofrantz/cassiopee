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
#include "converter.h"

using namespace K_FUNC;
using namespace K_FLD;
using namespace std;

// ============================================================================
/* Convert  structured array to a tetraedrical mesh */
// ============================================================================
PyObject* K_CONVERTER::convertStruct2Hexa(PyObject* self, PyObject* args)
{
  PyObject* array;
  if (!PyArg_ParseTuple(args, "O", &array)) return NULL;

  // Check array
  PyObject* tpl = NULL;
  E_Int nil, njl, nkl;
  FldArrayF* f; FldArrayI* cnl;
  char* varString; char* eltType;
  E_Int res;

  E_Int dim0 = -1;
  E_Int elt = 0;

  res = K_ARRAY::getFromArray(array, varString, 
                              f, nil, njl, nkl, cnl, eltType, true);
  
  if (res == 1)
  {   
    // 1D, 2D or 3D ?
    dim0 = 3;
    if (nil == 1)
    {
      if (njl == 1 || nkl == 1) dim0 = 1;
      else dim0 = 2;
    }
    else if (njl == 1)
    {
      if (nil == 1 || nkl == 1) dim0 = 1;
      else dim0 = 2;
    }
    else if (nkl == 1)
    {
      if (nil == 1 || njl == 1) dim0 = 1;
      else dim0 = 2;
    }
      
    // Build the unstructured mesh
    E_Int ni1 = E_max(1, E_Int(nil)-1);
    E_Int nj1 = E_max(1, E_Int(njl)-1);
    E_Int nk1 = E_max(1, E_Int(nkl)-1);
    E_Int ninj = nil*njl;
    E_Int ncells = ni1*nj1*nk1;// nb de cellules structurees
    E_Int nelts; // nb d elements non structures
    
    switch (dim0)
    {
      case 1:
      {
        nelts = ncells;
        elt = 1; // BAR
        tpl = K_ARRAY::buildArray(f->getNfld(), varString,
                                  f->getSize(), nelts,
                                  elt, NULL);
        E_Float* fnp = K_ARRAY::getFieldPtr(tpl);
        FldArrayF fn(f->getSize(), f->getNfld(), fnp, true); fn = *f;
        E_Int* cnnp = K_ARRAY::getConnectPtr(tpl);
        FldArrayI cn(nelts, 2, cnnp, true);
        E_Int* cn1 = cn.begin(1);
        E_Int* cn2 = cn.begin(2);
        E_Int ind1, ind2;
        if (nk1 == 1 && nj1 == 1)
        {
          for (E_Int i = 0; i < ni1; i++)
          {
            ind1 = i + 1;
            ind2 = ind1 + 1;
            cn1[i] = ind1;
            cn2[i] = ind2;
          }
        }
        else if (ni1 == 1 && nj1 == 1)
        {
          for (E_Int k = 0; k < nk1; k++)
          {
            ind1 = k*nil*njl + 1;
            ind2 = ind1 + nil*njl;
            cn1[k] = ind1;
            cn2[k] = ind2;
          }
        }
        else if (ni1 == 1 && nk1 == 1)
        {
          for (E_Int j = 0; j < nj1; j++)
          {
            ind1 = j*nil + 1;
            ind2 = ind1 + nil;
            cn1[j] = ind1;
            cn2[j] = ind2;
          }
        }
      }
      break;

      case 2:
      {
        nelts = ncells;
        elt = 3; // QUAD
        tpl = K_ARRAY::buildArray(f->getNfld(), varString,
                                  f->getSize(), nelts,
                                  elt, NULL);
        E_Float* fnp = K_ARRAY::getFieldPtr(tpl);
        FldArrayF fn(f->getSize(), f->getNfld(), fnp, true); fn = *f;
        E_Int* cnnp = K_ARRAY::getConnectPtr(tpl);
        FldArrayI cn(nelts, 4, cnnp, true);
        E_Int* cn1 = cn.begin(1);
        E_Int* cn2 = cn.begin(2);
        E_Int* cn3 = cn.begin(3);
        E_Int* cn4 = cn.begin(4);

        if (nk1 == 1)
        {
#pragma omp parallel default(shared) if (nj1 > __MIN_SIZE_MEAN__)
          {
            E_Int ind, ind1, ind2, ind3, ind4;
#pragma omp for
            for (E_Int j = 0; j < nj1; j++)
              for (E_Int i = 0; i < ni1; i++)
              {
                //starts from 1
                ind1 = i + j*nil + 1; //(i,j,1)
                ind2 = ind1 + 1;  //(i+1,j,1)
                ind3 = ind2 + nil;//(i+1,j+1,1)
                ind4 = ind3 - 1; //(i,j+1,1)
                ind = i + j*ni1;
                cn1[ind] = ind1;
                cn2[ind] = ind2;
                cn3[ind] = ind3;
                cn4[ind] = ind4;
              }
          }
        }
        else if (nj1 == 1)
        {
#pragma omp parallel default(shared) if (nk1 > __MIN_SIZE_MEAN__)
          {
            E_Int ind, ind1, ind2, ind3, ind4;
#pragma omp for
            for (E_Int k = 0; k < nk1; k++)
              for (E_Int i = 0; i < ni1; i++)
              {
                ind1 = i + k*ninj + 1;  //(i,1,k)
                ind2 = ind1 + ninj; //(i,1,k+1)
                ind3 = ind2 + 1;    //(i+1,1,k+1)
                ind4 = ind1 + 1;    //(i+1,1,k)
                ind = i + k*ni1;
                cn1[ind] = ind1;
                cn2[ind] = ind2;
                cn3[ind] = ind3;
                cn4[ind] = ind4;      
              }
          }
        }
        else // i1 = 1 
        {
#pragma omp parallel default(shared) if (nk1 > __MIN_SIZE_MEAN__)
          {
            E_Int ind, ind1, ind2, ind3, ind4;
#pragma omp for        
            for (E_Int k = 0; k < nk1; k++)
              for (E_Int j = 0; j < nj1; j++)
              {
                ind1 = 1 + j*nil + k*ninj; //(1,j,k)
                ind2 = ind1 + nil;  //(1,j+1,k)
                ind3 = ind2 + ninj;//(1,j+1,k+1)
                ind4 = ind3 - nil;   //(1,j,k+1)
                ind = j+k*nj1;
                cn1[ind] = ind1;
                cn2[ind] = ind2;
                cn3[ind] = ind3;
                cn4[ind] = ind4;
              }
          }// i1 = 1
        }
      }
      break;

      case 3:
      {
        nelts = ncells;
        elt = 7; //HEXA
        tpl = K_ARRAY::buildArray(f->getNfld(), varString,
                                  f->getSize(), nelts,
                                  elt, NULL);
        E_Float* fnp = K_ARRAY::getFieldPtr(tpl);
        FldArrayF fn(f->getSize(), f->getNfld(), fnp, true); fn = *f;
        E_Int* cnnp = K_ARRAY::getConnectPtr(tpl);
        FldArrayI cn(nelts, 8, cnnp, true);
        E_Int* cn1 = cn.begin(1);
        E_Int* cn2 = cn.begin(2);
        E_Int* cn3 = cn.begin(3);
        E_Int* cn4 = cn.begin(4);
        E_Int* cn5 = cn.begin(5);
        E_Int* cn6 = cn.begin(6);
        E_Int* cn7 = cn.begin(7);
        E_Int* cn8 = cn.begin(8);

#pragma omp parallel default(shared) if (nk1 > __MIN_SIZE_MEAN__)
          {
            E_Int ind, ind1, ind2, ind3, ind4, ind5, ind6, ind7, ind8;
#pragma omp for
            for (E_Int k = 0; k < nk1; k++)
              for (E_Int j = 0; j < nj1; j++)
                for (E_Int i = 0; i < ni1; i++)
                {
                  ind1 = 1 + i + j*nil + k*ninj; //A(  i,  j,k)
                  ind2 = ind1 + 1;              //B(i+1,  j,k)
                  ind3 = ind2 + nil;            //C(i+1,j+1,k)
                  ind4 = ind3 - 1;              //D(  i,j+1,k)
                  ind5 = ind1 + ninj;           //E(  i,  j,k+1)
                  ind6 = ind2 + ninj;           //F(i+1,  j,k+1)
                  ind7 = ind3 + ninj;           //G(i+1,j+1,k+1)
                  ind8 = ind4 + ninj;           //H(  i,j+1,k+1) 
                  ind = i+j*ni1+k*ni1*nj1;
                  cn1[ind] = ind1;
                  cn2[ind] = ind2;
                  cn3[ind] = ind3;
                  cn4[ind] = ind4;
                  cn5[ind] = ind5;
                  cn6[ind] = ind6;
                  cn7[ind] = ind7;
                  cn8[ind] = ind8;
                }
          }
      }
      break;
    }
  }  
  else if (res == 2)
  {
    RELEASESHAREDU(array, f, cnl);
    PyErr_SetString(PyExc_TypeError, 
                    "convertStruct2Hexa: array must be structured.");
    return NULL;
  }
  else
  {
     PyErr_SetString(PyExc_TypeError, 
                     "convertStruct2Hexa: array is invalid.");
     return NULL;
  }

  RELEASESHAREDB(res, array, f, cnl);
  return tpl;
}
