"""Firestore backend tools for ActiveRoutine Coach."""

from typing import Any, Dict, List, Optional
from google.cloud import firestore

# IMPORTANT: Hardcode project ID as a string. On Agent Platform, GOOGLE_CLOUD_PROJECT
# or google.auth.default() return the numeric project number which breaks Firestore SDK.
PROJECT_ID = "qwiklabs-gcp-03-9a71b17e4d3a"

# Initialize lazy client
_db_client: Optional[firestore.Client] = None


def get_db() -> firestore.Client:
    global _db_client
    if _db_client is None:
        _db_client = firestore.Client(project=PROJECT_ID)
    return _db_client


def get_workout(workout_id: str) -> Dict[str, Any]:
    """Retrieve details for a specific workout or routine by ID from Firestore.

    Args:
        workout_id: Unique ID of the workout (e.g. 'desk-stretch-1', 'hiit-quick-burn').

    Returns:
        Dict containing workout details, or an error message if not found.
    """
    db = get_db()
    doc_ref = db.collection("workouts").document(workout_id)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    return {"error": f"Workout '{workout_id}' not found in database."}


def search_workouts(
    category: Optional[str] = None,
    max_duration_minutes: Optional[int] = None,
    difficulty: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Search available workout and recovery routines in Firestore with optional filters.

    Args:
        category: Filter by category (e.g., 'Mobility', 'Cardio', 'Strength', 'Nutrition').
        max_duration_minutes: Maximum duration in minutes.
        difficulty: Filter by difficulty ('Beginner', 'Intermediate', 'Advanced').

    Returns:
        List of matching workout dictionaries.
    """
    db = get_db()
    query = db.collection("workouts")

    if category:
        query = query.where("category", "==", category)
    if difficulty:
        query = query.where("difficulty", "==", difficulty)

    results = []
    for doc in query.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        if max_duration_minutes and data.get("duration_minutes", 0) > max_duration_minutes:
            continue
        results.append(data)

    return results


def add_workout_routine(
    workout_id: str,
    title: str,
    category: str,
    duration_minutes: int,
    equipment_needed: List[str],
    difficulty: str,
    description: str,
    instructions: str,
    safety_notes: str = "",
) -> str:
    """Create or update a workout or recovery routine in Firestore.

    Args:
        workout_id: Unique identifier for the routine (e.g., 'core-burn-15').
        title: User-facing title.
        category: Category ('Mobility', 'Cardio', 'Strength', 'Nutrition').
        duration_minutes: Duration in minutes.
        equipment_needed: List of required equipment (e.g. ['None'], ['Dumbbells']).
        difficulty: Difficulty level ('Beginner', 'Intermediate', 'Advanced').
        description: Short overview.
        instructions: Step-by-step routine instructions.
        safety_notes: Safety guidelines or allergy disclaimers.

    Returns:
        Confirmation string.
    """
    db = get_db()
    item = {
        "id": workout_id,
        "title": title,
        "category": category,
        "duration_minutes": duration_minutes,
        "equipment_needed": equipment_needed,
        "difficulty": difficulty,
        "description": description,
        "instructions": instructions,
        "safety_notes": safety_notes,
    }
    db.collection("workouts").document(workout_id).set(item)
    return f"Successfully created workout routine '{title}' (ID: {workout_id}) in Firestore."


def log_completed_activity(
    workout_id: str,
    duration_minutes: int,
    notes: str = "",
) -> str:
    """Log a completed workout activity to the Firestore 'activity_logs' collection.

    Args:
        workout_id: ID of the workout completed.
        duration_minutes: Minutes spent on activity.
        notes: User reflection or notes on the session.

    Returns:
        Confirmation message with generated log ID.
    """
    db = get_db()
    log_ref = db.collection("activity_logs").document()
    log_data = {
        "log_id": log_ref.id,
        "workout_id": workout_id,
        "duration_minutes": duration_minutes,
        "notes": notes,
        "timestamp": firestore.SERVER_TIMESTAMP,
    }
    log_ref.set(log_data)
    return f"Logged completed workout '{workout_id}' for {duration_minutes} minutes (Log ID: {log_ref.id})."


def calculate_workout_stats(
    duration_minutes: int,
    category: str = "Cardio",
    intensity: str = "Moderate",
    weight_kg: float = 70.0,
) -> Dict[str, Any]:
    """Calculates estimated calorie expenditure and health metrics for a workout session.

    Args:
        duration_minutes: Duration of the exercise session in minutes.
        category: Category of workout ('Mobility', 'Cardio', 'Strength', 'Nutrition').
        intensity: Intensity level ('Low', 'Moderate', 'High').
        weight_kg: Body weight in kilograms (defaults to 70kg if unstated).

    Returns:
        Dict with estimated_calories_burned, met_score, and recommended_hydration_ml.
    """
    met_map = {
        "Mobility": {"Low": 2.5, "Moderate": 3.5, "High": 4.5},
        "Cardio": {"Low": 5.0, "Moderate": 7.5, "High": 10.0},
        "Strength": {"Low": 3.5, "Moderate": 6.0, "High": 8.0},
    }
    cat_mets = met_map.get(category, {"Low": 3.0, "Moderate": 5.0, "High": 7.0})
    met = cat_mets.get(intensity, 5.0)

    # Formula: Calories = MET * weight_kg * (duration_minutes / 60)
    calories = round(met * weight_kg * (duration_minutes / 60.0), 1)
    hydration_ml = int(duration_minutes * 12.5)  # ~250ml per 20 mins

    return {
        "duration_minutes": duration_minutes,
        "category": category,
        "intensity": intensity,
        "met_score": met,
        "estimated_calories_burned": calories,
        "recommended_hydration_ml": hydration_ml,
    }

