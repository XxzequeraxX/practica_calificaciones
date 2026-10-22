"""
=============================================================================
 Practica: Analisis y visualizacion de calificaciones con Pandas y Matplotlib
 Asignatura : Bases de Datos / Programacion (ISC)
 Estilo     : Cyberpunk / Modern Dark (fondo negro, acentos rojo neon)
=============================================================================
"""

import sys
import io
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # renderizado sin ventana grafica
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Forzar salida UTF-8 en Windows (evita UnicodeEncodeError con cp1252)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# PALETA CYBERPUNK
# ---------------------------------------------------------------------------
BG      = "#000000"   # fondo principal
ACCENT  = "#ff1e42"   # rojo neón (barras, líneas, histograma)
WHITE   = "#ffffff"   # texto y etiquetas
GRID    = "#2a0008"   # líneas de rejilla muy sutiles
ACCENT2 = "#ff6b81"   # segundo acento (líneas extra, leyendas)
ACCENT3 = "#ff9eb5"   # tercer acento
COLORS  = ["#ff1e42", "#ff6b81", "#ff9eb5", "#ffccd5"]   # paleta por materia

CSV_FILE    = "calificaciones_isc.csv"
OUT_BAR     = "promedio_materias.png"
OUT_HIST    = "histograma.png"
OUT_LINE    = "tendencia_unidades.png"
OUT_PROM    = "promedios_alumnos.csv"

# ===========================================================================
# CONFIGURACIÓN GLOBAL DE MATPLOTLIB (TEMA CYBERPUNK)
# ===========================================================================
def set_cyberpunk_style():
    """Aplica el tema Cyberpunk a todos los plots de Matplotlib."""
    plt.rcParams.update({
        # Fondos
        "figure.facecolor":    BG,
        "axes.facecolor":      BG,
        "savefig.facecolor":   BG,
        # Texto
        "text.color":          WHITE,
        "axes.labelcolor":     WHITE,
        "xtick.color":         WHITE,
        "ytick.color":         WHITE,
        "axes.titlecolor":     WHITE,
        "legend.facecolor":    "#0d0d0d",
        "legend.edgecolor":    ACCENT,
        "legend.labelcolor":   WHITE,
        # Rejilla
        "axes.grid":           True,
        "grid.color":          GRID,
        "grid.linewidth":      0.8,
        "grid.linestyle":      "--",
        # Bordes (spines)
        "axes.spines.top":     False,
        "axes.spines.right":   False,
        "axes.edgecolor":      ACCENT,
        # Tipografía
        "font.family":         "monospace",
        "axes.titlesize":      14,
        "axes.labelsize":      11,
        "xtick.labelsize":     9,
        "ytick.labelsize":     9,
        # Figura
        "figure.dpi":          150,
    })

set_cyberpunk_style()


