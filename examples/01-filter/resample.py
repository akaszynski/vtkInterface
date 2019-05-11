"""
Resampling & Interpolating
~~~~~~~~~~~~~~~~~~~~~~~~~~

Resample one mesh's point/cell arrays onto another meshes nodes.
"""
###############################################################################
# This example will resample a volumetric mesh's  scalar data onto the surface
# of a sphere contained in that volume.

# sphinx_gallery_thumbnail_number = 4
import pyvista
from pyvista import examples
import numpy as np

###############################################################################
# Querry a grids points onto a sphere
mesh = pyvista.Sphere(center=(4.5,4.5,4.5), radius=4.5)
data_to_probe = examples.load_uniform()

###############################################################################
# Plot the two datasets
p = pyvista.Plotter()
p.add_mesh(mesh, color=True)
p.add_mesh(data_to_probe, opacity=0.5)
p.show()

###############################################################################
# Run the algorithm and plot the result
result = mesh.sample(data_to_probe)

# Plot result
name = 'Spatial Point Data'
result.plot(scalars=name, clim=data_to_probe.get_data_range(name))



###############################################################################
# Interpolate
# +++++++++++
#
# Run a resampling from an interpolation built using a Gaussian kernal

# Download sample data
surface = examples.download_saddle_surface()
points = examples.download_sparse_points()


p = pyvista.Plotter()
p.add_mesh(points, point_size=30.0, render_points_as_spheres=True)
p.add_mesh(surface)
p.show()

###############################################################################
# Run the interpolation

interpolated = surface.interpolate(points, radius=12.0)


p = pyvista.Plotter()
p.add_mesh(points, point_size=30.0, render_points_as_spheres=True)
p.add_mesh(interpolated, scalars='val')
p.show()
