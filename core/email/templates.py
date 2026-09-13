def auth_code_template(code: str) -> dict:
    return {
        "subject": "Your login code",
        "text": f"Your code is {code}. It expires in 10 minutes.",
        "html": f"<p>Your login code is:</p><h2>{code}</h2><p>Expires in 10 minutes.</p>"
    }