# ===========================================================================
# GENERACIÓN DEL DATASET (si no existe calificaciones_isc.csv)
# ===========================================================================
def generar_dataset():
    """
    Genera un dataset realista de calificaciones ISC con exactamente 288 filas.

    Estructura:
      - 24 alumnos  (12 por grupo A, 12 por grupo B)
      - 4 materias  (Programacion, Bases de datos, Redes, Matematicas discretas)
      - 3 unidades  (1, 2, 3)

    Total: 24 × 4 × 3 = 288 filas  ← una fila = un alumno + materia + unidad
    """
    rng = np.random.default_rng(42)   # semilla fija para reproducibilidad

    nombres_a = [
        ("ISC240101", "Ana García López"),
        ("ISC240102", "Carlos Mendez Ruiz"),
        ("ISC240103", "Diana Torres Silva"),
        ("ISC240104", "Eduardo Ramírez Vega"),
        ("ISC240105", "Fernanda López Cruz"),
        ("ISC240106", "Gabriel Hernández Díaz"),
        ("ISC240107", "Hana Martínez Soto"),
        ("ISC240108", "Iván Flores Pérez"),
        ("ISC240109", "Julia Castillo Moreno"),
        ("ISC240110", "Kevin Vargas Reyes"),
        ("ISC240111", "Lucía Guerrero Campos"),
        ("ISC240112", "Miguel Ángel Fuentes"),
    ]
    nombres_b = [
        ("ISC240113", "Nadia Romero Blanco"),
        ("ISC240114", "Oscar Delgado Lara"),
        ("ISC240115", "Pamela Jiménez Rojas"),
        ("ISC240116", "Quetzal Morales Juárez"),
        ("ISC240117", "Rodrigo Salinas Gómez"),
        ("ISC240118", "Sofía Aguilar Nieto"),
        ("ISC240119", "Tomás Espinoza León"),
        ("ISC240120", "Ursula Valdez Méndez"),
        ("ISC240121", "Víctor Ríos Sandoval"),
        ("ISC240122", "Wendy Ochoa Ibarra"),
        ("ISC240123", "Ximena Peña Castro"),
        ("ISC240124", "Yael Ramos Serrano"),
    ]
    materias = [
        "Programacion",
        "Bases de datos",
        "Redes",
        "Matematicas discretas",
    ]
    unidades = [1, 2, 3]

    filas = []
    for grupo, alumnos in [("A", nombres_a), ("B", nombres_b)]:
        for matricula, nombre in alumnos:
            # Base de rendimiento por alumno (0-100, normal)
            base = float(rng.normal(75, 12))
            base = np.clip(base, 40, 100)
            for materia in materias:
                # Ajuste por materia (algunas más difíciles)
                ajuste_materia = {
                    "Programacion":          rng.normal(0, 5),
                    "Bases de datos":        rng.normal(-3, 5),
                    "Redes":                 rng.normal(2, 5),
                    "Matematicas discretas": rng.normal(-8, 7),
                }[materia]
                for unidad in unidades:
                    # Tendencia leve de mejora/empeoramiento por unidad
                    ajuste_unidad = (unidad - 1) * rng.normal(1, 3)
                    cal = base + ajuste_materia + ajuste_unidad + rng.normal(0, 4)
                    cal = float(np.clip(round(cal, 1), 0, 100))
                    # Asistencias (correlacionada con calificación)
                    asist = int(np.clip(
                        round(cal / 10 * 1.6 + rng.normal(0, 1)), 0, 16
                    ))
                    filas.append({
                        "matricula":    matricula,
                        "nombre":       nombre,
                        "grupo":        grupo,
                        "materia":      materia,
                        "unidad":       unidad,
                        "calificacion": cal,
                        "asistencias":  asist,
                    })

    df = pd.DataFrame(filas)
    df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
    print(f"[INFO] Dataset generado → {CSV_FILE}  ({len(df)} filas)")
    return df


# ===========================================================================
# EJERCICIO 1 – CARGA Y REVISIÓN INICIAL
# ===========================================================================
def ejercicio_1():
    """
    Carga el CSV en un DataFrame y muestra la información inicial.

    Por qué 288 filas y no 24:
      El dataset está en formato 'largo' (long/tidy). Cada fila representa
      una observación única: alumno + materia + unidad.
      Con 24 alumnos × 4 materias × 3 unidades = 288 registros.
      Esto facilita el análisis con groupby y evita columnas redundantes.
    """
    print("\n" + "═" * 60)
    print("  EJERCICIO 1 — CARGA Y REVISIÓN INICIAL")
    print("═" * 60)

    # Generar dataset si no existe
    if not os.path.exists(CSV_FILE):
        generar_dataset()

    df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")

    print("\n▶ Primeras 5 filas:")
    print(df.head().to_string(index=False))

    print(f"\n▶ Shape (filas, columnas): {df.shape}")
    print("""
  ¿Por qué 288 filas si hay 24 alumnos?
  ─────────────────────────────────────
  El CSV usa formato TIDY (largo): cada fila = 1 alumno + 1 materia + 1 unidad.
  Cálculo → 24 alumnos × 4 materias × 3 unidades = 288 observaciones.
  Ventaja: se pueden usar groupby/pivot sin reestructurar los datos.
""")

    print("▶ Tipos de columnas (dtypes):")
    print(df.dtypes.to_string())

    print("\n▶ Estadísticas descriptivas — calificacion y asistencias:")
    print(df[["calificacion", "asistencias"]].describe().round(2).to_string())

    return df


