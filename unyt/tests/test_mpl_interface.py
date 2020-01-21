"""Test Matplotlib ConversionInterface"""
import numpy as np
import pytest
from unyt._on_demand_imports import _matplotlib, NotAModule
from unyt import s, K, unyt_array, unyt_quantity
from unyt.exceptions import UnitConversionError
from unyt.mpl_interface import MplUnitsCM


check_matplotlib = pytest.mark.skipif(
    isinstance(_matplotlib.pyplot, NotAModule), reason="matplotlib not installed"
)


@pytest.fixture
def ax(scope="module"):
    mpl_units = MplUnitsCM()
    mpl_units.enable()
    fig, ax = _matplotlib.pyplot.subplots()
    yield ax
    _matplotlib.pyplot.close()
    mpl_units.disable()


@check_matplotlib
def test_label(ax):
    x = [0, 1, 2] * s
    y = [3, 4, 5] * K
    ax.plot(x, y)
    expected_xlabel = "$\\left(\\rm{s}\\right)$"
    assert ax.xaxis.get_label().get_text() == expected_xlabel
    expected_ylabel = "$\\left(\\rm{K}\\right)$"
    assert ax.yaxis.get_label().get_text() == expected_ylabel


@check_matplotlib
def test_convert_unit(ax):
    x = [0, 1, 2] * s
    y = [1000, 2000, 3000] * K
    ax.plot(x, y, yunits="Celcius")
    expected = y.to("Celcius")
    line = ax.lines[0]
    original_y_array = line.get_data()[1]
    converted_y_array = line.convert_yunits(original_y_array)
    results = converted_y_array == expected
    assert results.all()


@check_matplotlib
def test_convert_equivalency(ax):
    x = [0, 1, 2] * s
    y = [1000, 2000, 3000] * K
    ax.clear()
    ax.plot(x, y, yunits=("J", "thermal"))
    expected = y.to("J", "thermal")
    line = ax.lines[0]
    original_y_array = line.get_data()[1]
    converted_y_array = line.convert_yunits(original_y_array)
    results = converted_y_array == expected
    assert results.all()


@check_matplotlib
def test_dimensionless(ax):
    x = [0, 1, 2] * s
    y = [3, 4, 5] * K / K
    ax.plot(x, y)
    expected_ylabel = ""
    assert ax.yaxis.get_label().get_text() == expected_ylabel


@check_matplotlib
def test_conversionerror(ax):
    x = [0, 1, 2] * s
    y = [3, 4, 5] * K
    ax.plot(x, y)
    ax.xaxis.callbacks.exception_handler = None
    # Newer matplotlib versions catch our exception and raise a custom
    # ConversionError exception
    try:
        error_type = _matplotlib.units.ConversionError
    except AttributeError:
        error_type = UnitConversionError
    with pytest.raises(error_type):
        ax.xaxis.set_units("V")


@check_matplotlib
def test_ndarray_label(ax):
    x = [0, 1, 2] * s
    y = np.arange(3, 6)
    ax.plot(x, y)
    expected_xlabel = "$\\left(\\rm{s}\\right)$"
    assert ax.xaxis.get_label().get_text() == expected_xlabel
    expected_ylabel = ""
    assert ax.yaxis.get_label().get_text() == expected_ylabel


@check_matplotlib
def test_list_label(ax):
    x = [0, 1, 2] * s
    y = [3, 4, 5]
    ax.plot(x, y)
    expected_xlabel = "$\\left(\\rm{s}\\right)$"
    assert ax.xaxis.get_label().get_text() == expected_xlabel
    expected_ylabel = ""
    assert ax.yaxis.get_label().get_text() == expected_ylabel


@check_matplotlib
def test_errorbar(ax):
    x = unyt_array([8, 9, 10], "cm")
    y = unyt_array([8, 9, 10], "kg")
    y_scatter = [
        unyt_array([0.1, 0.2, 0.3], "kg"),
        unyt_array([0.1, 0.2, 0.3], "kg"),
    ]
    x_lims = (unyt_quantity(5, "cm"), unyt_quantity(12, "cm"))
    y_lims = (unyt_quantity(5, "kg"), unyt_quantity(12, "kg"))

    ax.errorbar(x, y, yerr=y_scatter)
    x_lims = (unyt_quantity(5, "cm"), unyt_quantity(12, "cm"))
    y_lims = (unyt_quantity(5, "kg"), unyt_quantity(12, "kg"))
    ax.set_xlim(*x_lims)
    ax.set_ylim(*y_lims)


@check_matplotlib
def test_hist2d(ax):
    x = np.random.normal(size=50000) * s
    y = 3 * x + np.random.normal(size=50000) * s
    ax.hist2d(x, y, bins=(50, 50))


@check_matplotlib
def test_imshow(ax):
    data = np.reshape(np.random.normal(size=10000), (100, 100))
    ax.imshow(data, vmin=data.min(), vmax=data.max())


@check_matplotlib
def test_hist(ax):
    data = np.random.normal(size=10000) * s
    bin_edges = np.linspace(data.min(), data.max(), 50)
    ax.hist(data, bins=bin_edges)
