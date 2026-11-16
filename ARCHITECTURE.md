# FORGE 2.0 — System Architecture & Design Specification

> **Motto**: PLAN. FOCUS. TRACK. GROW.  
> **Brand**: FORGE — Execute. Improve. Repeat.

---

## 1. Executive Summary & Separation of Concerns

FORGE 2.0 is a **Personal Execution and Productivity Operating System** designed for high-performance engineering routines. It coordinates daily scheduling, focus timers, habit consistency, actionable notifications, and productivity analytics.

### Separation of Concerns: Study Cursor vs. FORGE
* **Study Cursor = WHAT to learn**: Owns study tracks (GATE, SDE, AI Engineering, Aptitude), learning syllabi, quiz engines, AI quiz personas, and conceptual mastery milestones.
* **FORGE = WHEN to execute & TRACKING**: Owns daily planning, time blocking, reminders, Pomodoro/focus sessions, consistency metrics, and execution reviews.
* **The Golden Rule**: Study Cursor sets the curriculum. FORGE schedules and tracks execution. FORGE **never** alters curricula or marks topics complete without explicit user confirmation.

```
┌──────────────────────────────────────────────┐       ┌──────────────────────────────────────────────┐
│             STUDY CURSOR (Vite + React)      │       │              FORGE 2.0 BACKEND               │
│                                              │       │                                              │
│  • Curricula (GATE, SDE, AI, Aptitude)       │       │  • Daily & Weekly Planner                    │
│  • 5-Cluster GATE Mastery Engine             │       │  • Focus Session Timer (Pomodoro / Flow)     │
│  • AI Quiz Generator                         │       │  • Intelligent Notifications & Reminders     │
│  • Supabase `tracker_data` + localStorage    │       │  • Analytics, Reviews & Consistency Engine   │
└──────────────────────┬───────────────────────┘       └──────────────────────┬───────────────────────┘
                       │                                                      │
                       │             ┌────────────────────────┐               │
                       └────────────►│  StudyCursorAdapter    │◄──────────────┘
                                     │  (Read-Only Ingest +   │
                                     │  Explicit Confirmed    │
                                     │  Completion Push)      │
                                     └────────────────────────┘
```

---

## 2. macOS-Inspired Liquid Glassmorphism Design System

The visual design language combines the tactile depth, frosted translucency, and continuous surface highlights of **macOS Sequoia / Sonoma** with FORGE's signature **Obsidian Dark & Flame Accent** palette.

### 2.1 Color Palette & Surface Tokens

| Token Name | Hex / RGBA Value | Purpose / Application |
|---|---|---|
| **Background (Deep Obsidian)** | `#0C0D10` | Base canvas and system window underlay |
| **Glass Surface (Primary)** | `rgba(22, 24, 30, 0.72)` | Primary cards, panels, plasmoid widget body |
| **Glass Surface (Elevated)** | `rgba(32, 35, 45, 0.65)` | Active modals, dropdown menus, focused task cards |
| **Glass Border (Specular)** | `rgba(255, 255, 255, 0.12)` | 1px top-and-left subtle inner specular edge highlight |
| **Glass Border (Shadow)** | `rgba(0, 0, 0, 0.35)` | 1px bottom-and-right ambient border separation |
| **Flame Primary (Core)** | `#FF6B35` | Primary action buttons, active focus timer, badges |
| **Flame Gradient Start** | `#FF8A48` | Top gradient stop for primary interactive elements |
| **Flame Gradient End** | `#F74C1E` | Bottom gradient stop for primary interactive elements |
| **Purple Accent (Secondary)** | `#8B5CF6` | Secondary tags, AI insights, study track badges |
| **Electric Cyan (Metric)** | `#06B6D4` | GATE metrics, precision countdowns, analytics charts |
| **Text Primary** | `rgba(255, 255, 255, 0.95)` | Headings, active task titles, timer digits |
| **Text Secondary** | `rgba(255, 255, 255, 0.62)` | Subtitles, estimated durations, metadata badges |
| **Text Tertiary / Muted** | `rgba(255, 255, 255, 0.38)` | Placeholders, inactive breadcrumbs, timestamps |

