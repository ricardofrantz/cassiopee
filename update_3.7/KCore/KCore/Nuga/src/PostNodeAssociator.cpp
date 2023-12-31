/*



--------- NUGA v1.0



*/
//Authors : S�m Landier (sam.landier@onera.fr)

#include "Nuga/include/PostNodeAssociator.h"
#include "Nuga/include/KdTree.h"
#include "Nuga/include/defs.h"
#include "Nuga/include/MeshTool.h"
#include "Nuga/include/ContourSplitter.h"
#include "Nuga/include/MergingZipper.h"

#ifdef DEBUG_POSTNODEASSOCIATOR
#include "IO/DynArrayIO.h"
#include <sstream>
#endif


#ifdef E_TIME
#include "Nuga/include/chrono.h"
#endif
#ifdef WIN32
#ifdef E_DEBUG
#include "meshIO/meshIO.h"
#include <sstream>
#endif
#endif


///
PostNodeAssociator::PostNodeAssociator(bool nodal)
{
  _zipper = (nodal == true) ? new MergingZipper(parent_type::reorient) : new Zipper(parent_type::reorient);
}

///
PostNodeAssociator::~PostNodeAssociator(void)
{
  if (_zipper) delete _zipper;
}

///
void
PostNodeAssociator::make_pairs
(const K_FLD::FloatArray& pos, const std::vector< K_FLD::IntArray* >& components,
 std::vector<E_Int> &nmates, K_FLD::IntArray& OneSurface)
{
  std::vector<E_Int> omates;
  nmates.resize(pos.cols(), IDX_NONE);

  std::vector<E_Int> ncolors(pos.cols(), IDX_NONE);

  OneSurface.clear();

#ifdef E_TIME
  DELAUNAY::chrono c, glob;
  c.start();
  glob.start();
#endif
  
#ifdef DEBUG_POSTNODEASSOCIATOR
  {// components and their boundaries before calling make_pairs
    K_FLD::IntArray conB;
    for (size_t c = 0; c < components.size(); ++c)
    {
      NUGA::MeshTool::getBoundary(*components[c], conB);
    
      std::ostringstream o;
      o << "compB0_" << c << ".mesh";
      K_CONVERTER::DynArrayIO::write(o.str().c_str(), pos, conB, "BAR");
    }
  }
#endif

  // Set the zip mates (or merge them) and set the free nodes (external contours).
  __setZipMates(pos, components, nmates);
  
#ifdef DEBUG_POSTNODEASSOCIATOR
  {// components and their boundaries after calling make_pairs
    K_FLD::IntArray conB;
    for (size_t c = 0; c < components.size(); ++c)
    {
      NUGA::MeshTool::getBoundary(*components[c], conB);
    
      std::ostringstream o;
      o << "compB1_" << c << ".mesh";
      K_CONVERTER::DynArrayIO::write(o.str().c_str(), pos, conB, "BAR");
    }
  }
#endif

#ifdef E_TIME  
  std::cout << "setZipMates " << c.elapsed() << std::endl;
  c.start();
#endif

  // Intersections
  std::vector<K_FLD::IntArray> clean_comps;
  omates = nmates;
  __removeOverlaps(pos, components, nmates, clean_comps);

#ifdef E_TIME  
  std::cout << "remove overlaps " << c.elapsed() << std::endl;
#endif

  for (size_t comp = 0; comp < clean_comps.size(); ++comp)
    OneSurface.pushBack(clean_comps[comp]);

#ifdef WIN32
#ifdef E_DEBUG
  meshIO::write("cleaned.mesh", pos, OneSurface);
#endif
#endif

#ifdef E_TIME  
  c.start();
#endif

  // Make pairs for overlaps.
  K_FLD::FloatArray over, free;
  std::vector< std::vector<E_Int> > overlap_nodes;
  K_FLD::IntArray connectB;
  std::vector<E_Int> nodes, tmp, comp_colors;
  std::vector<K_FLD::IntArray> connectbs;
  NUGA::int_set_type dummy;
  E_Int color = 0;
  for (size_t comp = 0; comp < clean_comps.size(); ++comp)
  {
    NUGA::MeshTool::getBoundary(clean_comps[comp], connectB);
    connectbs.clear();
    ContourSplitter<K_MESH::Edge, E_Int>::splitConnectivity(connectB, dummy, connectbs);

    for (size_t k = 0; k < connectbs.size(); ++k)
    {
      connectbs[k].uniqueVals(nodes);
      tmp.clear();

      for (size_t n = 0; n < nodes.size(); ++n)
      {
        if (nmates[nodes[n]] == Zipper::OVERLAP)
          tmp.push_back(nodes[n]);
        ncolors[nodes[n]] = color;
      }
      if (!tmp.empty())
      {
        overlap_nodes.push_back(tmp);
        comp_colors.push_back(comp);
      }

      ++color;
    }
  }

  parent_type::__make_pairs(pos, overlap_nodes, comp_colors, nmates);

#ifdef E_TIME  
  std::cout << "Make pairs for overlaps " << c.elapsed() << std::endl;
#endif

  // Restore old mates
  {
    E_Int omate;
    for (size_t i = 0; i < nmates.size(); ++i)
    {
      if (nmates[i] != Zipper::OVERLAP)
        continue;
      omate = omates[i];
      if (omate < 0 || omate == IDX_NONE)
        continue;
      if (nmates[omate] != Zipper::OVERLAP)
        continue;
      
      nmates[i] = omate;
      nmates[omate] = i;
    }
  }
}

void
PostNodeAssociator::__setZipMates
(const K_FLD::FloatArray& pos, const std::vector<K_FLD::IntArray*>& components,
 std::vector<E_Int>& nmates)
{
  K_FLD::IntArray connectB;

  for (size_t comp = 0; comp < components.size(); ++comp)
  {
    K_FLD::IntArray& component = *components[comp];
    // Get the boundary.
    NUGA::MeshTool::getBoundary(component, connectB);
    
#ifdef DEBUG_POSTNODEASSOCIATOR
    std::ostringstream o;
    o << "component_" << comp << ".mesh";
    K_CONVERTER::DynArrayIO::write(o.str().c_str(), pos, connectB, "BAR");
#endif
    // Link the component's surfaces.
    _zipper->setMates(pos, component, connectB, nmates);

    if (reorient)// Reorient the component consistently.
      __reorientComponent(pos, component, nmates);

    // Merge joints. Only relevant for a nodal mesh.
    _zipper->merge(pos, component, connectB, nmates);
  }
}

