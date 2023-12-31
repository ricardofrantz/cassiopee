/*



--------- NUGA v1.0



*/
//Authors : S�m Landier (sam.landier@onera.fr)

#ifndef NUGA_VERTEX_H
#define NUGA_VERTEX_H

#include "Nuga/include/defs.h"

namespace NUGA
{
  struct vecval
  {
    double  vec[3];
    double  val2;
    int     flag; // e.g. used to store node id
    int     flag2;

    vecval()
    {
      vec[0] = vec[1] = vec[2] = val2 = FLOAT_MAX;
      flag = flag2 = -1;
    }

    vecval(const double*p, double v2):val2(v2)
    {
      vec[0] = p[0];
      vec[1] = p[1];
      vec[2] = p[2];
    }
  };

  using vertex = vecval;
  using direction = vecval;

  
}

#endif
