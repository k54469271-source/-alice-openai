
import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return "Alice server is running!"


@app.route("/alice", methods=["POST"])
def alice():
    data = request.get_json(silent=True) or {}

    user_text = (
        data.get("request", {})
        .get("command", "")
        .strip()
    )

    if not user_text:
        user_text = "Привет!"

    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        answer = "Сервер пока не настроен."
    else:
        try:
            response = requests.post(
                "https://api.openai.com/v1/responses",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4.1-mini",
                    "input": user_text,
                },
                timeout=20,
            )
            response.raise_for_status()
            result = response.json()

            answer = ""
            for item in result.get("output", []):
                if item.get("type") == "message":
                    for content in item.get("content", []):
                        if content.get("type") == "output_text":
                            answer += content.get("text", "")

            if not answer:
                answer = "Не получилось получить ответ."

        except Exception:
            answer = "Ошибка соединения с ИИ. Попробуй ещё раз."

    return jsonify({
        "response": {
            "text": answer[:1024],
            "end_session": False
        },
        "version": "1.0"
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
