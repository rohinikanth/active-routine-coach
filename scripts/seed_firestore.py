#!/usr/bin/env python3
"""Seed script to populate Firestore database with initial workout & recovery routines."""

from google.cloud import firestore

# IMPORTANT: Hardcode project ID as a string. On Agent Platform, GOOGLE_CLOUD_PROJECT
# or google.auth.default() return the numeric project number which breaks Firestore SDK.
PROJECT_ID = "qwiklabs-gcp-03-9a71b17e4d3a"

SEED_WORKOUTS = [
    {
        "id": "desk-stretch-1",
        "title": "10-Min Desk Stretch & Mobility",
        "category": "Mobility",
        "duration_minutes": 10,
        "equipment_needed": ["None"],
        "difficulty": "Beginner",
        "description": "Relieves tension in neck, shoulders, and lower back caused by prolonged sitting.",
        "instructions": "1. 1 min Neck Circles\n2. 2 min Seated Spine Twists\n3. 2 min Shoulder Rolls\n4. 3 min Standing Hip Flexor Stretch\n5. 2 min Deep Wrist & Forearm Stretches",
        "safety_notes": "No equipment needed. Suitable for all fitness levels during work breaks."
    },
    {
        "id": "hiit-quick-burn",
        "title": "15-Min No-Equipment Cardio HIIT",
        "category": "Cardio",
        "duration_minutes": 15,
        "equipment_needed": ["None"],
        "difficulty": "Intermediate",
        "description": "High-intensity interval session to boost energy and metabolism during lunch hours.",
        "instructions": "40s work, 20s rest x 3 rounds:\n- Jumping Jacks\n- High Knees\n- Bodyweight Squats\n- Mountain Climbers\n- Plank Hold",
        "safety_notes": "Keep hydrated and ensure clear floor space."
    },
    {
        "id": "core-stability-express",
        "title": "12-Min Core & Posture Builder",
        "category": "Strength",
        "duration_minutes": 12,
        "equipment_needed": ["Yoga Mat"],
        "difficulty": "Beginner",
        "description": "Strengthens abdominal wall, glutes, and lower back to support good ergonomic posture.",
        "instructions": "3 rounds:\n- 45s Bird-Dogs\n- 45s Glute Bridges\n- 45s Forearm Plank\n- 45s Dead Bugs\nRest 30s between rounds.",
        "safety_notes": "Focus on controlled movements rather than speed."
    },
    {
        "id": "post-workout-smoothie",
        "title": "Nut-Free Recovery Smoothie",
        "category": "Nutrition",
        "duration_minutes": 5,
        "equipment_needed": ["Blender"],
        "difficulty": "Beginner",
        "description": "A high-protein post-workout recovery smoothie completely safe for peanut and shellfish allergies.",
        "instructions": "Blend together:\n- 1 scoop Whey or Pea Protein Powder (Nut-Free)\n- 1 cup Oat Milk or Soy Milk\n- 1 Frozen Banana\n- 1 tbsp Chia Seeds\n- 1/2 cup Frozen Berries",
        "safety_notes": "Allergy-Safe: Free from peanuts, tree nuts, and shellfish."
    },
    {
        "id": "evening-winddown",
        "title": "8-Min Evening Stress Relief & Stretch",
        "category": "Mobility",
        "duration_minutes": 8,
        "equipment_needed": ["None"],
        "difficulty": "Beginner",
        "description": "Calming evening routine to lower cortisol and transition from work mode to rest.",
        "instructions": "Hold each pose for 60 seconds:\n- Child's Pose\n- Cat-Cow Flow\n- Legs-Up-The-Wall Pose\n- Reclined Bound Angle Pose\n- Seated Forward Fold",
        "safety_notes": "Breathe deeply and hold positions gently without straining."
    }
]


def seed_database():
    print(f"Connecting to Firestore for project: '{PROJECT_ID}'...")
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection("workouts")

    for item in SEED_WORKOUTS:
        doc_id = item["id"]
        collection_ref.document(doc_id).set(item)
        print(f"  ✓ Seeded document: workouts/{doc_id} ('{item['title']}')")

    print("Successfully seeded all workout items to Firestore!")


if __name__ == "__main__":
    seed_database()