### 2.2 Glassmorphism Material Parameters
* **Backdrop Blur**: `24px` to `36px` gaussian blur (`backdrop-filter: blur(28px) saturate(190%)`).
* **Corner Radius**:
  * Outer Windows & Widgets: `18px`
  * Cards & Containers: `12px` to `14px`
  * Chips, Badges & Buttons: `8px` or pill (`9999px`)
* **Layering & Shadows**:
  * Diffuse Ambient: `0 12px 32px 0 rgba(0, 0, 0, 0.45)`
  * Specular Glow: `inset 0 1px 1px 0 rgba(255, 255, 255, 0.15)`
  * Active Flame Glow: `0 0 20px rgba(255, 107, 53, 0.35)`

### 2.3 Cross-Platform Implementation
* **KDE Plasma 6 (QML)**: Implemented using `PlasmaCore.FrameSvgItem` or Qt Quick `Rectangle` layered with `MultiEffect` or `FastBlur`, combining `color: Qt.rgba(0.08, 0.09, 0.12, 0.75)` and `border.color: Qt.rgba(1, 1, 1, 0.12)`.
* **Flutter (Android)**: Implemented using `ClipRRect(borderRadius: ...)` wrapping a `BackdropFilter(filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20))` and decorated `Container` with translucent gradient fills and ambient box shadows.

---

## 3. Database Architecture & Data Models

FORGE owns its relational database (`forge.db`), powered by **SQLite** via **SQLAlchemy 2.0** and managed with **Alembic** migrations.

```
┌─────────────────┐       ┌─────────────────┐       ┌───────────────────────────────┐
│    Category     │◄──────┤      Goal       │◄──────┤       StudyCursor             │
│                 │       │                 │       │       TopicReference          │
└────────┬────────┘       └────────┬────────┘       └───────────────┬───────────────┘
         │                         │                                │
         │        ┌────────────────┴────────────────┐               │
         └───────►│              Task               │◄──────────────┘
                  └────────┬───────────────┬────────┘
                           │               │
                  ┌────────▼────────┐     ┌▼────────────────┐
                  │    Reminder     │     │  FocusSession   │
                  └─────────────────┘     └─────────────────┘
```

### 3.1 Entity Relationship Specification

#### 1. `Category`
Organizes goals and tasks into logical life and career domains.
* `id` (VARCHAR(36), PK): UUID.
* `name` (VARCHAR(64), UNIQUE, NOT NULL): e.g., "GATE 2027", "InfoEdge Internship", "DSA", "Academics", "Personal".
* `color` (VARCHAR(16), NOT NULL): Hex color code.
* `icon` (VARCHAR(32)): Icon name.
* `sort_order` (INTEGER, DEFAULT 0).
* `created_at` (TIMESTAMP, NOT NULL).
* `updated_at` (TIMESTAMP, NOT NULL).

#### 2. `Goal`
High-level strategic objectives with target milestones.
* `id` (VARCHAR(36), PK): UUID.
* `category_id` (VARCHAR(36), FK -> `Category.id`, NULLABLE).
* `title` (VARCHAR(128), NOT NULL).
* `description` (TEXT).
* `target_date` (DATE).
* `priority` (VARCHAR(16), NOT NULL, DEFAULT 'medium'): `low`, `medium`, `high`, `urgent`.
* `status` (VARCHAR(20), NOT NULL, DEFAULT 'active'): `active`, `paused`, `completed`, `archived`.
* `progress_percentage` (FLOAT, DEFAULT 0.0).
* `created_at` (TIMESTAMP, NOT NULL).
* `updated_at` (TIMESTAMP, NOT NULL).

