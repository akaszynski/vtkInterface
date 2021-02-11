"""These classes hold methods to apply general filters to any data type.

By inheriting these classes into the wrapped VTK data structures, a user
can easily apply common filters in an intuitive manner.

Example
-------
>>> import pyvista
>>> from pyvista import examples
>>> dataset = examples.load_uniform()

>>> # Threshold
>>> thresh = dataset.threshold([100, 500])

>>> # Slice
>>> slc = dataset.slice()

>>> # Clip
>>> clp = dataset.clip(invert=True)

>>> # Contour
>>> iso = dataset.contour()

"""

import numpy as np
import vtk

import pyvista
from pyvista.utilities import (abstract_class)
from .algorithm import _get_output
from .datasetfilters import DataSetFilters


@abstract_class
class StructuredGridFilters(DataSetFilters):
    """An internal class to manage filters/algorithms for structured grid datasets."""

    def extract_subset(dataset, voi, rate=(1, 1, 1), boundary=False):
        """Select piece (e.g., volume of interest).

        To use this filter set the VOI ivar which are i-j-k min/max indices
        that specify a rectangular region in the data. (Note that these are
        0-offset.) You can also specify a sampling rate to subsample the
        data.

        Typical applications of this filter are to extract a slice from a
        volume for image processing, subsampling large volumes to reduce data
        size, or extracting regions of a volume with interesting data.

        Parameters
        ----------
        voi : tuple(int)
            Length 6 iterable of ints: ``(xmin, xmax, ymin, ymax, zmin, zmax)``.
            These bounds specify the volume of interest in i-j-k min/max
            indices.

        rate : tuple(int)
            Length 3 iterable of ints: ``(xrate, yrate, zrate)``.
            Default: ``(1, 1, 1)``

        boundary : bool
            Control whether to enforce that the "boundary" of the grid is
            output in the subsampling process. (This only has effect
            when the rate in any direction is not equal to 1). When
            this is on, the subsampling will always include the boundary of
            the grid even though the sample rate is not an even multiple of
            the grid dimensions.  By default this is ``False``.

        Examples
        --------
        Split a grid in half.

        >>> import numpy as np
        >>> import pyvista
        >>> from pyvista import examples
        >>> grid = examples.load_structured()
        >>> voi_1 = grid.extract_subset([0, 80, 0, 40, 0, 1], boundary=True)
        >>> voi_2 = grid.extract_subset([0, 80, 40, 80, 0, 1], boundary=True)

        For fun, add the two grids back together and show they are
        identical to the original grid.

        >>> joined = voi_1.concatenate(voi_2, axis=1)
        >>> assert np.allclose(grid.points, joined.points)
        """
        alg = vtk.vtkExtractGrid()
        alg.SetVOI(voi)
        alg.SetInputDataObject(dataset)
        alg.SetSampleRate(rate)
        alg.SetIncludeBoundary(boundary)
        alg.Update()
        return _get_output(alg)

    def concatenate(dataset, other, axis, tolerance=0.0):
        """Concatenate a structured grids to this grid.

        Joins structured grids into a single structured grid.
        Grids must be of compatible dimension, and must be coincident
        along the seam. Grids must have the same point and cell data.
        Field data is ignored.

        Parameters
        ----------
        other : pyvista.StructuredGrid
            Structured grid to concatenate.

        axis : int
            Axis along which to concatenate.

        tolerance : float
            Tolerance for point coincidence along joining seam.

        Returns
        --------
        pyvista.StructuredGrid
            Concatenated grid.

        Examples
        --------
        Split a grid in half and join them.

        >>> import numpy as np
        >>> import pyvista
        >>> from pyvista import examples
        >>> grid = examples.load_structured()
        >>> voi_1 = grid.extract_subset([0, 80, 0, 40, 0, 1], boundary=True)
        >>> voi_2 = grid.extract_subset([0, 80, 40, 80, 0, 1], boundary=True)
        >>> joined = voi_1.concatenate(voi_2, axis=1)
        >>> print(grid.dimensions, 'same as', joined.dimensions)
        [80, 80, 1] same as [80, 80, 1]
        """
        if axis > 2:
            raise RuntimeError('Concatenation axis must be <= 2.')

        # check dimensions are compatible
        for i, (dim1, dim2) in enumerate(zip(dataset.dimensions,
                                             other.dimensions)):
            if i == axis:
                continue
            if dim1 != dim2:
                raise RuntimeError('StructuredGrids with dimensions %s and %s '
                                   'are not compatible.'
                                   % (dataset.dimensions, other.dimensions))

        # check point/cell variables are the same
        if not set(dataset.point_arrays.keys()) == \
               set(other.point_arrays.keys()):
            raise RuntimeError('Grid to concatenate has different point array names.')
        if not set(dataset.cell_arrays.keys()) == \
               set(other.cell_arrays.keys()):
            raise RuntimeError('Grid to concatenate has different cell array names.')

        # check that points are coincident (within tolerance) along seam
        if not np.allclose(np.take(dataset.points_matrix, indices=-1, axis=axis),
                           np.take(other.points_matrix, indices=0, axis=axis),
                           atol=tolerance):
            raise RuntimeError('Grids cannot be joined along axis %d, as points '
                               'are not coincident within tolerance of %f.'
                               % (axis, tolerance))

        # slice to cut off the repeated grid face
        slice_spec = [slice(None, None, None)] * 3
        slice_spec[axis] = slice(0, -1, None)

        # concatenate points, cutting off duplicate
        new_points = np.concatenate((dataset.points_matrix[slice_spec],
                                     other.points_matrix), axis=axis)

        # concatenate point arrays, cutting off duplicate
        new_point_data = {}
        for name, point_array in dataset.point_arrays.items():
            arr_1 = dataset._reshape_point_array(point_array)
            arr_2 = other._reshape_point_array(other.point_arrays[name])
            if not np.array_equal(np.take(arr_1, indices=-1, axis=axis),
                                  np.take(arr_2, indices=0, axis=axis)):
                raise RuntimeError('Grids cannot be joined along axis %d, as field '
                                   '`%s` is not identical along the seam.'
                                   % (axis, name))
            new_point_data[name] = np.concatenate((arr_1[slice_spec], arr_2),
                                                  axis=axis).ravel(order='F')

        new_dims = np.array(dataset.dimensions)
        new_dims[axis] += other.dimensions[axis] - 1

        # concatenate cell arrays
        new_cell_data = {}
        for name, cell_array in dataset.cell_arrays.items():
            arr_1 = dataset._reshape_cell_array(cell_array)
            arr_2 = other._reshape_cell_array(other.cell_arrays[name])
            new_cell_data[name] = np.concatenate((arr_1, arr_2),
                                                 axis=axis).ravel(order='F')

        # assemble output
        joined = pyvista.StructuredGrid()
        joined.dimensions = list(new_dims)
        joined.points = new_points.reshape((-1, 3), order='F')
        joined.point_arrays.update(new_point_data)
        joined.cell_arrays.update(new_cell_data)

        return joined
