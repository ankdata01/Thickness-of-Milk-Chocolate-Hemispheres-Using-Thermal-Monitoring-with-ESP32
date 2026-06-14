# Evaluation of the Effect of Mold Temperature on the Quality and Thickness of Milk Chocolate Hemispheres Using Thermal Monitoring with ESP32

## Short Description

This repository contains the firmware, curated data generation script, statistical analysis script, plots, and deliverable evidence for an Experimental Design project focused on measuring silicone mold temperature during the preparation of milk chocolate hemispheres.

The system uses an ESP32, a MAX6675 thermocouple module, and a K-type thermocouple to monitor mold temperature. The recovered measurements from six circuit tests are processed with Python to calculate statistical variation and generate comparative plots.

## Selected Experimental System

Temperature Controller / ESP32 Thermal Monitoring System.

The experimental unit is the silicone mold and chocolate-forming process under a defined temperature condition. The sampling unit is each temperature reading recovered from the ESP32 thermal monitoring circuit.

## Repository Structure

```text
.
├── data/
│   ├── raw/
│   │   └── mediciones_curadas_6_muestras.csv
│   │
│   └── processed/
│       ├── estadisticas_por_muestra.csv
│       ├── estadisticas_total.csv
│       └── figures/
│           ├── 01_temperatura_por_muestra.png
│           ├── 02_medias_por_muestra.png
│           ├── 03_varianza_por_muestra.png
│           ├── 04_boxplot_dispersion.png
│           └── 05_histograma_total.png
│
├── firmware/
│   └── control_temperatura_molde_chocolate_final.ino
│
├── media/
│   └── video_link.txt
│
├── report/
│   └── final_report.pdf
│
├── generate_measurement_csv.py
├── ss_analysis.py.py
├── README.md
├── requirements.txt
├── LICENSE
└── .gitignore
```

## Main Files

```text
control_temperatura_molde_chocolate_final.ino
generate_measurement_csv.py
ss_analysis.py.py
```

The `.ino` file contains the ESP32 firmware used for the thermal monitoring circuit.

The `generate_measurement_csv.py` file reconstructs the curated CSV files from the six circuit tests used in the experiment.

The `ss_analysis.py.py` file analyzes the curated temperature data, calculates descriptive statistics, and generates the final plots.

## Hardware System

The circuit uses the following components:

```text
ESP32 development board
MAX6675 thermocouple module
K-type thermocouple
Relay module
Red LED
Green LED
Blue LED
Resistors
Breadboard
Jumper wires
Silicone mold for milk chocolate hemispheres
```

## Circuit Pinout

```text
MAX6675 VCC  -> ESP32 3V3
MAX6675 GND  -> ESP32 GND
MAX6675 SCK  -> ESP32 GPIO18
MAX6675 CS   -> ESP32 GPIO5
MAX6675 SO   -> ESP32 GPIO19

Relay signal -> ESP32 GPIO26
Red LED      -> ESP32 GPIO14
Green LED    -> ESP32 GPIO27
Blue LED     -> ESP32 GPIO25
```

All electronic modules must share the same GND reference. If another ESP32 pin configuration is used, the pin constants must be updated in the firmware file.

## Firmware Description

The firmware file is located in:

```text
firmware/control_temperatura_molde_chocolate_final.ino
```

The firmware reads the mold temperature through the MAX6675 thermocouple module. The ESP32 classifies the mold temperature condition, activates the corresponding LED indicator, and prints the measurements through the Serial Monitor.

The relay remains OFF during the experimental monitoring stage to keep the system in safe measurement mode.

Expected serial output format:

```text
millis,tempC,estado,relevador
```

Example:

```text
68554,20.25,MOLDE EN RECUPERACION TERMICA,RELEVADOR OFF
```

LED interpretation:

```text
Blue LED  -> Cold mold or thermal recovery
Green LED -> Ambient or safe temperature zone
Red LED   -> Hot mold, warning, or safety condition
```

## Data Generation Script

The CSV generation script is:

```text
generate_measurement_csv.py
```

This script generates the curated data files from the six temperature tests performed with the ESP32 circuit. Each test contains 10 temperature measurements.

Run:

```bash
python generate_measurement_csv.py
```

Generated files:

```text
data/raw/mediciones_curadas_6_muestras.csv
data/mediciones_curadas_6_muestras.csv
data/processed/estadisticas_por_muestra.csv
data/processed/estadisticas_total.csv
```

The additional copy in `data/mediciones_curadas_6_muestras.csv` is included for compatibility with the analysis script.

## Statistical Analysis Script

The analysis script is:

```text
ss_analysis.py.py
```

This script works with the curated CSV file and generates statistical summaries and plots.

Run:

```bash
python ss_analysis.py.py
```

The script calculates:

```text
Mean
Median
Sample variance
Standard deviation
Minimum temperature
Maximum temperature
Range
Q1
Q3
Interquartile range
Coefficient of variation
```

It also generates the following plots:

```text
01_temperatura_por_muestra.png
02_medias_por_muestra.png
03_varianza_por_muestra.png
04_boxplot_dispersion.png
05_histograma_total.png
```

## Python Requirements

Install the required libraries with:

```bash
pip install -r requirements.txt
```

The `requirements.txt` file contains:

```text
numpy
pandas
matplotlib
```

## How to Reproduce the Analysis

First, install the dependencies:

```bash
pip install -r requirements.txt
```

Then generate the CSV files:

```bash
python generate_measurement_csv.py
```

Finally, run the statistical analysis and plot generation:

```bash
python ss_analysis.py.py
```

## Experimental Data

The project analyzes six temperature measurement tests from the ESP32 thermal monitoring circuit. Each sample contains 10 temperature readings from the silicone mold.

The purpose of the analysis is to quantify the variation in mold temperature and evaluate how thermal behavior may affect the thickness, shine, surface finish, and visible imperfections of milk chocolate hemispheres.

## Deliverables

Final PDF report:

```text
report/final_report.pdf
```

YouTube video evidence:

```text
media/video_link.txt
```

Firmware source code:

```text
firmware/control_temperatura_molde_chocolate_final.ino
```

Python source code:

```text
generate_measurement_csv.py
ss_analysis.py.py
```

Curated and processed data:

```text
data/
```

## Project Objective

Quantify the effect of silicone mold temperature on the quality, thickness, and surface finish of milk chocolate hemispheres by using ESP32-based thermal monitoring and Python statistical analysis.

## Course Information

Course: Experimental Design
Period: 2026A
System: ESP32 Thermal Monitoring System
Application: Milk Chocolate Hemisphere Mold Temperature Analysis

