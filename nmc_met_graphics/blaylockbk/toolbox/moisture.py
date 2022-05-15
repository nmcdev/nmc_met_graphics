## Brian Blaylock
## March 9, 2020

"""
=====================
Moisture Calculations
=====================

Calculations for moisture variables

    - TMP_RH_to_DPT

"""

import numpy as np


def TMP_RH_to_DPT(Tc, RH, method="Bolton"):
    """
    Convert Temperature (Celsius) and RH (%) to Dew Point (Celsius).

    Based on the Magnus formula (https://en.wikipedia.org/wiki/Dew_point)
        gamma = ln(RH / 100) + ((b*T) / (c+T))
        Td = c*gamma / (b-gamma)

        Where `T` is temperature in Celsius and `RH` is relative humidty in percent.
        Values of `b` and `c` depend on your approximation method.

    Parameters
    ----------
    Tc : int, float, or array_like
        Temperature in degrees Celsius
    RH : type must match `Tc`
        Relative Humidity in percent (range from 0-100%)
    method : {'Bolton', 'Sonntag'}
        Parameter values to use for b and c when computing dew point temperature.
        Default is constants from Bolton 1990. a=17.67; c=243.5 Celsius.

    Resources
    ---------
    - https://en.wikipedia.org/wiki/Dew_point#cite_ref-14
    - http://bmcnoldy.rsmas.miami.edu/humidity_conversions.pdf
    - https://www.cpc.ncep.noaa.gov/products/wesley/wgrib2/rpn_non-trivial_example.html
    - https://calcunation.com/calculator/dew-point.php
    - http://irtfweb.ifa.hawaii.edu/~tcs3/tcs3/Misc/Dewpoint_Calculation_Humidity_Sensor_E.pdf
    """
    assert np.all(RH <= 101), "Found RH > 101 %. All RH values must be 0-100%"
    assert (
        RH.max() > 1
    ), "All RH are < 1. Check your units: All RH values must be 0-100%"
    assert np.all(
        Tc < 273.15
    ), "Found a temperature > 273.15. `Tc` must be in degrees Celisus, not Kelvin"
    assert np.all(
        Tc < 50
    ), "Found a temperature > 50. `Tc` must be in degrees Celisus, not Farhenheit"

    # Constants are in order (b, c)
    # Where b is unitless, and c is in degrees C
    constants = {}
    constants["Bolton"] = (17.67, 243.5)  # Bolton 1980, Monthly Weather Review
    constants["Sonntag"] = (17.62, 243.12)  # Sonntag 1990

    b, c = constants[method]
    gamma = np.log(RH / 100) + (b * Tc) / (c + Tc)
    Td = c * gamma / (b - gamma)
    return Td
