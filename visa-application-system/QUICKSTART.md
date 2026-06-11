"""
Quick Start Guide - Visa Application Filing System

This guide will help you get the system running in under 10 minutes.
"""

# PREREQUISITES

## Required Software
- Python 3.11 or higher
- Docker and Docker Compose (recommended) OR
- PostgreSQL 14+, Redis 7+, MongoDB 7+

## Optional (for development)
- Tesseract OCR (if not using Docker)
- Git

---

# OPTION 1: DOCKER COMPOSE (RECOMMENDED)

## Step 1: Clone and Setup
```bash
cd visa-application-system
cp .env.example .env
```

## Step 2: Edit Environment Variables
Edit `.env` file and set:
```bash
SECRET_KEY=your-random-secret-key-here
DEBUG=true
```

## Step 3: Start All Services
```bash
docker-compose up -d
```

## Step 4: Verify Services
```bash
docker-compose ps
```

All services should show "healthy" status.

## Step 5: Access API
Open browser to: http://localhost:8000/api/docs

---

# OPTION 2: MANUAL INSTALLATION

## Step 1: Install System Dependencies

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y \
    python3.11 python3.11-venv python3-pip \
    postgresql postgresql-contrib \
    redis-server \
    mongodb \
    tesseract-ocr \
    poppler-utils \
    libpq-dev
```

### macOS
```bash
brew install python@3.11 postgresql redis mongodb-community tesseract poppler
```

## Step 2: Start Database Services

### PostgreSQL
```bash
# Ubuntu/Debian
sudo systemctl start postgresql
sudo -u postgres psql -c "CREATE USER postgres WITH PASSWORD 'postgres';"
sudo -u postgres psql -c "CREATE DATABASE visa_db OWNER postgres;"

# macOS
brew services start postgresql
```

### Redis
```bash
# Ubuntu/Debian
sudo systemctl start redis

# macOS
brew services start redis
```

### MongoDB
```bash
# Ubuntu/Debian
sudo systemctl start mongod

# macOS
brew services start mongodb-community
```

## Step 3: Setup Python Environment
```bash
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 4: Configure Environment
```bash
cp .env.example .env
# Edit .env with your database credentials
```

## Step 5: Initialize Database
```bash
python -c "from backend.database.session import init_db; init_db()"
```

## Step 6: Run Application
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

---

# FIRST TIME SETUP

## Create Test User

Use the API to create a test user:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123",
    "full_name": "Test User",
    "phone_number": "+8801712345678",
    "nationality": "Bangladeshi"
  }'
```

## Login and Get Token

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

Save the `access_token` from the response.

## Create Visa Application

```bash
curl -X POST http://localhost:8000/api/applications \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "destination_country": "SCH",
    "visa_type": "tourist"
  }'
```

## Check Country Requirements

```bash
curl http://localhost:8000/api/countries/SCH/requirements
```

---

# TESTING THE SYSTEM

## Test Document Upload Flow

1. Create an application (as shown above)
2. Note the application_id from response
3. Upload documents one by one:

```bash
curl -X POST http://localhost:8000/api/applications/{application_id}/documents \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "document_type": "passport",
    "file_path": "/path/to/passport.jpg",
    "file_name": "passport.jpg"
  }'
```

4. Check validation status:

```bash
curl http://localhost:8000/api/applications/{application_id}/validation \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

The system will return a list of missing documents.

---

# COMMON ISSUES & SOLUTIONS

## Issue: Database Connection Error
**Solution**: Ensure PostgreSQL is running and credentials in `.env` are correct

## Issue: OCR Not Working
**Solution**: 
- Docker: Tesseract is pre-installed
- Manual: Install tesseract-ocr and pytesseract

## Issue: Port Already in Use
**Solution**: Change port in docker-compose.yml or uvicorn command

## Issue: Module Import Errors
**Solution**: 
```bash
pip install -r requirements.txt
# Ensure you're in the project root directory
```

---

# NEXT STEPS

1. **Review Architecture**: See `docs/ARCHITECTURE.md`
2. **Customize Country Rules**: Edit `backend/services/country_rules.py`
3. **Configure OCR**: Choose between Tesseract, AWS Textract, or Google Vision
4. **Setup Email**: Configure SMTP settings in `.env`
5. **Build Frontend**: React frontend code goes in `/frontend`

---

# USEFUL COMMANDS

## View Logs
```bash
docker-compose logs -f backend
docker-compose logs -f celery_worker
```

## Restart Services
```bash
docker-compose restart
```

## Stop All Services
```bash
docker-compose down
```

## Clean Everything
```bash
docker-compose down -v  # Removes volumes too
```

## Run Tests
```bash
pytest tests/ -v
```

## Access Database
```bash
# PostgreSQL
docker-compose exec postgres psql -U postgres -d visa_db

# MongoDB
docker-compose exec mongodb mongosh -u mongo -p mongo
```

---

# SUPPORT

For issues:
1. Check logs: `docker-compose logs`
2. Review documentation in `/docs`
3. Check environment variables in `.env`
4. Ensure all required services are running
