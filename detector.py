from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__)

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def detect_ai_or_human(text):
    labels = ["AI-Generated", "Human-Written"]
    results = classifier(text, candidate_labels=labels)
    return results["labels"][0], float(results["scores"][0])

@app.route("/detect", methods=["POST"])
def detect():
    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"error": "Invalid request. Please provide 'text' field."}), 400

    text = data["text"]
    label, score = detect_ai_or_human(text)

    return jsonify({
        "label": label,
        "score": score
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
