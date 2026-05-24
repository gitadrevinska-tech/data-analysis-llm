# 🤖 Automātiskā Datu Analīze ar LLM

Rīks kas automātiski analizē MySQL datubāzi un ģenerē PDF atskaiti ar vizualizācijām, izmantojot OpenRouter API (Claude modelis).

## Kā tas strādā

1. **Savienojums** — lietotājs UI ievada DB savienojuma datus un izvēlas datubāzi
2. **Shēmas analīze** — sistēma nolasa datubāzes struktūru (tabulas, kolonnas, foreign keys, datu paraugi)
3. **Plāna ģenerēšana** — LLM izveido 5–7 vizualizāciju plānu balstoties uz shēmu
4. **SQL + Grafiki** — katram plāna punktam LLM ģenerē SQL, izpilda to, izveido grafiku un raksta analīzi
5. **PDF atskaite** — visi grafiki un ieskati tiek apkopoti PDF dokumentā

## Uzstādīšana

### 1. Klonē repozitoriju

```bash
git clone https://github.com/gitadrevinska-tech/data-analysis-llm.git
cd data-analysis-llm
```

### 2. Konfigurē

Izveido `.env` failu (skatīt `.env.example` kā paraugu):

```env
OPENROUTER_API_KEY=sk-or-...tava-atslega...
DB_HOST=
DB_PORT=3306
DB_USER=
DB_PASSWORD=
DB_NAME=
```

> **Piezīme:** DB datus var arī ievadīt tieši UI — nav obligāti jāraksta `.env` failā.

### 3. Palaid ar Docker Compose

```bash
docker compose up -d
```

### 4. Atver pārlūku

## Web UI

Atverot `http://localhost:5000`:

- **Datubāzes konfigurācija** — ievadi host, port, lietotāju, paroli un nospied "Savienoties"
- **Datubāzes izvēle** — no dropdown izvēlies datubāzi vai ievadi manuāli
- **Sākt Analīzi** — palaiž visu procesu ar vienu pogu
- **Izpildes žurnāls** — rāda progresu reāllaikā
- **Pārskatu vēsture** — saglabā visus pārskatus ar datubāzes nosaukumu un lejupielādes pogu

## Docker arhitektūra

Projekts sastāv no diviem konteineriem:

| Konteiners | Funkcija | Ports |
|---|---|---|
| data-analysis-llm | Galvenais analīzes process | — |
| data-analysis-ui | Web interfeiss (Flask) | 5000 |

## Projekta struktūra

## Tehnoloģijas

| Komponente | Tehnoloģija |
|---|---|
| LLM | OpenRouter API (claude-sonnet-4-5) |
| Datubāze | MySQL (mysql-connector-python) |
| Vizualizācijas | matplotlib + seaborn |
| Datu apstrāde | pandas |
| PDF ģenerēšana | reportlab |
| Web UI | Flask |
| Konteineri | Docker + Docker Compose |

## Prasības

- Docker Desktop
- OpenRouter API atslēga
- Piekļuve MySQL serverim
