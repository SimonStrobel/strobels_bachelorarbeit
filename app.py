"""This script creates a Streamlit app for the Solar Roof Calculator.

Docs:
    https://streamlit.io
"""

import streamlit as st
import pandas as pd

from formulas.annual_solar_yield import annual_solar_yield
from formulas.relative_yield_potential import get_relative_yield
from formulas.roof_areas_scheffler import (
    flat_roof_area_scheffler,
    gable_roof_area_scheffler,
    pitched_roof_area_scheffler,
)
from formulas.roof_areas_tum import (
    flat_roof_area_tum,
    gable_roof_area_tum,
    pitched_roof_area_tum,
)


# -------------------------------------------------
# Title and General Description
# -------------------------------------------------
st.set_page_config(page_title="Solar Roof Calculator", layout="wide")
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
(
    tab_scheffler,
    tab_tum,
    tab_solar_yield,
    tab_relative_yield_potential,
    tab_total_electricity_yield,
) = st.tabs(
    [
        "Scheffler Roof Area",
        "TUM Roof Area",
        "Annual Solar Yield",
        "Relative Yield Potential",
        "Total Electricity Yield",
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
        ["Gable", "Pitched", "Flat"],
        key="scheffler_roof_type",
    )

    building_area = st.number_input(
        "Building area (m²)",
        min_value=0.0,
        value=100.0,
        step=10.0,
        key="scheffler_building_area",
    )

    if roof_type == "Flat":
        roof_area = flat_roof_area_scheffler(building_area)

    elif roof_type == "Gable":
        titl_angle = st.number_input(
            "Roof pitch (radians)",
            min_value=0.0,
            value=0.3,
            step=0.05,
            key="scheffler_titl_angle_gable",
        )
        roof_area = gable_roof_area_scheffler(building_area, titl_angle)

    elif roof_type == "Pitched":
        reduction_factor = st.number_input(
            "Reduction factor (0 - 1)",
            min_value=0.0,
            max_value=1.0,
            value=1.0,
            step=0.1,
            key="scheffler_reduction_factor_pitched1",
        )
        titl_angle = st.number_input(
            "Roof pitch (radians)",
            min_value=0.0,
            value=0.3,
            step=0.05,
            key="scheffler_titl_angle_pitched1",
        )
        roof_area = pitched_roof_area_scheffler(
            building_area, reduction_factor, titl_angle
        )

    else:
        st.error("Invalid roof type selected. Please choose a valid option.")

    # Displays Result
    st.subheader("Calculated Scheffler Roof Area")
    st.success(f"**Roof area:** {roof_area:.2f} m²")


# -------------------------------------------------
# TUM Roof Area Tab
# -------------------------------------------------
with tab_tum:
    st.header("TUM Roof Area")

    # User Inputs
    roof_type = st.selectbox(
        "Select Roof Type",
        ["Gable", "Pitched", "Flat"],
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

    if roof_type == "Flat":
        roof_area_tum = flat_roof_area_tum(building_area_tum)

    elif roof_type == "Gable":
        reduction_factor = st.number_input(
            "Reduction factor (0 - 1)",
            min_value=0.0,
            max_value=1.0,
            value=1.0,
            step=0.1,
            key="tum_reduction_factor_gable",
        )
        titl_angle = st.number_input(
            "Roof pitch (radians)",
            min_value=0.0,
            value=0.3,
            step=0.05,
            key="tum_titl_angle_pitched1",
        )
        roof_area_tum = gable_roof_area_tum(
            building_area_tum, reduction_factor, titl_angle
        )

    elif roof_type == "Pitched":
        reduction_factor = st.number_input(
            "Reduction factor (0 - 1)",
            min_value=0.0,
            max_value=1.0,
            value=1.0,
            step=0.1,
            key="tum_reduction_factor_pitched1",
        )
        titl_angle = st.number_input(
            "Roof pitch (radians)",
            min_value=0.0,
            value=0.3,
            step=0.05,
            key="tum_titl_angle_pitched1",
        )
        roof_area_tum = pitched_roof_area_tum(
            building_area_tum, reduction_factor, titl_angle
        )

    else:
        st.error("Invalid roof type selected. Please choose a valid option.")

    # Displays Result
    st.subheader("Calculated TUM Roof Area")
    st.success(f"**Roof area:** {roof_area_tum:.2f} m²")


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


# -------------------------------------------------
# Total Electricity Yield (Excel-Upload)
# -------------------------------------------------
with tab_total_electricity_yield:
    st.header("Total Electricity Yield for Multiple Buildings (from Excel)")

    st.write(
        """
        Upload an Excel file that contains **at least** the following columns:
        - **building**  
        - **building_area**  
        - **roof** (e.g., *mixed*, *pitched*, *flat*, *gable*, etc.)  
        - **tilt_angle** (in degrees)  
        - **orientation** (in degrees; for example, 0 = South, -90 = East, 90 = West, 180 = North)  
        - **module_efficiency** (between 0 and 1)  
        - **solar_irradiation** (in kWh/m²)  
        """
    )

    reduction_factor = st.number_input(
        "Reduction factor (0 - 1)",
        min_value=0.0,
        max_value=1.0,
        value=1.0,
        step=0.1,
        key="total_reduction_factor",
    )

    uploaded_file = st.file_uploader("Please upload an Excel file", type=["xlsx"])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)

        st.subheader("Uploaded Data")
        st.dataframe(df)

        required_cols = [
            "building",
            "building_area",
            "roof",
            "tilt_angle",
            "orientation",
            "module_efficiency",
            "solar_irradiation",
        ]
        missing_cols = [col.lower() for col in required_cols if col not in df.columns]

        if missing_cols:
            st.error(
                f"The following columns are missing from the Excel file: {missing_cols}"
            )

        else:

            # -------------------------------------------------
            # Helper functions to compute Scheffler & TUM areas
            # -------------------------------------------------

            def compute_roof_area_scheffler(
                building_area: float,
                roof_type: str,
                reduction_factor: float,
                titl_angle: float,
            ) -> float:
                """Compute the roof area (Scheffler) given the building area, roof type, and tilt (in degrees).

                Args:
                    building_area (float): The area of the building in square meters.
                    roof_type (str): The type of the roof.
                    reduction_factor (float): The reduction factor.
                    titl_angle (float): The pitch of the roof.

                Returns:
                    float: The roof area in square meters.
                """
                roof_type_lower = str(roof_type).lower()

                if "flat" in roof_type_lower:
                    return flat_roof_area_scheffler(building_area)

                if "gable" in roof_type_lower:
                    return gable_roof_area_scheffler(building_area, titl_angle)

                elif "pitched" in roof_type_lower:
                    return pitched_roof_area_scheffler(
                        building_area, reduction_factor, titl_angle
                    )

                else:
                    # If no match, default
                    st.warning(f"Invalid roof type: {roof_type}")
                    return -1.0

            def compute_roof_area_tum(
                building_area: float,
                roof_type: str,
                reduction_factor: float,
                titl_angle: float,
            ) -> float:
                """Compute the roof area (TUM) given the building area, roof type, and tilt (in degrees).

                Args:
                    building_area (float): The area of the building in square meters.
                    roof_type (str): The type of the roof.
                    reduction_factor (float): The reduction factor.
                    titl_angle (float): The pitch of the roof.

                Returns:
                    float: The roof area in square meters.
                """
                roof_type_lower = str(roof_type).lower()

                if "flat" in roof_type_lower:
                    return flat_roof_area_tum(building_area)

                if "gable" in roof_type_lower:
                    return gable_roof_area_tum(
                        building_area,
                        reduction_factor=reduction_factor,
                        titl_angle=titl_angle,
                    )

                elif "pitched":
                    return pitched_roof_area_tum(
                        building_area,
                        reduction_factor=reduction_factor,
                        titl_angle=titl_angle,
                    )

                else:
                    # If no match, default
                    st.warning(f"Invalid roof type: {roof_type}")
                    return -1.0

            # -------------------------------------------------
            # Compute Scheffler & TUM areas for each row
            # -------------------------------------------------
            df["computed_scheffler_area"] = df.apply(
                lambda row: compute_roof_area_scheffler(
                    row["building_area"],
                    row["roof"],
                    reduction_factor,
                    row["tilt_angle"],
                ),
                axis=1,
            )

            df["computed_tum_area"] = df.apply(
                lambda row: compute_roof_area_tum(
                    row["building_area"],
                    row["roof"],
                    reduction_factor,
                    row["tilt_angle"],
                ),
                axis=1,
            )

            # -------------------------------------------------
            # Compute yields
            # -------------------------------------------------
            def compute_row_yields(row: pd.Series) -> tuple:
                """Compute the electricity yields (Scheffler & TUM) for a given row.

                Args:
                    row (pd.Series): A row from the DataFrame.

                Returns:
                    tuple: The Scheffler and TUM electricity yields.
                """
                tilt_deg = row["tilt_angle"]
                orientation_deg = row["orientation"]
                rel_yield = get_relative_yield(int(orientation_deg), int(tilt_deg))

                solar_irr = row["solar_irradiation"]
                eff = row["module_efficiency"]

                # Electricity yield according to Scheffler
                scheffler_yield = annual_solar_yield(
                    roof_area=row["computed_scheffler_area"],
                    solar_irradiation=solar_irr,
                    module_efficiency=eff,
                    relative_yield=rel_yield,
                )

                # Electricity yield according to TUM
                tum_yield = annual_solar_yield(
                    roof_area=row["computed_tum_area"],
                    solar_irradiation=solar_irr,
                    module_efficiency=eff,
                    relative_yield=rel_yield,
                )

                return scheffler_yield, tum_yield

            df["scheffler_yield"], df["tum_yield"] = zip(
                *df.apply(compute_row_yields, axis=1)
            )
            df["total_yield"] = df["scheffler_yield"] + df["tum_yield"]

            # -------------------------------------------------
            # Displays updated DataFrame
            # -------------------------------------------------
            st.subheader("Calculated Roof Areas and Yields per Building")
            st.dataframe(df)

            # -------------------------------------------------
            # Summaries
            # -------------------------------------------------
            total_scheffler = df["scheffler_yield"].sum()
            total_tum = df["tum_yield"].sum()
            total_all = df["total_yield"].sum()

            st.write("---")
            st.write("### Summary of Total Yields")
            st.success(f"**Total Scheffler Yield:** {total_scheffler:,.2f} kWh")
            st.success(f"**Total TUM Yield:** {total_tum:,.2f} kWh")
    else:
        st.info(
            "Please upload an Excel file to start the total electricity yield calculation."
        )