#### 3. `StudyCursorConnection`
Configuration and state for the Study Cursor integration.
* `id` (VARCHAR(36), PK): UUID.
* `name` (VARCHAR(64), NOT NULL): e.g., "Local Study Cursor".
* `workspace_path` (VARCHAR(255)): Filesystem path to `study-cursor` directory.
* `sync_mode` (VARCHAR(32), NOT NULL, DEFAULT 'manifest_and_cloud'): `manifest_only`, `supabase_cloud`, `manifest_and_cloud`.
* `supabase_url` (VARCHAR(255)): Optional cached Supabase URL.
* `last_sync_at` (TIMESTAMP).
* `sync_status` (VARCHAR(24), DEFAULT 'idle'): `idle`, `syncing`, `success`, `error`.
* `error_message` (TEXT).
* `created_at` (TIMESTAMP, NOT NULL).
* `updated_at` (TIMESTAMP, NOT NULL).

#### 4. `StudyCursorTopicReference`
Cached reference linking a FORGE task to a canonical Study Cursor topic.
* `id` (VARCHAR(36), PK): UUID.
* `connection_id` (VARCHAR(36), FK -> `StudyCursorConnection.id`).
* `track_category` (VARCHAR(32), NOT NULL): `gate`, `sde`, `ai`, `aptitude`.
* `subject_key` (VARCHAR(64), NULLABLE): e.g., `discreteMathematics`, `operatingSystems`.
* `topic_id` (VARCHAR(64), NOT NULL, INDEX): e.g., `dm-1`, `sde-4`, `ai-12`, `apt-1`.
* `topic_title` (VARCHAR(255), NOT NULL).
* `cluster_name` (VARCHAR(128)): e.g., `Cluster 1: Foundations & Problem Solving`.
* `weightage` (VARCHAR(64)): e.g., `7–9 Marks`.
* `subtopics_json` (TEXT): JSON array of subtopics.
* `status_in_study_cursor` (VARCHAR(24), NOT NULL, DEFAULT 'pending'): `pending`, `done`.
* `last_verified_at` (TIMESTAMP).

#### 5. `Task`
Core unit of daily execution.
* `id` (VARCHAR(36), PK): UUID.
* `goal_id` (VARCHAR(36), FK -> `Goal.id`, NULLABLE).
* `category_id` (VARCHAR(36), FK -> `Category.id`, NULLABLE).
* `study_cursor_topic_ref_id` (VARCHAR(36), FK -> `StudyCursorTopicReference.id`, NULLABLE).
* `title` (VARCHAR(255), NOT NULL).
* `description` (TEXT).
* `priority` (VARCHAR(16), NOT NULL, DEFAULT 'medium'): `low`, `medium`, `high`, `urgent`.
* `status` (VARCHAR(24), NOT NULL, DEFAULT 'pending'): `pending`, `in_progress`, `completed`, `cancelled`.
* `scheduled_date` (DATE, INDEX): Targeted planning date (`YYYY-MM-DD`).
* `scheduled_time` (TIME, NULLABLE): Specific block start time.
* `estimated_duration_minutes` (INTEGER, NOT NULL, DEFAULT 45).
* `actual_duration_minutes` (INTEGER, NOT NULL, DEFAULT 0).
* `is_recurring` (BOOLEAN, DEFAULT FALSE).
* `recurrence_rule` (VARCHAR(64), NULLABLE): e.g., `daily`, `weekly:wednesday`.
* `subtasks_json` (TEXT): JSON list of `{ id, title, completed }`.
* `completed_at` (TIMESTAMP, NULLABLE).
* `created_at` (TIMESTAMP, NOT NULL).
* `updated_at` (TIMESTAMP, NOT NULL).

#### 6. `Reminder`
Scheduled notifications for tasks or reviews.
* `id` (VARCHAR(36), PK): UUID.
* `task_id` (VARCHAR(36), FK -> `Task.id`, CASCADE, NOT NULL).
* `reminder_time` (TIMESTAMP, NOT NULL, INDEX).
* `status` (VARCHAR(20), NOT NULL, DEFAULT 'scheduled'): `scheduled`, `triggered`, `snoozed`, `dismissed`.
* `snooze_count` (INTEGER, DEFAULT 0).
* `target_platform` (VARCHAR(24), NOT NULL, DEFAULT 'all'): `all`, `kde`, `android`.
* `created_at` (TIMESTAMP, NOT NULL).
* `updated_at` (TIMESTAMP, NOT NULL).

