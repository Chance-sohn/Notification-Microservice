from flask import Flask, jsonify, request

app = Flask(__name__)
WARNING_THRESHOLD = 75

def is_number(value):
    """ Return True for int/float values, but not booleans """
    return isinstance(value, (int, float)) and not isinstance(value, bool)


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.post("/notification")
def notification():
    """ Return a budget status notification based on current spending and a limit """
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    current = data.get("current")
    limit = data.get("limit")

    if not is_number(current) or not is_number(limit):
        return jsonify({"error": "current and limit must be numeric"}), 400

    if current < 0:
        return jsonify({"error": "current cannot be negative"}), 400

    if limit <= 0:
        return jsonify({"error": "limit must be greater than zero"}), 400

    percentage = round((current / limit) * 100, 2)
    remaining = round(max(limit - current, 0), 2)

    if current >= limit:
        over_by = round(current - limit, 2)

        if over_by > 0:
            level = "alert"
            message = (
                f"Budget exceeded. You are ${over_by:.2f} over your "
                f"${limit:.2f} budget."
            )
        else:
            level = "alert"
            message = f"You have reached your ${limit:.2f} budget limit."

    elif percentage >= WARNING_THRESHOLD:
        level = "warning"
        message = (
            f"Warning: You have used {percentage:.2f}% of your budget. "
            f"${remaining:.2f} remains."
        )

    else:
        level = "normal"
        message = (
            f"You have used {percentage:.2f}% of your budget. "
            f"${remaining:.2f} remains."
        )

    return jsonify({
        "level": level,
        "message": message,
        "current": round(current, 2),
        "limit": round(limit, 2),
        "percentage": percentage,
        "remaining": remaining,
    }), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5010, debug=True)
