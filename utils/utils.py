import json

def load_data(file_path="data/startup_data.json"):
    with open(file_path, "r") as f:
        return json.load(f)

def search_startup_data(question, data):
    question = question.lower()
    results = []

    for entry in data:
        # Search in multiple fields
        searchable_text = f"{entry.get('title', '')} {entry.get('decision', '')} {entry.get('source', '')} {' '.join(entry.get('tags', []))}".lower()
        if any(word in searchable_text for word in question.split()):
            results.append({
                "title": entry.get("title", ""),
                "decision": entry.get("decision", ""),
                "source": entry.get("source", ""),
                "tags": entry.get("tags", [])
            })

    if results:
        return results[0]  # return first match for MVP
    else:
        return "Sorry, no answer found for your question."