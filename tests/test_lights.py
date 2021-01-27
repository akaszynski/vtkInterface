import math

import numpy as np
import pytest
import vtk

import pyvista
from pyvista.plotting import system_supports_plotting

# TODO: invalid cases, once checks are in place

def test_init():
    position = (1, 1, 1)
    color = (0.5, 0.5, 0.5)
    light_type = 'headlight'
    light = pyvista.Light(position=position, color=color, light_type=light_type)
    assert isinstance(light, pyvista.Light)
    assert light.position == position
    assert light.ambient_color == color
    assert light.diffuse_color == color
    assert light.specular_color == color
    assert light.light_type == light.HEADLIGHT

    # check repr too
    assert repr(light) is not None


def test_colors():
    light = pyvista.Light()

    color = (0, 1, 0)
    light.diffuse_color = color
    assert light.diffuse_color == color
    color = (0, 0, 1)
    light.specular_color = color
    assert light.specular_color == color
    color = (1, 0, 0)
    light.ambient_color = color
    assert light.ambient_color == color

    # test whether strings raise but don't test the result
    for valid in 'white', 'r', '#c0ffee':
        light.diffuse_color = valid
        light.specular_color = valid
        light.ambient_color = valid
    with pytest.raises(ValueError):
        light.diffuse_color = 'invalid'
    with pytest.raises(ValueError):
        light.specular_color = 'invalid'
    with pytest.raises(ValueError):
        light.ambient_color = 'invalid'


def test_positioning():
    light = pyvista.Light()

    position = (1, 1, 1)
    light.position = position
    assert light.position == position
    # with no transformation matrix this is also the world position
    assert light.world_position == position

    focal_point = (2, 2, 2)
    light.focal_point = focal_point
    assert light.focal_point == focal_point
    # with no transformation matrix this is also the world focal point
    assert light.world_focal_point == focal_point

    elev, azim = (45, 30)
    expected_position = (0.5 / math.sqrt(2),
                         1 / math.sqrt(2),
                         math.sqrt(3) / (2 * math.sqrt(2)))  # TODO: fix this style
    light.positional = True
    light.set_direction_angle(elev, azim)
    assert not light.positional
    assert light.focal_point == (0, 0, 0)
    assert all(math.isclose(coord_have, coord_expect) for coord_have, coord_expect
               in zip(light.position, expected_position))  # TODO: fix this style

    with pytest.raises(AttributeError):
        light.world_position = position
    with pytest.raises(AttributeError):
        light.world_focal_point = focal_point


def test_transforms():
    position = (1, 2, 3)
    focal_point = (4, 5, 6)
    light = pyvista.Light(position=position)
    light.focal_point = focal_point

    trans_array = np.arange(4 * 4).reshape(4, 4)
    trans_matrix = pyvista.vtkmatrix_from_array(trans_array)

    assert light.transform_matrix is None
    light.transform_matrix = trans_array
    assert isinstance(light.transform_matrix, vtk.vtkMatrix4x4)
    array = pyvista.array_from_vtkmatrix(light.transform_matrix)
    assert np.array_equal(array, trans_array)
    light.transform_matrix = trans_matrix
    matrix = light.transform_matrix
    assert all(matrix.GetElement(i, j) == trans_matrix.GetElement(i, j)
               for i in range(4) for j in range(4))

    linear_trans = trans_array[:-1, :-1]
    shift = trans_array[:-1, -1]
    assert light.position == position
    assert np.allclose(light.world_position, linear_trans @ position + shift)
    assert light.focal_point == focal_point
    assert np.allclose(light.world_focal_point, linear_trans @ focal_point + shift)

    with pytest.raises(ValueError):
        light.transform_matrix = 'invalid'


def test_intensity():
    light = pyvista.Light()

    intensity = 0.5
    light.intensity = intensity
    assert light.intensity == intensity


def test_switch_state():
    light = pyvista.Light()

    light.switch_on()
    assert light.on
    light.switch_off()
    assert not light.on
    light.on = False
    assert not light.on


def test_positional():
    light = pyvista.Light()

    # default is directional light
    assert not light.positional
    light.positional = True
    assert light.positional
    light.positional = False
    assert not light.positional


def test_shape():
    light = pyvista.Light()

    exponent = 1.5
    light.exponent = exponent
    assert light.exponent == exponent

    cone_angle = 45
    light.cone_angle = cone_angle
    assert light.cone_angle == cone_angle

    attenuation_values = (3, 2, 1)
    light.attenuation_values = attenuation_values
    assert light.attenuation_values == attenuation_values

    shadow_attenuation = 0.5
    light.shadow_attenuation = shadow_attenuation
    assert light.shadow_attenuation == shadow_attenuation


@pytest.mark.parametrize(
    'int_code,enum_code',
    [
        (1, pyvista.Light.HEADLIGHT),
        (2, pyvista.Light.CAMERA_LIGHT),
        (3, pyvista.Light.SCENE_LIGHT),
    ]
)
def test_type_properties(int_code, enum_code):
    light = pyvista.Light()

    # test that the int and enum codes match up
    assert int_code == enum_code

    # test that both codes work
    light.light_type = int_code
    assert light.light_type == int_code
    light.light_type = enum_code
    assert light.light_type == enum_code


def test_type_setters():
    light = pyvista.Light()

    light.set_headlight()
    assert light.is_headlight
    light.set_camera_light()
    assert light.is_camera_light
    light.set_scene_light()
    assert light.is_scene_light


def test_type_invalid():
    with pytest.raises(TypeError):
        light = pyvista.Light(light_type=['invalid'])
    with pytest.raises(ValueError):
        light = pyvista.Light(light_type='invalid')

    light = pyvista.Light()

    with pytest.raises(TypeError):
        light.light_type = ['invalid']


def test_from_vtk():
    vtk_light = vtk.vtkLight()

    # pyvista attr -- value -- vtk name triples:
    configuration = [
        ('light_type', pyvista.Light.CAMERA_LIGHT, 'SetLightType'),  # resets transformation!
        ('position', (1, 1, 1), 'SetPosition'),
        ('focal_point', (2, 2, 2), 'SetFocalPoint'),
        ('ambient_color', (1, 0, 0), 'SetAmbientColor'),
        ('diffuse_color', (0, 1, 0), 'SetDiffuseColor'),
        ('specular_color', (0, 0, 1), 'SetSpecularColor'),
        ('intensity', 0.5, 'SetIntensity'),
        ('on', False, 'SetSwitch'),
        ('positional', True, 'SetPositional'),
        ('exponent', 1.5, 'SetExponent'),
        ('cone_angle', 45, 'SetConeAngle'),
        ('attenuation_values', (3, 2, 1), 'SetAttenuationValues'),
        ('shadow_attenuation', 0.5, 'SetShadowAttenuation'),
    ]

    # set the vtk light
    for _, value, vtkname in configuration:
        vtk_setter = getattr(vtk_light, vtkname)
        vtk_setter(value)
    light = pyvista.Light.from_vtk(vtk_light)
    for pvname, value, _ in configuration:
        assert getattr(light, pvname) == value

    # invalid case
    with pytest.raises(TypeError):
        pyvista.Light.from_vtk('invalid')
    with pytest.raises(TypeError):
        pyvista.Light('invalid')