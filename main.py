"""
main.py — Galvenais skripts. Palaid ar: python main.py
DB konfigurācija tiek nolasīta no vides mainīgajiem (iestata UI vai .env).
"""
import os, sys
 
 
def check_config():
    from config import OPENROUTER_API_KEY
    if "IERAKSTI" in OPENROUTER_API_KEY or not OPENROUTER_API_KEY:
        print("Lūdzu ieraksti savu OpenRouter API atslēgu .env failā!")
        sys.exit(1)
 
 
def main():
    print("=" * 65)
    print("  AUTOMĀTISKA DATU ANALĪZE AR LLM")
    print("=" * 65)
 
    check_config()
 
    from config import OUTPUT_DIR, CHARTS_DIR, DB_CONFIG
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(CHARTS_DIR, exist_ok=True)
 
    import step1_plan_generator as step1
    import step2_chart_generator as step2
    import step3_pdf_builder as step3
    from db_utils import get_schema
 
    # DB nosaukums — no env mainīgā (UI iestata) vai no config.py
    database = os.environ.get("DB_NAME") or DB_CONFIG.get("database", "")
    if not database:
        print("KĻŪDA: Datubāze nav norādīta! Iestatiet DB_NAME vai .env failu.")
        sys.exit(1)
 
    print(f"\n  Datubāze : {database}")
    print(f"  Host     : {DB_CONFIG.get('host', '?')}")
    print(f"  Izvade   : {OUTPUT_DIR}")
 
    # ── 1. SOLIS ────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  1. SOLIS: SHĒMAS NOLASĪŠANA UN PLĀNA ĢENERĒŠANA")
    print("-" * 65)
 
    try:
        schema = get_schema(database)
    except Exception as e:
        print(f"KĻŪDA: Nevar nolasīt shēmu — {e}")
        sys.exit(1)
 
    plan = step1.generate_plan(schema)
    if not plan:
        print("Neizdevās ģenerēt plānu!"); sys.exit(1)
 
    print(f"\n  {len(plan)} vizuāļi plānā:")
    for i, item in enumerate(plan, 1):
        print(f"   {i}. [{item.get('chart_type','?')}] {item.get('name','?')}")
 
    # ── 2. SOLIS ────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  2. SOLIS: SQL + GRAFIKI + IESKATI")
    print("-" * 65)
 
    results = step2.run(plan, database, schema)
    success = sum(1 for r in results if not r.get("error"))
    print(f"\n  ✅ {success}/{len(results)} vizuāļi veiksmīgi")
 
    # ── 3. SOLIS ────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  3. SOLIS: PDF ĢENERĒŠANA")
    print("-" * 65)
 
    pdf_path = step3.build_pdf(results, database)
 
    print("\n" + "=" * 65)
    print("  VISS PABEIGTS!")
    print("=" * 65)
    print(f"  PDF     : {os.path.abspath(pdf_path)}")
    print(f"  Grafiki : {os.path.abspath(CHARTS_DIR)}/")
    print("=" * 65)
 
 
if __name__ == "__main__":
    main()
 