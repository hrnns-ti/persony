# Persony Documentation

Detailed documentation for Persony Backend API, database schema, deployment guide, and development workflow.

## 📚 Table of Contents

1. [Quick Start](#quick-start)
2. [API Reference](#api-reference)
3. [Database Schema](#database-schema)
4. [Security](#security)
5. [Deployment](#deployment)
6. [Development Guide](#development-guide)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Installation

```bash
# Clone repository
git clone <repository_url>
cd persony

# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Setup Oracle Database

```bash
# Start Docker container
docker run -d \
  --name persony-oracle \
  -p 1521:1521 \
  -e ORACLE_RANDOM_PASSWORD=true \
  gvenzl/oracle-xe:21-full

# Wait 2-3 minutes, then check logs
docker logs persony-oracle
```

### Create Database User & Schema

```bash
# Enter container shell
docker exec -it persony-oracle bash

# Login as SYS (use password from logs)
sqlplus sys/[PASSWORD]@localhost:1521/XEPDB1 as sysdba

# Run SQL commands
CREATE USER PERSONY_APP IDENTIFIED BY persony_pass
  DEFAULT TABLESPACE users
  TEMPORARY TABLESPACE temp
  QUOTA UNLIMITED ON users;

GRANT CONNECT, RESOURCE TO PERSONY_APP;

EXIT;

# Login as PERSONY_APP
sqlplus PERSONY_APP/persony_pass@localhost:1521/XEPDB1

# Create tables (from db/schema.sql)
@db/schema.sql

EXIT;
```

### Configure Environment

Create `.env` file in project root:

```env
FLASK_APP=app
FLASK_ENV=development

# Oracle Database
ORACLE_USER=PERSONY_APP
ORACLE_PASSWORD=persony_pass
ORACLE_DSN=localhost:1521/XEPDB1
ORACLE_MIN_CONN=1
ORACLE_MAX_CONN=5

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
```

### Run Application

```bash
flask run
# or
python app.py
```

Server: `http://127.0.0.1:5000`

---

## API Reference

### Authentication Flow

```
1. User calls POST /api/users/register → get user ID
2. User calls POST /api/users/login → get JWT access_token
3. User includes "Authorization: Bearer <token>" in subsequent requests
4. Protected endpoints verify token and extract user_id
```

### Error Responses

All errors follow standard HTTP status codes:

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Missing/invalid token
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error response format:

```json
{
  "errors": {
    "field_name": "Error message"
  }
}
```

### User Endpoints

#### Register User

**Request**:
```
POST /api/users/register
Content-Type: application/json

{
  "email": "john@example.com",
  "name": "John Doe",
  "password": "mypassword123",
  "confirm_password": "mypassword123"
}
```

**Response (201)**:
```json
{
  "id": 1,
  "email": "john@example.com",
  "name": "John Doe",
  "created_at": "2025-12-05T10:30:00+00:00"
}
```

**Error Cases**:
- `400` - Missing email/password/confirm_password
- `400` - Passwords don't match
- `400` - Email already registered (ORA-00001)

#### Login User

**Request**:
```
POST /api/users/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "mypassword123"
}
```

**Response (200)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NDg4MDkwNSwianRpIjoiZGQzOTI2NzAtMjkwNC00MGY3LWE3YTEtMTY3MGVlMTJhY2Y2IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3NjQ4ODA5MDUsImNzcmYiOiI3ZWFjMmIyYi1kMWU5LTQyZDMtYmI1Mi05YTc1MWYzYzAxMGIiLCJleHAiOjE3NjQ4ODE4MDV9.YwuOSiKuMKN2epOVb6XAwIZc-2lPPXh52XLkXllGM1s",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "name": "John Doe"
  }
}
```

**Error Cases**:
- `400` - Missing email/password
- `401` - Invalid credentials (email not found or password wrong)

### Calendar Endpoints (Protected)

**All require**: `Authorization: Bearer <access_token>` header

#### Get All Events

**Request**:
```
GET /api/calendar/events
Authorization: Bearer <token>
```

**Response (200)**:
```json
[
  {
    "id": 1,
    "title": "Team Meeting",
    "description": "Weekly sync",
    "start_at": "2025-12-06T10:00:00Z",
    "end_at": "2025-12-06T11:00:00Z",
    "is_all_day": false,
    "location": "Conference Room A",
    "color": "#FF5733"
  }
]
```

#### Create Event

**Request**:
```
POST /api/calendar/events
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Team Meeting",
  "description": "Weekly sync",
  "start_at": "2025-12-06T10:00:00Z",
  "end_at": "2025-12-06T11:00:00Z",
  "is_all_day": false,
  "location": "Conference Room A",
  "color": "#FF5733"
}
```

**Response (201)**:
```json
{
  "id": 1,
  "message": "Event created successfully"
}
```

**Validation**:
- `title` - required, string
- `start_at`, `end_at` - required, ISO 8601 format (e.g., "2025-12-06T10:00:00Z")
- `description`, `location`, `color` - optional, string
- `is_all_day` - optional, boolean

#### Update Event

**Request**:
```
PUT /api/calendar/events/<id>
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated Title",
  "description": "Updated description",
  "start_at": "2025-12-06T14:00:00Z",
  "end_at": "2025-12-06T15:00:00Z",
  "is_all_day": false,
  "location": "New Location",
  "color": "#00FF00"
}
```

**Response (200)**:
```json
{
  "id": 1,
  "message": "Event updated successfully"
}
```

#### Delete Event

**Request**:
```
DELETE /api/calendar/events/<id>
Authorization: Bearer <token>
```

**Response (200)**:
```json
{
  "message": "Event deleted successfully"
}
```

### Common Endpoints

#### Health Check

**Request**:
```
GET /api/health
```

**Response (200)**:
```json
{
  "status": "OK 🚀"
}
```

#### Database Ping

**Request**:
```
GET /api/db-ping
```

**Response (200)**:
```json
{
  "database": "OK"
}
```

---

## Database Schema

### USERS Table

```sql
CREATE TABLE USERS (
  ID            NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  EMAIL         VARCHAR2(255) UNIQUE NOT NULL,
  PASSWORD_HASH VARCHAR2(255) NOT NULL,
  NAME          VARCHAR2(255),
  CREATED_AT    TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP
);

CREATE INDEX IDX_USERS_EMAIL ON USERS(EMAIL);
```

**Columns**:
- `ID` - Unique identifier (auto-generated)
- `EMAIL` - User email, must be unique
- `PASSWORD_HASH` - Scrypt hashed password (never store plain text)
- `NAME` - User's display name
- `CREATED_AT` - Account creation timestamp

### CALENDAR_EVENTS Table

```sql
CREATE TABLE CALENDAR_EVENTS (
  ID          NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  USER_ID     NUMBER NOT NULL,
  TITLE       VARCHAR2(255) NOT NULL,
  DESCRIPTION VARCHAR2(2000),
  START_AT    TIMESTAMP WITH TIME ZONE NOT NULL,
  END_AT      TIMESTAMP WITH TIME ZONE NOT NULL,
  IS_ALL_DAY  NUMBER(1) DEFAULT 0,
  LOCATION    VARCHAR2(255),
  COLOR       VARCHAR2(32),
  CREATED_AT  TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP,
  UPDATED_AT  TIMESTAMP WITH TIME ZONE
);

ALTER TABLE CALENDAR_EVENTS
  ADD CONSTRAINT FK_CAL_EVENTS_USER
  FOREIGN KEY (USER_ID) REFERENCES USERS(ID);

CREATE INDEX IDX_CAL_EVENTS_USER_ID ON CALENDAR_EVENTS(USER_ID);
CREATE INDEX IDX_CAL_EVENTS_START_AT ON CALENDAR_EVENTS(START_AT);
```

**Columns**:
- `ID` - Unique identifier
- `USER_ID` - Reference to USERS.ID (owner)
- `TITLE` - Event title
- `DESCRIPTION` - Event details
- `START_AT`, `END_AT` - Event time range
- `IS_ALL_DAY` - Boolean flag (0/1)
- `LOCATION` - Event location
- `COLOR` - Hex color code for UI display
- `CREATED_AT`, `UPDATED_AT` - Timestamps

---

## Security

### SQL Injection Prevention

Always use **parameterized queries** with bind parameters:

```python
# ✅ SECURE - Bind parameters prevent SQL injection
cursor.execute(
    "SELECT * FROM USERS WHERE EMAIL = :email",
    {"email": user_input}
)

# ❌ VULNERABLE - String concatenation allows injection
cursor.execute(f"SELECT * FROM USERS WHERE EMAIL = '{user_input}'")
```

The `oracledb` driver automatically:
1. Separates SQL structure from data
2. Pre-compiles queries
3. Escapes special characters in parameter values
4. Prevents injection attacks

### Password Security

- Passwords are hashed using **Werkzeug Scrypt** (PBKDF2 with Scrypt salt)
- Never stored plain text
- Hash comparison is constant-time to prevent timing attacks

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Store
password_hash = generate_password_hash(password)

# Verify
if check_password_hash(password_hash, user_input):
    # Password correct
```

### JWT Token Security

- **Token Format**: Header.Payload.Signature
- **Secret Key**: Change `JWT_SECRET_KEY` in production
- **Expiration**: Tokens expire after 1 hour (configurable)
- **Subject (`sub`)**: Contains user ID for identity verification

```python
# Create token (login endpoint)
access_token = create_access_token(identity=str(user_id))

# Verify token (protected endpoint)
@jwt_required()
def protected():
    user_id = get_jwt_identity()  # Extract from token
```

### Row-Level Security

Users can only access their own data:

```python
cursor.execute(
    "SELECT * FROM CALENDAR_EVENTS WHERE USER_ID = :user_id",
    {"user_id": authenticated_user_id}
)
```

Even if an attacker modifies `user_id` parameter, they can only see their own events.

### HTTPS in Production

- Always use HTTPS (TLS/SSL) in production
- Set secure JWT cookie flags
- Implement CORS carefully (whitelist frontend domains)

```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {"origins": ["https://yourdomain.com"]}
})
```

---

## Deployment

### Option 1: Render.com (Free Tier)

1. **Push to GitHub**
   ```bash
   git remote add origin <your-repo>
   git push -u origin main
   ```

2. **Connect to Render**
   - Go to render.com
   - Connect GitHub account
   - Create "Web Service"
   - Select repository

3. **Configure Build**
   ```
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app
   ```

4. **Add Environment Variables**
   - `ORACLE_USER=PERSONY_APP`
   - `ORACLE_PASSWORD=<strong_password>`
   - `ORACLE_DSN=<cloud_oracle_dsn>`
   - `JWT_SECRET_KEY=<strong_secret>`

5. **Deploy**
   - Click Deploy
   - Wait 2-3 minutes

### Option 2: Railway.app (Free Tier)

1. **Connect GitHub**
   - Go to railway.app
   - Connect GitHub

2. **Create Project**
   - New Project → GitHub Repo

3. **Add Environment Variables**
   - Set same as Render above

4. **Auto-Deploy**
   - Railway automatically detects Flask app
   - Builds and deploys

### Oracle Cloud Database Setup

For production, use **Oracle Always Free Autonomous Database**:

1. Create Oracle Cloud account (always free tier available)
2. Create Autonomous Database instance
3. Download wallet (.zip file)
4. Extract connection details
5. Update `.env` with cloud DSN

```env
ORACLE_DSN=<cloud_instance>.oraclecloud.com:1522/<service_name>
```

### Production Checklist

- [ ] Change `JWT_SECRET_KEY` to strong random key
- [ ] Use strong `ORACLE_PASSWORD` (20+ chars, mixed)
- [ ] Enable HTTPS only (enforce in reverse proxy)
- [ ] Setup error logging (e.g., Sentry)
- [ ] Enable database backups
- [ ] Setup monitoring/alerts
- [ ] Use production WSGI server (Gunicorn)
- [ ] Implement rate limiting
- [ ] Regular security audits
- [ ] Keep dependencies updated

---

## Development Guide

### Project Structure

```
persony/
├── app.py                    # Entry point
├── .env                      # Local config
├── requirements.txt          # Dependencies
├── src/
│   ├── __init__.py          # Application factory
│   ├── db.py                # Oracle connection pool
│   ├── common/
│   │   ├── __init__.py
│   │   └── routes.py        # Health, db-ping
│   ├── user/
│   │   ├── __init__.py
│   │   └── routes.py        # Register, login
│   └── calendar/
│       ├── __init__.py
│       └── routes.py        # CRUD events
└── db/
    └── schema.sql           # DDL scripts
```

### Adding New Module

1. **Create folder** `src/[module_name]/`
2. **Create files**:
   - `__init__.py` → `from .routes import bp`
   - `routes.py` → `bp = Blueprint(...)`

3. **Define routes**:
   ```python
   from flask import Blueprint

   bp = Blueprint("mymodule", __name__, url_prefix="/api/mymodule")

   @bp.get("/items")
   def get_items():
       # Your logic
       return jsonify([])
   ```

4. **Register in `src/__init__.py`**:
   ```python
   from src.mymodule import bp as mymodule_bp
   app.register_blueprint(mymodule_bp)
   ```

5. **Test with Thunder Client**

### Database Query Pattern

```python
with get_connection() as conn:
    with conn.cursor() as cur:
        # Execute query
        cur.execute(
            "SELECT * FROM USERS WHERE ID = :id",
            {"id": user_id}
        )
        
        # Fetch result
        row = cur.fetchone()
        
        # Or fetch all
        rows = cur.fetchall()
    
    # Commit changes (if INSERT/UPDATE/DELETE)
    conn.commit()
```

### Protected Endpoint Pattern

```python
from flask_jwt_extended import jwt_required, get_jwt_identity

@bp.get("/my-items")
@jwt_required()
def get_my_items():
    user_id = int(get_jwt_identity())
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM MY_TABLE WHERE USER_ID = :user_id",
                {"user_id": user_id}
            )
            rows = cur.fetchall()
    
    return jsonify(rows)
```

---

## Troubleshooting

### Oracle Connection Issues

**Error**: `DPY-4001: no credentials specified`

**Solution**:
- Check `.env` has `ORACLE_USER`, `ORACLE_PASSWORD`, `ORACLE_DSN`
- Restart Flask after changing `.env`
- Verify `get_pool()` is called with correct parameters

**Error**: `ORA-12514: TNS:listener was not given the SERVICE_NAME`

**Solution**:
- Verify service name in `ORACLE_DSN` is correct
- Check Oracle container is running: `docker ps`
- Check container logs: `docker logs persony-oracle`

### JWT Issues

**Error**: `Missing Authorization Header`

**Solution**:
- Add header: `Authorization: Bearer <token>`
- Use correct token format (from login response)

**Error**: `Invalid token`

**Solution**:
- Token might be expired (1 hour default)
- Login again to get fresh token
- Check `JWT_SECRET_KEY` matches between app instances

### Port Conflicts

**Error**: `Address already in use` (port 1521)

**Solution**:
```bash
# Check what's using port
lsof -i :1521

# Or use different port in Docker
docker run -p 1522:1521 ...
```

### Slow Queries

**Optimization**:
- Add indexes on frequently queried columns
- Use `EXPLAIN PLAN` to analyze queries
- Monitor connection pool utilization

```sql
-- Add index
CREATE INDEX idx_events_user ON CALENDAR_EVENTS(USER_ID);

-- Check query plan
EXPLAIN PLAN FOR SELECT * FROM USERS WHERE EMAIL = 'test@example.com';
SELECT PLAN_TABLE_OUTPUT FROM TABLE(DBMS_XPLAN.DISPLAY());
```

---

**Last Updated**: December 5, 2025  
**Version**: 0.1.0
