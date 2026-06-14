"""
Analisis de mediciones del molde de silicona para experimento de chocolate.

Este programa NO requiere volver a correr el experimento.
Trabaja con un archivo CSV curado a partir de las capturas del Serial Monitor.

Entradas principales:
    data/mediciones_curadas_6_muestras.csv

Salidas:
    resultados/estadisticas_por_muestra.csv
    resultados/estadisticas_total.csv
    resultados/01_temperatura_por_muestra.png
    resultados/02_medias_por_muestra.png
    resultados/03_varianza_por_muestra.png
    resultados/04_boxplot_dispersion.png
    resultados/05_histograma_total.png

Uso:
    python analisis_desde_capturas.py
    python analisis_desde_capturas.py --csv data/mediciones_curadas_6_muestras.csv --out resultados
"""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


REQUIRED_COLUMNS = {
    "muestra",
    "punto",
    "tiempo_visible",
    "millis",
    "temperatura_C",
    "estado",
    "relevador",
    "archivo_fuente",
    "nota",
}


def load_data(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"No existe el archivo: {csv_path}")

    df = pd.read_csv(csv_path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas en el CSV: {sorted(missing)}")

    df["temperatura_C"] = pd.to_numeric(df["temperatura_C"], errors="coerce")
    df["punto"] = pd.to_numeric(df["punto"], errors="coerce").astype("Int64")
    df["millis"] = pd.to_numeric(df["millis"], errors="coerce")

    if df["temperatura_C"].isna().any():
        bad = df[df["temperatura_C"].isna()]
        raise ValueError(
            "Hay temperaturas vacias o no numericas. Revisa estas filas:\n"
            + bad.to_string(index=False)
        )

    return df.sort_values(["muestra", "punto"]).reset_index(drop=True)


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
    stats["coef_variacion_%"] = stats["desviacion_estandar_C"] / stats["media_C"] * 100

    cols = [
        "muestra", "n", "media_C", "mediana_C", "varianza_muestral_C2",
        "desviacion_estandar_C", "minimo_C", "maximo_C", "rango_C",
        "Q1_C", "Q3_C", "IQR_C", "coef_variacion_%",
    ]
    stats = stats[cols]

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


def quality_report(df: pd.DataFrame) -> list[str]:
    messages: list[str] = []
    counts = df.groupby("muestra")["temperatura_C"].count()

    for sample, n in counts.items():
        if n != 10:
            messages.append(f"ADVERTENCIA: {sample} tiene {n} lecturas; se esperaban 10.")

    state_counts = df.groupby("muestra")["estado"].nunique()
    for sample, n_states in state_counts.items():
        if n_states > 1:
            states = ", ".join(df.loc[df["muestra"] == sample, "estado"].dropna().unique())
            messages.append(f"REVISION: {sample} contiene mas de un estado del firmware: {states}")

    if df["nota"].fillna("").str.contains("incertidumbre|revisar|visible", case=False).any():
        messages.append("NOTA: el CSV conserva notas de trazabilidad porque los datos provienen de capturas, no de un log crudo.")

    return messages


def save_plots(df: pd.DataFrame, stats: pd.DataFrame, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)

    # 1) Temperatura por muestra en el tiempo local de 10 puntos
    plt.figure(figsize=(10, 6))
    for sample, group in df.groupby("muestra", sort=True):
        plt.plot(group["punto"], group["temperatura_C"], marker="o", label=sample)
    plt.xlabel("Punto de lectura dentro de la muestra")
    plt.ylabel("Temperatura del molde (°C)")
    plt.title("Figura 1. Temperatura por muestra; permite observar estabilidad y ruido dentro de cada medición de 10 s")
    plt.xticks(range(1, int(df["punto"].max()) + 1))
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / "01_temperatura_por_muestra.png", dpi=200)
    plt.close()

    # 2) Medias por muestra
    plt.figure(figsize=(8, 5))
    plt.bar(stats["muestra"], stats["media_C"])
    plt.xlabel("Muestra")
    plt.ylabel("Temperatura media (°C)")
    plt.title("Figura 2. Media por muestra; compara el nivel térmico central de cada corrida")
    plt.xticks(rotation=30, ha="right")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(out / "02_medias_por_muestra.png", dpi=200)
    plt.close()

    # 3) Varianza por muestra
    plt.figure(figsize=(8, 5))
    plt.bar(stats["muestra"], stats["varianza_muestral_C2"])
    plt.xlabel("Muestra")
    plt.ylabel("Varianza muestral (°C²)")
    plt.title("Figura 3. Varianza por muestra; cuantifica la variación interna de cada medición")
    plt.xticks(rotation=30, ha="right")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(out / "03_varianza_por_muestra.png", dpi=200)
    plt.close()

    # 4) Boxplot
    labels = []
    values = []
    for sample, group in df.groupby("muestra", sort=True):
        labels.append(sample)
        values.append(group["temperatura_C"].to_numpy())
    plt.figure(figsize=(8, 5))
    plt.boxplot(values, tick_labels=labels)
    plt.xlabel("Muestra")
    plt.ylabel("Temperatura del molde (°C)")
    plt.title("Figura 4. Dispersión por muestra; muestra mediana, rango intercuartílico y valores extremos")
    plt.xticks(rotation=30, ha="right")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(out / "04_boxplot_dispersion.png", dpi=200)
    plt.close()

    # 5) Histograma total
    plt.figure(figsize=(8, 5))
    plt.hist(df["temperatura_C"], bins="auto", edgecolor="black")
    plt.xlabel("Temperatura del molde (°C)")
    plt.ylabel("Frecuencia")
    plt.title("Figura 5. Histograma total; resume la dispersión global de las 60 lecturas recuperadas")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(out / "05_histograma_total.png", dpi=200)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Analisis de datos recuperados desde capturas del Serial Monitor.")
    parser.add_argument("--csv", default="data/mediciones_curadas_6_muestras.csv", help="CSV curado con las lecturas recuperadas")
    parser.add_argument("--out", default="resultados", help="Carpeta de salida")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    csv_path = Path(args.csv)
    out = Path(args.out)
    if not csv_path.is_absolute():
        csv_path = base_dir / csv_path
    if not out.is_absolute():
        out = base_dir / out

    df = load_data(csv_path)
    stats, total_stats = compute_stats(df)

    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "datos_usados_para_analisis.csv", index=False)
    stats.to_csv(out / "estadisticas_por_muestra.csv", index=False)
    total_stats.to_csv(out / "estadisticas_total.csv", index=False)

    save_plots(df, stats, out)

    messages = quality_report(df)
    with open(out / "notas_de_calidad.txt", "w", encoding="utf-8") as f:
        f.write("Notas de calidad y trazabilidad\n")
        f.write("================================\n\n")
        if messages:
            for msg in messages:
                f.write(f"- {msg}\n")
        else:
            f.write("No se detectaron problemas automaticos en el archivo curado.\n")

    print("Analisis terminado.")
    print(f"Datos usados: {csv_path}")
    print(f"Resultados en: {out}")
    print("\nResumen por muestra:")
    print(stats.round(4).to_string(index=False))
    print("\nResumen total:")
    print(total_stats.round(4).to_string(index=False))
    if messages:
        print("\nNotas:")
        for msg in messages:
            print("-", msg)


if __name__ == "__main__":
    main()
