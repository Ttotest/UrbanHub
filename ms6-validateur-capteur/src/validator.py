"""Application FastAPI du microservice ms6-validateur-capteur (UrbanHub).

Point d'entree uvicorn :

    uvicorn src.validator:app --host 0.0.0.0 --port 8000

L'application est volontairement minimaliste et delegue chaque
responsabilite a un module dedie (Clean Code C19.2) :

  - configuration des seuils  -> :mod:`src.config`
  - logique metier pure       -> :mod:`src.logic`
  - schemas Pydantic          -> :mod:`src.schemas`
  - routes HTTP               -> :mod:`src.routes`

Ce module ne contient donc que le wiring FastAPI.
"""
from fastapi import FastAPI

from src.routes import router


app = FastAPI(
    title="UrbanHub - MS6 Validateur de donnees capteur",
    version="1.0.0",
    description=(
        "Valide et classifie les donnees capteur (co2, temperature, noise, "
        "pm25, humidity, illuminance) selon des seuils modere / critique."
    ),
)
app.include_router(router)
