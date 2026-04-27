"""Application FastAPI du microservice ms6-validateur-capteur.

Point d'entree uvicorn : `uvicorn src.validator:app --host 0.0.0.0 --port 8000`.

L'application est volontairement minimaliste et delegue :
  - la configuration des seuils a `src.config`
  - la logique metier a `src.logic`
  - les schemas Pydantic a `src.schemas`
  - les routes HTTP a `src.routes`
"""
from fastapi import FastAPI

from src.routes import router


app = FastAPI(
    title="UrbanHub - MS6 Validateur de donnees capteur",
    version="1.0.0",
    description=(
        "Valide et classifie les donnees capteur (co2, temperature, noise, "
        "pm25, humidity) selon des seuils modere / critique."
    ),
)
app.include_router(router)