#### 7. `FocusSession`
Logged intervals of deep work linked to tasks and topics.
* `id` (VARCHAR(36), PK): UUID.
* `task_id` (VARCHAR(36), FK -> `Task.id`, NULLABLE).
* `study_cursor_topic_ref_id` (VARCHAR(36), FK -> `StudyCursorTopicReference.id`, NULLABLE).
* `session_type` (VARCHAR(24), NOT NULL, DEFAULT 'pomodoro'): `pomodoro`, `flow`, `short_break`, `long_break`.
* `start_time` (TIMESTAMP, NOT NULL).
* `end_time` (TIMESTAMP, NULLABLE).
* `planned_duration_minutes` (INTEGER, NOT NULL).
* `actual_duration_minutes` (INTEGER, NOT NULL, DEFAULT 0).
* `status` (VARCHAR(24), NOT NULL, DEFAULT 'active'): `active`, `paused`, `completed`, `abandoned`.
* `notes` (TEXT).
* `created_at` (TIMESTAMP, NOT NULL).

#### 8. `DailyReview`
Structured evening retrospectives for accountability.
* `id` (VARCHAR(36), PK): UUID.
* `review_date` (DATE, UNIQUE, NOT NULL): `YYYY-MM-DD`.
* `planned_tasks_count` (INTEGER, NOT NULL, DEFAULT 0).
* `completed_tasks_count` (INTEGER, NOT NULL, DEFAULT 0).
* `focus_minutes_total` (INTEGER, NOT NULL, DEFAULT 0).
* `accomplishments` (TEXT).
* `obstacles` (TEXT).
* `tomorrow_priorities` (TEXT).
* `energy_rating` (INTEGER): Scale 1 to 5.
* `created_at` (TIMESTAMP, NOT NULL).
* `updated_at` (TIMESTAMP, NOT NULL).

#### 9. `WeeklyReview`
End-of-week strategic analysis and velocity calibration.
* `id` (VARCHAR(36), PK): UUID.
* `week_start_date` (DATE, NOT NULL): Monday.
* `week_end_date` (DATE, NOT NULL): Sunday.
* `total_tasks_completed` (INTEGER, NOT NULL, DEFAULT 0).
* `total_focus_hours` (FLOAT, NOT NULL, DEFAULT 0.0).
* `consistency_score` (FLOAT, DEFAULT 0.0): 0 to 100%.
* `weak_areas` (TEXT).
* `recommendations` (TEXT).
* `created_at` (TIMESTAMP, NOT NULL).

#### 10. `SyncMetadata`
Tracks sync operations across devices and Study Cursor.
* `id` (VARCHAR(36), PK): UUID.
* `source_device` (VARCHAR(64), NOT NULL): e.g., `linux-plasmoid`, `android-phone`.
* `entity_type` (VARCHAR(32), NOT NULL): `task`, `focus_session`, `study_cursor_sync`.
* `entity_id` (VARCHAR(36), NOT NULL).
* `operation` (VARCHAR(16), NOT NULL): `create`, `update`, `delete`.
* `client_timestamp` (TIMESTAMP, NOT NULL).
* `server_timestamp` (TIMESTAMP, NOT NULL).
* `status` (VARCHAR(16), NOT NULL, DEFAULT 'applied'): `applied`, `conflict_resolved`.

---

## 4. REST API Specification (`/api/v1`)

### 4.1 Global Standards
* **Prefix**: `/api/v1`
* **Content Type**: `application/json`
* **Response Format**:
  ```json
  {
    "success": true,
    "data": { ... },
    "error": null,
    "timestamp": "2026-11-16T18:55:00Z"
  }
  ```
* **Security & Auth**:
  * Localhost connections (KDE widget, CLI) bypass tokens or use a local session key.
  * LAN connections (Android) require `Authorization: Bearer <API_TOKEN>` generated during device pairing.

