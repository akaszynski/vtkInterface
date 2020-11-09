"""Image regression module"""
import vtk
from vtk.util.numpy_support import numpy_to_vtk, vtk_to_numpy
import numpy as np


# def _window_to_image(pl):
#     """Older method using potentially slower vtkWindowToImageFilter"""
#     ifilter = vtk.vtkWindowToImageFilter()
#     ifilter.SetInput(pl.ren_win)
#     ifilter.ReadFrontBufferOff()
#     if pl.image_transparent_background:
#         ifilter.SetInputBufferTypeToRGBA()
#     else:
#         ifilter.SetInputBufferTypeToRGB()
#     ifilter.Update()
#     return ifilter.GetOutput()



def wrap_image_array(arr):
    """Wrap a numpy array as a pyvista.UniformGrid.

    Parameters
    ----------
    arr : np.ndarray
        A ``np.uint8`` ``(X, Y, (3 or 4)`` array.  For example
        ``(768, 1024, 3)``.

    """
    if arr.ndim != 3:
        raise ValueError('Expecting a X by Y by (3 or 4) array')
    if arr.shape[2] not in [3, 4]:
        raise ValueError('Expecting a X by Y by (3 or 4) array')
    if arr.dtype != np.uint8:
        raise ValueError('Expecting a np.uint8 array')

    from pyvista import wrap
    img = vtk.vtkImageData()
    img.SetDimensions(arr.shape[1], arr.shape[0], 1)
    wrap_img = wrap(img)
    wrap_img.point_arrays['PNGImage'] = arr[::-1].reshape(-1, arr.shape[2])
    return wrap_img


def image_from_window(ren_win, as_vtk=False, ignore_alpha=False):
    """Extract the image from the render window as an array"""
    width, height = ren_win.GetSize()
    arr = vtk.vtkUnsignedCharArray()
    ren_win.GetRGBACharPixelData(0, 0, width - 1, height - 1, 0, arr)
    data = vtk_to_numpy(arr).reshape(height, width, -1)[::-1]
    if ignore_alpha:
        data = data[:, :, :-1]
    if as_vtk:
        return wrap_image_array(data)
    return data


# def compare_plotters(pl1, pl2):
#     img_diff = vtk.vtkImageDifference()
#     img_diff.SetInputData(image_from_window(pl1, ignore_alpha=True))
#     img_diff.SetImageData(image_from_window(pl2, ignore_alpha=True))
#     img_diff.Update()
#     return img_diff.GetError()


def compare_images(im1, im2, threshold=1, use_vtk=False):
    """Compare two different images of the same size.

    Parameters
    ----------
    im1 : filename, np.ndarray, vtkRenderWindow, or vtkImageData
        Render window, numpy array representing the output of a render
        window, or ``vtkImageData``

    im2 : filename, np.ndarray, vtkRenderWindow, or vtkImageData
        Render window, numpy array representing the output of a render
        window, or ``vtkImageData``

    threshold : int
        Threshold tolerance for pixel differences.  This should be
        greater than 0, otherwise it will always return an error, even
        on identical images.

    fast : bool
        Compute the mean pixel error over the entire image using
        numpy.  The difference between pixel is calculated for each
        RGB channel, summed, and then divided by the number of pixels.
        This is faster than using ``vtk.vtkImageDifference`` but
        potentially less accurate.

    Returns
    -------
    error : float
        Total error between the images if using ``use_vtk``, and the
        mean pixel error when ``use_vtk=False``.

    """
    from pyvista import wrap, UniformGrid, read, Plotter

    def to_img(img):
        if isinstance(img, UniformGrid):  # pragma: no cover
            return img
        elif isinstance(img, vtk.vtkImageData):
            return wrap(img)
        elif isinstance(img, str):
            return read(img)
        elif isinstance(img, np.ndarray):
            return wrap_image_array(img)
        elif isinstance(img, Plotter):
            if img._first_time:  # must be rendered first else segfault
                img._on_first_render_request()
                img.render()
            return image_from_window(img.ren_win, True, ignore_alpha=True)
        else:
            raise TypeError(f'Unsupported data type {type(img)}.  Should be '
                            'Either a np.ndarray, vtkRenderWindow, or vtkImageData')

    im1 = to_img(im1)
    im2 = to_img(im2)

    if use_vtk:
        img_diff = vtk.vtkImageDifference()
        img_diff.SetThreshold(threshold)
        img_diff.SetInputData(im1)
        img_diff.SetImageData(im2)
        img_diff.AllowShiftOff()  # vastly increases compute time
        img_diff.AveragingOff()  # increases compute time
        img_diff.Update()
        return img_diff.GetError()

    # otherwise, simply compute the mean pixel differnce
    diff = np.abs(im1.point_arrays[0] - im2.point_arrays[0])
    return np.sum(diff) / im1.point_arrays[0].shape[0]
    
