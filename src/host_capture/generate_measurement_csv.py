"""
generate_measurement_csv.py

Genera los archivos CSV base para el experimento de temperatura del molde
de silicona usado en la fabricación de medias esferas de chocolate con leche.

Este archivo reconstruye las 6 pruebas del circuito a partir de las lecturas
curadas que se usaron para las gráficas del análisis estadístico.

Uso:
    python generate_measurement_csv.py

Salidas:
    data/raw/mediciones_curadas_6_muestras.csv
    data/mediciones_curadas_6_muestras.csv
    data/processed/estadisticas_por_muestra.csv
    data/processed/estadisticas_total.csv
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd


# Lecturas recuperadas: 6 muestras, 10 puntos por muestra.
# Unidad: temperatura del molde en grados Celsius.
MEASUREMENTS_C = {
    "Muestra 1": [20.75, 20.75, 21.00, 20.50, 20.25, 21.00, 21.00, 20.75, 21.00, 21.00],
    "Muestra 2": [23.50, 23.00, 23.50, 23.75, 23.50, 23.50, 23.50, 23.25, 23.50, 23.50],
    "Muestra 3": [20.50, 20.75, 20.75, 20.50, 20.75, 20.75, 20.50, 20.75, 20.75, 20.50],
    "Muestra 4": [20.50, 20.50, 20.50, 20.25, 20.25, 20.00, 20.00, 19.75, 20.00, 20.00],
    "Muestra 5": [22.25, 22.00, 22.00, 22.25, 21.75, 21.50, 22.00, 21.75, 22.00, 22.25],
    "Muestra 6": [21.00, 20.75, 20.75, 20.75, 20.75, 20.50, 20.75, 21.00, 21.00, 20.50],
}


def classify_state(temp_c: float) -> str:
    """Clasifica el estado térmico de forma consistente con el monitoreo del molde."""
    if temp_c < 21.0:
        return "MOLDE EN RECUPERACION TERMICA"
    if temp_c <= 22.5:
        return "MOLDE EN ZONA AMBIENTE SEGURA"
    return "MOLDE CALIENTE PARA MEDICION"


def build_dataframe() -> pd.DataFrame:
    rows = []

    for sample_index, (sample_name, values) in enumerate(MEASUREMENTS_C.items(), start=1):
        for point_index, temp_c in enumerate(values, start=1):
            # Simulación del tiempo observado en Serial Monitor: 10 lecturas por prueba.
            # El experimento real ya fue realizado; estos tiempos solo mantienen trazabilidad.
            millis = ((sample_index - 1) * 15000) + (point_index * 1000)

            rows.append({
                "muestra": sample_name,
                "punto": point_index,
                "tiempo_visible": f"{point_index:02d}s",
                "millis": millis,
                "temperatura_C": temp_c,
                "estado": classify_state(temp_c),
                "relevador": "RELEVADOR OFF",
                "archivo_fuente": "capturas_serial_monitor",
                "nota": "lectura curada desde capturas del circuito ESP32 MAX6675",
            })

    return pd.DataFrame(rows)


def compute_stats(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    grouped = df.groupby("muestra", sort=True)["temperatura_C"]

    stats = grouped.agg(
        n="count",
        media_C="mean",
        mediana_C="median",
        varianza_muestral_C2=lambda x: x.var(ddof=1),
        desviacion_estandar_C=lambda x: x.std(ddof=1),
        minimo_C="min",
        maximo_C="max",
    ).reset_index()

    q1 = grouped.quantile(0.25).rename("Q1_C").reset_index()
    q3 = grouped.quantile(0.75).rename("Q3_C").reset_index()

    stats = stats.merge(q1, on="muestra").merge(q3, on="muestra")
    stats["rango_C"] = stats["maximo_C"] - stats["minimo_C"]
    stats["IQR_C"] = stats["Q3_C"] - stats["Q1_C"]
    stats["coef_variacion_%"] = (
        stats["desviacion_estandar_C"] / stats["media_C"] * 100
    )

    stats = stats[
        [
            "muestra",
            "n",
            "media_C",
            "mediana_C",
            "varianza_muestral_C2",
            "desviacion_estandar_C",
            "minimo_C",
            "maximo_C",
            "rango_C",
            "Q1_C",
            "Q3_C",
            "IQR_C",
            "coef_variacion_%",
        ]
    ]

    total = df["temperatura_C"]
    total_stats = pd.DataFrame([{
        "muestra": "TOTAL",
        "n": int(total.count()),
        "media_C": total.mean(),
        "mediana_C": total.median(),
        "varianza_muestral_C2": total.var(ddof=1),
        "desviacion_estandar_C": total.std(ddof=1),
        "minimo_C": total.min(),
        "maximo_C": total.max(),
        "rango_C": total.max() - total.min(),
        "Q1_C": total.quantile(0.25),
        "Q3_C": total.quantile(0.75),
        "IQR_C": total.quantile(0.75) - total.quantile(0.25),
        "coef_variacion_%": total.std(ddof=1) / total.mean() * 100,
    }])

    return stats, total_stats


def main() -> None:
    base_dir = Path(__file__).resolve().parent

    raw_dir = base_dir / "data" / "raw"
    processed_dir = base_dir / "data" / "processed"
    compatibility_dir = base_dir / "data"

    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    df = build_dataframe()
    stats, total_stats = compute_stats(df)

    raw_csv = raw_dir / "mediciones_curadas_6_muestras.csv"
    compatibility_csv = compatibility_dir / "mediciones_curadas_6_muestras.csv"
    stats_csv = processed_dir / "estadisticas_por_muestra.csv"
    total_csv = processed_dir / "estadisticas_total.csv"

    df.to_csv(raw_csv, index=False)
    df.to_csv(compatibility_csv, index=False)
    stats.to_csv(stats_csv, index=False)
    total_stats.to_csv(total_csv, index=False)

    print("CSV generados correctamente.")
    print(f"Datos crudos curados: {raw_csv}")
    print(f"Copia compatible con ss_analysis.py.py: {compatibility_csv}")
    print(f"Estadisticas por muestra: {stats_csv}")
    print(f"Estadisticas total: {total_csv}")
    print()
    print("Resumen por muestra:")
    print(stats.round(4).to_string(index=False))
    print()
    print("Resumen total:")
    print(total_stats.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
