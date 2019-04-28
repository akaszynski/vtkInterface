"""
Streamlines
~~~~~~~~~~~

Integrate a vector field to generate streamlines.
"""
################################################################################
# This example generates streamlines of blood velocity. An isosurface of speed
# provides context. The starting positions for the streamtubes were determined
# by experimenting with the data.

# sphinx_gallery_thumbnail_number = 1
import vtki
from vtki import examples

################################################################################
# Download a sample dataset containing a vector field that can be integrated.

mesh = examples.download_carotid()



################################################################################
# Run the stream line filtering algorithm.

streamlines, src = mesh.streamlines(return_source=True, max_time=100.0,
                           initial_step_length=2., terminal_speed=0.1,
                           n_points=25, source_radius=2.0,
                           source_center=(133.1, 116.3, 5.0) )

################################################################################
# Display the results! Please note that because this dataset's velocity field
# was measured with low resolution, many streamlines travel outside the artery.

p = vtki.Plotter(notebook=1)
p.add_mesh(mesh.outline(), color='k')
p.add_mesh(streamlines.tube(radius=0.15))
p.add_mesh(src)
p.add_mesh(mesh.contour([160]).wireframe(),
           color='grey', opacity=0.25)
p.camera_position = [(182., 177., 50),
                     (139, 105, 19),
                     (-0.2, -0.2, 1)]
p.show()


################################################################################
# Here is another example of blood flow:
mesh = examples.download_blood_vessels().cell_data_to_point_data()
mesh.set_active_scalar('velocity')
streamlines, src = mesh.streamlines(return_source=True, source_radius=10,
                           source_center=(92.46, 74.37, 135.5) ,)


################################################################################
boundary = mesh.decimate_boundary().wireframe()

p = vtki.Plotter(notebook=1)
p.add_mesh(streamlines.tube(radius=0.2), ligthing=False)
p.add_mesh(src)
p.add_mesh(boundary, color='grey', opacity=0.25)
p.camera_position = [(10, 9.5, -43),
                     (87.0, 73.5, 123.0),
                     (-0.5, -0.7, 0.5)]
p.show()
