import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from prism.config import DB_PATH

def init_db(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS runs (
        run_id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL,
        input_type TEXT,
        source_text TEXT,
        normalized_text TEXT,
        tone TEXT,
        audience TEXT,
        objective TEXT,
        selected_outputs TEXT,
        fact_graph TEXT,
        generated_outputs TEXT,
        guardrail_result TEXT,
        revision_count INTEGER,
        provenance TEXT,
        rendered_assets TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_run(state: Dict[str, Any], db_path: str = DB_PATH) -> str:
    init_db(db_path)
    run_id = state.get("run_id") or str(uuid.uuid4())[:8]
    created_at = datetime.utcnow().isoformat()

    # Collect generated outputs dictionary
    gen_outputs = {}
    if state.get("linkedin_output"):
        gen_outputs["linkedin"] = state["linkedin_output"]
    if state.get("twitter_output"):
        gen_outputs["twitter"] = state["twitter_output"]
    if state.get("summary_output"):
        gen_outputs["summary"] = state["summary_output"]
    if state.get("advisory_output"):
        gen_outputs["advisory"] = state["advisory_output"]
    if state.get("presentation_output"):
        gen_outputs["presentation"] = state["presentation_output"]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO runs (
        run_id, created_at, input_type, source_text, normalized_text,
        tone, audience, objective, selected_outputs, fact_graph,
        generated_outputs, guardrail_result, revision_count, provenance, rendered_assets
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        run_id,
        created_at,
        state.get("input_type", "text"),
        state.get("source_text", ""),
        state.get("normalized_text", ""),
        state.get("tone", "professional"),
        state.get("audience", "General"),
        state.get("objective", "Multi-channel synthesis"),
        json.dumps(state.get("selected_outputs", [])),
        json.dumps(state.get("fact_graph", {})),
        json.dumps(gen_outputs),
        json.dumps(state.get("guardrail_result", {})),
        state.get("revision_count", 0),
        json.dumps(state.get("provenance", [])),
        json.dumps(state.get("rendered_assets", {}))
    ))
    conn.commit()
    conn.close()
    return run_id

def get_run(run_id: str, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "run_id": row[0],
        "created_at": row[1],
        "input_type": row[2],
        "source_text": row[3],
        "normalized_text": row[4],
        "tone": row[5],
        "audience": row[6],
        "objective": row[7],
        "selected_outputs": json.loads(row[8] or "[]"),
        "fact_graph": json.loads(row[9] or "{}"),
        "generated_outputs": json.loads(row[10] or "{}"),
        "guardrail_result": json.loads(row[11] or "{}"),
        "revision_count": row[12],
        "provenance": json.loads(row[13] or "[]"),
        "rendered_assets": json.loads(row[14] or "{}")
    }

def list_runs(db_path: str = DB_PATH, limit: int = 50) -> List[Dict[str, Any]]:
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT run_id, created_at, input_type, tone, audience, selected_outputs, revision_count
    FROM runs ORDER BY created_at DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()

    runs = []
    for r in rows:
        runs.append({
            "run_id": r[0],
            "created_at": r[1],
            "input_type": r[2],
            "tone": r[3],
            "audience": r[4],
            "selected_outputs": json.loads(r[5] or "[]"),
            "revision_count": r[6]
        })
    return runs

def delete_run(run_id: str, db_path: str = DB_PATH) -> bool:
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM runs WHERE run_id = ?", (run_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted
