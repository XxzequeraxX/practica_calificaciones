"""
=============================================================================
 dashboard.py — Dashboard interactivo Cyberpunk con Flask
 Visualiza las gráficas, el CSV de promedios y permite aplicar filtros.
=============================================================================
"""

import os
import io
import base64
import pandas as pd
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Rutas a los archivos generados por practica_pandas.py
# ---------------------------------------------------------------------------
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
CSV_FILE    = os.path.join(BASE_DIR, "calificaciones_isc.csv")
PROM_FILE   = os.path.join(BASE_DIR, "promedios_alumnos.csv")
IMG_BAR     = os.path.join(BASE_DIR, "promedio_materias.png")
IMG_HIST    = os.path.join(BASE_DIR, "histograma.png")
IMG_LINE    = os.path.join(BASE_DIR, "tendencia_unidades.png")


def img_to_b64(path):
    """Convierte una imagen a base64 para insertarla en HTML inline."""
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# ---------------------------------------------------------------------------
# Plantilla HTML (todo inline — no necesita carpeta templates/)
# ---------------------------------------------------------------------------
HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Dashboard Calificaciones ISC</title>
  <style>
    /* ============================================================
       CYBERPUNK DARK THEME
    ============================================================ */
    :root {
      --bg:       #000000;
      --panel:    #0b0b0b;
      --accent:   #ff1e42;
      --accent2:  #ff6b81;
      --white:    #ffffff;
      --muted:    #888888;
      --border:   #2a0008;
      --font:     'Courier New', Courier, monospace;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--white);
      font-family: var(--font);
      min-height: 100vh;
    }

    /* ─── HEADER ─────────────────────────────────────────────── */
    header {
      background: var(--panel);
      border-bottom: 2px solid var(--accent);
      padding: 20px 40px;
      display: flex;
      align-items: center;
      gap: 16px;
    }
    header .logo {
      font-size: 1.8rem;
      font-weight: bold;
      color: var(--accent);
      letter-spacing: 3px;
      text-shadow: 0 0 12px var(--accent);
    }
    header p {
      color: var(--muted);
      font-size: 0.8rem;
      margin-top: 4px;
    }

    /* ─── NAV TABS ────────────────────────────────────────────── */
    nav {
      background: var(--panel);
      display: flex;
      gap: 0;
      border-bottom: 1px solid var(--border);
    }
    nav button {
      background: transparent;
      border: none;
      border-bottom: 3px solid transparent;
      color: var(--muted);
      font-family: var(--font);
      font-size: 0.85rem;
      letter-spacing: 1px;
      padding: 12px 28px;
      cursor: pointer;
      transition: all 0.2s;
    }
    nav button:hover  { color: var(--white); }
    nav button.active {
      color: var(--accent);
      border-bottom-color: var(--accent);
      text-shadow: 0 0 8px var(--accent);
    }

    /* ─── MAIN CONTENT ────────────────────────────────────────── */
    main { padding: 32px 40px; max-width: 1300px; margin: 0 auto; }

    .tab-content { display: none; }
    .tab-content.active { display: block; }

    /* ─── SECTION TITLE ─────────────────────────────────────── */
    .section-title {
      font-size: 1.1rem;
      color: var(--accent);
      letter-spacing: 2px;
      text-transform: uppercase;
      margin-bottom: 20px;
      border-left: 4px solid var(--accent);
      padding-left: 12px;
    }

    /* ─── CHARTS GRID ────────────────────────────────────────── */
    .charts-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(560px, 1fr));
      gap: 24px;
    }
    .chart-card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-top: 2px solid var(--accent);
      border-radius: 4px;
      padding: 18px;
    }
    .chart-card h3 {
      color: var(--accent2);
      font-size: 0.82rem;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      margin-bottom: 12px;
    }
    .chart-card img {
      width: 100%;
      border-radius: 4px;
      border: 1px solid var(--border);
    }
    .chart-placeholder {
      width: 100%; height: 220px;
      display: flex; align-items: center; justify-content: center;
      color: var(--muted); font-size: 0.8rem;
      border: 1px dashed var(--border); border-radius: 4px;
    }

    /* ─── TABLE ──────────────────────────────────────────────── */
    .table-wrapper {
      overflow-x: auto;
      background: var(--panel);
      border: 1px solid var(--border);
      border-top: 2px solid var(--accent);
      border-radius: 4px;
      padding: 0;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.82rem;
    }
    thead th {
      background: #110005;
      color: var(--accent);
      text-align: left;
      padding: 10px 16px;
      letter-spacing: 1px;
      text-transform: uppercase;
      border-bottom: 1px solid var(--border);
      white-space: nowrap;
    }
    tbody tr { border-bottom: 1px solid var(--border); }
    tbody tr:hover { background: #100003; }
    tbody td { padding: 8px 16px; color: var(--white); white-space: nowrap; }
    tbody td.low { color: var(--accent); font-weight: bold; }

    /* ─── FILTER PANEL ───────────────────────────────────────── */
    .filter-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }
    .filter-group label {
      display: block;
      color: var(--muted);
      font-size: 0.72rem;
      letter-spacing: 1px;
      text-transform: uppercase;
      margin-bottom: 6px;
    }
    .filter-group select,
    .filter-group input {
      width: 100%;
      background: var(--panel);
      border: 1px solid var(--accent);
      border-radius: 3px;
      color: var(--white);
      font-family: var(--font);
      font-size: 0.85rem;
      padding: 7px 10px;
      outline: none;
    }
    .filter-group select option { background: var(--bg); }
    .btn {
      background: var(--accent);
      border: none;
      border-radius: 3px;
      color: var(--white);
      cursor: pointer;
      font-family: var(--font);
      font-size: 0.85rem;
      font-weight: bold;
      letter-spacing: 1px;
      padding: 9px 22px;
      transition: box-shadow 0.2s;
      text-transform: uppercase;
    }
    .btn:hover { box-shadow: 0 0 14px var(--accent); }
    .btn-secondary {
      background: transparent;
      border: 1px solid var(--accent);
      color: var(--accent);
      margin-left: 8px;
    }
    .btn-secondary:hover { background: #1a0008; }

    /* ─── STATS CARDS ────────────────────────────────────────── */
    .stats-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: 16px;
      margin-bottom: 28px;
    }
    .stat-card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-top: 2px solid var(--accent);
      border-radius: 4px;
      padding: 16px 20px;
    }
    .stat-card .val {
      font-size: 1.8rem;
      font-weight: bold;
      color: var(--accent);
      text-shadow: 0 0 8px var(--accent);
    }
    .stat-card .lbl {
      color: var(--muted);
      font-size: 0.72rem;
      letter-spacing: 1px;
      text-transform: uppercase;
      margin-top: 4px;
    }

    /* ─── RESULT BOX ─────────────────────────────────────────── */
    #filter-result {
      margin-top: 18px;
      background: var(--panel);
      border: 1px solid var(--border);
      border-left: 3px solid var(--accent);
      border-radius: 4px;
      padding: 14px 18px;
      font-size: 0.83rem;
      color: var(--white);
    }
    #filter-result .count {
      font-size: 1.4rem;
      color: var(--accent);
      font-weight: bold;
    }

    /* ─── FOOTER ─────────────────────────────────────────────── */
    footer {
      text-align: center;
      color: var(--border);
      font-size: 0.72rem;
      padding: 24px;
      border-top: 1px solid var(--border);
      margin-top: 48px;
    }
    footer span { color: var(--accent); }
  </style>