### 4.2 API Endpoint Directory

#### Health & Status
* `GET /api/v1/health`: Service health, uptime, database connection status.
* `GET /api/v1/status`: Summary of active sessions, today's metrics, and sync status.

#### Categories & Goals
* `GET /api/v1/categories`: List all categories.
* `POST /api/v1/categories`: Create a new category.
* `GET /api/v1/goals`: List active/archived goals (with optional category filter).
* `POST /api/v1/goals`: Create goal.
* `GET /api/v1/goals/{id}`: Goal details with associated tasks and progress.
* `PATCH /api/v1/goals/{id}`: Update goal attributes.
* `DELETE /api/v1/goals/{id}`: Delete or archive goal.

#### Tasks & Daily Planner
* `GET /api/v1/tasks`: Query tasks by date range (`date_from`, `date_to`), status, priority, or goal.
* `POST /api/v1/tasks`: Create task (with optional `study_cursor_topic_id`).
* `GET /api/v1/tasks/{id}`: Get task details.
* `PATCH /api/v1/tasks/{id}`: Update task properties (title, time, status, duration).
* `POST /api/v1/tasks/{id}/complete`: Mark task complete, update actual duration, and return celebration payload.
* `POST /api/v1/tasks/{id}/reschedule`: Shift task to new date/time with reason tracking.
* `DELETE /api/v1/tasks/{id}`: Delete task.
* `GET /api/v1/planner/today`: Aggregated daily view (scheduled tasks, focus targets, active streaks).
* `GET /api/v1/planner/week`: 7-day calendar matrix with workload balancing scores.

#### Reminders
* `GET /api/v1/reminders`: List active reminders.
* `POST /api/v1/reminders`: Schedule reminder for task.
* `POST /api/v1/reminders/{id}/snooze`: Snooze reminder by `minutes` (default 10).
* `POST /api/v1/reminders/{id}/dismiss`: Dismiss reminder.

#### Focus Sessions
* `POST /api/v1/focus/start`: Start a session (`task_id`, `topic_ref_id`, `type`, `planned_duration`).
* `POST /api/v1/focus/{id}/pause`: Pause active session.
* `POST /api/v1/focus/{id}/resume`: Resume paused session.
* `POST /api/v1/focus/{id}/finish`: Complete session, log actual duration, prompt for topic completion.
* `GET /api/v1/focus/active`: Get currently running session (if any).
* `GET /api/v1/focus/history`: Retrieve session logs.

#### Reviews & Analytics
* `GET /api/v1/reviews/daily/{date}`: Fetch or generate daily review for `date`.
* `POST /api/v1/reviews/daily`: Save completed daily review.
* `GET /api/v1/reviews/weekly/{start_date}`: Fetch or generate weekly review.
* `POST /api/v1/reviews/weekly`: Save completed weekly review.
* `GET /api/v1/analytics/dashboard`: Key metrics (completion rate, focus hours, streak status, goal progress).
* `GET /api/v1/analytics/velocity`: Planned vs actual study hours across tracks.

#### Study Cursor Integration
* `GET /api/v1/integrations/study-cursor/status`: Connection state, last sync, topic counts.
* `POST /api/v1/integrations/study-cursor/sync`: Trigger bi-directional synchronization check.
* `GET /api/v1/integrations/study-cursor/topics`: List imported study topics with statuses and filters.
* `POST /api/v1/integrations/study-cursor/import-topic`: Schedule a topic into the daily planner.
* `POST /api/v1/integrations/study-cursor/confirm-completion`: User-confirmed topic completion push back to Study Cursor.

---

## 5. Study Cursor Adapter Architecture

The `StudyCursorAdapter` provides clean, decoupled communication between FORGE and Study Cursor:

