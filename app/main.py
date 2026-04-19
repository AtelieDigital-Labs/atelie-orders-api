# app/main.py
from fastapi import FastAPI

app = FastAPI(
    title="Ateliê Digital - Orders API",
    description="Microsserviço de gerenciamento de pedidos.",
    version="0.1.0",
)

