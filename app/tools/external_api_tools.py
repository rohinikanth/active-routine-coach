"""External Public API tools for ActiveRoutine Coach."""

import json
import os
from typing import Any, Dict, List
import urllib.request


def fetch_public_exercise_catalog(limit: int = 5) -> List[Dict[str, Any]]:
    """Fetch real exercise routines and equipment info from the free Wger Workout Manager API.

    Args:
        limit: Number of exercises to retrieve (1 to 10, default 5).

    Returns:
        List of exercise dictionaries with name, category, equipment, and description.
    """
    safe_limit = min(max(1, limit), 10)
    url = f"https://wger.de/api/v2/exerciseinfo/?limit={safe_limit}"

    headers = {"User-Agent": "ActiveRoutineCoach/1.0"}
    # Read optional API key from environment variable if provided
    api_key = os.environ.get("WGER_API_KEY")
    if api_key:
        headers["Authorization"] = f"Token {api_key}"

    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode())
            exercises = []

            for item in data.get("results", []):
                translations = item.get("translations", [])
                en_trans = next((t for t in translations if t.get("language") == 2), None)
                if not en_trans and translations:
                    en_trans = translations[0]

                name = en_trans.get("name") if en_trans else "Exercise Routine"
                desc = en_trans.get("description_source", "") if en_trans else ""
                clean_desc = desc.replace("<p>", "").replace("</p>", "\n").replace("&nbsp;", " ").strip()

                equipment = [eq.get("name") for eq in item.get("equipment", []) if eq.get("name")]
                category = item.get("category", {}).get("name", "General")

                exercises.append({
                    "name": name,
                    "category": category,
                    "equipment": equipment or ["Bodyweight"],
                    "description": clean_desc[:250] if clean_desc else "Standard exercise routine.",
                })

            return exercises
    except Exception as e:
        return [{"error": f"Failed to fetch public exercise data from Wger API: {str(e)}"}]
