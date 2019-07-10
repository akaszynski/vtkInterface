"""
Plot with Opacity
~~~~~~~~~~~~~~~~~

Plot a mesh's scalar array with an opacity trasfer funciton or opacity mapping
based on a scalar array.
"""

import pyvista as pv
from pyvista import examples

# Load St Helens DEM and warp the topography
image = examples.download_st_helens()
mesh = image.warp_by_scalar()


###############################################################################
# Global Value
# ++++++++++++
#
# You can also apply a global opacity value to the mesh by passing a single
# float between 0 and 1 which would enable you to see objects behind the mesh:

p = pv.Plotter()
p.add_mesh(image.contour(), line_width=5,)
p.add_mesh(mesh, opacity=0.4, color=True)
p.show()

###############################################################################
# Note that you can specify ``use_transparency=True`` to convert opacities to
# transperencies in any of the following examples.


###############################################################################
# Transfer Functions
# ++++++++++++++++++
#
# It's possible to apply an opacity mapping to any scalar array plotted. You
# can specify either a single static value to make the mesh transparent on all
# cells, or use a transfer function where the scalar array plotted is mapped
# to the opacity. We have several predefined transfer functions.
#
# Opacity transfer functions are:
#
# - ``'linear'``: linearly vary (increase) opacity across the plotted scalar range from low to high
# - ``'linear_r'``: linearly vary (increase) opacity across the plotted scalar range from high to low
# - ``'geom'``: on a log scale, vary (increase) opacity across the plotted scalar range from low to high
# - ``'geom_r'``: on a log scale, vary (increase) opacity across the plotted scalar range from high to low
# - ``'sigmoid'``: vary (increase) opacity on a sigmoidal s-curve across the plotted scalar range from low to high
# - ``'sigmoid_r'``: vary (increase) opacity on a sigmoidal s-curve across the plotted scalar range from high to low

# Show the linear opacity transfer function
mesh.plot(opacity="linear")

###############################################################################

# Show the sigmoid opacity transfer function
mesh.plot(opacity="sigmoid")

###############################################################################
# It's also possible to use your own transfer function that will be linearly
# mapped to the scalar array plotted. For example, we can create an opacity
# mapping as:
opacity = [0, 0.2, 0.9, 0.2, 0.1]

###############################################################################
# That opacity mapping will have an opacity of 0.0 at the minimum scalar range,
# a value or 0.9 at the middle of the scalar range, and a value of 0.1 at the
# maximum of the scalar range:

mesh.plot(opacity=opacity)

###############################################################################
# Opacity mapping is often useful when plotting DICOM images. For example,
# download the sample knee DICOM image:
knee = examples.download_knee()

###############################################################################
# And here we inspect the DICOM image with a few different opacity mappings:
p = pv.Plotter(shape=(2, 2), border=False)

p.add_mesh(knee, cmap="bone", stitle="No Opacity")
p.view_xy()

p.subplot(0, 1)
p.add_mesh(knee, cmap="bone", opacity="linear", stitle="Linear Opacity")
p.view_xy()

p.subplot(1, 0)
p.add_mesh(knee, cmap="bone", opacity="sigmoid", stitle="Sigmoidal Opacity")
p.view_xy()

p.subplot(1, 1)
p.add_mesh(knee, cmap="bone", opacity="geom_r", stitle="Log Scale Opacity")
p.view_xy()

p.show()

###############################################################################
# Opacity by Array
# ++++++++++++++++
#
# You can also use a scalar array associated with the mesh to give each cell
# its own opacity/transperency value derived from a scalar field. For exmple,
# an uncertainty array from a modelling result could be used to hide regions of
# a mesh that are uncertain and highlight regions that are well resolved.
#
# The following is a demonstartion of plotting a mesh with colored values and
# using a second array to control the transperancy of the mesh

model = examples.download_model_with_variance()
contours = model.contour(10, scalars='Temperature')
print(contours.scalar_names)

###############################################################################
# Make sure to flag ``use_transparency=True`` since we want areas of high
# variance to have high transperency.

p = pv.Plotter(shape=(1,2))

p.subplot(0,0)
p.add_text('Opacity by Array')
p.add_mesh(contours.copy(), scalars='Temperature',
           opacity='Temperature_var',
           use_transparency=True,
           cmap='bwr')

p.subplot(0,1)
p.add_text('No Opacity')
p.add_mesh(contours, scalars='Temperature',
           cmap='bwr')
p.show()
