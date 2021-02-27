"""
Extract Surface
~~~~~~~~~~~~~~~

You can extract the surface of nearly any object within ``pyvista``
using the ``extract_surface`` filter.
"""

# sphinx_gallery_thumbnail_number = 2

import numpy as np
import pyvista as pv
from vtk import VTK_QUADRATIC_HEXAHEDRON

###############################################################################
# Create a quadratic cell and extract its surface
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Here we create a single hexahedral cell and then extract its surface
# to demonstrate how to extract the surface of a UnstructuredGrid.


lin_pts = np.array([[-1, -1, -1],  # point 0
                    [ 1, -1, -1],  # point 1
                    [ 1,  1, -1],  # point 2
                    [-1,  1, -1],  # point 3
                    [-1, -1,  1],  # point 4
                    [ 1, -1,  1],  # point 5
                    [ 1,  1,  1],  # point 6
                    [-1,  1,  1]], np.double)  # point 7

# these are the "midside" points of a quad cell
quad_pts = np.array([
    (lin_pts[1] + lin_pts[0])/2.0,
    (lin_pts[1] + lin_pts[2])/2.0,
    (lin_pts[2] + lin_pts[3])/2.0,
    (lin_pts[3] + lin_pts[0])/2.0,
    (lin_pts[4] + lin_pts[5])/2.0,
    (lin_pts[5] + lin_pts[6])/2.0,
    (lin_pts[6] + lin_pts[7])/2.0,
    (lin_pts[7] + lin_pts[4])/2.0,
    (lin_pts[0] + lin_pts[4])/2.0,
    (lin_pts[1] + lin_pts[5])/2.0,
    (lin_pts[2] + lin_pts[6])/2.0,
    (lin_pts[3] + lin_pts[7])/2.0], np.double)

# introduce a minor variation to the location of the mid-side points
quad_pts += np.random.random(quad_pts.shape)*0.3
pts = np.vstack((lin_pts, quad_pts))

# create the grid

# If you are using vtk>=9, you do not need the offset array
offset = np.array([0])
cells = np.asarray(np.hstack((20, np.arange(20))), dtype=np.int64)
celltypes = np.array([VTK_QUADRATIC_HEXAHEDRON])
grid = pv.UnstructuredGrid(offset, cells, celltypes, pts)

# finally, extract the surface and plot it
surf = grid.extract_surface()
surf.plot(show_scalar_bar=False)


###############################################################################
# Quadratic Surface Subdivision
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Should your UnstructuredGrid contain quadratic cells, you can
# generate a smooth surface based on the "shape functions" of each
# cell.

surf_subdivided = grid.extract_surface(subdivision=5)
surf_subdivided.plot(show_scalar_bar=False)
