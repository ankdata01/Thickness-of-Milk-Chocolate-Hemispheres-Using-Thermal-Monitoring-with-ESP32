# Practice 1 — Variation Sources (ESP32 + MAX6675)

## What this repo contains
Firmware for ESP32 (MicroPython) and a Python host script used to capture **real serial measurements** from a MAX6675 + K-type thermocouple setup and compare:
- 10 sequential steady-state samples (baseline / natural variation)
- 10 blocked/randomized samples (induced variation via time blocks)

## Deliverables
- Template link: `report/template_link.txt`
- YouTube evidence: `media/video_link.txt`
- Final report (PDF): `report/Reporte_Practica_1.pdf`
- Source code: this repository

## Setup (Windows)
Create and activate a venv:
```bash
py -m venv .venv
.\.venv\Scripts\activate