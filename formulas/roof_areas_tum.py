"""This file contains the roof areas formulas according to TUM."""

from math import cos, radians


def flat_roof_area_tum(building_area: float) -> float:
    """Computes the flat roof area (Dachfläche) given the building area (Gebäudegrundfläche).

    According to:
      roof_area =  building_area * 0.5

    Args:
        building_area (float): The area of the building in square meters.

    Returns:
        float: The flat roof area in square meters.
    """
    return building_area * 0.5


def gable_roof_area_tum(
    building_area: float, reduction_factor: float, tilt_angle: float
) -> float:
    """Computes the flat roof area (Dachfläche) given the building area (Gebäudegrundfläche).

    According to:
      roof_area =  building_area * 0.5 * reduction_factor * 1/cos(alpha)

    Args:
        building_area (float): The area of the building in square meters.
        reduction_factor (float): The reduction factor.
        tilt_angle (float): The angle of the roof.

    Returns:
        float: The flat roof area in square meters.
    """
    tilt_angle_rad = radians(tilt_angle)
    return building_area * 0.5 * reduction_factor * 1 / cos(tilt_angle_rad)


def pitched_roof_area_tum(
    building_area: float, reduction_factor: float, tilt_angle: float
) -> float:
    """Computes the pitched roof area (Dachfläche) given the building area (Gebäudegrundfläche).

    According to:
      roof_area =  building_area * reduction_factor * 1/cos(tilt_angle)

    Args:
        building_area (float): The area of the building in square meters.
        reduction_factor (float): The reduction factor.
        tilt_angle (float): The pitch of the roof.

    Returns:
        float: The pitched roof area in square meters.
    """
    tilt_angle_rad = radians(tilt_angle)
    return building_area * reduction_factor * 1 / cos(tilt_angle_rad)
