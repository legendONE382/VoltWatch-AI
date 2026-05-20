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


@csrf_exempt
@require_POST
def analyze_anomaly(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    required_fields = ["location", "voltage", "current", "temperature"]
    if any(field not in payload for field in required_fields):
        return JsonResponse({"error": "Missing required anomaly fields."}, status=400)

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        return JsonResponse({"error": "MISTRAL_API_KEY is not configured."}, status=500)

    prompt = (
        "URGENT GRID FAULT EVENT DETECTED. You are an autonomous senior power systems engineer. "
        "Provide exactly 3 concise technical sentences describing immediate dispatch protocol, "
        "stabilization sequence, and crew safety actions for this transformer anomaly. "
        f"Location: {payload['location']}. "
        f"Voltage: {payload['voltage']}V. "
        f"Current: {payload['current']}A. "
        f"Temperature: {payload['temperature']}°C."
    )

    mistral_payload = {
        "model": "mistral-small-latest",
        "messages": [
            {"role": "system", "content": "You produce high-urgency electrical grid dispatch instructions."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 220,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(MISTRAL_URL, headers=headers, json=mistral_payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"].strip()
    except requests.RequestException as exc:
        return JsonResponse({"error": f"Failed to reach Mistral API: {str(exc)}"}, status=502)
    except (KeyError, IndexError, TypeError):
        return JsonResponse({"error": "Unexpected Mistral API response format."}, status=502)

    return JsonResponse({"dispatch": content})
