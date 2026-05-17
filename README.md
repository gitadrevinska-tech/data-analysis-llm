\# 🤖 Automātiskā Datu Analīze ar LLM



Rīks kas automātiski analizē MySQL datubāzi un ģenerē PDF atskaiti ar vizualizācijām, izmantojot OpenRouter API (Claude modelis).



\## Kā tas strādā



\## Uzstādīšana



\### 1. Klonē repozitoriju

```bash

git clone https://github.com/gitadrevinska-tech/data-analysis-llm.git

cd data-analysis-llm

```



\### 2. Konfigurē

Izveido `.env` failu (skatīt `.env.example` kā paraugu):

```env

OPENROUTER\_API\_KEY=sk-or-...tava-atslega...

DB\_HOST=87.110.123.151

DB\_PORT=3306

DB\_USER=fita

DB\_PASSWORD=

DB\_NAME=direct\_payments

```



\### 3. Palaid ar Docker Compose

```bash

docker compose up -d

```



\### 4. Atver pārlūku



\## Docker Compose arhitektūra



Projekts sastāv no \*\*diviem konteineriem\*\*:



| Konteiners | Funkcija | Ports |

|---|---|---|

| `data-analysis-llm` | Galvenais analīzes process (Python) | — |

| `data-analysis-ui` | Web interfeiss (Flask) | 5000 |



Abi konteineri dalās ar kopīgu `output` mapi kur tiek saglabāti PDF un grafiki.



\## Web UI



Palaižot `docker compose up -d` un atverot `http://localhost:5000`:



\- \*\*Sākt Analīzi\*\* — palaiž visu procesu ar vienu pogu

\- \*\*Izpildes Žurnāls\*\* — rāda progresu reāllaikā

\- \*\*Pārskatu Vēsture\*\* — saglabā visus iepriekšējos pārskatus ar lejupielādes pogu



\## Rezultāts



Pēc izpildes mapē `output/` atradīsies:

\- `report.pdf` — pilna PDF atskaite ar visiem vizuāļiem un analīzi

\- `charts/` — individuālie grafiku PNG faili



\## Projekta struktūra



\## Tehnoloģijas



| Komponente | Tehnoloģija |

|---|---|

| LLM | OpenRouter API (claude-sonnet-4-5) |

| Datubāze | MySQL (mysql-connector-python) |

| Vizualizācijas | matplotlib + seaborn |

| Datu apstrāde | pandas |

| PDF ģenerēšana | reportlab |

| Web UI | Flask |

| Konteineri | Docker + Docker Compose |



\## Prasības



\- Docker Desktop

\- OpenRouter API atslēga

\- Piekļuve MySQL serverim

