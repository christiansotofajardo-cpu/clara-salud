# CLARA Salud

### Bilingual Health Information and Comprehension Support

**Open-source educational prototype | Version 0.5.1 | November 2026**

**Developed by IDE SpA — Chile**

**[Live Demo](https://clara-salud.onrender.com)** | **[API Status](https://clara-salud.onrender.com/api/status)** | **[API Documentation](https://clara-salud.onrender.com/api/docs)**

---

## 1. Overview

**CLARA Salud** is a bilingual digital health communication prototype designed to help women and adolescent girls access understandable sexual and reproductive health information, express questions in their own words, and check what they have understood.

The project addresses a fundamental challenge: **access to health information does not necessarily mean comprehension**.

CLARA combines structured, source-linked information retrieval with a guided *teach-back* approach. Users can read an explanation, describe their understanding, and receive preliminary feedback about key concepts and possible misunderstandings.

The prototype currently supports **Spanish and English**.

CLARA is an educational research and development prototype. It is not a medical device, a diagnostic tool, or a substitute for professional healthcare.

## 2. The Problem

Sexual and reproductive health information can be difficult to understand because of technical terminology, misinformation, language barriers, and limited opportunities to ask questions without judgment.

Even when accurate information is available, users may leave an interaction with incomplete or incorrect understanding.

CLARA explores a communication-centered solution by integrating:

1. Accessible, bilingual health information.
2. Questions expressed in natural language.
3. Structured retrieval from a controlled knowledge library.
4. Guided explanation in the user's own words.
5. Preliminary detection of important conceptual misunderstandings.
6. Explanatory feedback intended to support better understanding.

## 3. Current Prototype Features

### Bilingual user interface

The web application provides Spanish and English interaction, including information retrieval and guided comprehension activities.

### Structured health information

The current knowledge library includes **60 educational knowledge entries: 30 in Spanish and 30 in English**.

The initial topics include:

- Emergency contraception and time-sensitive information.
- Regular contraceptive methods.
- Pregnancy prevention and common misconceptions.
- Sexually transmitted infections and prevention.
- General safety guidance and referral to professional healthcare.

The knowledge entries include alternative question formulations, related topics, and references to recognized health information sources.

### Question answering

Users can submit free-text questions. A deterministic, rule-based retrieval engine attempts to select relevant information from the knowledge library.

The system can provide direct information, identify related background information, or indicate when it does not have a sufficiently supported answer.

It does not currently use a generative language model to produce unrestricted medical advice.

### Guided teach-back

Users can select an educational topic, read an explanation, and describe what they understood.

The prototype uses heuristic linguistic rules to detect selected concepts and possible misconceptions and provide formative feedback.

This functionality is experimental. Its scores are **not validated measures of health literacy, clinical understanding, or individual competence**.

### Safety-oriented responses

The system includes rules intended to identify selected urgent or sensitive situations and encourage users to seek appropriate healthcare.

These safeguards are incomplete and have not undergone comprehensive clinical safety validation.

## 4. Technology and Architecture

CLARA uses a lightweight web architecture:

- **Backend:** Python, FastAPI and Pydantic.
- **Frontend:** HTML, CSS and JavaScript.
- **Deployment:** Render.
- **Knowledge representation:** JSON.
- **Information retrieval:** deterministic linguistic matching, synonyms, intent rules and structured knowledge entries.
- **Comprehension assessment:** experimental heuristic teach-back engines.
- **Languages:** Spanish (`es`) and English (`en`).

The prototype does not require proprietary external AI services to operate.

The CLARA codebase is designed as an independent implementation and does not include proprietary EVALIA or MetaSistema software.

### Repository structure

```text
clara-salud/
├── clara/
│   ├── main.py
│   ├── engine.py
│   ├── engine_en.py
│   ├── retrieval.py
│   ├── data/
│   │   ├── es.json
│   │   ├── en.json
│   │   ├── knowledge_es.json
│   │   └── knowledge_en.json
│   └── static/
│       ├── index.html
│       ├── styles.css
│       └── app.js
├── requirements.txt
├── render.yaml
└── README.md
```

## 5. Run Locally

Use Python 3.11 or a compatible supported version.

Clone the repository:

```bash
git clone https://github.com/christiansotofajardo-cpu/clara-salud.git
cd clara-salud
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows, activate the environment with:

```powershell
.venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Start the application:

```bash
uvicorn clara.main:app --host 127.0.0.1 --port 8000
```

Then visit:

- Web interface: http://127.0.0.1:8000
- API status: http://127.0.0.1:8000/api/status
- API documentation: http://127.0.0.1:8000/api/docs

## 6. API

The current API provides the following endpoints.

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/status` | GET | Application and knowledge-library status |
| `/api/catalog?lang=es` | GET | Educational topics in Spanish |
| `/api/catalog?lang=en` | GET | Educational topics in English |
| `/api/ask` | POST | Bilingual health information retrieval |
| `/api/assess` | POST | Experimental teach-back feedback |

Example Spanish question:

```bash
curl -X POST http://127.0.0.1:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Cuáles son los métodos anticonceptivos sin hormonas?",
    "lang": "es"
  }'
