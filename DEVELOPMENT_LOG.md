# FORGE 2.0 — Development Log & Engineering Journal

## Project Metadata
- **Project Name**: FORGE 2.0 (Personal Execution System)
- **Motto**: PLAN. FOCUS. TRACK. GROW.
- **Repository**: `PARENT/FORGE`
- **Sibling Project**: `PARENT/study-cursor` (Preserved learning tracker)
- **Primary Platforms**: Linux (Fedora 45 / KDE Plasma 6 / Wayland) & Android (Flutter / Material 3)
- **Design Paradigm**: macOS-like Liquid Glassmorphism with Flame & Obsidian Dark Accents

---

## [Phase 0] Workspace & Environment Audit (Completed 2026-11-16)
- **Workspace Verification**:
  - Confirmed parent directory `/run/media/saiudheep/New Volume/PROJECTS/PERSONAL/` holds `study-cursor` and `FORGE`.
  - Confirmed `FORGE/` existed as an empty directory (0 files, 0 subdirectories).
  - Verified `study-cursor` Git repository status: clean working tree on `main`, up to date with `origin/main`.
- **Study Cursor Architecture Audit**:
  - Framework: Vite 6.1.0 + React 18.3.1 SPA with Context API state management (`TrackerContext.jsx`).
  - Persistence: Supabase PostgREST table `tracker_data` (Key-Value `id` -> `value` JSONB) + `localStorage` offline fallback.
  - Curricula:
    - GATE CS: 11 Subjects across 5 Clusters, 62 topics.
    - Aptitude: 10 topics (fixed 15 minutes/day).
    - SDE Prep: 34 topics in `seedData.js`.
    - AI Engineering: 39 topics in `seedData.js`.
  - Preservation Commitment: Zero modifications to Study Cursor curricula, quiz engines, or data structures.
- **Host & Environment Audit**:
  - Fedora Linux 45 (KDE Plasma Desktop Edition), Wayland session (`wayland-1`).
  - Python 3.15.2 available with `ensurepip` (pip 26.1.2).
  - KDE packaging tool `kpackagetool6 2.0` available.
  - Independent Git repository initialized inside `FORGE/` on branch `main`.

---

## [Phase 1] Architecture, Contracts & Design Specifications (In Progress)
- **Visual Design Identity**: macOS-inspired Glassmorphism with deep translucent obsidian surfaces, background blurs, subtle specular highlights, and vibrant flame (`#FF5722` / `#FF7A00`) and purple (`#7C3AED`) glow accents.
- **System Architecture**:
  - Decoupled backend service built with Python, FastAPI, SQLAlchemy 2, Alembic, and SQLite.
  - Dedicated `StudyCursorAdapter` for safe, read-only topic ingestion and explicit, user-confirmed completion sync.
  - Desktop Client: KDE Plasma 6 QML Plasmoid communicating via localhost with native KDE notifications and systemd user service management.
  - Mobile Client: Flutter Android client with offline-first persistence, local notifications, and LAN synchronization.
- **Database Schema**: Comprehensive 10-table domain model defined with UUIDs, indexing, foreign keys, and ISO-8601 timestamps.
- **API Specification**: Standardized `/api/v1` RESTful interface with Pydantic validation, OpenAPI documentation, and token-based LAN client authentication.
