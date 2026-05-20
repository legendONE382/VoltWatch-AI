import json
import os

import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"


@require_GET
def dashboard(request):
    return render(request, "monitoring/dashboard.html")


def _build_prompt(payload):
    location = payload["location"]
    has_manual = "situation" in payload and isinstance(payload.get("situation"), str) and payload["situation"].strip()

    if has_manual:
        situation = payload["situation"].strip()
        system_prompt = (
            "You are an emergency electrical grid dispatcher. "
            "Return exactly 3 technical sentences in markdown with containment protocol, field isolation steps, "
            "and crew/public safety controls."
        )
        user_prompt = (
            "MANUAL INCIDENT OVERRIDE RECEIVED. Build an urgent containment dispatch protocol for this event. "
            f"Location: {location}. Incident: {situation}."
        )
        return system_prompt, user_prompt, "manual"

    required = ["voltage", "current", "temperature"]
    if any(k not in payload for k in required):
        raise ValueError("Automated simulation payload requires location, voltage, current, and temperature.")

    system_prompt = (
        "You are an autonomous senior power systems engineer. "
        "Return exactly 3 concise technical sentences in markdown for transformer anomaly response."
    )
    user_prompt = (
        "AUTOMATED GRID ANOMALY DETECTED. Provide immediate triage, stabilization sequence, and crew safety actions. "
        f"Location: {location}. Voltage: {payload['voltage']}V. Current: {payload['current']}A. Temperature: {payload['temperature']}°C."
    )
    return system_prompt, user_prompt, "automated"


@csrf_exempt
@require_POST
def telemetry_proxy(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    if not isinstance(payload, dict) or "location" not in payload:
        return JsonResponse({"error": "Payload must include location."}, status=400)

    try:
        system_prompt, user_prompt, payload_type = _build_prompt(payload)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        return JsonResponse({"error": "MISTRAL_API_KEY is not configured."}, status=500)

    mistral_payload = {
        "model": "mistral-small-latest",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 260,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(MISTRAL_URL, headers=headers, json=mistral_payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        dispatch = data["choices"][0]["message"]["content"].strip()
    except requests.RequestException as exc:
        return JsonResponse({"error": f"Failed to reach Mistral API: {exc}"}, status=502)
    except (KeyError, IndexError, TypeError):
        return JsonResponse({"error": "Unexpected Mistral API response format."}, status=502)

    return JsonResponse({"dispatch": dispatch, "type": payload_type})
