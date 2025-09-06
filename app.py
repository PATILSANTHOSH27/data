import json
import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# GitHub raw URLs (replace with your actual repo + branch)
DISEASES_URL = "https://raw.githubusercontent.com/PATILSANTHOSH27/data/main/diseases.json"
SYMPTOMS_URL = "https://raw.githubusercontent.com/PATILSANTHOSH27/data/main/symptoms.json"
PREVENTIONS_URL = "https://raw.githubusercontent.com/PATILSANTHOSH27/data/main/preventions.json"


def load_json_from_url(url):
    """Fetch JSON data from GitHub raw URL"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()["entries"]
    except Exception as e:
        print(f"Error loading {url}: {e}")
        return []


# Load JSON data from GitHub
diseases_data = load_json_from_url(DISEASES_URL)
symptoms_data = load_json_from_url(SYMPTOMS_URL)
preventions_data = load_json_from_url(PREVENTIONS_URL)


def find_entity_info(entity_list, disease_name):
    """Helper to fetch info from JSON by disease name"""
    disease_name = disease_name.lower()
    for entry in entity_list:
        if entry["value"].lower() == disease_name:
            return entry["synonyms"]
    return None


@app.route("/", methods=["GET"])
def index():
    return "Dialogflow Webhook is running ✅ (data from GitHub)"


@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(silent=True, force=True)
    
    intent = req.get("queryResult", {}).get("intent", {}).get("displayName")
    params = req.get("queryResult", {}).get("parameters", {})
    disease_name = params.get("sa")  # your entity name is 'sa'

    response_text = "Sorry, I couldn't find information for that."

    if intent == "disease" and disease_name:
        # Lookup from GitHub-hosted JSONs
        symptoms = find_entity_info(symptoms_data, disease_name)
        preventions = find_entity_info(preventions_data, disease_name)
        disease_info = find_entity_info(diseases_data, disease_name)

        response_text = f"Here is what I know about {disease_name}:\n"

        if disease_info:
            response_text += f"\n📝 General Info: {', '.join(disease_info)}"
        if symptoms:
            response_text += f"\n🤒 Symptoms: {', '.join(symptoms)}"
        if preventions:
            response_text += f"\n🛡 Prevention: {', '.join(preventions)}"

    return jsonify({"fulfillmentText": response_text})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
