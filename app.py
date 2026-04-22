from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data["message"]
    lang = data.get("lang", "en")

    system_prompt = "You are a first aid assistant. Give short, safe advice for minor injuries only."

    if lang == "hi":
        system_prompt += " Reply in Hindi."

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )

    return jsonify({"reply": response.choices[0].message.content})


@app.route("/analyze-image", methods=["POST"])
def analyze_image():
    image = request.json["image"]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Identify injury and give first aid advice."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this injury"},
                    {"type": "image_url", "image_url": {"url": image}}
                ]
            }
        ]
    )

    return jsonify({"reply": response.choices[0].message.content})


if __name__ == "__main__":
    app.run()