```

Example English question:

```bash
curl -X POST http://127.0.0.1:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What emergency contraception options are available?",
    "lang": "en"
  }'
```

## 7. Initial Technical Validation

Two automated technical validation rounds were conducted on **November 6, 2026**, using the publicly deployed prototype.

The regression suite contained:

- 26 Spanish health information queries.
- 26 English health information queries.
- 8 additional teach-back API checks.

### Results

| Indicator | v0.5 | v0.5.1 |
|---|---:|---:|
| Spanish expected-route matches | 17/26 | 26/26 |
| English expected-route matches | 16/26 | 26/26 |
| Total expected-route matches | 33/52 | 52/52 |
| Expected-route matching rate | 63.5% | 100% |

The updated version improved the classification of several specific question types, including emergency contraception, time windows, contraceptive choices, and selected misconceptions.

**Interpretation:** These are technical regression results measuring agreement with predefined expected response routes. The same test suite informed development and correction. Therefore, the reported 100% is **not an independent generalization estimate**, a clinical accuracy measure, or evidence of efficacy among real users.

The eight teach-back checks confirmed technical API responses, not validated comprehension outcomes.

Independent testing, clinical review, and participant-based evaluation remain future requirements.

## 8. Health Sources

The initial educational knowledge base references materials from institutions including:

- [World Health Organization — Emergency contraception](https://www.who.int/news-room/fact-sheets/detail/emergency-contraception)
- [World Health Organization — Family planning](https://www.who.int/news-room/fact-sheets/detail/family-planning-contraception)
- [World Health Organization — Sexually transmitted infections](https://www.who.int/news-room/fact-sheets/detail/sexually-transmitted-infections-(stis))
- [Centers for Disease Control and Prevention — Contraception](https://www.cdc.gov/contraception/)
- [World Health Organization — HIV post-exposure prophylaxis](https://www.who.int/publications/i/item/9789240095137)

The inclusion of institutional references does not imply endorsement of CLARA by these organizations.

**All educational content remains subject to qualified clinical review, localization, and periodic updating.**

## 9. Privacy, Safety and Responsible Development

The current prototype does not require account registration and does not use an application-managed database to store users' questions or assessment answers.

However, infrastructure providers may process operational request metadata. The present implementation should not be interpreted as a clinically approved, confidential healthcare service.

Users should avoid entering names, identification numbers, contact information, detailed medical histories, or other sensitive personal data.

CLARA cannot:

- Diagnose medical conditions.
- Determine individualized medication suitability.
- Replace professional clinical evaluation.
- Guarantee the detection of emergencies.
- Provide comprehensive safeguarding or crisis intervention.

Urgent medical symptoms, possible HIV exposure, and sexual violence require timely assessment by appropriate healthcare and support services.

Testing involving adolescents or sensitive health information must follow appropriate consent, safeguarding, privacy, and ethical review procedures.

## 10. Development Roadmap

The current version is a functional proof of concept, not the final planned platform.

The next stage of development will focus on the following capabilities.

### A. Spoken and written interaction

Introduce speech recognition so users can ask questions and complete teach-back activities orally or in writing.

### B. Bilingual multimodal feedback

Develop written and spoken explanations and comprehension feedback in Spanish and English.

### C. Expanded and clinically reviewed knowledge

Increase coverage through structured, versioned, professionally reviewed health knowledge libraries, while preserving source traceability and uncertainty handling.

### D. Improved comprehension assessment

Develop and evaluate more context-sensitive methods for identifying understanding, incomplete explanations, and misconceptions, without presenting experimental scores as validated clinical measurements.

### E. Clinical and user-centered validation

Conduct independent question-answer testing, healthcare professional review, usability studies, accessibility assessments, and ethically approved pilot studies.

### F. International accessibility and scalability

Evaluate adaptation to additional languages and health systems, with particular attention to underserved populations, adolescent safeguarding, digital accessibility, and local healthcare referral pathways.

## 11. Intended Impact

CLARA aims to support more equitable access to understandable health information and help users become active participants in communication about their health.

Its proposed contribution is not simply answering questions, but supporting a cycle of:

**Ask → Understand → Explain → Receive Feedback → Clarify**

Future research will evaluate whether this approach improves understanding, reduces selected misconceptions, and supports informed health-related decision-making.

These outcomes are project objectives, not demonstrated effects of the current prototype.

## 12. Project and Licensing

**Project:** CLARA Salud  
**Developer:** IDE SpA, Chile  
**Prototype version:** 0.5.1  
**Initial public prototype:** 2026  
**Repository:** https://github.com/christiansotofajardo-cpu/clara-salud  
**Live demo:** https://clara-salud.onrender.com

The project is intended for release under the **MIT License**. The license grant takes effect through the repository's `LICENSE` file, subject to confirmation of ownership and the inclusion of the license in the repository.

CLARA is an independent prototype developed for open-source, responsible digital health innovation.

---

**CLARA Salud — Because providing information is not the same as ensuring understanding.**
