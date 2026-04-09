# 🟣 SmartDesk — Méthodologie & Choix techniques

Ce document retrace les décisions prises durant le développement de SmartDesk,
les problèmes rencontrés et les raisons derrière chaque choix technique.

---

## 🎯 Objectif du projet

Concevoir un agent IA de support IT capable de traiter automatiquement les
tickets simples et d'escalader les cas complexes — le tout exposé via une API
REST et piloté depuis un dashboard Streamlit.

L'enjeu n'était pas seulement technique : il s'agissait de produire un outil
crédible dans un contexte professionnel réel, avec une expérience utilisateur
pensée pour deux profils distincts (employé et administrateur).

---

## 🏗️ Découpage en phases

Le projet a été structuré en 4 phases successives, chacune apportant une
brique fonctionnelle indépendante et testable.

| Phase | Livrable | Concept introduit |
|---|---|---|
| 1 — Base de connaissances | 8 documents FAQ vectorisés dans ChromaDB | RAG, recherche sémantique |
| 2 — Agent IA | Logique de décision `RÉPONSE_AUTO` / `ESCALADE` | Agent, prompt engineering |
| 3 — API REST | Endpoint `POST /ticket` avec Swagger | FastAPI, architecture REST |
| 4 — Dashboard | Vues Employé et Admin dans Streamlit | UX, séparation des rôles |

Ce découpage permettait de valider chaque composant avant de passer au suivant,
et de limiter les régressions lors des ajouts.

---

## 🔑 Décisions clés

### Pourquoi RAG plutôt qu'un prompt statique ?

Un prompt contenant toute la FAQ IT aurait dépassé les limites de contexte pour
une base documentaire réelle. Avec ChromaDB, l'agent ne récupère que les 2 ou 3
documents les plus pertinents par rapport au ticket soumis — ce qui rend la
réponse plus précise et le système plus scalable.

### Pourquoi deux vues séparées (employé / admin) ?

La décision de séparer les vues répond à un principe UX fondamental : chaque
utilisateur ne voit que ce dont il a besoin. L'employé n'a pas à savoir qu'une
IA traite sa demande — cela évite la méfiance et maintient une expérience
professionnelle. L'admin, lui, a besoin de visibilité complète sur les KPIs et
les escalades.

### Pourquoi FastAPI plutôt qu'une intégration directe dans Streamlit ?

Exposer l'agent via une API REST le rend consommable par n'importe quel système
externe (Jira, ServiceNow, Slack…). C'est une décision d'architecture orientée
vers la réutilisabilité et la séparation des responsabilités.

### Pourquoi ChromaDB local ?

Pour une démo portfolio, un serveur vectoriel externe (Pinecone, Weaviate)
aurait ajouté de la complexité sans valeur ajoutée. ChromaDB en local suffit
pour démontrer le concept RAG et peut être remplacé par une solution cloud
sans modifier le code métier.

### Gestion sécurisée de la clé API

La clé Anthropic est stockée dans un fichier `.env` non versionné, chargé via
`python-dotenv`. Elle n'apparaît à aucun moment dans le code ni sur GitHub.
C'est une pratique standard en environnement professionnel.

---

## 🐛 Problèmes rencontrés

### Encodage UTF-8 sur Windows

Les caractères accentués généraient des erreurs à l'affichage dans le terminal
Windows. Résolution appliquée en ajoutant en tête de script :

```python
sys.stdout.reconfigure(encoding='utf-8')
```

Ce problème, trouvé et corrigé de manière autonome, illustre l'importance de
tester sur l'environnement cible et pas uniquement en développement.

---

## 📐 Architecture finale

```
smartdesk/
├── data/         → FAQ IT + logs des tickets
├── docs/         → Captures d'écran pour la documentation
├── src/
│   ├── pages/    → Vue Admin (Streamlit multipage)
│   ├── accueil.py → Vue Employé (point d'entrée Streamlit)
│   ├── agent.py  → Logique de décision IA
│   ├── main.py   → API REST (FastAPI)
│   └── rag.py    → Indexation et recherche sémantique (ChromaDB)
```

Chaque fichier a une responsabilité unique — ce principe de séparation des
responsabilités facilite la maintenance et les évolutions futures.

---

## 🔜 Améliorations identifiées

- **Mémoire multi-tours** : maintenir l'historique de conversation dans la
  session pour permettre des échanges de suivi sans répéter le contexte.
- **Connexion à un vrai système de ticketing** : Jira ou ServiceNow via leurs
  API REST, en remplaçant simplement le endpoint `POST /ticket`.
- **Déploiement** : Railway ou Render pour rendre l'API accessible sans
  installation locale.

---

## 👤 Auteur

**Déhollin HOLLAT** — Chef de Projet Data IA  
