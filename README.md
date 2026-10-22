# Práctica: Análisis y visualización de calificaciones con Pandas y Matplotlib

> Proyecto completo de análisis de datos académicos desarrollado en Python. Incluye generación de dataset, análisis estadístico con Pandas, visualizaciones con Matplotlib (tema **Cyberpunk**) y un dashboard web interactivo con Flask.

---

## Estructura del proyecto

```
practica_calificaciones/
├── practica_pandas.py       ← Script principal (Ejercicios 1–6)
├── dashboard.py             ← Dashboard web interactivo (Flask)
├── requirements.txt         ← Dependencias Python
├── README.md                ← Este archivo
│
│   (generados automáticamente al ejecutar practica_pandas.py)
├── calificaciones_isc.csv   ← Dataset: 288 filas
├── promedios_alumnos.csv    ← Promedios generales por alumno
├── promedio_materias.png    ← Gráfica de barras
├── histograma.png           ← Histograma de calificaciones
└── tendencia_unidades.png   ← Gráfica de líneas por unidad
```

---

## Requisitos previos

- **Python 3.10+** instalado y en el PATH
- Conexión a internet (solo para instalar dependencias)

Verifica tu versión de Python:
```bash
python --version
```

---

## Instalación de dependencias

Abre una terminal dentro de la carpeta `practica_calificaciones/` y ejecuta:

```bash
pip install -r requirements.txt
```

Esto instala: `pandas`, `matplotlib`, `numpy` y `flask`.

---

## Ejecución

### Paso 1 — Análisis principal (Ejercicios 1 al 6)

**PowerShell (Windows):**
```powershell
$env:PYTHONUTF8="1"; python practica_pandas.py
```

**CMD (Windows):**
```cmd
set PYTHONUTF8=1 && python practica_pandas.py
```

**Linux / macOS / Terminal con UTF-8:**
```bash
python practica_pandas.py
```

**¿Qué hace este script?**

| Ejercicio | Descripción |
|-----------|-------------|
| **1** | Carga (o genera) `calificaciones_isc.csv`, muestra las primeras filas, shape, dtypes y `describe()` |
| **2** | Aplica 3 filtros vectorizados sin loops: Grupo A, calificación < 70, Bases de datos Grupo B ≥ 80 |
| **3** | Agrega columna `situacion` con `np.where()` (Aprobado / Reprobado) |
| **4** | Calcula promedios por materia, grupo, alumno y unidad; exporta `promedios_alumnos.csv` |
| **5** | Genera 3 gráficas PNG con tema Cyberpunk (fondo negro, rojo neón) |
| **6** | Imprime conclusiones: materia más baja, tendencia por unidad, alumnos bajo 70 |

Al finalizar se habrán creado en la misma carpeta:
- `calificaciones_isc.csv`
- `promedios_alumnos.csv`
- `promedio_materias.png`
- `histograma.png`
- `tendencia_unidades.png`

---

### Paso 2 — Dashboard web interactivo (opcional)

```bash
python dashboard.py
```

Luego abre tu navegador en:

```
http://127.0.0.1:5000
```

**Pestañas del dashboard:**

| Pestaña | Contenido |
|---------|-----------|
| **Gráficas** | Las 3 imágenes PNG embebidas en pantalla completa |
| **Promedios** | Tabla ordenada de promedios por alumno con indicador de reprobado |
| **Filtros** | Panel interactivo para filtrar por grupo, materia, unidad, rango de calificación y situación |
| **Dataset** | Vista de las primeras 50 filas del CSV completo |

> **Nota:** Ejecuta primero `practica_pandas.py` antes de iniciar el dashboard para que los archivos existan.

---

## Dataset generado (`calificaciones_isc.csv`)

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `matricula` | string | Matrícula del alumno (ISC240101–ISC240124) |
| `nombre` | string | Nombre completo |
| `grupo` | string | Grupo A o B (12 alumnos cada uno) |
| `materia` | string | Una de 4 materias |
| `unidad` | int | Unidad 1, 2 o 3 |
| `calificacion` | float | Calificación (0–100) |
| `asistencias` | int | Asistencias (0–16) |

**¿Por qué 288 filas con solo 24 alumnos?**

El CSV usa formato **tidy (largo)**: cada fila representa una sola observación.

$$24 \text{ alumnos} \times 4 \text{ materias} \times 3 \text{ unidades} = \mathbf{288} \text{ filas}$$

Esto facilita el uso de `groupby`, `pivot_table` y filtros vectorizados sin necesitar reestructurar los datos.

---

## Gráficas generadas

### `promedio_materias.png` — Barras por materia
- Eje Y de 0 a 100
- Línea punteada en 70 (mínimo aprobatorio)
- Etiquetas de valor sobre cada barra

### `histograma.png` — Distribución de calificaciones
- Barras debajo de 70 en rojo oscuro
- Línea vertical blanca en 70

### `tendencia_unidades.png` — Línea por unidad/materia
- Una línea por materia con anotaciones de valor
- Permite visualizar si el rendimiento mejora o empeora por unidad

---

## Solución de problemas

| Problema | Solución |
|----------|----------|
| `ModuleNotFoundError: No module named 'pandas'` | Ejecuta `pip install -r requirements.txt` |
| `ModuleNotFoundError: No module named 'flask'` | Ejecuta `pip install flask` |
| El dashboard muestra "Ejecuta practica_pandas.py primero" | Ejecuta `python practica_pandas.py` antes que `dashboard.py` |
| Gráficas con fondo blanco | Asegúrate de usar el script sin modificaciones al bloque de `rcParams` |

---

## Tecnologías utilizadas

- **Python 3.10+**
- **Pandas** — manipulación de datos
- **NumPy** — operaciones vectorizadas
- **Matplotlib** — visualización con tema Cyberpunk personalizado
- **Flask** — servidor web del dashboard interactivo

---

*Práctica desarrollada para la asignatura ISC — Análisis de datos académicos.*
