"""
Multi-Window Plot
~~~~~~~~~~~~~~~~~


Subplotting: having multiple scenes in a single window
"""

import pyvista as pv
from pyvista import examples

###############################################################################
# This example shows how to create a multi-window plotter by specifying the
# ``shape`` parameter.  The window generated is a two by two window by setting
# ``shape=(2, 2)``. Use the :func:`pyvista.BasePlotter.subplot` function to
# select the subplot you wish to be the active subplot.

plotter = pv.Plotter(shape=(2, 2))

plotter.subplot(0, 0)
plotter.add_text("Render Window 0", font_size=30)
plotter.add_mesh(examples.load_globe())

plotter.subplot(0, 1)
plotter.add_text("Render Window 1", font_size=30)
plotter.add_mesh(pv.Cube(), show_edges=True, color="tan")

plotter.subplot(1, 0)
plotter.add_text("Render Window 2", font_size=30)
sphere = pv.Sphere()
plotter.add_mesh(sphere, scalars=sphere.points[:, 2])
plotter.add_scalar_bar("Z")
# plotter.add_axes()
plotter.add_axes(interactive=True)

plotter.subplot(1, 1)
plotter.add_text("Render Window 3", font_size=30)
plotter.add_mesh(pv.Cone(), color="g", show_edges=True)
plotter.show_bounds(all_edges=True)

# Display the window
plotter.show()


###############################################################################
plotter = pv.Plotter(shape=(1, 2))

# Note that the (0, 0) location is active by default
# load and plot an airplane on the left half of the screen
plotter.add_text("Airplane Example\n", font_size=30)
plotter.add_mesh(examples.load_airplane(), show_edges=False)

# load and plot the uniform data example on the right-hand side
plotter.subplot(0, 1)
plotter.add_text("Uniform Data Example\n", font_size=30)
plotter.add_mesh(examples.load_uniform(), show_edges=True)

# Display the window
plotter.show()


###############################################################################
# Split the rendering window in half and subdivide it in a nr. of vertical or
# horizontal subplots.

# This defines the position of the vertical/horizontal splitting, in this
# case 40% of the vertical/horizontal dimension of the window
pv.rcParams['multi_rendering_splitting_position'] = 0.40

# shape="3|1" means 3 plots on the left and 1 on the right,
# shape="4/2" means 4 plots on top of 2 at bottom.
plotter = pv.Plotter(shape='3|1', window_size=(1000,1200))

plotter.subplot(0)
plotter.add_text("Airplane Example")
plotter.add_mesh(examples.load_airplane(), show_edges=False)

# load and plot the uniform data example on the right-hand side
plotter.subplot(1)
plotter.add_text("Uniform Data Example")
plotter.add_mesh(examples.load_uniform(), show_edges=True)

plotter.subplot(2)
plotter.add_text("A Sphere")
plotter.add_mesh(pv.Sphere(), show_edges=True)

plotter.subplot(3)
plotter.add_text("A Cone")
plotter.add_mesh(pv.Cone(), show_edges=True)

# Display the window
plotter.show()


###############################################################################
# Create a layout grid and register groups which can span over multiple rows
# and columns.
import numpy as np # numpy is imported for a more convenient slice notation through np.s_

shape = (5,5) # 5 by 5 grid
groups = [
    (0,np.s_[:]),               # First group spans over all columns of the first row (0)
    ([1,3],0),                  # Second group spans over row 1-3 of the first column (0)
    (np.s_[2:],[1,2]),          # Third group spans over rows 2-4 and columns 1-2
    (np.s_[1:-1],slice(3,None)),# Fourth group spans over rows 1-3 and columns 3-4
    (4,[3,4]),                  # Fifth group spans over column 3-4 of the last row (4)
]

plotter = pv.Plotter(shape=shape,groups=groups)

# Access all subplots and groups and plot something:
# Note that a group can be accessed through any of its composing cells
plotter.subplot(0,0)
plotter.add_text("Group 1")
plotter.add_mesh(pv.Cylinder(direction=[0,1,0],height=20))
plotter.view_yz()
plotter.camera.Zoom(5)
plotter.camera_set = True

plotter.subplot(2,0)
plotter.add_text("Group 2")
plotter.add_mesh(pv.ParametricCatalanMinimal(), show_edges=False, color="tan")
plotter.view_isometric()
plotter.camera.Zoom(2)
plotter.camera_set = True

plotter.subplot(2,1)
plotter.add_text("Group 3")
plotter.add_mesh(examples.load_uniform(), show_edges=True)

plotter.subplot(1,3)
plotter.add_text("Group 4")
plotter.add_mesh(examples.load_globe())

plotter.subplot(4,3)
plotter.add_text("Group 5")
plotter.add_mesh(pv.Cube(), show_edges=True, color="tan")

plotter.subplot(1,1)
plotter.add_text("Cell (1,1)")
sphere = pv.Sphere()
plotter.add_mesh(sphere, scalars=sphere.points[:, 2])
plotter.add_scalar_bar("Z")
plotter.add_axes(interactive=True)

plotter.subplot(1,2)
plotter.add_text("Cell (1,2)")
plotter.add_mesh(pv.Cone(), show_edges=True)

plotter.subplot(4,0)
plotter.add_text("Cell (4,0)")
plotter.add_mesh(examples.load_airplane(), show_edges=False)

# Display the window
plotter.show()