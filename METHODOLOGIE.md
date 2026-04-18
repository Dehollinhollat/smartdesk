# 🟣 SmartDesk — Méthodologie

**Auteur :** Déhollin HOLLAT, Chef de Projet Data IA
> Agent IA de support IT capable de traiter automatiquement les tickets simples et d'escalader les cas complexes — exposé via une API REST et piloté depuis un dashboard Streamlit avec deux vues distinctes (employé et administrateur).

---

## 📋 Sommaire

- [Pourquoi ce projet ?](#pourquoi-ce-projet)
- [Vue d'ensemble du pipeline](#vue-densemble-du-pipeline)
- [Phase 1 — Base de connaissances RAG](#phase-1--base-de-connaissances-rag)
- [Phase 2 — Agent IA et logique de décision](#phase-2--agent-ia-et-logique-de-décision)
- [Phase 3 — API REST FastAPI](#phase-3--api-rest-fastapi)
- [Phase 4 — Dashboard Streamlit](#phase-4--dashboard-streamlit)
- [Décisions techniques](#décisions-techniques)
- [Difficultés rencontrées](#difficultés-rencontrées)
- [Résultats et performances](#résultats-et-performances)
- [Limites et évolutions](#limites-et-évolutions)
- [Lexique](#lexique)

---

## Pourquoi ce projet ?

Dans la plupart des entreprises, le support IT est encore géré manuellement : un employé soumet un ticket, un technicien le lit, répond ou le redirige. Pour les demandes simples et répétitives (réinitialisation de mot de passe, problème de connexion Wi-Fi, accès refusé…), ce processus mobilise du temps humain pour des tâches à faible valeur ajoutée.

**SmartDesk automatise le traitement des tickets IT simples** : l'agent IA analyse la demande, consulte la base de connaissances interne, et décide seul de répondre ou d'escalader — sans intervention humaine pour les cas courants.

Deux profils d'utilisateurs ont été pensés dès le départ :
- **L'employé** : soumet sa demande via un formulaire simple, sans savoir qu'une IA traite sa requête
- **L'administrateur** : accède à un dashboard complet avec KPIs, historique des tickets et suivi des escalades

---

## Vue d'ensemble du pipeline

<!-- Image : schéma architecture SmartDesk -->
![Architecture SmartDesk](docs/images/architecture.png)

```
👤 Employé soumet un ticket
│
▼
🌐 API FastAPI
POST /ticket
│
▼
🔍 rag.py
Recherche sémantique dans ChromaDB
Récupère les 2-3 documents FAQ les plus pertinents
│
▼
🤖 agent.py
Claude API (claude-haiku)
Analyse ticket + documents récupérés
│
▼
Décision de l'agent
│
├─── Score élevé ──► RÉPONSE_AUTO
│                    Réponse directe à l'employé
│
└─── Score faible ──► ESCALADE
Ticket transmis à un technicien
│
▼
📋 tickets_log.json
Archivage de tous les tickets
│
▼
📊 Dashboard Admin (Streamlit)
KPIs + historique + escalades
```
---

## Phase 1 — Base de connaissances RAG

**Fichier :** `src/rag.py`

La base de connaissances contient **8 documents FAQ IT** couvrant les problèmes les plus fréquents : mots de passe, Wi-Fi, imprimantes, accès VPN, messagerie, etc.

Ces documents sont **vectorisés** et stockés dans ChromaDB — une base de données spécialisée dans la recherche par similarité sémantique. Concrètement, chaque document est converti en une suite de nombres (un vecteur) qui représente son sens.

Quand un ticket arrive, la même opération est faite sur le texte du ticket — et on cherche les documents dont le vecteur est le plus proche. Le résultat : les 2 ou 3 documents les plus pertinents sont extraits et transmis à l'agent.

| Étape | Ce qui se passe |
|---|---|
| Indexation | Les 8 FAQ sont lus, découpés et vectorisés dans ChromaDB |
| Recherche | Le ticket entrant est vectorisé et comparé à la base |
| Résultat | Les 2-3 documents les plus proches sont retournés |

<!-- Image : exemple de recherche RAG dans le terminal -->
![RAG SmartDesk](docs/images/rag_result.png)

---

## Phase 2 — Agent IA et logique de décision

**Fichier :** `src/agent.py`

L'agent reçoit deux entrées : le ticket de l'employé et les documents FAQ récupérés par le RAG. Il les envoie à **Claude API** avec un prompt structuré qui lui demande de prendre une décision binaire :

- **`RÉPONSE_AUTO`** : le problème est connu et documenté → l'agent rédige une réponse directe
- **`ESCALADE`** : le problème est trop complexe ou non documenté → le ticket est transmis à un technicien humain

Le prompt est conçu pour forcer une réponse structurée — l'agent ne peut pas répondre de façon vague. Il doit choisir entre les deux options et justifier sa décision.

| Situation | Décision de l'agent |
|---|---|
| Problème dans la FAQ + réponse claire | ✅ RÉPONSE_AUTO |
| Problème partiellement documenté | ⚠️ RÉPONSE_AUTO avec mise en garde |
| Problème non documenté | 🔴 ESCALADE |
| Ticket ambigu ou incomplet | 🔴 ESCALADE |

<!-- Image : exemple de réponse agent dans le terminal -->
![Agent SmartDesk](docs/images/agent_result.png)

---

## Phase 3 — API REST FastAPI

**Fichier :** `src/main.py`

Le pipeline (RAG + agent) est exposé via une **API REST FastAPI**. Cela permet à n'importe quel système externe (Jira, ServiceNow, Slack, interface web) de soumettre des tickets sans connaître le code Python.

| Endpoint | Usage |
|---|---|
| `GET /` | Health check |
| `POST /ticket` | Soumettre un ticket et recevoir une décision |
| `GET /tickets` | Récupérer l'historique des tickets (usage admin) |

Chaque ticket traité est archivé dans `data/tickets_log.json` avec l'horodatage, la décision, la réponse et le statut.

<!-- Image : capture Swagger FastAPI SmartDesk -->
![Swagger SmartDesk](docs/images/swagger.png)

---

## Phase 4 — Dashboard Streamlit

**Fichiers :** `src/accueil.py`, `src/pages/Admin.py`

Le dashboard Streamlit propose **deux vues distinctes** accessibles depuis la même application :

### Vue Employé (`accueil.py`)
- Formulaire simple : titre du ticket + description
- Aucune mention de l'IA — l'expérience est identique à un formulaire de support classique
- Affichage de la réponse ou d'un message de prise en charge

### Vue Admin (`pages/Admin.py`)
- KPIs en temps réel : nombre de tickets traités, taux de résolution automatique, taux d'escalade
- Historique complet des tickets avec filtres
- Visualisation des escalades en attente

<!-- Image : capture vue Employé -->
![Vue Employé](docs/images/vue_employe.png)

<!-- Image : capture vue Admin -->
![Vue Admin](docs/images/vue_admin.png)

---

## Décisions techniques

### Pourquoi RAG plutôt qu'un prompt statique ?

Un prompt contenant toute la FAQ IT aurait dépassé les limites de contexte pour une base documentaire réelle. Avec ChromaDB, l'agent ne récupère que les 2 ou 3 documents les plus pertinents — ce qui rend la réponse plus précise et le système plus scalable.

### Pourquoi deux vues séparées ?

Chaque utilisateur ne voit que ce dont il a besoin. L'employé n'a pas à savoir qu'une IA traite sa demande — cela évite la méfiance et maintient une expérience professionnelle. L'admin a besoin de visibilité complète sur les KPIs et les escalades.

### Pourquoi FastAPI plutôt qu'une intégration directe dans Streamlit ?

Exposer l'agent via une API REST le rend consommable par n'importe quel système externe (Jira, ServiceNow, Slack…). C'est une décision d'architecture orientée vers la réutilisabilité et la séparation des responsabilités.

### Pourquoi ChromaDB local ?

Pour un portfolio, un serveur vectoriel externe (Pinecone, Weaviate) aurait ajouté de la complexité sans valeur ajoutée. ChromaDB en local suffit pour démontrer le concept RAG et peut être remplacé par une solution cloud sans modifier le code métier.

| Choix technique | Alternative possible | Raison du choix |
|---|---|---|
| ChromaDB local | Pinecone, Weaviate | Simplicité, pas de coût |
| claude-haiku | GPT-3.5, Mistral | Cohérence avec l'écosystème Anthropic |
| FastAPI | Flask, Django | Rapidité, documentation Swagger automatique |
| Streamlit | React, Dash | Déploiement rapide, adapté au prototypage |

---

## Difficultés rencontrées

### Encodage UTF-8 sur Windows

Les caractères accentués généraient des erreurs à l'affichage dans le terminal Windows. Résolution appliquée en ajoutant en tête de script :

```python
sys.stdout.reconfigure(encoding='utf-8')
```

Ce problème illustre l'importance de tester sur l'environnement cible et pas uniquement en développement.

### Séparation des vues Streamlit

Streamlit gère les applications multipages via un dossier `pages/` — la structure du projet a dû être adaptée pour respecter cette convention tout en maintenant une séparation claire entre la logique métier (`agent.py`, `rag.py`) et la présentation (`accueil.py`, `Admin.py`).

---

## Résultats et performances

Tests réalisés sur plusieurs types de tickets :

| Type de ticket | Décision agent | Correct ? |
|---|---|---|
| "Mon mot de passe ne fonctionne plus" | ✅ RÉPONSE_AUTO | ✅ |
| "Je n'arrive pas à me connecter au Wi-Fi" | ✅ RÉPONSE_AUTO | ✅ |
| "Mon écran est cassé" | 🔴 ESCALADE | ✅ |
| "L'imprimante du 3ème étage fait un bruit bizarre" | 🔴 ESCALADE | ✅ |
| "Comment installer un logiciel ?" | ✅ RÉPONSE_AUTO | ✅ |

---

## Limites et évolutions

| Limite actuelle | Evolution possible |
|---|---|
| FAQ limitée à 8 documents | Enrichissement continu de la base documentaire |
| Pas de mémoire multi-tours | Historique de conversation par session |
| ChromaDB local | Migration vers Pinecone ou Weaviate en cloud |
| Pas de déploiement cloud | Railway ou Render pour rendre l'API accessible |
| Pas de connexion ticketing | Intégration Jira ou ServiceNow via API REST |

---

## Lexique

| Terme | Définition simple |
|---|---|
| **RAG** | Retrieval Augmented Generation — technique qui donne à l'IA accès à une base de documents avant de répondre |
| **ChromaDB** | Base de données spécialisée dans la recherche par similarité de sens |
| **Vecteur** | Représentation mathématique du sens d'un texte — deux textes similaires ont des vecteurs proches |
| **Agent IA** | Programme capable de prendre des décisions autonomes en fonction d'un contexte |
| **Escalade** | Transfert d'un ticket vers un humain quand l'IA ne peut pas répondre seule |
| **FastAPI** | Framework Python pour créer des APIs web rapidement |
| **Streamlit** | Outil Python pour créer des interfaces web sans HTML ni CSS |
| **Endpoint** | Point d'entrée d'une API — une URL qui accepte des requêtes |
| **Prompt engineering** | Art de formuler les instructions données à une IA pour obtenir la réponse souhaitée |

---

**Auteur :** Déhollin HOLLAT, Chef de Projet Data IA
