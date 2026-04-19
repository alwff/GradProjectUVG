import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.markers import MarkerStyle
from matplotlib.ticker import FuncFormatter
from datetime import datetime
from matplotlib.gridspec import GridSpec

# ======================================
# TAREAS
# ======================================

tasks = [

    {"name": "Diseño arquitectura del sistema",
     "start": "2026-03-15", "end": "2026-04-05",
     "progress": 0, "depends_on": [], "milestone": False, "tipo": "dev"},

    {"name": "Adquisición de equipos y materiales",
     "start": "2026-04-20", "end": "2026-04-30",
     "progress": 0, "depends_on": ["Diseño arquitectura del sistema"],
     "milestone": False, "tipo": "dev"},

    {"name": "Modelado y creación base de datos",
     "start": "2026-04-01", "end": "2026-04-25",
     "progress": 0, "depends_on": ["Diseño arquitectura del sistema"],
     "milestone": False, "tipo": "dev"},

    {"name": "Implementación lector código barras",
     "start": "2026-04-20", "end": "2026-05-15",
     "progress": 0, "depends_on": ["Modelado y creación base de datos"],
     "milestone": False, "tipo": "dev"},

    {"name": "Integración lector con base de datos",
     "start": "2026-05-10", "end": "2026-05-30",
     "progress": 0, "depends_on": ["Implementación lector código barras"],
     "milestone": False, "tipo": "dev"},

    {"name": "Desarrollo entorno base Unity",
     "start": "2026-04-15", "end": "2026-05-20",
     "progress": 0, "depends_on": ["Diseño arquitectura del sistema"],
     "milestone": False, "tipo": "dev"},

    {"name": "Implementación cuadros interactivos",
     "start": "2026-05-20", "end": "2026-06-15",
     "progress": 0, "depends_on": ["Desarrollo entorno base Unity"],
     "milestone": False, "tipo": "dev"},

    {"name": "Implementación modo Web",
     "start": "2026-06-15", "end": "2026-07-15",
     "progress": 0, "depends_on": ["Integración lector con base de datos"],
     "milestone": False, "tipo": "dev"},

    {"name": "Implementación modo VR",
     "start": "2026-07-01", "end": "2026-08-15",
     "progress": 0, "depends_on": ["Implementación modo Web"],
     "milestone": False, "tipo": "dev"},

    {"name": "Integración base datos",
     "start": "2026-08-01", "end": "2026-08-31",
     "progress": 0, "depends_on": ["Implementación modo VR"],
     "milestone": False, "tipo": "dev"},

    {"name": "Pruebas funcionales",
     "start": "2026-09-01", "end": "2026-09-30",
     "progress": 0, "depends_on": ["Integración base datos"],
     "milestone": False, "tipo": "dev"},

    {"name": "Optimización de rendimiento",
     "start": "2026-09-20", "end": "2026-10-10",
     "progress": 0, "depends_on": ["Pruebas funcionales"],
     "milestone": False, "tipo": "dev"},

    {"name": "Redacción trabajo de graduación",
     "start": "2026-08-15", "end": "2026-11-05",
     "progress": 0, "depends_on": ["Pruebas funcionales"],
     "milestone": False, "tipo": "doc"},

    # HITOS
    {"name": "Entrega Trabajo Graduación",
     "start": "2026-11-05", "end": "2026-11-05",
     "progress": 0, "depends_on": ["Redacción trabajo de graduación"],
     "milestone": True, "tipo": "milestone"},

    {"name": "Entrega Póster Científico",
     "start": "2026-11-15", "end": "2026-11-15",
     "progress": 0, "depends_on": ["Entrega Trabajo Graduación"],
     "milestone": True, "tipo": "milestone"},

    {"name": "Showcase Póster",
     "start": "2026-11-18", "end": "2026-11-18",
     "progress": 0, "depends_on": ["Entrega Póster Científico"],
     "milestone": True, "tipo": "milestone"},
]

# ======================================
# DATAFRAME
# ======================================

