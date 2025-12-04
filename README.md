# Persony Backend

[![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen)](https://github.com)
[![License](https://img.shields.io/badge/license-Apache-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.14%2B-blue)](https://www.python.org)

A production-ready Flask REST API with JWT authentication, Oracle Database integration, and modular architecture. Persony is a comprehensive personal management system featuring **user authentication**, **calendar management**, and **secure API endpoints**.

## 🚀 Quick Features

- ✅ **User Authentication** - Register, login, JWT tokens
- ✅ **Protected Endpoints** - Row-level security per user
- ✅ **Calendar CRUD** - Full create, read, update, delete operations
- ✅ **Oracle Database** - SQL injection safe, connection pooling
- ✅ **Modular Code** - Clean blueprints architecture
- ✅ **Docker Support** - Oracle Database in container
- ✅ **Production Ready** - Error handling, validation, security

## 📋 Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | Flask 3.1.x |
| Database | Oracle 21c XE |
| Auth | Flask-JWT-Extended |
| Driver | oracledb (thin) |
| Password | Werkzeug |
| Config | python-dotenv |

## 📁 Project Structure

```
persony/
├── app.py                  # Entry point
├── .env                    # Configuration
├── requirements.txt        # Dependencies
├── src/
│   ├── __init__.py        # App factory
│   ├── db.py              # DB connection pool
│   ├── common/            # Health check routes
│   ├── user/              # Auth (register, login)
│   └── calendar/          # Calendar CRUD
└── db/
    └── schema.sql         # Database DDL
```

## 🔧 Installation & Setup

### 1. Prerequisites

- Python 3.14+
- Docker Desktop (For Database)
- Git

### 2. Clone & Setup

```bash
git clone <repository>
cd persony

# Create virtualenv
python -m venv .venv

# Activate (Windows)
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup Oracle Database

```bash
# Start container
docker run -d --name persony-oracle -p 1521:1521 \
  -e ORACLE_RANDOM_PASSWORD=true gvenzl/oracle-xe:21-full

# Wait 2-3 minutes, then check
docker logs persony-oracle
```

### 4. Create Database User

```bash
docker exec -it persony-oracle bash
sqlplus sys/[PASSWORD_FROM_LOGS]@localhost:1521/XEPDB1 as sysdba

CREATE USER PERSONY_APP IDENTIFIED BY persony_pass
  DEFAULT TABLESPACE users
  TEMPORARY TABLESPACE temp
  QUOTA UNLIMITED ON users;
GRANT CONNECT, RESOURCE TO PERSONY_APP;

# Exit and login as PERSONY_APP
sqlplus PERSONY_APP/persony_pass@localhost:1521/XEPDB1
@db/schema.sql
EXIT;
```

### 5. Configure `.env`

```env
FLASK_APP=app
FLASK_ENV=development

ORACLE_USER=PERSONY_APP
ORACLE_PASSWORD=persony_pass
ORACLE_DSN=localhost:1521/XEPDB1
ORACLE_MIN_CONN=1
ORACLE_MAX_CONN=5

JWT_SECRET_KEY=your-secret-key-change-in-production
```

### 6. Run

```bash
flask run
# Server: http://127.0.0.1:5000
```

## 📚 API Endpoints

### Auth

```
POST   /api/users/register      # Create account
POST   /api/users/login         # Get JWT token
```

### Calendar (Protected - requires JWT)

```
GET    /api/calendar/events     # List events
POST   /api/calendar/events     # Create event
PUT    /api/calendar/events/<id> # Update event
DELETE /api/calendar/events/<id> # Delete event
```

### Utilities

```
GET    /api/health              # Health check
GET    /api/db-ping             # Database check
```

**See [DOCUMENTATION.md](DOCUMENTATION.md) for detailed API examples, request/response formats, and all parameters.**

## 🧪 Testing

Use **Thunder Client** (VS Code extension):

1. Register user: `POST /api/users/register`
2. Login: `POST /api/users/login` → copy `access_token`
3. Test calendar: `GET /api/calendar/events` + `Authorization: Bearer <token>`

## 🛡️ Security Highlights

- **SQL Injection Safe** - Parameterized queries with bind parameters
- **Password Hashing** - Werkzeug Scrypt hashing
- **JWT Auth** - Stateless token-based authentication
- **Row-Level Security** - Users only see own data
- **Input Validation** - All inputs validated before processing

## 🚀 Deploy to Production

### Render.com (Recommended)

```
1. Push code to GitHub
2. Connect to Render.com
3. Create Web Service
4. Build: pip install -r requirements.txt
5. Start: gunicorn app:app
6. Add environment variables
7. Deploy!
```

### Railway.app

```
1. Connect GitHub repo
2. Add environment variables
3. Auto-deploys on push
```

**Production Setup**: [See DOCUMENTATION.md - Deployment section](DOCUMENTATION.md#deployment)

## 📖 Documentation

Complete guides available:

- 🔧 **[DOCUMENTATION.md](DOCUMENTATION.md)** - Full technical documentation
  - Quick Start
  - Complete API Reference with examples
  - Database Schema
  - Security Deep-Dive
  - Deployment Guides
  - Development Guide
  - Troubleshooting

- 📋 **[README.md](README.md)** - You're reading this!

## 🤔 FAQ

**Q: Is it production-ready?**  
A: Yes! Includes auth, security, error handling, modular architecture, and deployment guides.

**Q: Can I use PostgreSQL instead of Oracle?**  
A: Not directly, but `src/db.py` can be adapted. Oracle was specifically chosen for this project.

**Q: How do I add new features?**  
A: Create new module in `src/[feature]/`, define routes with Blueprint, register in `src/__init__.py`. [See Development Guide](DOCUMENTATION.md#development-guide)

**Q: What if I have deployment issues?**  
A: Check [Troubleshooting section](DOCUMENTATION.md#troubleshooting) in DOCUMENTATION.md

## 🐛 Issues & Support

- Check [Troubleshooting](DOCUMENTATION.md#troubleshooting) section
- Verify `.env` configuration
- Check Flask logs for stack traces
- Verify Oracle container is running: `docker ps`

## 📝 License

MIT License - Feel free to use commercially or personally.

## 🎯 Next Steps

1. 🚧 Backend still progress (you are here)
2. 🔄 Deploy to cloud (Render/Railway)
3. ⏭️ Build frontend (React/Vue)
4. 📱 Mobile app (React Native/Flutter)

---

**Checkpoint 1: Complete** ✅  
Backend fully functional with user auth + calendar CRUD + Oracle DB

**Version**: 0.1.0  
**Last Updated**: December 5, 2025  
**Status**: Production Ready 🚀

### Get Started

```bash
# Fresh install takes ~10 minutes
git clone <repo> && cd persony
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# ... setup Oracle (see Installation section)
flask run
```

**Built with tears💧**