# ===========================================================================
# EJERCICIO 2 – FILTROS SIN LOOPS
# ===========================================================================
def ejercicio_2(df):
    """
    Aplica filtros vectorizados (sin loops Python) para contar registros
    que cumplen condiciones específicas.
    """
    print("\n" + "═" * 60)
    print("  EJERCICIO 2 — FILTROS SIN BUCLES")
    print("═" * 60)

    # Filtro 1: Grupo A
    grupo_a = df[df["grupo"] == "A"]
    print(f"\n▶ Registros del Grupo A            : {len(grupo_a)}")

    # Filtro 2: Calificación reprobatoria
    reprobados = df[df["calificacion"] < 70]
    print(f"▶ Registros con calificación < 70  : {len(reprobados)}")

    # Filtro 3: Bases de datos, Grupo B, calificación >= 80
    bd_b_buenos = df[
        (df["materia"] == "Bases de datos") &
        (df["grupo"] == "B") &
        (df["calificacion"] >= 80)
    ]
    print(f"▶ Bases de datos · Grupo B · ≥ 80 : {len(bd_b_buenos)}")

    return grupo_a, reprobados, bd_b_buenos


# ===========================================================================
# EJERCICIO 3 – COLUMNA CALCULADA CON np.where
# ===========================================================================
def ejercicio_3(df):
    """
    Agrega la columna 'situacion' sin usar loops:
      'Aprobado'  si calificacion >= 70
      'Reprobado' en caso contrario
    """
    print("\n" + "═" * 60)
    print("  EJERCICIO 3 — COLUMNA CALCULADA: situacion")
    print("═" * 60)

    df["situacion"] = np.where(df["calificacion"] >= 70, "Aprobado", "Reprobado")

    print("\n▶ Muestra con columna 'situacion':")
    print(df[["matricula", "nombre", "materia", "unidad",
              "calificacion", "situacion"]].head(10).to_string(index=False))

    return df


# ===========================================================================
# EJERCICIO 4 – RESÚMENES Y EXPORTACIÓN
# ===========================================================================
def ejercicio_4(df):
    """
    Calcula y muestra resúmenes estadísticos con groupby.
    Exporta promedios por alumno a promedios_alumnos.csv.
    """
    print("\n" + "═" * 60)
    print("  EJERCICIO 4 — RESÚMENES ESTADÍSTICOS")
    print("═" * 60)

    # 4.1 Promedio por materia
    prom_materia = df.groupby("materia")["calificacion"].mean().round(2)
    print("\n▶ Promedio por materia:")
    print(prom_materia.to_string())

    # 4.2 Promedio por grupo y materia
    prom_grupo_materia = (df.groupby(["grupo", "materia"])["calificacion"]
                            .mean().round(2))
    print("\n▶ Promedio por grupo y materia:")
    print(prom_grupo_materia.to_string())

    # 4.3 Promedio general por alumno (descendente) — preserva matricula y nombre
    prom_alumno = (df.groupby(["matricula", "nombre"])["calificacion"]
                     .mean().round(2)
                     .sort_values(ascending=False))
    print("\n▶ Promedio general por alumno (descendente):")
    print(prom_alumno.to_string())

    # 4.4 Promedio por unidad
    prom_unidad = df.groupby("unidad")["calificacion"].mean().round(2)
    print("\n▶ Promedio por unidad:")
    print(prom_unidad.to_string())

    # 4.5 Conteo aprobados / reprobados
    conteo_sit = df["situacion"].value_counts()
    print("\n▶ Conteo Aprobados / Reprobados:")
    print(conteo_sit.to_string())

    # 4.6 Exportar promedios por alumno
    #     reset_index() convierte el MultiIndex en columnas normales
    prom_alumno_df = prom_alumno.reset_index()
    prom_alumno_df.columns = ["matricula", "nombre", "promedio_general"]
    prom_alumno_df.to_csv(OUT_PROM, index=False, encoding="utf-8-sig")
    print(f"\n▶ Exportado → {OUT_PROM}  ({len(prom_alumno_df)} filas)")

    return prom_materia, prom_grupo_materia, prom_alumno, prom_unidad


