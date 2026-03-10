# GEMINI.md - Backend Mandates (research/)

## Overview
This directory handles the core RAG logic, Django models, and DRF API views.

## Mandates
- **Django/DRF:** Follow Django REST Framework best practices for serializers and views.
- **RAG Pipeline:** When modifying `rag_pipeline.py`, ensure logic is modular and maintainable. Use LangChain abstractions where appropriate.
- **Vector Database:** Be mindful of ChromaDB operations; minimize re-indexing if possible.
- **Testing:** Add or update Django test cases in `tests.py` for any changes in logic or views.
- **Async:** Use Django's async capabilities where performance bottlenecks are identified (e.g., long-running LLM calls).

## Common Tasks
- Run tests: `python manage.py test research`
- Add migrations: `python manage.py makemigrations research`
- Apply migrations: `python manage.py migrate`
