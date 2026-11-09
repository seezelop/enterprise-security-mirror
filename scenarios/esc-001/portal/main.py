import hashlib
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel


app = FastAPI(
    title="ESM Enterprise Portal",
    version="0.1.0"
)

bearer = HTTPBearer()


# ============================================================
# DEMO USERS
# ============================================================

# Usuarios y contraseñas exclusivamente ficticios.
# Implementación simplificada para laboratorio, no producción.

DEMO_USERS = {
    "cliente1": ("Cliente123!", "cliente", 1),
    "cliente2": ("Cliente456!", "cliente", 2),
    "empleado1": ("Empleado123!", "empleado", None),
    "admin1": ("Admin123!", "administrador", None),
}


# ============================================================
# CUSTOMER DATA
# ============================================================

CUSTOMERS = {
    1: {
        "id": 1,
        "name": "Empresa Demo Norte",
        "plan": "Corporativo"
    },
    2: {
        "id": 2,
        "name": "Empresa Demo Sur",
        "plan": "PyME"
    },
}


# ============================================================
# SESSIONS AND AUDIT
# ============================================================

SESSIONS = {}
AUDIT_LOG = []

LOG_FILE = Path(__file__).parent / "logs" / "events.jsonl"


def audit(event, username, result, **details):
    """Registra eventos de seguridad en memoria y formato JSONL."""

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "username": username,
        "result": result,
        **details,
    }

    AUDIT_LOG.append(record)

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")

    print(json.dumps(record), flush=True)


# ============================================================
# AUTHENTICATION
# ============================================================

class LoginRequest(BaseModel):
    username: str
    password: str


def current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
):
    username = SESSIONS.get(credentials.credentials)

    if username is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    return username


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ESM Enterprise Portal"
    }


@app.post("/login")
def login(data: LoginRequest):

    user = DEMO_USERS.get(data.username)

    valid = (
        user is not None
        and secrets.compare_digest(
            hashlib.sha256(data.password.encode()).digest(),
            hashlib.sha256(user[0].encode()).digest(),
        )
    )

    if not valid:
        audit(
            "login",
            data.username,
            "failure"
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = secrets.token_urlsafe(32)

    SESSIONS[token] = data.username

    audit(
        "login",
        data.username,
        "success"
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ============================================================
# CUSTOMER ACCESS CONTROL
# ============================================================

@app.get("/customers/{customer_id}")
def customer_details(
    customer_id: int,
    username: str = Depends(current_user),
):

    user = DEMO_USERS[username]

    role = user[1]
    assigned_customer = user[2]

    # --------------------------------------------------------
    # SECURITY CONTROL: OBJECT-LEVEL AUTHORIZATION
    # Previene el acceso de un cliente a recursos de otro.
    # --------------------------------------------------------

    if role == "cliente" and assigned_customer != customer_id:

        audit(
            "customer_access",
            username,
            "denied",
            customer_id=customer_id,
            role=role,
            assigned_customer=assigned_customer,
        )

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    customer = CUSTOMERS.get(customer_id)

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    # Registrar acceso autorizado.
    audit(
        "customer_access",
        username,
        "allowed",
        customer_id=customer_id,
        role=role,
        assigned_customer=assigned_customer,
    )

    return customer


# ============================================================
# AUDIT ENDPOINT
# ============================================================

@app.get("/audit")
def get_audit(
    username: str = Depends(current_user),
):

    if DEMO_USERS[username][1] != "administrador":

        audit(
            "audit_access",
            username,
            "denied"
        )

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    audit(
        "audit_access",
        username,
        "allowed"
    )

    return AUDIT_LOG
