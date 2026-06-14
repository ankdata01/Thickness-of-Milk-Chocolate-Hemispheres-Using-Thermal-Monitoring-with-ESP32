# Evaluation of the Effect of Mold Temperature on the Quality and Thickness of Milk Chocolate Hemispheres Using Thermal Monitoring with ESP32

## Short Description

This repository contains the firmware and Python analysis script used for an Experimental Design project focused on measuring silicone mold temperature during the preparation of milk chocolate hemispheres.

The system uses an ESP32, a MAX6675 thermocouple module, and a K-type thermocouple to monitor mold temperature. The recovered measurements are analyzed with Python to calculate statistical variation and generate plots.

## Main Files

```text
control_temperatura_molde_chocolate_final.ino
ss_analysis.py
```

The `.ino` file contains the ESP32 firmware for the thermal monitoring circuit.

The `.py` file analyzes the curated temperature data obtained from Serial Monitor captures and generates statistical summaries and plots.

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

## ESP32 Circuit Pinout

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

All electronic modules must share the same GND reference.

## Firmware File

```text
control_temperatura_molde_chocolate_final.ino
```

This firmware reads the temperature from the K-type thermocouple through the MAX6675 module. The ESP32 classifies the mold temperature condition, activates the corresponding LED indicator, and prints the measurements through the Serial Monitor.

The firmware works in safe monitoring mode by default. In this mode, the relay remains OFF to avoid activating any high-voltage heating device during the experimental measurement stage.

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
Red LED   -> Hot container, warning, or safety condition
```

## Python Analysis File

```text
ss_analysis.py
```

This Python script does not require running the experiment again. It works with a curated CSV file created from the Serial Monitor captures.

Expected input file:

```text
data/mediciones_curadas_6_muestras.csv
```

The CSV must include the following columns:

```text
muestra
punto
tiempo_visible
millis
temperatura_C
estado
relevador
archivo_fuente
nota
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

## Python Requirements

Install the required libraries with:

```bash
pip install -r requirements.txt
```

The `requirements.txt` file should contain:

```text
numpy
pandas
matplotlib
```

## How to Run the Analysis

Run the script with the default input and output paths:

```bash
python ss_analysis.py
```

Or specify the input CSV and output folder manually:

```bash
python ss_analysis.py --csv data/mediciones_curadas_6_muestras.csv --out resultados
```

## Output Files

The script generates the following files inside the output folder:

```text
resultados/datos_usados_para_analisis.csv
resultados/estadisticas_por_muestra.csv
resultados/estadisticas_total.csv
resultados/notas_de_calidad.txt
resultados/01_temperatura_por_muestra.png
resultados/02_medias_por_muestra.png
resultados/03_varianza_por_muestra.png
resultados/04_boxplot_dispersion.png
resultados/05_histograma_total.png
```

## Data Analysis Purpose

The analysis compares the temperature behavior of the silicone mold across different chocolate-forming samples. The statistical results are used to quantify measurement variation and evaluate how mold temperature affects the final thickness, shine, surface finish, and visible imperfections of the milk chocolate hemispheres.

## Deliverables

Final PDF report: included separately in the project submission.

YouTube video evidence: included as a public video link in the project submission.

Firmware source code: `control_temperatura_molde_chocolate_final.ino`

Python analysis source code: `ss_analysis.py`

## Course Information

Course: Experimental Design
Period: 2026A
System: ESP32 Thermal Monitoring System
Application: Milk Chocolate Hemisphere Mold Temperature Analysis
