# VoltWatch AI

A stateless Django command-center application that simulates IoT electrical-transformer telemetry, detects hazardous anomalies in the browser, and uses a secure Django proxy to request emergency dispatch guidance from the Mistral AI API.

> **Key principle:** No server-side database is required. All telemetry history and dispatch logs are persisted in the user’s browser via `localStorage`.

---

## Features

- **Real-time telemetry simulation** (every 4 seconds) for Lagos grid locations.
- **Client-side anomaly detection** using thresholds:
  - Temperature > **95°C**
  - Voltage > **260V**
- **AI dispatch proxy** via Django to Mistral (`mistral-small-latest`) using `MISTRAL_API_KEY`.
- **Manual incident injection panel** for judge/demo scenarios.
- **Live KPI analytics**:
  - Total Telemetry Logs
  - Active Grid Anomalies
  - AI Triage Rate
- **Regional status grid** with animated health indicators.
- **Audio accessibility** with **🔊 Read Dispatch Aloud** (Web Speech API).
- **Vercel-ready** deployment with WSGI routing and WhiteNoise static support.

---

## Tech Stack

- **Backend:** Django 4.2+, Requests, WhiteNoise
- **Frontend:** Tailwind CSS (CDN), vanilla JavaScript
- **Persistence:** Browser `localStorage` only
- **AI Integration:** Mistral Chat Completions API

---

## Project Structure

```text
.
├── manage.py
├── requirements.txt
├── vercel.json
├── monitoring/
│   ├── __init__.py
│   ├── views.py
│   └── templates/
│       └── monitoring/
│           └── dashboard.html
└── voltwatch/
    ├── __init__.py
    ├── settings.py
    ├── urls.py
    └── wsgi.py
```

---

## How the Site Works

## 1) Django serves one dashboard + one API endpoint

- `GET /` renders the dashboard page.
- `POST /api/telemetry/` accepts telemetry or manual-incident payloads and proxies them to Mistral.

The URL routing is defined in `voltwatch/urls.py` and mapped to views in `monitoring/views.py`.

## 2) Frontend simulation loop generates telemetry

Inside `dashboard.html`, JavaScript runs a loop every 4 seconds:

1. Pick a random Lagos location.
2. Generate realistic voltage/current/temperature values.
3. Compute anomaly status (`is_anomaly`) from thresholds.
4. Save the new event into the local `logs` array.
5. Persist logs in `localStorage`.
6. Re-render KPIs, region statuses, telemetry table, and dispatch feed.

If the event is anomalous, the frontend automatically calls `POST /api/telemetry/` to request AI triage guidance.

## 3) Manual incident injector (judge interaction)

The Judge Panel allows selecting a location and entering incident text (example: flooding, explosion, etc.).

When **Trigger Emergency** is clicked:

1. Button disables to prevent duplicate submissions.
2. Frontend posts `{ location, situation }` to `/api/telemetry/`.
3. Backend requests a 3-sentence technical containment protocol from Mistral.
4. The result is appended to the same local history array as a `manual-override` entry.
5. UI re-renders immediately.

## 4) Backend proxy logic (stateless)

`monitoring/views.py`:

- Validates JSON payloads.
- Detects payload type:
  - **Automated simulation:** `location`, `voltage`, `current`, `temperature`
  - **Manual incident:** `location`, `situation`
- Builds dynamic prompts tailored to event type.
- Sends request to `https://api.mistral.ai/v1/chat/completions` with model `mistral-small-latest`.
- Returns JSON response: `{ dispatch, type }`.

No ORM models or migrations are used.

## 5) Browser persistence model

All runtime logs are stored under a `localStorage` key (`voltwatch_logs_v2`).

This means:

- Data persists on refresh for that browser/profile.
- Data is isolated per user/browser.
- Reset button clears local cache and UI state.

## 6) Accessibility enhancement

Each dispatch card has **🔊 Read Dispatch Aloud**.
Clicking it uses `window.speechSynthesis` to read the dispatch text for operations-room playback.

---

## Local Development

### Prerequisites

- Python 3.10+
- A Mistral API key

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export MISTRAL_API_KEY="your_api_key_here"
python manage.py runserver
```

Open: `http://127.0.0.1:8000/`

---

## API Contract

### `POST /api/telemetry/`

### A) Automated Simulation Payload

```json
{
  "location": "Alausa Substation",
  "voltage": 268.7,
  "current": 214.4,
  "temperature": 99.1
}
```

### B) Manual Incident Payload

```json
{
  "location": "Magboro Transmission Substation",
  "situation": "Transformer explosion due to lightning strike"
}
```

### Success Response

```json
{
  "dispatch": "...markdown technical protocol...",
  "type": "automated"
}
```

(or `"type": "manual"`)

---

## Deployment (Vercel)

This repository is configured for Vercel using:

- `vercel.json` routing all traffic to `voltwatch/wsgi.py`
- `app = application` export in WSGI
- WhiteNoise middleware/static configuration in Django settings

Set environment variable in Vercel project settings:

- `MISTRAL_API_KEY`

Then deploy.

---

## Notes

- This is a simulation/demo architecture and not a replacement for SCADA/OT-grade production controls.
- For production hardening, add authentication, rate limiting, audit trails, and strict host/CORS settings.
