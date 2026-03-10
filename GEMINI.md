# GEMINI.md - Project-Wide Mandates

## Core Principles
- **Surgical Changes:** Prioritize targeted, minimal changes over large refactors unless explicitly requested.
- **Context Efficiency:** Be mindful of context usage; use `grep_search` and `glob` to find relevant code before reading entire files.
- **Validation:** Always verify changes by running relevant tests and checking for linting/type errors.

## Tech Stack
- **Backend:** Django with Django REST Framework (DRF), ChromaDB, Sentence Transformers, and LangChain for RAG operations.
- **Frontend:** React (Vite) with Axios for API communication.

## Quality Standards
- **Python:** Adhere to PEP 8 standards and DRF conventions.
- **JavaScript/React:** Use functional components and hooks. Follow the project's ESLint configuration.
- **Documentation:** Update related docstrings or comments when modifying logic.

## Common Operations
- **Backend:** `python manage.py runserver` for the development server.
- **Frontend:** `npm run dev` in the `rag-frontend/` directory for the Vite dev server.
- **Tests:** `python manage.py test` for backend tests.