</head>
<body>

<!-- ══════════════════════════════════════════════════════════
     HEADER
═══════════════════════════════════════════════════════════ -->
<header>
  <div>
    <div class="logo">◈ CALIFICACIONES ISC</div>
    <p>Práctica: Análisis y visualización con Pandas & Matplotlib &nbsp;|&nbsp; Dashboard Interactivo</p>
  </div>
</header>

<!-- ══════════════════════════════════════════════════════════
     NAV TABS
═══════════════════════════════════════════════════════════ -->
<nav>
  <button class="active" onclick="switchTab('graficas', this)">▣ Gráficas</button>
  <button onclick="switchTab('promedios', this)">▣ Promedios</button>
  <button onclick="switchTab('filtros', this)">▣ Filtros</button>
  <button onclick="switchTab('datos', this)">▣ Dataset</button>
</nav>

<!-- ══════════════════════════════════════════════════════════
     MAIN
═══════════════════════════════════════════════════════════ -->
<main>

  <!-- ── ESTADÍSTICAS RÁPIDAS (siempre visibles) ────────────── -->
  <div class="stats-row" style="margin-bottom:28px">
    <div class="stat-card">
      <div class="val">{{ stats.total }}</div>
      <div class="lbl">Registros totales</div>
    </div>
    <div class="stat-card">
      <div class="val">{{ stats.alumnos }}</div>
      <div class="lbl">Alumnos</div>
    </div>
    <div class="stat-card">
      <div class="val">{{ "%.1f"|format(stats.prom_global) }}</div>
      <div class="lbl">Promedio global</div>
    </div>
    <div class="stat-card">
      <div class="val">{{ stats.aprobados }}%</div>
      <div class="lbl">Aprobados</div>
    </div>
    <div class="stat-card">
      <div class="val">{{ stats.reprobados }}%</div>
      <div class="lbl">Reprobados</div>
    </div>
  </div>

  <!-- ══ TAB: GRÁFICAS ══════════════════════════════════════ -->
  <div id="tab-graficas" class="tab-content active">
    <p class="section-title">Visualizaciones</p>
    <div class="charts-grid">

      <div class="chart-card">
        <h3>Promedio por Materia</h3>
        {% if imgs.bar %}
          <img src="data:image/png;base64,{{ imgs.bar }}" alt="Promedio por materia"/>
        {% else %}
          <div class="chart-placeholder">Ejecuta practica_pandas.py para generar esta gráfica</div>
        {% endif %}
      </div>

      <div class="chart-card">
        <h3>Distribución de Calificaciones</h3>
        {% if imgs.hist %}
          <img src="data:image/png;base64,{{ imgs.hist }}" alt="Histograma"/>
        {% else %}
          <div class="chart-placeholder">Ejecuta practica_pandas.py para generar esta gráfica</div>
        {% endif %}
      </div>

      <div class="chart-card" style="grid-column: 1 / -1;">
        <h3>Tendencia por Unidad y Materia</h3>
        {% if imgs.line %}
          <img src="data:image/png;base64,{{ imgs.line }}" alt="Tendencia por unidad"/>
        {% else %}
          <div class="chart-placeholder">Ejecuta practica_pandas.py para generar esta gráfica</div>
        {% endif %}
      </div>

    </div>
  </div><!-- /tab-graficas -->

  <!-- ══ TAB: PROMEDIOS ═════════════════════════════════════ -->
  <div id="tab-promedios" class="tab-content">
    <p class="section-title">Promedios por Alumno</p>
    {% if prom_rows %}
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Matrícula</th>
            <th>Nombre</th>
            <th>Promedio General</th>
            <th>Situación</th>
          </tr>
        </thead>
        <tbody>
          {% for r in prom_rows %}
          <tr>
            <td>{{ loop.index }}</td>
            <td>{{ r.matricula }}</td>
            <td>{{ r.nombre }}</td>
            <td class="{{ 'low' if r.promedio_general < 70 else '' }}">
              {{ "%.2f"|format(r.promedio_general) }}
            </td>
            <td class="{{ 'low' if r.promedio_general < 70 else '' }}">
              {{ "Reprobado" if r.promedio_general < 70 else "Aprobado" }}
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    {% else %}
    <p style="color:var(--muted)">Ejecuta <code>practica_pandas.py</code> primero para generar <code>promedios_alumnos.csv</code>.</p>
    {% endif %}
  </div><!-- /tab-promedios -->

  <!-- ══ TAB: FILTROS ═══════════════════════════════════════ -->
  <div id="tab-filtros" class="tab-content">
    <p class="section-title">Filtros Interactivos</p>

    <div class="filter-grid">
      <div class="filter-group">
        <label>Grupo</label>
        <select id="f-grupo">
          <option value="">Todos</option>
          <option value="A">Grupo A</option>
          <option value="B">Grupo B</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Materia</label>
        <select id="f-materia">
          <option value="">Todas</option>
          <option>Programacion</option>
          <option>Bases de datos</option>
          <option>Redes</option>
          <option>Matematicas discretas</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Unidad</label>
        <select id="f-unidad">
          <option value="">Todas</option>
          <option value="1">Unidad 1</option>
          <option value="2">Unidad 2</option>
          <option value="3">Unidad 3</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Calificación mínima</label>
        <input type="number" id="f-cal-min" min="0" max="100" placeholder="0"/>
      </div>
      <div class="filter-group">
        <label>Calificación máxima</label>
        <input type="number" id="f-cal-max" min="0" max="100" placeholder="100"/>
      </div>
      <div class="filter-group">
        <label>Situación</label>
        <select id="f-sit">
          <option value="">Todas</option>
          <option>Aprobado</option>
          <option>Reprobado</option>
        </select>
      </div>
    </div>

    <button class="btn" onclick="applyFilter()">▶ Aplicar Filtro</button>
    <button class="btn btn-secondary" onclick="resetFilter()">✕ Limpiar</button>

    <div id="filter-result" style="display:none"></div>
    <div id="filter-table-wrap" style="margin-top:16px;display:none" class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Matrícula</th><th>Nombre</th><th>Grupo</th>
            <th>Materia</th><th>Unidad</th><th>Calificación</th>
            <th>Situación</th>
          </tr>
        </thead>
        <tbody id="filter-tbody"></tbody>
      </table>
    </div>
  </div><!-- /tab-filtros -->

  <!-- ══ TAB: DATASET ═══════════════════════════════════════ -->
  <div id="tab-datos" class="tab-content">
    <p class="section-title">Dataset Completo (primeras 50 filas)</p>
    {% if raw_rows %}
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Matrícula</th><th>Nombre</th><th>Grupo</th>
            <th>Materia</th><th>Unidad</th>
            <th>Calificación</th><th>Asistencias</th>
          </tr>
        </thead>
        <tbody>
          {% for r in raw_rows %}
          <tr>
            <td>{{ r.matricula }}</td>
            <td>{{ r.nombre }}</td>
            <td>{{ r.grupo }}</td>
            <td>{{ r.materia }}</td>
            <td>{{ r.unidad }}</td>
            <td class="{{ 'low' if r.calificacion < 70 else '' }}">{{ r.calificacion }}</td>
            <td>{{ r.asistencias }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    {% else %}
    <p style="color:var(--muted)">No se encontró <code>calificaciones_isc.csv</code>. Ejecuta <code>practica_pandas.py</code> primero.</p>
    {% endif %}
  </div><!-- /tab-datos -->

</main>

<footer>
  Dashboard Cyberpunk · Práctica Pandas &amp; Matplotlib · <span>ISC</span>
</footer>

<!-- ══════════════════════════════════════════════════════════
     JAVASCRIPT
═══════════════════════════════════════════════════════════ -->
<script>
  // ── Tab switching ──────────────────────────────────────────
  function switchTab(name, btn) {
    document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));
    document.querySelectorAll("nav button").forEach(b => b.classList.remove("active"));
    document.getElementById("tab-" + name).classList.add("active");
    btn.classList.add("active");
  }

  // ── Filter API call ───────────────────────────────────────
  function applyFilter() {
    const params = new URLSearchParams({
      grupo:   document.getElementById("f-grupo").value,
      materia: document.getElementById("f-materia").value,
      unidad:  document.getElementById("f-unidad").value,
      cal_min: document.getElementById("f-cal-min").value || "0",
      cal_max: document.getElementById("f-cal-max").value || "100",
      sit:     document.getElementById("f-sit").value,
    });

    fetch("/api/filter?" + params)
      .then(r => r.json())
      .then(data => {
        const res = document.getElementById("filter-result");
        const wrap = document.getElementById("filter-table-wrap");
        res.style.display = "block";
        wrap.style.display = "block";

        res.innerHTML = `
          Resultado: <span class="count">${data.count}</span> registros encontrados
          &nbsp;|&nbsp; Promedio de calificación: <span class="count">${data.prom}</span>
        `;

        const tbody = document.getElementById("filter-tbody");
        tbody.innerHTML = data.rows.map(r => `
          <tr>
            <td>${r.matricula}</td>
            <td>${r.nombre}</td>
            <td>${r.grupo}</td>
            <td>${r.materia}</td>
            <td>${r.unidad}</td>
            <td class="${parseFloat(r.calificacion) < 70 ? 'low' : ''}">${r.calificacion}</td>
            <td class="${r.situacion === 'Reprobado' ? 'low' : ''}">${r.situacion || ''}</td>
          </tr>
        `).join("");
      })
      .catch(err => console.error(err));
  }

  function resetFilter() {
    ["f-grupo","f-materia","f-unidad","f-sit"].forEach(id => document.getElementById(id).value = "");
    ["f-cal-min","f-cal-max"].forEach(id => document.getElementById(id).value = "");
    document.getElementById("filter-result").style.display = "none";
    document.getElementById("filter-table-wrap").style.display = "none";
  }
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# ROUTES
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Página principal del dashboard."""
    # Imágenes
    imgs = {
        "bar":  img_to_b64(IMG_BAR),
        "hist": img_to_b64(IMG_HIST),
        "line": img_to_b64(IMG_LINE),
    }

    # Promedios por alumno
    prom_rows = []
    if os.path.exists(PROM_FILE):
        df_prom = pd.read_csv(PROM_FILE, encoding="utf-8-sig")
        prom_rows = df_prom.to_dict(orient="records")

    # Dataset raw (primeras 50 filas)
    raw_rows = []
    if os.path.exists(CSV_FILE):
        df_raw = pd.read_csv(CSV_FILE, encoding="utf-8-sig").head(50)
        raw_rows = df_raw.to_dict(orient="records")

    # Estadísticas rápidas
    stats = {"total": 0, "alumnos": 0, "prom_global": 0,
             "aprobados": 0, "reprobados": 0}
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
        stats["total"]      = len(df)
        stats["alumnos"]    = df["matricula"].nunique()
        stats["prom_global"] = round(df["calificacion"].mean(), 2)
        sit = (df["calificacion"] >= 70).mean() * 100
        stats["aprobados"]  = round(sit, 1)
        stats["reprobados"] = round(100 - sit, 1)

    return render_template_string(HTML,
                                  imgs=imgs,
                                  prom_rows=prom_rows,
                                  raw_rows=raw_rows,
                                  stats=stats)


@app.route("/api/filter")
def api_filter():
    """API de filtros — devuelve JSON con los registros filtrados."""
    if not os.path.exists(CSV_FILE):
        return jsonify({"count": 0, "prom": "N/A", "rows": []})

    df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")

    # Aplicar columna situacion si no existe
    if "situacion" not in df.columns:
        df["situacion"] = df["calificacion"].apply(
            lambda x: "Aprobado" if x >= 70 else "Reprobado"
        )

    grupo   = request.args.get("grupo", "")
    materia = request.args.get("materia", "")
    unidad  = request.args.get("unidad", "")
    sit     = request.args.get("sit", "")
    cal_min = float(request.args.get("cal_min", 0))
    cal_max = float(request.args.get("cal_max", 100))

    mask = (df["calificacion"] >= cal_min) & (df["calificacion"] <= cal_max)
    if grupo:
        mask &= df["grupo"] == grupo
    if materia:
        mask &= df["materia"] == materia
    if unidad:
        mask &= df["unidad"] == int(unidad)
    if sit:
        mask &= df["situacion"] == sit

    result = df[mask].head(200)  # máx 200 filas en tabla
    prom   = round(result["calificacion"].mean(), 2) if len(result) > 0 else "N/A"

    return jsonify({
        "count": int(mask.sum()),
        "prom":  prom,
        "rows":  result.to_dict(orient="records"),
    })


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("  Dashboard Cyberpunk — Calificaciones ISC")
    print("  URL: http://127.0.0.1:5000")
    print("=" * 60)
    if not os.path.exists(CSV_FILE):
        print("[!] No se encontró calificaciones_isc.csv.")
        print("    Ejecuta primero: python practica_pandas.py")
    app.run(debug=True, port=5000)
