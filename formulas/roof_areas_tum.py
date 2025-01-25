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
    building_area: float, reduction_factor: float, roof_pitch: float
) -> float:
    """Computes the flat roof area (Dachfläche) given the building area (Gebäudegrundfläche).

    According to:
      roof_area =  building_area * 0.5 * reduction_factor * 1/cos(alpha)

    Args:
        building_area (float): The area of the building in square meters.
        reduction_factor (float): The reduction factor.
        roof_pitch (float): The angle of the roof.

    Returns:
        float: The flat roof area in square meters.
    """
    roof_pitch_rad = radians(roof_pitch)
    return building_area * 0.5 * reduction_factor * 1 / cos(roof_pitch_rad)


def pitched_roof_area_tum(
    building_area: float, reduction_factor: float, roof_pitch: float
) -> float:
    """Computes the pitched roof area (Dachfläche) given the building area (Gebäudegrundfläche).

    According to:
      roof_area =  building_area * reduction_factor * 1/cos(roof_pitch)

    Args:
        building_area (float): The area of the building in square meters.
        reduction_factor (float): The reduction factor.
        roof_pitch (float): The pitch of the roof.

    Returns:
        float: The pitched roof area in square meters.
    """
    roof_pitch_rad = radians(roof_pitch)
    return building_area * reduction_factor * 1 / cos(roof_pitch_rad)
