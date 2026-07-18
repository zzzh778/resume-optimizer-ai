"""
Token 消耗追踪模块。

记录每次 AI 调用产生的 token 消耗和成本。
"""

from datetime import datetime

from database import _get_conn

# DeepSeek 官方价格（每 1K tokens）
PRICING = {
    "deepseek-chat": {"input": 0.00027, "output": 0.0011},
    "deepseek-reasoner": {"input": 0.00055, "output": 0.0022},
}

DEFAULT_MODEL = "deepseek-chat"


def _calc_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    price = PRICING.get(model, PRICING[DEFAULT_MODEL])
    input_cost = (input_tokens / 1000) * price["input"]
    output_cost = (output_tokens / 1000) * price["output"]
    return round(input_cost + output_cost, 6)


def save_token_usage(
    user_id: int,
    model: str,
    input_tokens: int,
    output_tokens: int,
    total_tokens: int,
):
    cost = _calc_cost(model, input_tokens, output_tokens)
    conn = _get_conn()
    conn.execute(
        "INSERT INTO api_usage (user_id, model_name, input_tokens, output_tokens, total_tokens, estimated_cost) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, model, input_tokens, output_tokens, total_tokens, cost),
    )
    conn.commit()
    conn.close()


def save_analysis_token_batch(user_id: int, token_data: list[dict]):
    for item in token_data:
        save_token_usage(
            user_id=user_id,
            model=item.get("model", DEFAULT_MODEL),
            input_tokens=item.get("input_tokens", 0),
            output_tokens=item.get("output_tokens", 0),
            total_tokens=item.get("total_tokens", 0),
        )


def get_token_stats() -> dict:
    conn = _get_conn()
    today = datetime.now().strftime("%Y-%m-%d")

    total_input = conn.execute("SELECT COALESCE(SUM(input_tokens), 0) FROM api_usage").fetchone()[0]
    total_output = conn.execute("SELECT COALESCE(SUM(output_tokens), 0) FROM api_usage").fetchone()[0]
    total_all = conn.execute("SELECT COALESCE(SUM(total_tokens), 0) FROM api_usage").fetchone()[0]
    total_cost = conn.execute("SELECT COALESCE(SUM(estimated_cost), 0) FROM api_usage").fetchone()[0]

    today_input = conn.execute(
        "SELECT COALESCE(SUM(input_tokens), 0) FROM api_usage WHERE date(created_at) = ?",
        (today,),
    ).fetchone()[0]
    today_output = conn.execute(
        "SELECT COALESCE(SUM(output_tokens), 0) FROM api_usage WHERE date(created_at) = ?",
        (today,),
    ).fetchone()[0]
    today_all = conn.execute(
        "SELECT COALESCE(SUM(total_tokens), 0) FROM api_usage WHERE date(created_at) = ?",
        (today,),
    ).fetchone()[0]
    today_cost = conn.execute(
        "SELECT COALESCE(SUM(estimated_cost), 0) FROM api_usage WHERE date(created_at) = ?",
        (today,),
    ).fetchone()[0]

    model_usage = conn.execute(
        "SELECT model_name, COUNT(*) as calls, SUM(total_tokens) as tokens, SUM(estimated_cost) as cost "
        "FROM api_usage GROUP BY model_name ORDER BY cost DESC"
    ).fetchall()

    conn.close()
    return {
        "total": {"input": total_input, "output": total_output, "tokens": total_all, "cost": round(total_cost, 6)},
        "today": {"input": today_input, "output": today_output, "tokens": today_all, "cost": round(today_cost, 6)},
        "models": [dict(r) for r in model_usage],
    }
