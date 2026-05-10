"""
step1_plan_generator.py — 1. rīks: LLM ģenerē vizualizāciju plānu no DB shēmas.
"""
from config import PLAN_SEPARATOR
from db_utils import get_schema
from llm_utils import ask_llm

PLAN_SYSTEM_PROMPT = """Tu esi datu analītiķis. Tev tiek dota MySQL datubāzes shēma.
Tava uzdevums ir izveidot vizualizāciju plānu.

Katrs plāna punkts ir TIEŠI šādā formātā (izmanto tieši šīs atslēgvārdus):
NOSAUKUMS: <īss vizualizācijas nosaukums latviešu valodā>
APRAKSTS: <ko šis vizuālis parādīs>
CHART_TYPE: <viens no: bar_chart, line_chart, pie_chart, scatter_plot, histogram, heatmap, box_plot>
SQL_HINTS: <tabulas un kolonnas kas jāizmanto>
---VIZUALIS---

Izveido 5-7 dažādus vizuāļus. Atbildi tikai ar plānu, bez ievada teksta.
"""

def generate_plan(schema: str) -> list:
    print("⏳ Ģenerēju vizualizāciju plānu ar LLM...")
    raw_text = ask_llm(
        system=PLAN_SYSTEM_PROMPT,
        user=f"Lūdzu izveido vizualizāciju plānu šai datubāzei:\n\n{schema}",
        max_tokens=2000,
    )
    print("\n📋 LLM plāns:\n")
    print(raw_text)
    print("\n" + "="*60 + "\n")

    plan_items = []
    for section in raw_text.split("---VIZUALIS---"):
        section = section.strip()
        if not section:
            continue
        item = {}
        for line in section.split("\n"):
            line = line.strip()
            if not line or ":" not in line:
                continue
            key, _, val = line.partition(":")
            key = key.strip().upper()
            val = val.strip()
            if "NOSAUKUMS" in key:
                item["name"] = val
            elif "APRAKSTS" in key:
                item["description"] = val
            elif "CHART_TYPE" in key or "TIPS" in key or "TYPE" in key:
                item["chart_type"] = val
            elif "SQL" in key:
                item["sql_hints"] = val

        # Ja nav chart_type, uzstāda noklusējumu
        if "name" in item:
            if "chart_type" not in item:
                item["chart_type"] = "bar_chart"
            if "description" not in item:
                item["description"] = item["name"]
            plan_items.append(item)

    print(f"✅ Parsēti {len(plan_items)} plāna punkti")
    return plan_items
