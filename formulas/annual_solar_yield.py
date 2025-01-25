"""This file contains the annual solar yield formula."""


def annual_solar_yield(
    roof_area: float,
    solar_irradiation: float,
    module_efficiency: float,
    relative_yield: float,
) -> float:
    """Computes the annual solar yield (Stromertrag pro Jahr) given:

    According to:
        Stromertrag = (Dachfläche) * (Solare Einstrahlung) * (Wirkungsgrad) * (relatives Ertragspotential)

    Args:
        roof_area (float): The area of the roof in square meters.
        solar_irradiation (float): The solar irradiation in kWh/m^2.
        module_efficiency (float): The efficiency of the solar module.
        relative_yield (float): The relative yield potential.

    Returns:
        float: The annual solar yield in kWh.
    """
    return roof_area * solar_irradiation * module_efficiency * relative_yield