```
┌─────────────────────────────────────────────────────────────┐
│                     StudyCursorAdapter                      │
├─────────────────────────────────────────────────────────────┤
│ 1. ManifestReader:                                          │
│    Reads `seedData.js` / `seed-data.json` for catalog       │
│                                                             │
│ 2. CloudSyncReader:                                         │
│    Queries Supabase `tracker_data` for live completion state│
│                                                             │
│ 3. TopicMapper:                                             │
│    Maps `dm-1`, `sde-4`, `ai-12` to FORGE Tasks             │
│                                                             │
│ 4. VerifiedCompletionPusher:                                │
│    Requires user confirmation, updates Supabase & FORGE DB  │
└─────────────────────────────────────────────────────────────┘
```

### The 11-Step Verified Synchronization Cycle
1. **Catalog Ingestion**: FORGE reads Study Cursor topics (GATE, SDE, AI, Aptitude) without altering files.
2. **State Refresh**: Live progress is checked via Supabase `tracker_data` (or offline fallback).
3. **Planner Import**: User selects an eligible topic (e.g., `OS: Virtual Memory & Multi-level Paging`) to schedule for today at 4:00 PM.
4. **Task Binding**: FORGE creates a Task linked to `StudyCursorTopicReference(id='os-5')`.
5. **Reminder Trigger**: At 3:55 PM, KDE and Android fire actionable notifications: *"Focus on OS: Virtual Memory"*.
6. **Focus Initiation**: User hits *"Start Focus"* $\rightarrow$ FORGE starts a 50-minute Focus Session.
7. **Session Completion**: Timer elapses or user finishes sitting $\rightarrow$ FORGE logs 52 actual minutes.
8. **Explicit Confirmation Gate**: FORGE UI displays prompt:
   > *"You completed 52 minutes of focus on OS: Virtual Memory. Did you finish this topic?"*  
   > `[ Yes, Mark Complete in Study Cursor ]`  `[ No, Continue Next Session ]`
9. **Authorized Push**: If confirmed, `StudyCursorAdapter` updates Supabase `tracker_data` (`status: done`, `completedAt: now()`, `currentIndex + 1`).
10. **State Reconciliation**: Study Cursor updates its local state on next load/sync.
11. **History Recorded**: FORGE logs the sync event in `SyncMetadata` and updates streak statistics.

---

## 6. Multi-Platform Implementation Architecture

### 6.1 Backend Daemon & Service (`systemd`)
* Runs as a user service: `systemctl --user start forge.service`.
* Listens on `127.0.0.1:8000` (localhost) and optionally on local LAN interface with token authentication.
* Auto-starts on login, maintains SQLite connection pool, and executes background reminder checks.

### 6.2 KDE Plasma 6 Desktop Plasmoid (QML)
* Built with Qt 6 / QML for KDE Plasma 6 on Wayland.
* Employs macOS-style translucent glass card (`rgba(22, 24, 30, 0.75)` with `28px` blur and specular borders).
* Surfaces:
  * Current active focus timer with pause/stop controls.
  * Today's task list with instant one-click completion.
  * Next upcoming reminder countdown.
  * Study Cursor synchronization indicator.
* Triggers native KDE notifications via `kdialog` / `org.freedesktop.Notifications`.

### 6.3 Android Client (Flutter)
* Built with Flutter & Dart, implementing Material 3 with customized macOS-like frosted glass cards.
* Local SQLite cache for zero-latency offline performance.
* Background sync worker that automatically synchronizes with the FORGE backend when connected to the home Wi-Fi network.
* Push notifications via `flutter_local_notifications`.

---

## 7. Security, Reliability & Quality Assurance Strategy

1. **Zero Credential Exposure**: No API keys or tokens committed to source code; loaded via `.env` or system keychain.
2. **LAN Authentication**: Cryptographically secure bearer tokens for Android clients connecting over local Wi-Fi.
3. **Automated Testing Suite**:
   * Unit tests for every SQLAlchemy model and migration.
   * Integration tests for all `/api/v1` endpoints with Pytest and HTTPX.
   * Adapter tests validating that Study Cursor curriculum files are never mutated and topic statuses are preserved.
4. **Safe Database Migrations**: Every schema change managed through versioned Alembic scripts with explicit upgrade and downgrade paths.
