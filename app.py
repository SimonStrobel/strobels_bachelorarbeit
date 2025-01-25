"""This script creates a Streamlit app for the Solar Roof Calculator."""

import streamlit as st

from formulas.annual_solar_yield import annual_solar_yield
from formulas.relative_yield_potential import get_relative_yield
from formulas.roof_areas_scheffler import (
    gable_roof_area_scheffler,
    pitched_roof_area_scheffler_one,
    pitched_roof_area_scheffler_two,
    flat_roof_area_scheffler,
)
from formulas.roof_areas_tum import (
    gable_roof_area_tum,
    pitched_roof_area_tum,
    flat_roof_area_tum,
)

# -------------------------------------------------
# Title and General Description
# -------------------------------------------------
st.set_page_config(page_title="Solar Roof Calculator", layout="centered")
st.title("Solar Roof Calculator by Simon Strobel")
st.markdown(
    """
Welcome to the **Solar Roof Calculator**. Use the tabs below to:
1. Compute **roof areas** using either *Scheffler* or *TUM* formulas.
2. Estimate the **Annual Solar Yield** from a given roof area.
"""
)


# -------------------------------------------------
# Tabs
# -------------------------------------------------
tab_scheffler, tab_tum, tab_solar_yield, tab_relative_yield_potential = st.tabs(
    [
        "Scheffler Roof Area",
        "TUM Roof Area",
        "Annual Solar Yield",
        "Relative Yield Potential",
    ]
)


# -------------------------------------------------
# Scheffler Roof Area Tab
# -------------------------------------------------
with tab_scheffler:
    st.header("Scheffler Roof Area")

    # User Inputs
    roof_type = st.selectbox(
        "Select Roof Type",
        ["Gable", "Pitched - Variation 1", "Pitched - Variation 2", "Flat"],
        key="scheffler_roof_type",
    )

    building_area = st.number_input(
        "Building area (m²)",
        min_value=0.0,
        value=100.0,
        step=10.0,
        key="scheffler_building_area",
    )

    if roof_type == "Gable":
        roof_area = gable_roof_area_scheffler(building_area)

    elif roof_type == "Pitched - Variation 1":
        roof_area = pitched_roof_area_scheffler_one(building_area)

    elif roof_type == "Pitched - Variation 2":
        roof_pitch = st.number_input(
            "Roof pitch (radians)",
            min_value=0.0,
            value=0.3,
            step=0.05,
            key="scheffler_roof_pitch",
        )
        roof_area = pitched_roof_area_scheffler_two(building_area, roof_pitch)

    elif roof_type == "Flat":
        st.warning(
            "No formula was provided for the flat roof (Scheffler). Returning 0."
        )
        roof_area = flat_roof_area_scheffler(building_area)

    else:
        st.error("Invalid roof type selected. Please choose a valid option.")

    # Displays Result
    st.subheader("Calculated Scheffler Roof Area")
    st.info(f"**Roof area:** {roof_area:.2f} m²")


