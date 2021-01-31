"""
Plotter Lighting Systems
~~~~~~~~~~~~~~~~~~~~~~~~

The :class:`pyvista.Plotter` class comes with three options for the default
lighting system:

  * a light kit consisting of a headlight and four camera lights,
  * an illumination system containing three lights arranged around the camera,
  * no lighting.

With meshes that don't have depth information encoded in their color the
importance of an appropriate lighting setup becomes paramount for accurate
visualization.

The default ``lighting='light kit'`` option recreates a lighting setup that
corresponds to a ``vtk.vtkLightKit``. We can check what type of lights this
lighting comprises:
"""
# sphinx_gallery_thumbnail_number = 3
import pyvista as pv

# default: light kit
plotter = pv.Plotter()
light_types = [light.light_type for light in plotter.renderer.lights]

# Remove from plotters so output is not produced in docs
pv.plotting._ALL_PLOTTERS.clear()

light_types


###############################################################################
# Add a white terrain to the scene:

from pyvista import examples

mesh = examples.download_st_helens().warp_by_scalar()
plotter = pv.Plotter()
plotter.add_mesh(mesh, color='white')
plotter.show()


###############################################################################
# Switching to three-lights illumination gives a different character to the
# figure, in this case showing less contrast when viewing the mountain from
# the top, but having more contrast with views closer to the side. This becomes
# especially clear when exploring the figures interactively.

plotter = pv.Plotter(lighting='three lights')
plotter.add_mesh(mesh, color='white')
plotter.show()

###############################################################################
# Again we can check what kind of lights this setting uses:

plotter = pv.Plotter(lighting='three lights')
light_types = [light.light_type for light in plotter.renderer.lights]

# Remove from plotters so output is not produced in docs
pv.plotting._ALL_PLOTTERS.clear()

light_types


###############################################################################
# We can introduce our own lighting from scratch by disabling any lighting
# on plotter initialization. Adding a single scene light to a scene will
# often result in ominous visuals due to objects casting large shadows on
# themselves:

plotter = pv.Plotter(lighting='none')
plotter.add_mesh(mesh, color='white')
light = pv.Light()
light.set_direction_angle(30, 0)
plotter.add_light(light)
plotter.show()
