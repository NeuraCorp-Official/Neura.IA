import os
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING

_client = MongoClient(os.environ.get("MONGODB_URI"))
db = _client["neuracorp"]

col_sessions = db["sessions"]
col_messages = db["messages"]
col_memories = db["important_memories"]

SESSION_ID = datetime.now().strftime("%Y%m%d_%H%M%S")


def _criar_sessao():
    col_sessions.update_one(
        {"_id": SESSION_ID},
        {"$setOnInsert": {
            "_id":       SESSION_ID,
            "data":      datetime.now().strftime("%Y-%m-%d"),
            "criado_em": datetime.now()
        }},
        upsert=True
    )

_criar_sessao()


def remember(user_input: str, response: str):
    col_messages.insert_one({
        "session_id": SESSION_ID,
        "user":       user_input,
        "neura":      response,
        "criado_em":  datetime.now()
    })


def get_memory_da_sessao(limit: int = 10) -> list:
    return list(
        col_messages
        .find({"session_id": SESSION_ID}, {"_id": 0, "user": 1, "neura": 1})
        .sort("criado_em", ASCENDING)
        .limit(limit)
    )


def get_messages_by_session(session_id: str) -> list:
    return list(
        col_messages
        .find({"session_id": session_id}, {"_id": 0, "user": 1, "neura": 1, "criado_em": 1})
        .sort("criado_em", ASCENDING)
    )


def remember_important(texto: str):
    col_memories.insert_one({
        "session_id": SESSION_ID,
        "texto":      texto,
        "criado_em":  datetime.now()
    })


def get_important_memories(session_id: str = None) -> list:
    sid  = session_id or SESSION_ID
    docs = list(
        col_memories
        .find({"session_id": sid}, {"_id": 0, "texto": 1, "criado_em": 1})
        .sort("criado_em", ASCENDING)
    )
    return [(d["texto"], str(d["criado_em"])) for d in docs]


def get_all_sessions() -> list:
    pipeline = [
        {"$lookup": {
            "from": "messages",
            "localField": "_id",
            "foreignField": "session_id",
            "as": "msgs"
        }},
        {"$project": {
            "id": "$_id",
            "data": 1,
            "criado_em": 1,
            "total_msgs": {"$size": "$msgs"}
        }},
        {"$sort": {"criado_em": DESCENDING}}
    ]
    return [
        (r["id"], r["data"], str(r["criado_em"]), r["total_msgs"])
        for r in list(col_sessions.aggregate(pipeline))
    ]