# -------------------------------------------------
# TUM Roof Area Tab
# -------------------------------------------------
with tab_tum:
    st.header("TUM Roof Area")

    # User Inputs
    roof_type = st.selectbox(
        "Select Roof Type",
        ["Gable", "Pitched - Variation 1", "Pitched - Variation 2", "Flat"],
        key="tum_roof_type",
    )

    building_area_tum = st.number_input(
        "Building area (m²)",
        min_value=0.0,
        value=120.0,
        step=10.0,
        key="tum_building_area",
    )

    roof_area_tum = 0.0

    if roof_type == "Gable":
        reduction_factor = st.number_input(
            "Reduction factor (0 - 1)",
            min_value=0.0,
            max_value=1.0,
            value=1.0,
            step=0.1,
            key="tum_reduction_factor_gable",
        )
        alpha = st.number_input(
            "Alpha (roof angle in radians)",
            min_value=0.0,
            value=0.3,
            step=0.05,
            key="tum_alpha",
        )
        roof_area_tum = gable_roof_area_tum(building_area_tum, reduction_factor, alpha)

    elif roof_type == "Pitched - Variation 1":
        reduction_factor = st.number_input(
            "Reduction factor (0 - 1)",
            min_value=0.0,
            max_value=1.0,
            value=1.0,
            step=0.1,
            key="tum_reduction_factor_pitched1",
        )
        roof_pitch = st.number_input(
            "Roof pitch (radians)",
            min_value=0.0,
            value=0.3,
            step=0.05,
            key="tum_roof_pitch_pitched1",
        )
        roof_area_tum = pitched_roof_area_tum(
            building_area_tum, reduction_factor, roof_pitch
        )

    elif roof_type == "Pitched - Variation 2":
        st.info("Using the TUM pitched roof formula for Variation 2 as well.")
        reduction_factor = st.number_input(
            "Reduction factor (0 - 1)",
            min_value=0.0,
            max_value=1.0,
            value=1.0,
            step=0.1,
            key="tum_reduction_factor_pitched2",
        )
        roof_pitch = st.number_input(
            "Roof pitch (radians)",
            min_value=0.0,
            value=0.3,
            step=0.05,
            key="tum_roof_pitch_pitched2",
        )
        roof_area_tum = pitched_roof_area_tum(
            building_area_tum, reduction_factor, roof_pitch
        )

    elif roof_type == "Flat":
        roof_area_tum = flat_roof_area_tum(building_area_tum)

    else:
        st.error("Invalid roof type selected. Please choose a valid option.")

    # Displays Result
    st.subheader("Calculated TUM Roof Area")
    st.info(f"**Roof area:** {roof_area_tum:.2f} m²")


# -------------------------------------------------
# Annual Solar Yield Tab
# -------------------------------------------------
with tab_solar_yield:
    st.header("Annual Solar Yield")

    st.latex(
        r"""
    \text{Annual Solar Yield} 
    = \text{Roof Area} \times \text{Solar Irradiation} 
    \times \text{Module Efficiency} \times \text{Relative Yield}
    """
    )

    # Inputs
    roof_area_for_yield = st.number_input(
        "Roof area (m²)", min_value=0.0, value=80.0, step=10.0, key="solar_roof_area"
    )
    solar_irradiation = st.number_input(
        "Solar irradiation (kWh/m²)",
        min_value=0.0,
        value=1000.0,
        step=50.0,
        key="solar_irradiation",
    )
    module_efficiency = st.number_input(
        "Module efficiency (0 - 1)",
        min_value=0.0,
        max_value=1.0,
        value=0.15,
        step=0.01,
        key="solar_efficiency",
    )
    relative_yield = st.number_input(
        "Relative yield potential",
        min_value=0.0,
        max_value=2.0,
        value=1.0,
        step=0.1,
        key="solar_relative_yield",
    )

    if st.button("Compute Annual Solar Yield"):
        yield_result = annual_solar_yield(
            roof_area=roof_area_for_yield,
            solar_irradiation=solar_irradiation,
            module_efficiency=module_efficiency,
            relative_yield=relative_yield,
        )
        st.success(f"**Estimated annual solar yield:** {yield_result:.2f} kWh")
    else:
        st.info("Enter values and click the button to calculate the solar yield.")


# -------------------------------------------------
# Relative Yield Potential Tab
# -------------------------------------------------

with tab_relative_yield_potential:
    st.header("Relative Yield Potential")

    orientation = st.number_input(
        "Orientation (degrees)",
        min_value=-90,
        max_value=180,
        value=0,
        step=15,
        key="orientation",
    )
    tilt = st.number_input(
        "Tilt (degrees)", min_value=0, max_value=90, value=0, step=10, key="tilt"
    )

    if st.button("Get Relative Yield"):
        yield_result = get_relative_yield(orientation, tilt)
        st.success(f"**Relative yield potential:** {yield_result:.2f}")
    else:
        st.info("Enter values and click the button to calculate the relative yield.")
