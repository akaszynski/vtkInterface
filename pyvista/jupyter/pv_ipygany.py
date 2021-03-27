"""Support for the ipygany plotter."""

import warnings

import numpy as np
from IPython import display
from traitlets import Enum


# not to be imported at the init level
try:
    import ipygany
except ImportError:
    raise ImportError('Install ``ipygany`` to use this feature.')

try:
    from ipywidgets import (FloatSlider, FloatRangeSlider, Dropdown, Layout,
                            Select, VBox, HBox, AppLayout, jslink, HTML)
except ImportError:
    raise ImportError('Install ``ipywidgets`` to use this feature.')


from ipygany.vtk_loader import get_ugrid_data
from ipygany.ipygany import _grid_data_to_data_widget
from ipygany import Scene, PolyMesh, Component, IsoColor
from ipygany.colormaps import colormaps

import pyvista as pv


# will not be necessary after
# https://github.com/QuantStack/ipygany/pull/98#issuecomment-799191830
def pyvista_polydata_to_polymesh(obj):
    """Import a mesh from ``pyvista`` or ``vtk``.

    Parameters
    ----------
    obj : pyvista compatible object
        Any object compatible with pyvista.  Includes most ``vtk``
        objects.

    Returns
    -------
    PolyMesh
        ``ipygany.PolyMesh`` object.

    Examples
    --------
    Convert a pyvista mesh to a PolyMesh

    >>> import pyvista as pv
    >>> from ipygany import PolyMesh
    >>> pv_mesh = pv.Sphere()
    >>> mesh = PolyMesh.from_pyvista(pv_mesh)
    >>> mesh
    PolyMesh(data=[Data(components=[Component(array=array([-6.1232343e-17,
    6.1232343e-17, -1.0811902e-01, -2.1497…

    """
    # attempt to wrap non-pyvista objects
    if not pv.is_pyvista_dataset(obj):
        mesh = pv.wrap(obj)
        if not pv.is_pyvista_dataset(mesh):
            raise TypeError(f'Object type ({type(mesh)}) cannot be converted to '
                            'a pyvista dataset')
    else:
        mesh = obj

    # PolyMesh requires vertices and triangles, so we need to
    # convert the mesh to an all triangle polydata
    if not isinstance(obj, pv.PolyData):
        # unlikely case that mesh does not have extract_surface
        if not hasattr(mesh, 'extract_surface'):
            mesh = mesh.cast_to_unstructured_grid()
        surf = mesh.extract_surface()
    else:
        surf = mesh

    # convert to an all-triangular surface
    if surf.is_all_triangles():
        trimesh = surf
    else:
        trimesh = surf.triangulate()

    # finally, pass the triangle vertices to PolyMesh
    triangle_indices = trimesh.faces.reshape(-1, 4)[:, 1:]

    if not triangle_indices.size:
        warnings.warn('Unable to convert mesh to triangular PolyMesh')

    return PolyMesh(
        vertices=trimesh.points,
        triangle_indices=triangle_indices,
        data=_grid_data_to_data_widget(get_ugrid_data(trimesh))
    )


def color_float_to_hex(r, g, b):
    """Convert RGB to hex."""
    def clamp(x):
        x = round(x*255)
        return max(0, min(x, 255))
    return "#{0:02x}{1:02x}{2:02x}".format(clamp(r), clamp(g), clamp(b))


class NotAllTrianglesError(ValueError):
    """Exception when a mesh does not contain all triangles."""

    def __init__(self, message='Mesh must consist of only triangles'):
        """Empty init."""
        ValueError.__init__(self, message)


def check_colormap(cmap):
    """Attempt to convert a colormap to ``ipygany``."""
    if cmap not in colormaps:
        # attempt to matplotlib cmaps to ipygany
        if cmap.capitalize() in colormaps:
            cmap = cmap.capitalize()

    if cmap not in colormaps:
        allowed = ', '.join([f"'{clmp}'" for clmp in colormaps.keys()])
        raise ValueError(f'``cmap`` "{cmap} is not supported by ``ipygany``\n'
                         'Pick from one of the following:\n'
                         + allowed)
    return cmap


def ipygany_obj_from_actor(actor):
    """Convert a vtk actor to a ipygany scene."""
    mapper = actor.GetMapper()
    if mapper is None:
        return
    dataset = mapper.GetInputAsDataSet()
    pmesh = pyvista_polydata_to_polymesh(dataset)
    prop = actor.GetProperty()
    pmesh.default_color = color_float_to_hex(*prop.GetColor())

    # determine if there are active scalars
    scalars_name = mapper.GetArrayName()
    valid_mode = mapper.GetScalarModeAsString() in ['UsePointData', 'UseCellData']
    if valid_mode:
        if not scalars_name:
            scalars_name = dataset.active_scalars_name

        # ensure this is a valid scalar
        if scalars_name in [data.name for data in pmesh.data]:
            mn, mx = mapper.GetScalarRange()
            cmesh = IsoColor(pmesh, input=(scalars_name), min=mn, max=mx)
            if hasattr(mapper, 'cmap'):
                cmap = check_colormap(mapper.cmap)
                cmesh.colormap = colormaps[cmap]
            return cmesh

    return pmesh


def ipygany_camera_from_plotter(plotter):
    """Return an ipygany camera dict from a ``pyvista.Plotter`` object."""
    position, target, up = plotter.camera_position
    # TODO: camera position appears twice as far within ipygany, adjust:

    position = np.array(position, copy=True)
    position -= (position - np.array(target))/2

    return {'position': position.tolist(),
            'target': target,
            'up': up}


def show_ipygany(plotter, return_viewer, height=None, width=None):
    """Show an ipygany scene."""
    # convert each mesh in the plotter to an ipygany scene
    actors = plotter.renderer._actors
    meshes = []
    for actor in actors.values():
        ipygany_obj = ipygany_obj_from_actor(actor)
        if ipygany_obj is not None:
            meshes.append(ipygany_obj)

    bc_color = color_float_to_hex(*plotter.background_color)
    scene = Scene(meshes,
                  background_color=bc_color,
                  camera=ipygany_camera_from_plotter(plotter))

    # optionally size of the plotter
    if height is not None:
        scene.layout.height = f'{height}'
    if width is not None:
        scene.layout.width = f'{width}'

    cbar = None
    if len(plotter.scalar_bars):
        for mesh in meshes:
            if isinstance(mesh, ipygany.IsoColor):
                cbar = ipygany.ColorBar(mesh)
                colored_mesh = mesh
                break

    # Simply return the scene
    if return_viewer:
        return scene

    if cbar is not None:
        # Colormap choice widget
        colormap_dd = Dropdown(
            options=colormaps,
            description='Colormap:'
        )
        jslink((colored_mesh, 'colormap'), (colormap_dd, 'index'))

        # sensible colorbar maximum width, or else it looks bad when
        # window is large.
        cbar.layout.max_width = '500px'

        # Create a slider that will dynamically change the boundaries of the colormap
        # colormap_slider_range = FloatRangeSlider(value=[height_min, height_max],
        #                                          min=height_min, max=height_max,
        #                                          step=(height_max - height_min) / 100.)

        # jslink((colored_mesh, 'range'), (colormap_slider_range, 'value'))

        # create app
        title = HTML(value=f'<h3>{list(plotter.scalar_bars.keys())[0]}</h3>')
        legend = VBox((title, colormap_dd, cbar))
        scene = AppLayout(center=scene,
                          footer=legend,
                          pane_heights=[0, 0, '150px'])

    display.display_html(scene)
