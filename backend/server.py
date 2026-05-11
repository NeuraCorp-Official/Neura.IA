from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

from flask import Flask, request, jsonify
from flask_cors import CORS
from mind import decidir_resposta
from memory import get_all_sessions, get_messages_by_session, get_important_memories

app = Flask(__name__)
CORS(app)


@app.route("/chat", methods=["POST"])
def chat():
    data     = request.get_json()
    mensagem = data.get("mensagem", "").strip()
    if not mensagem:
        return jsonify({"resposta": "Fala algo aí."})
    resposta = decidir_resposta(mensagem)
    return jsonify({"resposta": resposta})


@app.route("/sessions", methods=["GET"])
def sessions():
    rows = get_all_sessions()
    return jsonify([
        {"id": r[0], "data": r[1], "criado_em": r[2], "total_msgs": r[3]}
        for r in rows
    ])


@app.route("/sessions/<session_id>/messages", methods=["GET"])
def session_messages(session_id):
    rows = get_messages_by_session(session_id)
    return jsonify([
        {"user": r[0], "neura": r[1], "criado_em": r[2]}
        for r in rows
    ])


@app.route("/sessions/<session_id>/memories", methods=["GET"])
def session_memories(session_id):
    rows = get_important_memories(session_id)
    return jsonify([
        {"texto": r[0], "criado_em": r[1]}
        for r in rows
    ])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)