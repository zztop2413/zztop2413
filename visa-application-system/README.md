# Visa Application Filing System

A fully automated web-based visa application filing system for Bangladeshi applicants applying to Schengen countries, China, Thailand, Malaysia, and Singapore.

## Features

### Core Functionality
- **Automated Document Processing**: OCR-powered extraction of applicant information from uploaded documents
- **Smart Form Filling**: Automatic population of visa application forms from extracted data
- **Document Validation**: Real-time checking for missing or invalid documents
- **Country-Specific Rules**: Compliance with each destination country's requirements
- **Human Agent Handoff**: Applications prepared for final submission by human agents

### Supported Countries
1. **Schengen Area** (26 countries including France, Germany, Italy, Spain, etc.)
2. **China**
3. **Thailand**
4. **Malaysia**
5. **Singapore**

### Key Features by Country
- **Schengen**: GDPR compliance, travel insurance verification, biometric requirements
- **China**: Invitation letter validation, specific photo specifications
- **Thailand**: Visa exemption rules, financial proof requirements
- **Malaysia**: eVISA integration support, digital photo specs
- **Singapore**: SafeTravel framework compliance

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (relational data), MongoDB (document storage)
- **Cache**: Redis
- **OCR**: Tesseract, AWS Textract, or Google Vision API
- **Authentication**: JWT tokens with bcrypt password hashing

### Frontend (Planned)
- **Framework**: React 18+ with TypeScript
- **UI Library**: Material-UI or Ant Design
- **File Upload**: react-dropzone
- **State Management**: Redux Toolkit

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Task Queue**: Celery with Redis
- **Cloud Storage**: AWS S3 / Azure Blob / Local storage

## Project Structure

```
visa-application-system/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── models/                 # SQLAlchemy database models
│   │   └── __init__.py
│   ├── services/               # Business logic services
│   │   ├── auth.py            # Authentication service
│   │   ├── document_processor.py  # OCR & data extraction
│   │   └── country_rules.py   # Country-specific requirements
│   ├── schemas.py             # Pydantic validation schemas
│   └── database/              # Database configuration
│       └── session.py
├── config/
│   └── settings.py            # Application configuration
├── docs/
│   └── ARCHITECTURE.md        # Detailed architecture documentation
├── .env.example               # Environment variables template
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # Docker orchestration
└── README.md                  # This file
```

## Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Tesseract OCR (or AWS/GCP account for cloud OCR)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd visa-application-system
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Start required services (Docker)**
```bash
docker-compose up -d postgres redis mongodb
```

6. **Initialize database**
```bash
python -c "from backend.database.session import init_db; init_db()"
```

7. **Run the application**
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

8. **Access API documentation**
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/user/profile` - Get current user profile

### Countries
- `GET /api/countries` - List supported countries
- `GET /api/countries/{code}/requirements` - Get country requirements

### Applications
- `POST /api/applications` - Create new visa application
- `GET /api/applications` - List user's applications
- `GET /api/applications/{id}` - Get application details
- `GET /api/applications/{id}/validation` - Validate application completeness

### Documents
- `POST /api/applications/{id}/documents` - Upload document
- `GET /api/applications/{id}/documents` - List application documents

### Submission
- `POST /api/applications/{id}/submit-for-review` - Submit for agent review

## Document Requirements by Country

### Schengen Countries
- Passport (valid 6+ months)
- Photograph (35mm x 45mm, white background)
- Travel insurance (€30,000+ coverage)
- Flight itinerary
- Accommodation proof
- Financial proof (bank statements)
- Employment letter
- Bank statements (3-6 months)

### China
- Passport (valid 6+ months)
- Photograph (33mm x 48mm)
- Invitation letter
- Flight itinerary
- Hotel booking
- Financial proof
- Employment certificate

### Thailand
- Passport (valid 6+ months)
- Photograph (35mm x 45mm)
- Flight itinerary
- Accommodation proof
- Financial proof

### Malaysia
- Passport (valid 6+ months)
- Photograph (35mm x 50mm)
- Flight itinerary
- Accommodation proof
- Financial proof
- Return ticket

### Singapore
- Passport (valid 6+ months)
- Photograph (35mm x 45mm)
- Flight itinerary
- Accommodation proof
- Financial proof
- Local contact information

## Security & Compliance

### Data Protection
- **GDPR Compliance**: For Schengen applications
- **Bangladesh Data Protection Act**: User consent and data rights
- **Country-Specific Regulations**: PDPA for Thailand, Malaysia, Singapore

### Security Features
- End-to-end encryption for sensitive data
- JWT-based authentication with refresh tokens
- Role-based access control (RBAC)
- Complete audit logging
- Secure file storage with access controls

### Privacy
- Data minimization principles
- Purpose limitation
- Storage limitation policies
- Right to data deletion

## Workflow

1. **User Registration**: Applicant creates account with verified email
2. **Destination Selection**: Choose target country
3. **Document Upload**: Upload all required documents
4. **Automated Processing**: 
   - OCR extracts text from documents
   - NLP identifies key information
   - Cross-document consistency checks
5. **Gap Analysis**: System identifies missing documents
6. **Form Generation**: Auto-fills official visa application forms
7. **Human Agent Review**: Application queued for agent verification
8. **Final Submission**: Human agent submits to embassy/consulate

## Development

### Running Tests
```bash
pytest tests/ -v --cov=backend
```

### Code Formatting
```bash
black backend/ config/
flake8 backend/ config/
```

### Type Checking
```bash
mypy backend/
```

## Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Production Considerations
- Use production-grade database (PostgreSQL cluster)
- Configure proper SSL/TLS certificates
- Set up load balancing
- Implement monitoring (Prometheus + Grafana)
- Configure centralized logging (ELK stack)
- Set up backup strategies
- Implement rate limiting
- Configure proper CORS for production domains

## Legal Disclaimer

This system assists with visa application preparation but does not guarantee approval. All applications are subject to review and approval by respective embassies/consulates. Users are responsible for ensuring accuracy of information provided.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Email: support@visasystem.com

## Acknowledgments

- FastAPI team for the excellent framework
- Tesseract OCR community
- All embassy/consulate websites for requirement information
