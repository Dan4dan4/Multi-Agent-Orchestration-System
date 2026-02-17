# RAG Frontend Redesign — Built by Claude

## Overview
Rebuilt the frontend from a basic dark-brown themed layout with a simple query input and file upload side by side into a modern, minimal, chat-first interface (similar to ChatGPT/Perplexity) using plain CSS — no frameworks.

## Files Modified

### `index.html`
- Added Google Fonts preconnect links and Inter font (weights 400, 500, 600)
- Updated page title from "rag-frontend" to "RAG Assistant"

### `src/index.css`
- Added full CSS reset (`*`, `*::before`, `*::after` with `box-sizing: border-box`)
- Defined CSS custom properties (variables) for the entire design system:
  - Color palette: light/neutral backgrounds, indigo accent (`#4f46e5`)
  - Financial badge colors: blue for percentages, green for dollar amounts
  - Shadows, border radii, and transition timing
- Set Inter as the primary font family with system font fallbacks
- Configured `html`, `body`, and `#root` for full-height layout

### `src/App.jsx`
- Removed imports for `RagChat`, `QueryBox`, `Navbar`, and `UploadBox`
- Simplified to a single `<div className="app">` wrapping `<ChatInterface />`

### `src/App.css`
- Replaced old dark-brown styling with a minimal full-height flex column layout

## Files Created

### `src/components/chat/ChatInterface.jsx`
The main (and only) component, containing everything:

**State management:**
- `messages` — array of `{ role: 'user' | 'assistant', content: string }`
- `input` — current textarea value
- `loading` — whether a response is being fetched
- `file` — currently selected file for upload
- `uploadStatus` — tracks upload state (`""`, `"uploading"`, `"success"`, `"error"`)
- `documentName` — name of the last successfully uploaded document
- `dragOver` — whether a file is being dragged over the chat area

**Features implemented:**
- **Message history** with user (right-aligned, indigo) and assistant (left-aligned, light gray) bubbles
- **Auto-scroll** to bottom on new messages using `useRef` and `scrollIntoView`
- **Auto-expanding textarea** that grows with content up to 160px max height
- **Enter to send**, Shift+Enter for newline
- **Paperclip file upload button** using a hidden file input triggered by an SVG icon button
- **Drag-and-drop file upload** with a purple dashed overlay when dragging files over the chat
- **File chip** showing the selected filename with Upload/Remove buttons and status text
- **Upload feedback** — on success, an assistant message confirms the upload and the document name appears in the header
- **Financial data parsing** via `parseFinancialData()` — uses regex to wrap percentages and dollar amounts in `<span>` tags with badge classes, rendered via `dangerouslySetInnerHTML`
- **Typing indicator** — 3 bouncing dots animation while waiting for API response
- **Empty state** — welcome screen with app icon, title, description, and 3 clickable suggestion chips
- **Header bar** with app title (chat bubble icon) and document indicator (file icon + filename)

**API integration:**
- Uses existing `askRag()` from `src/api/api.js` for questions
- Uses existing `uploadDocument()` from `src/api/api.js` for file uploads
- No changes to the API layer were needed

### `src/components/chat/ChatInterface.css`
All styles for the chat interface (~280 lines):

- **Container** — centered max-width 820px, full-height flex column
- **Header** — flex row with border-bottom, title left, document indicator right
- **Messages area** — scrollable flex column with 16px gap between messages
- **Message bubbles** — 75% max-width, rounded corners with flattened corner on the sender's side
- **Financial badges** — inline `border-radius: 12px` pills, blue for percentages, green for dollars
- **Typing indicator** — 3 dots with staggered `bounce` keyframe animation
- **File chip bar** — inline-flex chip with icon, filename, status, upload button, and remove button
- **Input bar** — flex row with paperclip button, auto-expanding textarea, and send button (indigo circle)
- **Drag overlay** — absolute positioned with dashed border and upload icon
- **Empty state** — centered column with icon, heading, description, and wrapped suggestion chips
- **Responsive** — `@media (max-width: 640px)` adjustments for padding, bubble width, and suggestion layout

## Files Deleted

| File | What it was |
|------|-------------|
| `src/components/QueryBox.jsx` | Original query input with separate answer display |
| `src/components/QueryBox.css` | Styles for QueryBox |
| `src/components/upload/Upload.jsx` | Standalone file upload form |
| `src/components/upload/Upload.css` | Styles for Upload |
| `src/components/layout/Navbar.jsx` | Top navigation bar |
| `src/components/layout/Navbar.css` | Styles for Navbar |
| `src/components/rag/RagChat.jsx` | Alternative RAG chat component (unused) |
| `src/components/chat/Chat.jsx` | Empty chat component placeholder |

Empty directories (`upload/`, `layout/`, `rag/`) were also removed.

## Final File Structure

```
src/
├── api/
│   └── api.js              (unchanged)
├── assets/
│   └── react.svg
├── components/
│   └── chat/
│       ├── ChatInterface.jsx
│       └── ChatInterface.css
├── App.jsx
├── App.css
├── index.css
└── main.jsx
```

## Component Architecture

```
App
└── ChatInterface
    ├── Header (app title + document status indicator)
    ├── MessagesArea
    │   ├── EmptyState (welcome + suggestion chips)  — or —
    │   ├── MessagesList
    │   │   ├── Message (user) — right-aligned indigo bubble
    │   │   └── Message (assistant) — left-aligned gray bubble with financial badges
    │   └── TypingIndicator (3 bouncing dots)
    ├── FileChipBar (selected file + upload/remove actions)
    ├── InputBar
    │   ├── FileUploadButton (paperclip icon)
    │   ├── Textarea (auto-expanding)
    │   └── SendButton (arrow icon)
    └── DragOverlay (shown when dragging files)
```

## Clear Document Cache on New Tab/Page Load

**Problem:** When a user opened a new tab, the backend still had previously uploaded documents in the `TEMP_DOCS` list and ChromaDB. Questions would get answered using old documents even though the user hadn't uploaded anything in the new session.

**Backend endpoint (already existed, no changes needed):**
- `POST /rag/clear_docs/` in `research/views.py` — clears `TEMP_DOCS = []` and deletes the ChromaDB collection

**Changes made:**

### `src/api/api.js`
- Added `clearDocs` export: `export const clearDocs = () => api.post("/rag/clear_docs/");`

### `src/components/chat/ChatInterface.jsx`
- Imported `clearDocs` from `../../api/api`
- Added a `useEffect(() => { clearDocs().catch(() => {}); }, [])` that calls `clearDocs()` once on component mount (i.e. when a new tab is opened), clearing any stale documents from previous sessions
- Errors are silently caught to avoid console noise if the backend isn't ready

---

## Design System

| Token | Value |
|-------|-------|
| Primary background | `#ffffff` |
| Secondary background | `#f7f7f8` |
| Accent color | `#4f46e5` (indigo) |
| User bubble | Indigo with white text |
| Assistant bubble | Light gray with dark text |
| Percent badge | Blue background (`#dbeafe`) |
| Dollar badge | Green background (`#dcfce7`) |
| Font | Inter, 15px base |
| Border radius | 8px / 16px / 24px |
