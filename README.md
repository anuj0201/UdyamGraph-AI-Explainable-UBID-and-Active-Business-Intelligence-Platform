# 🚀 UdyamGraph AI — Explainable UBID & Business Intelligence Platform 🧠📊

UdyamGraph AI is an Explainable AI-powered Business Intelligence Platform designed to detect duplicate business entities, generate unique UBIDs, classify business activity status, and visualize relationships between records using interactive graph analytics. 📊🧠

The platform combines fuzzy matching, explainable scoring, review workflows, and graph visualization to build a smart entity resolution system for business records. ⚡

---

# ✨ Features

- 🆔 Automatic UBID Generation
- 🧠 Explainable AI Entity Matching
- 🔍 Fuzzy Similarity Detection
- 📊 Interactive Relationship Graph
- ✅ Review Queue Workflow
- 🏢 Business Status Classification
- ✏️ Editable Business Status
- 🌙 Professional Dark Dashboard UI
- ⚡ FastAPI + Next.js Full Stack Architecture

---

# 🛠️ Tech Stack

## 🎨 Frontend
- Next.js
- React.js
- Axios
- React Force Graph

## ⚙️ Backend
- FastAPI
- SQLAlchemy
- SQLite

## 🤖 AI & Matching
- RapidFuzz
- Rule-Based Explainable AI

---

# 📈 AI Matching Logic

The system compares:
- 🪪 PAN
- 🧾 GSTIN
- 🏢 Business Name
- 📍 Address
- 📞 Phone Number

Using weighted confidence scoring, the platform decides whether to:
- ✅ auto merge records
- 🔎 send records for review
- 🆕 create a new entity

The platform also generates explainable reasons for every decision. 🧠

---

# ▶️ Run Locally

## ⚙️ Backend

```bash
uvicorn app.main:app --reload

##🎨 Frontend
cd Udyam-Frontend
npm install
npm run dev

Frontend runs on:

http://localhost:3000
