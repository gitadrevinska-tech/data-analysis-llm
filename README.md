# 🤖 Automātiskā Datu Analīze ar LLM

Rīks kas automātiski analizē MySQL datubāzi un ģenerē PDF atskaiti ar vizualizācijām, izmantojot Anthropic Claude API.

## Kā tas strādā

```
MySQL DB shēma
     │
     ▼
[1. Solis] LLM ģenerē vizualizāciju plānu
     │         (nosaukums, tips, SQL padomi)
     ▼
[2. Solis] Katram plāna punktam:
     │   ├── LLM ģenerē SQL vaicājumu
     │   ├── SQL tiek validēts un izpildīts
     │   ├── LLM ģenerē Python vizualizācijas kodu
     │   └── LLM ģenerē datu ieskatus (latviešu val.)
     ▼
[3. Solis] Visi vizuāļi + ieskati → PDF atskaite
```

## Uzstādīšana

### 1. Klonē repozitoriju

```bash
git clone https://github.com/Greyzly/data-analysis-llm.git
cd data-analysis-llm
```

### 2. Instalē atkarības

```bash
pip install -r requirements.txt
```

### 3. Konfigurē

Atver `config.py` un norādi savu Anthropic API atslēgu:

```python
ANTHROPIC_API_KEY = "sk-ant-..."   # <-- maini šo!
```

API atslēgu var iegūt: https://console.anthropic.com/

Datubāzes savienojuma dati arī atrodas `config.py`:

```python
DB_CONFIG = {
    "host": "87.110.123.151",
    "port": 3306,
    "user": "fita",
    "password": "2026-04-28",
}
```

### 4. Palaid

```bash
python main.py
```

## Rezultāts

Pēc izpildes mapē `output/` atradīsies:
- `report.pdf` — pilna PDF atskaite ar visiem vizuāļiem un analīzi
- `charts/` — individuālie grafiku PNG faili

## Projekta struktūra

```
data-analysis-llm/
├── main.py                  # Galvenais skripts
├── config.py                # Konfigurācija (DB + API)
├── db_utils.py              # MySQL savienojums un palīgfunkcijas
├── step1_plan_generator.py  # 1. rīks: LLM ģenerē vizualizāciju plānu
├── step2_chart_generator.py # 2. rīks: SQL + grafiki + ieskati
├── step3_pdf_builder.py     # 3. rīks: PDF atskaites celtniecība
├── requirements.txt         # Python atkarības
└── output/                  # Ģenerētie faili (tiek izveidots automātiski)
    ├── report.pdf
    └── charts/
```

## Tehnoloģijas

| Komponente | Tehnoloģija |
|---|---|
| LLM | Anthropic Claude (claude-sonnet-4) |
| Datubāze | MySQL (mysql-connector-python) |
| Vizualizācijas | matplotlib + seaborn |
| Datu apstrāde | pandas |
| PDF ģenerēšana | reportlab |

## Prasības

- Python 3.10+
- Anthropic API atslēga
- Piekļuve MySQL serverim
