"""
step2_chart_generator.py — 2. rīks: SQL + vizualizācija + ieskati katram plāna punktam.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from config import CHARTS_DIR
from db_utils import run_query, validate_sql
from llm_utils import ask_llm

os.makedirs(CHARTS_DIR, exist_ok=True)
sns.set_theme(style="whitegrid", palette="muted")
COLORS = sns.color_palette("muted", 12)

# ── SQL ──────────────────────────────────────────────────────────────────────

SQL_SYSTEM = """Tu esi MySQL eksperts. Ģenerē TIKAI SQL vaicājumu bez jebkāda cita teksta,
bez ```sql``` blokiem, bez komentāriem. Tikai tīrs SQL kas beidzas ar semikolu.
Vaicājumam jāatgriež MAX 50 rindas. Izmanto LIMIT kur nepieciešams.
Skaitliskās vērtības noapaļo līdz 2 decimālzīmēm."""

def generate_sql(schema: str, plan_item: dict, database: str) -> str:
    prompt = f"""Datubāze: {database}
Shēma:
{schema}

Vizualizācija: {plan_item['name']}
Apraksts: {plan_item['description']}
Vizuāla tips: {plan_item['chart_type']}
SQL ieteikumi: {plan_item.get('sql_hints', '')}

Uzraksti SQL vaicājumu lai izgūtu datus šim vizuālim."""
    sql = ask_llm(SQL_SYSTEM, prompt, max_tokens=500)
    return sql.replace("```sql", "").replace("```", "").strip()

# ── Vizualizācija ─────────────────────────────────────────────────────────────

VIZ_SYSTEM = """Tu esi Python matplotlib/seaborn eksperts.
Ģenerē TIKAI Python kodu bez jebkāda teksta vai paskaidrojumiem. Bez ```python``` blokiem.

Pieejamie mainīgie (jau definēti): df, out_path, title, plt, sns, pd, COLORS

Prasības:
- fig, ax = plt.subplots(figsize=(10, 6))
- ax.set_title(title, fontsize=14, fontweight='bold')
- Uzstādi ass nosaukumus
- Beidzot: plt.tight_layout(); plt.savefig(out_path, dpi=150, bbox_inches='tight'); plt.close()
- Ja datu ir daudz, parādi TOP 15
- ax.tick_params(axis='x', rotation=45) ja nepieciešams
- Neizmanto plt.show()"""

def generate_chart_code(plan_item: dict, df: pd.DataFrame) -> str:
    col_info = {col: str(df[col].dtype) for col in df.columns}
    prompt = f"""Vizualizācija: {plan_item['name']}
Vizuāla tips: {plan_item['chart_type']}
Apraksts: {plan_item['description']}
DataFrame kolonnas: {col_info}
Datu paraugs: {df.head(3).to_dict(orient='records')}
Kopā rindas: {len(df)}

Uzraksti Python kodu šī vizuāļa izveidošanai."""
    code = ask_llm(VIZ_SYSTEM, prompt, max_tokens=800)
    return code.replace("```python", "").replace("```", "").strip()

def execute_chart_code(code: str, df: pd.DataFrame, out_path: str, title: str) -> bool:
    local_vars = {"df": df.copy(), "out_path": out_path, "title": title,
                  "plt": plt, "sns": sns, "pd": pd, "COLORS": COLORS}
    try:
        exec(code, local_vars)
        return True
    except Exception as e:
        print(f"    ⚠️  Koda kļūda: {e} — izmantoju rezerves grafiku")
        _fallback_chart(df, out_path, title)
        return False

def _fallback_chart(df, out_path, title):
    fig, ax = plt.subplots(figsize=(10, 6))
    num_cols = df.select_dtypes("number").columns.tolist()
    if num_cols and len(df.columns) >= 2:
        x_col, y_col = df.columns[0], num_cols[0]
        data = df.nlargest(15, y_col) if len(df) > 15 else df
        ax.bar(data[x_col].astype(str), data[y_col], color=COLORS[0])
        ax.set_xlabel(x_col); ax.set_ylabel(y_col)
    else:
        ax.text(0.5, 0.5, "Nav pietiekamu datu", ha="center", va="center", transform=ax.transAxes)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout(); plt.savefig(out_path, dpi=150, bbox_inches="tight"); plt.close()

# ── Ieskati ───────────────────────────────────────────────────────────────────

INSIGHT_SYSTEM = """Tu esi datu analītiķis. Uzraksti 3-5 teikumu analīzi latviešu valodā.
Iekļauj konkrētus skaitļus, tendences un svarīgākos secinājumus. Sāc ar galveno atziņu."""

def generate_insight(plan_item: dict, df: pd.DataFrame) -> str:
    prompt = f"""Vizualizācija: {plan_item['name']}
Apraksts: {plan_item['description']}
Datu statistika:\n{df.describe(include='all').to_string()}
Pirmās 5 rindas:\n{df.head(5).to_string()}
Uzraksti analīzi latviešu valodā."""
    return ask_llm(INSIGHT_SYSTEM, prompt, max_tokens=400)

# ── Galvenā funkcija ──────────────────────────────────────────────────────────

def process_plan_item(plan_item: dict, database: str, schema: str, index: int) -> dict:
    print(f"\n{'='*60}\n  📊 {index}. {plan_item['name']}\n{'='*60}")
    result = {"name": plan_item["name"], "description": plan_item["description"],
              "chart_type": plan_item["chart_type"], "chart_path": None,
              "insight": "", "sql": "", "error": None}

    print("  1️⃣  Ģenerēju SQL...")
    sql = generate_sql(schema, plan_item, database)
    result["sql"] = sql
    print(f"     {sql[:100]}...")

    valid, err = validate_sql(database, sql)
    if not valid:
        print(f"  ⚠️  SQL kļūda, mēģinu vēlreiz: {err}")
        plan_item2 = dict(plan_item)
        plan_item2["sql_hints"] = plan_item.get("sql_hints","") + f" KĻŪDA: {err}"
        sql = generate_sql(schema, plan_item2, database)
        result["sql"] = sql
        valid, err = validate_sql(database, sql)
        if not valid:
            result["error"] = f"SQL kļūda: {err}"; return result

    print("  2️⃣  Izpildu SQL...")
    try:
        df = run_query(database, sql)
        print(f"     ✅ {len(df)} rindas, {len(df.columns)} kolonnas")
    except Exception as e:
        result["error"] = str(e); return result

    if df.empty:
        result["error"] = "Nav datu"; return result

    print("  3️⃣  Ģenerēju grafiku...")
    out_path = os.path.join(CHARTS_DIR, f"chart_{index:02d}.png")
    code = generate_chart_code(plan_item, df)
    execute_chart_code(code, df, out_path, plan_item["name"])
    result["chart_path"] = out_path
    print(f"     ✅ Saglabāts: {out_path}")

    print("  4️⃣  Ģenerēju ieskatus...")
    result["insight"] = generate_insight(plan_item, df)
    print(f"     ✅ Ieskats gatavs")

    return result

def run(plan: list, database: str, schema: str) -> list:
    return [process_plan_item(item, database, schema, i) for i, item in enumerate(plan, 1)]
