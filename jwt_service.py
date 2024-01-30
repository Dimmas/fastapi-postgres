from datetime import datetime, timezone
from typing import Any
from jwt import encode, decode

JWT_SECRET = 'super_pass'


def sign_token(payload: Any) -> str:
    return encode(
        {"iat": datetime.now(tz=timezone.utc), **payload},
        JWT_SECRET,
        algorithm="HS256"
    )


def decode_token(token: str) -> Any:
    try:
        return decode(token, JWT_SECRET, algorithms=["HS256"])
    except:
        return False
