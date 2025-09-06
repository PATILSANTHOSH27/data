import json
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load data from JSON files
with open("diseases.json") as f:
    diseases_data = json.load(f)["entries"]

with open("symptoms.json") as f:
    symptoms_data = json.load(f)["entries"]

with open("preventions.json") as f:
    preventions_data = json.load(f)["entries"]


def find_entity_info(entity_list, disease_name):
    """Helper to fetch info from JSON by disease name"""
    for entry in entity_list:
        if entry["value"].lower() == disease_name.lower():
            return entry["synonyms"]
    return None


@app.route("/", methods=["GET"])
def index():
    return "Dialogflow Webhook is running ✅"


@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(silent=True, force=True)
    
    intent = req.get("queryResult", {}).get("intent", {}).get("displayName")
    params = req.get("queryResult", {}).get("parameters", {})
    disease_name = params.get("sa")  # your entity name is 'sa'

    response_text = "Sorry, I couldn't find information for that."

    if intent == "disease" and disease_name:
        # Check in all JSON files
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

