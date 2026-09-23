# ActiveRoutine Coach & Productivity Companion

ActiveRoutine Coach is an AI assistant built with Google Agent Development Kit (ADK) and deployed to Vertex AI Agent Runtime. It helps users stay active with quick, low-friction micro-routines (stretches, micro-workouts, posture resets, and recovery nutrition), tracks personal habits, remembers allergies across sessions, and generates motivational badge images.

---

## Key Features & Connected Services

- **Vertex AI Memory Bank**: Preserves user preferences, daily schedules, and allergies across sessions, automatically customizing recommendations.
- **Google Cloud Firestore**: Provides persistence for workout routines and activity logs. Supports searching, retrieving, adding new routines, and logging activity completions.
- **Domain Stats Calculator**: Calculates total calorie burn and MET (Metabolic Equivalent of Task) metrics for logged activities.
- **Wger Exercise API Integration**: Fetches exercise suggestions from the free public Wger REST API (`https://wger.de/api/v2/exerciseinfo/`).
- **Gemini Image Generation & Public Cloud Storage**: Generates motivational badge images using `gemini-3.1-flash-lite-image`, saves artifacts locally, and uploads image bytes directly to a public Google Cloud Storage bucket to return public HTTPS URLs.
- **Agent Engine Sandbox Code Execution**: Securely executes Python scripts in an isolated Agent Engine sandbox environment (`AgentEngineSandboxCodeExecutor`).
- **A2UI Rich Card Rendering**: Emits A2UI schema version 0.8 surfaces (Cards, Columns, Rows, Text, Images) transformed via `a2ui_callback` for native card rendering in dev UI and web frontends.
- **FastAPI A2A Proxy & Web UI**: Includes a lightweight FastAPI web proxy (`frontend/main.py`) that communicates with the deployed agent over the Agent-to-Agent (A2A) protocol.

---

## Code Architecture

- **`app/agent.py`**: Main ADK root agent configuration, Memory Bank callback, A2UI system prompt generation, code executor setup, and tool registrations.
- **`app/a2ui_utils.py`**: A2UI message extractor and callback handler (`a2ui_callback`).
- **`app/tools/firestore_tools.py`**: Firestore CRUD tools (`get_workout`, `search_workouts`, `add_workout_routine`, `log_completed_activity`) and `calculate_workout_stats`.
- **`app/tools/external_api_tools.py`**: Wger public REST API tool (`fetch_public_exercise_catalog`).
- **`app/tools/image_tools.py`**: Gemini image generation & GCS upload tool (`generate_routine_image`).
- **`frontend/`**: FastAPI proxy server (`main.py`) and chat interface (`static/index.html`) using the A2A protocol.
- **`agents-cli-manifest.yaml`**: Project deployment configuration for Vertex AI Agent Runtime.

---

## Local Setup & Execution

### Prerequisites

- Python 3.10+
- `uv` package manager installed
- Google Cloud SDK (`gcloud`) authenticated with Application Default Credentials (ADC)

### 1. Install Dependencies

```bash
uv sync
```

### 2. Run the ADK Local Dev UI

To test the agent locally using the ADK dev UI:

```bash
uv run adk web --port 8080 --allow_origins "*"
```

> **Note**: In the ADK web interface, turn Token Streaming OFF (via the gear icon) for A2UI cards to render automatically.

### 3. Run the FastAPI Frontend Proxy Locally

Set the environment variables and launch the FastAPI server:

```bash
export AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_ID>/locations/<LOCATION>/reasoningEngines/<REASONING_ENGINE_ID>"
export AGENT_DIRECTORY="app"
uv run python frontend/main.py
```

---

## Deployment Instructions

### Deploy Agent to Vertex AI Agent Runtime

```bash
agents-cli deploy --region us-central1 --no-confirm-project
```

### Deploy Frontend Proxy to Cloud Run

```bash
gcloud run deploy active-routine-coach-frontend \
  --source ./frontend \
  --region us-central1 \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_ID>/locations/us-central1/reasoningEngines/<REASONING_ENGINE_ID>",AGENT_DIRECTORY="app" \
  --allow-unauthenticated
```
