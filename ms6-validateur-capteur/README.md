# MS6 — Validateur de donnees capteur (UrbanHub)

Numero etudiant : MI202627
Epreuve : EC03 Partie 1 — Pipelines CI/CD
Session : avril 2026

## Role

Microservice de validation et classification des donnees capteur de la plateforme UrbanHub.
Joue le role de "porte de qualite" entre la collecte IoT et le traitement d'evenements :
chaque mesure brute est evaluee par rapport a deux seuils (modere et critique) et
classifiee normal / moderate / critical.

Couvre les exigences BC01 :
- EX-ENV-02 : seuils de pollution configurables (`src/config.py`)
- EX-ENV-03 : depassements generent des evenements classifies (level critical -> valid=false)
- EX-INC-02 : incidents horodates (timestamp UTC ISO-8601)

## Endpoints

- `POST /validate` — valide une donnee capteur
- `GET /health` — healthcheck (utilise par le compose)
- `GET /docs` — documentation OpenAPI (utilise par le job build du pipeline)

### Exemples

```json
POST /validate  { "sensor": "co2", "value": 500.0 }
-> { "valid": true, "level": "normal", "sensor": "co2", "value": 500.0,
     "threshold": 800, "timestamp": "2026-04-27T09:00:00Z" }

POST /validate  { "sensor": "co2", "value": 1500.0 }
-> { "valid": false, "level": "critical", "sensor": "co2", "value": 1500.0,
     "threshold": 1000, "timestamp": "2026-04-27T09:00:00Z" }

POST /validate  { "sensor": "ghost", "value": 1.0 }
-> { "valid": false, "level": "unknown", "message": "Capteur non repertorie" }
```

### Capteurs supportes (5 minimum, conforme au sujet)

| Capteur     | Modere | Critique | Unite   |
|-------------|--------|----------|---------|
| co2         | 800    | 1000     | ppm     |
| temperature | 35     | 40       | C       |
| noise       | 70     | 85       | dB      |
| pm25        | 25     | 50       | ug/m3   |
| humidity    | 70     | 85       | percent |

`humidity` est le **capteur supplementaire** ajoute conformement a la consigne
"ajouter au moins un capteur supplementaire".

## Architecture (clean code modulaire — exigence C19.2)

```
src/
├── validator.py   # FastAPI app (point d'entree uvicorn)
├── routes.py      # router /validate, /health
├── logic.py       # validate_sensor_data() pure (testable sans HTTP)
├── schemas.py     # SensorData, ValidationResult (Pydantic)
└── config.py      # THRESHOLDS + get_thresholds()
```

Chaque fonction a une responsabilite unique. La logique metier (`logic.py`)
est independante de FastAPI et du protocole HTTP, ce qui facilite la
testabilite et la complexite cyclomatique faible mesuree par SonarCloud.

## Lancement local

```bash
pip install -r requirements.txt -r requirements-dev.txt
uvicorn src.validator:app --reload --host 0.0.0.0 --port 8000
# puis : http://localhost:8000/docs
```

## Tests + couverture (>= 80 %)

```bash
pytest tests/ \
  --tb=short \
  --junitxml=03_rapport_tests/rapport_tests.xml \
  --cov=src \
  --cov-report=term \
  --cov-report=xml:03_rapport_tests/coverage.xml \
  --cov-fail-under=80 \
  2>&1 | tee 03_rapport_tests/rapport_tests.txt
```

## Pipeline GitHub Actions

Workflow : `.github/workflows/ms6-validateur.yml`
Jobs sequentiels : **test → quality → build → deploy-staging**.

- `test` : pytest + coverage avec gate 80 %
- `quality` : SonarCloud + Snyk + flake8 (apres + avant via workflow_dispatch)
- `build` : docker build + push `ghcr.io/<org>/urbanhub/ms6-validateur:<sha>` puis `docker run` + `curl /docs`
- `deploy-staging` : `docker compose up -d ms6-validateur` puis vérification healthcheck

GitHub Secrets requis : `SONAR_TOKEN`, `SNYK_TOKEN`, `GHCR_TOKEN` (optionnel — `GITHUB_TOKEN` fonctionne aussi).

## Service docker-compose (groupe)

```yaml
ms6-validateur:
  image: ghcr.io/<org>/urbanhub/ms6-validateur:latest
  build: ./ms6-validateur-capteur
  ports: ["8006:8000"]
  networks: [urbanhub-network]
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/docs"]
    interval: 10s
    timeout: 3s
    retries: 5
```

## Declaration d'utilisation d'IA (obligatoire — Format de rendu EC03)

- **Outil IA utilise** : Cursor + Claude (Anthropic) — assistant de codage de l'IDE.
- **Parties concernees** :
  - Generation du squelette de `validator.py`, `logic.py`, `schemas.py`, `routes.py`, `config.py` a partir de la specification §3 du sujet.
  - Generation des tests `tests/test_validator.py` couvrant les 4 cas obligatoires (normal / moderate / critical / unknown) plus le capteur ajoute (humidity).
  - Generation du `Dockerfile`, du `requirements.txt` (versions fixees), du workflow `.github/workflows/ms6-validateur.yml`.
  - Aide a la redaction de la synthese `06_synthese/synthese_avant_apres.pdf`.
- **Prompts utilises** (extraits) :
  1. "Voici le sujet EC03 (PDF) et le format de rendu. Genere le scaffold du microservice ms6-validateur-capteur conforme exact au sujet : 5 capteurs, endpoint POST /validate, classification normal/moderate/critical/unknown, code modulaire (config + logic + schemas + routes + validator)."
  2. "Genere tests/test_validator.py avec au moins 5 tests pytest couvrant test_normal, test_moderate, test_critical, test_unknown_sensor, test_capteur_ajoute, plus tests de la logique pure pour atteindre >= 80 % de couverture."
  3. "Genere le workflow GitHub Actions a 4 jobs sequentiels test -> quality -> build -> deploy-staging conforme au sujet (push ghcr.io, docker run + curl /docs, port 8006:8000, secrets SONAR_TOKEN/SNYK_TOKEN/GHCR_TOKEN)."
  4. "Pour la phase 'apres' du livrable C18 : propose des versions epinglees securisees pour fastapi, uvicorn, pydantic et explique l'impact Snyk."

L'etudiant reste **entierement responsable** du code rendu : chaque fichier a ete relu, complete, adapte au contexte du monorepo `UrbanHub` (organisation `tsioryrobson`) et aux conventions deja en place dans le groupe (architecture hexagonale legere, sonar-project.properties, structure 03_rapport_tests / 04_analyse_avant / 05_analyse_apres / 06_synthese). Aucun copier-coller massif sans comprehension n'a ete realise.
