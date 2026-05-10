"""
main.py — Galvenais skripts. Palaid ar: python main.py
"""
import os, sys
from config import OPENROUTER_API_KEY, OUTPUT_DIR, CHARTS_DIR

def check_config():
    if "IERAKSTI" in OPENROUTER_API_KEY:
        print("Ludzu ieraksti savu OpenRouter API atslegu config.py faila!")
        sys.exit(1)

def main():
    print("=" * 65)
    print("  AUTOMATISKA DATU ANALIZE AR LLM")
    print("=" * 65)
    check_config()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(CHARTS_DIR, exist_ok=True)

    from db_utils import get_schema
    from config import DB_CONFIG
    import step1_plan_generator as step1
    import step2_chart_generator as step2
    import step3_pdf_builder as step3

    database = DB_CONFIG["database"]
    print(f"\n Datubaze: {database}")

    print("\n" + "-"*65)
    print("  1. SOLIS: PLANA GENERESANA")
    print("-"*65)
    schema = get_schema(database)
    plan = step1.generate_plan(schema)
    if not plan:
        print("Neizdevas generert planu!"); sys.exit(1)
    print(f"\n {len(plan)} vizuali plana:")
    for i, item in enumerate(plan, 1):
        print(f"   {i}. [{item['chart_type']}] {item['name']}")

    print("\n" + "-"*65)
    print("  2. SOLIS: SQL + GRAFIKI + IESKATI")
    print("-"*65)
    results = step2.run(plan, database, schema)
    success = sum(1 for r in results if not r.get("error"))
    print(f"\n {success}/{len(results)} vizuali veiksmigi")

    print("\n" + "-"*65)
    print("  3. SOLIS: PDF GENERESANA")
    print("-"*65)
    pdf_path = step3.build_pdf(results, database)

    print("\n" + "="*65)
    print("  VISS PABEIGTS!")
    print("="*65)
    print(f"  PDF: {os.path.abspath(pdf_path)}")
    print(f"  Grafiki: {os.path.abspath(CHARTS_DIR)}/")
    print("="*65)

if __name__ == "__main__":
    main()
