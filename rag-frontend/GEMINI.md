# GEMINI.md - Frontend Mandates (rag-frontend/)

## Overview
This directory contains the React (Vite) frontend for interacting with the RAG backend.

## Mandates
- **Functional Components:** Use React functional components and hooks exclusively.
- **Styling:** Use `App.css` and directory-specific CSS files. Avoid inline styles unless necessary.
- **API Interaction:** Centralize API calls in `src/api/api.js` using Axios.
- **State Management:** Use local component state or Context API for simple global state. Avoid introducing complex state managers unless necessary.
- **Linting:** Always run `npm run lint` before committing changes to ensure adherence to ESLint rules.

## Common Tasks
- Run dev server: `npm run dev`
- Build project: `npm run build`
- Fix linting: `npm run lint -- --fix`
