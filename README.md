# Bachelorarbeit von Simon Strobel

## Usage

Run the Docker-Container with the following command:

```bash
docker build -t app . && docker run -p 8501:8501 app
```

> [!NOTE]
> If using the Excel-Feature, make sure the Excel-File has the following structure:
>
> - building
> - building_area
> - roof
> - tilt_angle
> - orientation module_efficiency
> - solar_irradiation
