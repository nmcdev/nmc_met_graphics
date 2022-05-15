## Brian Blaylock
## April 23, 2020   COVID-19 Era

"""
=================
Unit Converstions
=================

Functions to convert various units

    - K_to_C
    - K_to_F
    - C_to_K
    - C_to_F
    - F_to_C
    - ms_to_mph
    - mm_to_inches
    - Pa_to_hPa

"""
########################################################################
# Longitude
def to_180(lon):
    """
    Wrap longitude from degrees [0, 360] to degrees [-180, 180].

    Parameters
    ----------
    lon : array_like
        Longitude values
    """
    if isinstance(lon, list):
        np.array(lon)
    lon = (lon + 180) % 360 - 180
    return lon


def to_360(lon):
    """
    Wrap longitude from degrees [-180, 180] to degrees [0, 360].

    Parameters
    ----------
    lon : array_like
        Longitude values
    """
    if isinstance(lon, list):
        np.array(lon)
    lon = (lon - 360) % 360
    return lon


# --- Temperature -------------------------------------------------------------
def K_to_C(K):
    """Convert Kelvin to Celsius"""
    return K - 273.15


def K_to_F(K):
    """convert Kelvin to Fahrenheit"""
    return (K - 273.15) * 9 / 5.0 + 32


def C_to_K(T_C):
    """Converts celsius to Kelvin"""
    return T_C + 273.15


def C_to_F(C):
    """Converts Celsius to Fahrenheit"""
    return C * 9 / 5.0 + 32


def F_to_C(F):
    """Convert Fahrenheit to Celsius"""
    return (F - 32) * 5 / 9


# --- Wind --------------------------------------------------------------------
def ms_to_mph(ms):
    """Convert m/s to MPH"""
    return ms * 2.2369


# --- Precipitation -----------------------------------------------------------
def mm_to_inches(mm):
    """Convert mm to inches"""
    return mm * 0.0394


# --- Pressure ----------------------------------------------------------------
def Pa_to_hPa(Pa):
    """Convert pascals to hectopascals (millibars, mb)"""
    return Pa / 100
