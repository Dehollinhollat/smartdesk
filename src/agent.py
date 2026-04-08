import anthropic
import os
import json
from dotenv import load_dotenv
from rag import rechercher_faq
from datetime import datetime

load_dotenv()
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def traiter_ticket(employe, description, priorite):
    """Traite un ticket IT et retourne une réponse ou une escalade"""

    # Recherche RAG dans la FAQ
    docs_faq, metas_faq = rechercher_faq(description)
    contexte_faq = "\n".join([
        f"[{m['categorie']}] {d}" for d, m in zip(docs_faq, metas_faq)
    ])

    prompt = f"""Tu es un agent de support IT professionnel. 
Tu reçois un ticket d'un employé et tu as accès à la base de connaissances FAQ ci-dessous.

BASE DE CONNAISSANCES FAQ :
{contexte_faq}

TICKET REÇU :
- Employé : {employe}
- Priorité : {priorite}
- Description : {description}

INSTRUCTIONS :
1. Si la FAQ contient une réponse adaptée au problème, génère une réponse claire et professionnelle pour l'employé.
2. Si le problème est complexe, non documenté dans la FAQ, ou de priorité Bloquant avec intervention physique requise, réponds avec ESCALADE.
3. Commence toujours ta réponse par "RÉPONSE_AUTO:" ou "ESCALADE:" selon ta décision.
4. Sois concis, professionnel et bienveillant.

Ta réponse :"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )

    texte = response.content[0].text
    escalade = texte.startswith("ESCALADE:")

    # Logger le ticket
    log_entry = {
        "id": f"TK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "employe": employe,
        "description": description,
        "priorite": priorite,
        "escalade": escalade,
        "faq_consultee": [m["sujet"] for m in metas_faq]
    }

    try:
        with open("data/tickets_log.json", "r", encoding="utf-8") as f:
            logs = json.load(f)
    except:
        logs = []

    logs.append(log_entry)

    with open("data/tickets_log.json", "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    return {
        "employe": employe,
        "description": description,
        "priorite": priorite,
        "escalade": escalade,
        "reponse": texte,
        "faq_consultee": [m["sujet"] for m in metas_faq]
    }

if __name__ == "__main__":
    tickets_test = [
        ("Marc Dupont", "Mon mot de passe a expiré, je ne peux plus accéder à ma messagerie.", "Haute"),
        ("Lucas Martin", "Écran bleu au démarrage, impossible de démarrer Windows.", "Bloquant"),
        ("Kevin Nguyen", "Comment installer Microsoft Teams sur mon poste ?", "Basse"),
    ]

    for employe, description, priorite in tickets_test:
        print(f"\n{'='*60}")
        print(f"TICKET — {employe} [{priorite}]")
        print(f"Description : {description}")
        print(f"{'='*60}")
        resultat = traiter_ticket(employe, description, priorite)
        print(f"Escalade : {'OUI' if resultat['escalade'] else 'NON'}")
        print(f"FAQ consultée : {resultat['faq_consultee']}")
        print(f"Réponse :\n{resultat['reponse']}")