# ===========================================================================
# EJERCICIO 5 – GRÁFICAS CON ESTILO CYBERPUNK
# ===========================================================================
def _save(fig, path):
    """Guarda la figura y muestra mensaje de confirmación."""
    fig.savefig(path, bbox_inches="tight", dpi=150)
    print(f"  [✓] Guardada → {path}")


def grafica_barras(prom_materia):
    """Gráfica de barras: promedio por materia (eje Y: 0 – 100)."""
    fig, ax = plt.subplots(figsize=(9, 5))

    materias = prom_materia.index.tolist()
    valores  = prom_materia.values
    x_pos    = np.arange(len(materias))

    bars = ax.bar(x_pos, valores, color=ACCENT, width=0.5,
                  edgecolor=ACCENT2, linewidth=1.2, zorder=3)

    # Etiquetas de valor sobre cada barra
    for bar, val in zip(bars, valores):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.8,
                f"{val:.1f}",
                ha="center", va="bottom",
                color=WHITE, fontsize=9, fontweight="bold")

    ax.set_xticks(x_pos)
    ax.set_xticklabels(materias, rotation=15, ha="right")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
    ax.set_title("Promedio por Materia", fontsize=15, fontweight="bold",
                 color=ACCENT, pad=14)
    ax.set_xlabel("Materia")
    ax.set_ylabel("Calificación promedio")

    # Línea de aprobación
    ax.axhline(70, color=ACCENT2, linewidth=1, linestyle="--",
               label="Mín. aprobatorio (70)", zorder=2)
    ax.legend()

    _save(fig, OUT_BAR)
    plt.close(fig)


def grafica_histograma(df):
    """Histograma de todas las calificaciones con línea vertical en 70."""
    fig, ax = plt.subplots(figsize=(9, 5))

    n, bins, patches = ax.hist(
        df["calificacion"], bins=20,
        color=ACCENT, edgecolor=BG, linewidth=0.6, zorder=3, alpha=0.9
    )
    # Resaltar barras reprobatorias en tono más oscuro
    for patch, left in zip(patches, bins[:-1]):
        if left < 70:
            patch.set_facecolor("#7a0f20")

    # Línea vertical aprobatorio
    ax.axvline(70, color=WHITE, linewidth=1.8, linestyle="--",
               label="Mín. aprobatorio (70)", zorder=4)

    ax.set_title("Distribución de Calificaciones", fontsize=15,
                 fontweight="bold", color=ACCENT, pad=14)
    ax.set_xlabel("Calificación")
    ax.set_ylabel("Frecuencia")
    ax.legend()

    _save(fig, OUT_HIST)
    plt.close(fig)


