# UNABZen Backend (MVP)

Backend base para el MVP de **UNABZen**, una aplicación de autocuidado emocional para estudiantes.

## Qué incluye

- Modo invitado con sesión JWT.
- Endpoints para check-in emocional.
- Biblioteca de ejercicios.
- Registro de diario emocional.
- Registro de sesiones Pomodoro.
- Evaluación básica de crisis por palabras clave.
- Endpoint de privacidad para borrar datos del usuario.
- Estructura preparada para OAuth/OIDC y sincronización futura.

## Stack

- FastAPI
- SQLAlchemy 2.x (async)
- SQLite para el MVP
- Pydantic v2
- JWT para sesión de API

## Estructura

```text
app/
  core/
    config.py
    database.py
    security.py
  models/
    base.py
    entities.py
  schemas/
    auth.py
    checkin.py
    content.py
    crisis.py
    journal.py
    pomodoro.py
    privacy.py
  services/
    crisis.py
    recommendation.py
  routers/
    auth.py
    checkins.py
    content.py
    crisis.py
    journal.py
    pomodoro.py
    privacy.py
  main.py
```

## Instalación

<<<<<<< HEAD
### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
=======
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate    # Windows
>>>>>>> 4a05cb32710a5f851774039b92b13f766ec9b48b
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Documentación

Con el servidor arriba:

- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Flujo recomendado del MVP

1. El usuario entra como invitado.
2. Hace check-in rápido.
3. El backend recomienda ejercicios cortos según el estado.
4. Puede usar diario y Pomodoro.
5. Si escribe frases de riesgo, se activa respuesta de crisis.
6. Si desea sincronizar en el futuro, se conecta OAuth/OIDC real.

## OAuth/OIDC

El endpoint `/auth/oauth/verify` queda como **stub técnico**. La verificación real del `id_token` debe hacerse por proveedor (Google/Apple/Microsoft) en una siguiente iteración.

<<<<<<< HEAD
Para pruebas locales usa `provider = "dev"` y envía también `email`.

=======
>>>>>>> 4a05cb32710a5f851774039b92b13f766ec9b48b
## Próximos pasos sugeridos

- Cambiar SQLite por PostgreSQL.
- Agregar Alembic con migraciones reales.
- Implementar refresh tokens rotativos.
- Integrar verificación OIDC real.
- Añadir SyncQueue y endpoints `/sync/pull` y `/sync/push`.
