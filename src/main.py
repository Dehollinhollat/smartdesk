from fastapi import FastAPI
from pydantic import BaseModel
from agent import traiter_ticket

app = FastAPI(
    title="SmartDesk API",
    description="Agent IA de support IT avec RAG et escalade automatique",
    version="1.0.0"
)

class Ticket(BaseModel):
    employe: str
    description: str
    priorite: str = "Moyenne"

@app.get("/")
def accueil():
    return {"message": "SmartDesk API opérationnelle", "version": "1.0.0"}

@app.post("/ticket")
def soumettre_ticket(ticket: Ticket):
    resultat = traiter_ticket(
        employe=ticket.employe,
        description=ticket.description,
        priorite=ticket.priorite
    )
    return resultat
