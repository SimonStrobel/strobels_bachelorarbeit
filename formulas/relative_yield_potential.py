"""This file contains the formula for the relative yield potential."""

# Orientierungen (Spalten) in Grad:
orientations = [
    -90,
    -75,
    -60,
    -45,
    -30,
    -15,
    0,
    15,
    30,
    45,
    60,
    75,
    90,
    105,
    120,
    135,
    150,
    165,
    180,
]

# Neigungen (Zeilen) in Grad:
tilt_angles = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]

data = [
    # Neigung = 0°
    [84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84],
    # Neigung = 10°
    [83, 85, 87, 89, 90, 91, 91, 91, 90, 89, 87, 85, 83, 81, 79, 77, 76, 75, 75],
    # Neigung = 20°
    [82, 86, 90, 92, 95, 96, 96, 96, 94, 92, 89, 85, 81, 77, 73, 70, 67, 66, 65],
    # Neigung = 30°
    [81, 86, 90, 94, 97, 99, 99, 98, 96, 93, 89, 84, 79, 74, 68, 63, 59, 57, 56],
    # Neigung = 40°
    [78, 84, 90, 94, 97, 100, 100, 99, 97, 93, 88, 82, 76, 69, 63, 56, 51, 48, 47],
    # Neigung = 50°
    [74, 81, 87, 92, 96, 98, 99, 97, 95, 91, 85, 79, 72, 65, 57, 50, 44, 40, 39],
    # Neigung = 60°
    [70, 77, 83, 88, 92, 94, 95, 94, 91, 87, 81, 75, 68, 60, 52, 45, 38, 33, 31],
    # Neigung = 70°
    [64, 71, 77, 83, 86, 89, 89, 88, 85, 81, 75, 69, 62, 54, 46, 39, 32, 27, 26],
    # Neigung = 80°
    [57, 64, 70, 75, 79, 81, 81, 80, 77, 73, 68, 62, 55, 48, 40, 33, 27, 23, 21],
    # Neigung = 90°
    [50, 56, 62, 66, 69, 70, 71, 70, 68, 64, 60, 54, 48, 41, 34, 28, 23, 19, 17],
]
building_matrix = {}
for i, tilt in enumerate(tilt_angles):
    building_matrix[tilt] = {}
    for j, ori in enumerate(orientations):
        building_matrix[tilt][ori] = data[i][j]


def get_relative_yield(orientation: int, tilt: int) -> float:
    """This function returns the relative yield potential for a given orientation and tilt.

    Args:
        orientation (int): The orientation in degrees.
        tilt (int): The tilt in degrees.

    Returns:
        float: The relative yield potential.
    """
    return building_matrix[tilt][orientation]