df = pd.DataFrame(tasks)
df["start"] = pd.to_datetime(df["start"])
df["end"] = pd.to_datetime(df["end"])
df["duration"] = (df["end"] - df["start"]).dt.days
df = df.iloc[::-1].reset_index(drop=True)

# ======================================
# COLORES
# ======================================

COLOR_DEV = "#5F6F7A"
COLOR_DOC = "#6C5B7B"
MILESTONE_COLOR = "#B0B7C3"
MILESTONE_EDGE = "#6C757D"
TODAY_COLOR = "#D62828"

# ======================================
# FIGURA
# ======================================

fig = plt.figure(figsize=(15, 8))
gs = GridSpec(1, 2, width_ratios=[1.3, 4], wspace=0.02)

ax_legend = fig.add_subplot(gs[0])
ax = fig.add_subplot(gs[1])

ax.set_facecolor("#F8F9FA")
ax_legend.set_facecolor("#F1F3F5")

today_dt = datetime.today()

# ======================================
# LEYENDA
# ======================================

for i, task in df.iterrows():
    numero = len(df) - i
    ax_legend.text(0.1, i,
                   f"{numero}. {task['name']}",
                   va="center",
                   fontsize=12)

ax_legend.set_xlim(0, 1)
ax_legend.set_ylim(-1, len(df))
ax_legend.axis("off")

# ======================================
# GANTT
# ======================================

for i, task in df.iterrows():
    numero = len(df) - i

    if task["milestone"]:
        ax.scatter(task["start"], i,
                   marker=MarkerStyle("D"),
                   s=90,
                   facecolor=MILESTONE_COLOR,
                   edgecolor=MILESTONE_EDGE,
                   linewidth=1.2)
    else:
        color = COLOR_DEV if task["tipo"] == "dev" else COLOR_DOC
        ax.barh(i, task["duration"], left=task["start"], height=0.6, color=color)

        ax.text(task["start"] + pd.Timedelta(days=2),
                i,
                str(numero),
                va="center",
                ha="left",
                color="white",
                fontsize=11,
                weight="bold")

# ======================================
# DEPENDENCIAS
# ======================================

task_positions = {row["name"]: idx for idx, row in df.iterrows()}

for i, task in df.iterrows():
    for dep in task["depends_on"]:
        if dep in task_positions:
            dep_index = task_positions[dep]
            ax.annotate("",
                        xy=(task["start"], i),
                        xytext=(df.loc[dep_index, "end"], dep_index),
                        arrowprops=dict(
                            arrowstyle="->",
                            color="black",
                            linewidth=1.2,
                            connectionstyle="angle3,angleA=0,angleB=90"
                        ))

# Línea hoy
#ax.axvline(mdates.date2num(today_dt),
#           color=TODAY_COLOR,
#           linestyle="--",
#           linewidth=1.5)

# ======================================
# EJE EN ESPAÑOL + SEMANAS
# ======================================

meses_es = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
}

def formato_mes(x, pos=None):
    fecha = mdates.num2date(x)
    return meses_es[fecha.month]

def semana_del_mes(x, pos=None):
    fecha = mdates.num2date(x)
    semana = (fecha.day - 1) // 7 + 1
    return f"S{semana}"

ax.set_xlim(df["start"].min(),
            pd.to_datetime("2026-11-30"))

ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(FuncFormatter(formato_mes))

ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
ax.xaxis.set_minor_formatter(FuncFormatter(semana_del_mes))

ax.tick_params(axis='x', which='major', pad=25, labelsize=13)
ax.tick_params(axis='x', which='minor', labelsize=12)

ax.grid(which="major", axis="x", color="#DADDE2", linewidth=1.2)
ax.grid(which="minor", axis="x", color="#ECEFF3", linestyle="--", alpha=0.4)

ax.set_yticks([])

for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)

plt.suptitle("Diagrama de Gantt", fontsize=16, weight="bold")
plt.subplots_adjust(left=0.05, right=0.98, top=0.90, bottom=0.10)

plt.savefig(r"C:\Users\aleja\Downloads\gantt_final.png", dpi=300)

plt.show()

