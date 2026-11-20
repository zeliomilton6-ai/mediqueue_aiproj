from database import get_completed_durations, get_patients

DEFAULT_SERVICE_MINUTES = 15

def average_service_time(department):
    history = get_completed_durations(department)
    if not history:
        return DEFAULT_SERVICE_MINUTES
    return sum(history) / len(history)

def predict_wait(patient_id):
    """
    Transparent baseline estimate: number of patients ahead multiplied
    by the department's average completed service duration.
    Not a validated clinical or operational AI model.
    """
    waiting = get_patients(status="Waiting")
    target = next((p for p in waiting if p["id"] == patient_id), None)
    if target is None:
        return None

    ahead = []
    for patient in waiting:
        if patient["department"] != target["department"]:
            continue
        if patient["id"] == patient_id:
            break
        ahead.append(patient)

    average = average_service_time(target["department"])
    return {
        "people_ahead": len(ahead),
        "minutes": round(len(ahead) * average)
    }