def grafica_tendencia(df):
    """Línea: promedio por unidad para cada materia."""
    fig, ax = plt.subplots(figsize=(9, 5))

    materias = df["materia"].unique()
    unidades = sorted(df["unidad"].unique())

    for mat, color in zip(materias, COLORS):
        promedios = (
            df[df["materia"] == mat]
            .groupby("unidad")["calificacion"]
            .mean()
            .reindex(unidades)
        )
        ax.plot(unidades, promedios.values,
                marker="o", linewidth=2.2,
                color=color, label=mat, zorder=3)
        # Anotación del valor en cada punto
        for u, v in zip(unidades, promedios.values):
            ax.annotate(f"{v:.1f}",
                        xy=(u, v), xytext=(4, 4),
                        textcoords="offset points",
                        color=color, fontsize=7.5)

    ax.set_xticks(unidades)
    ax.set_xticklabels([f"Unidad {u}" for u in unidades])
    ax.set_ylim(50, 100)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
    ax.set_title("Tendencia de Calificaciones por Unidad y Materia",
                 fontsize=14, fontweight="bold", color=ACCENT, pad=14)
    ax.set_xlabel("Unidad")
    ax.set_ylabel("Calificación promedio")
    ax.legend(loc="lower right")

    _save(fig, OUT_LINE)
    plt.close(fig)


def ejercicio_5(df, prom_materia):
    """Genera y guarda las 3 gráficas con tema Cyberpunk."""
    print("\n" + "═" * 60)
    print("  EJERCICIO 5 — GRÁFICAS")
    print("═" * 60)

    grafica_barras(prom_materia)
    grafica_histograma(df)
    grafica_tendencia(df)


# ===========================================================================
# EJERCICIO 6 – INTERPRETACIÓN Y CONCLUSIONES
# ===========================================================================
def ejercicio_6(df, prom_materia, prom_unidad):
    """
    Imprime respuestas interpretativas con base en los datos calculados.
    """
    print("\n" + "═" * 60)
    print("  EJERCICIO 6 — INTERPRETACIÓN Y CONCLUSIONES")
    print("═" * 60)

    # 6.1 Materia con menor promedio
    materia_min = prom_materia.idxmin()
    val_min     = prom_materia.min()
    print(f"\n▶ Materia con MENOR promedio: {materia_min} ({val_min:.2f})")

    # 6.2 Tendencia: unidad 3 vs unidades 1 y 2
    u1, u2, u3 = prom_unidad[1], prom_unidad[2], prom_unidad[3]
    tendencia = "mejora" if u3 > u2 > u1 else \
                "empeora" if u3 < u2 < u1 else \
                "fluctúa"
    print(f"\n▶ Tendencia por unidad:")
    print(f"   Unidad 1: {u1:.2f}  |  Unidad 2: {u2:.2f}  |  Unidad 3: {u3:.2f}")
    print(f"   Interpretación: el rendimiento {tendencia} a lo largo de las unidades.")

    # 6.3 Alumnos con promedio general < 70
    prom_alumno = (df.groupby(["matricula", "nombre"])["calificacion"]
                     .mean().round(2))
    bajo_70 = (prom_alumno < 70).sum()
    total_alumnos = prom_alumno.shape[0]
    print(f"\n▶ Alumnos con promedio general < 70: {bajo_70} de {total_alumnos}")

    # 6.4 Porcentaje aprobados/reprobados
    conteo = df["situacion"].value_counts(normalize=True) * 100
    for sit, pct in conteo.items():
        print(f"   {sit}: {pct:.1f}%")

    print("\n✔  Análisis completo. Archivos generados:")
    for f in [OUT_BAR, OUT_HIST, OUT_LINE, OUT_PROM]:
        print(f"   • {f}")


# ===========================================================================
# PUNTO DE ENTRADA
# ===========================================================================
if __name__ == "__main__":
    df                              = ejercicio_1()
    ejercicio_2(df)
    df                              = ejercicio_3(df)
    prom_mat, prom_gm, prom_al, prom_un = ejercicio_4(df)
    ejercicio_5(df, prom_mat)
    ejercicio_6(df, prom_mat, prom_un)
    print("\n" + "═" * 60)
    print("  PRÁCTICA FINALIZADA")
    print("═" * 60 + "\n")
