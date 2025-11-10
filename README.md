# Voice Agent Platform - Secure Multi-Tenant Authentication with MFA

A production-ready authentication system with Multi-Factor Authentication (MFA) for a multi-tenant voice agent platform.

## Features

- ✅ Multi-tenant architecture with company isolation
- ✅ Email/Password authentication
- ✅ Time-based One-Time Password (TOTP) MFA
- ✅ JWT-based session management
- ✅ Row-Level Security in PostgreSQL
- ✅ Audit logging
- ✅ Password reset functionality
- ✅ Role-based access control (RBAC)

## Tech Stack

- **Backend**: Python FastAPI
- **Frontend**: Next.js 14 (App Router)
- **Database**: PostgreSQL with Row-Level Security
- **Authentication**: JWT + TOTP (pyotp)

## Project Structure

```
voice-agent-auth/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── auth.py
│   │   ├── dependencies.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── users.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── mfa.py
│   │       └── email.py
│   ├── alembic/
│   │   └── versions/
│   ├── tests/
│   ├── requirements.txt
│   ├── .env.example
│   └── alembic.ini
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   ├── setup-mfa/
│   │   │   └── dashboard/
│   │   ├── components/
│   │   ├── lib/
│   │   └── types/
│   ├── package.json
│   └── .env.local.example
├── database/
│   ├── init.sql
│   └── test_data.sql
├── docker-compose.yml
└── README.md
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Option 1: Using Docker (Recommended)

1. Clone the repository
2. Copy environment files:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
```

3. Start all services:
```bash
docker-compose up -d
```

4. Run database migrations:
```bash
docker-compose exec backend alembic upgrade head
```

5. Load test data:
```bash
docker-compose exec db psql -U postgres -d voice_agent_db -f /docker-entrypoint-initdb.d/test_data.sql
```

6. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Local Development

#### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup PostgreSQL and update .env with your database URL
# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

### Backend (.env)

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/voice_agent_db
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@yourcompany.com
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Test Credentials

After loading test data:

### Company 1: TechCorp
- Admin: admin@techcorp.com / SecurePass123!
- Manager: manager@techcorp.com / SecurePass123!
- User: user@techcorp.com / SecurePass123!

### Company 2: StartupXYZ
- Admin: admin@startupxyz.com / SecurePass123!

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new company and user
- `POST /api/auth/login` - Login with email/password
- `POST /api/auth/verify-mfa` - Verify MFA code
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout user

### MFA Management
- `POST /api/auth/mfa/setup` - Generate MFA secret and QR code
- `POST /api/auth/mfa/enable` - Enable MFA with verification
- `POST /api/auth/mfa/disable` - Disable MFA
- `GET /api/auth/mfa/backup-codes` - Generate backup codes

### User Management
- `GET /api/users/me` - Get current user profile
- `PUT /api/users/me` - Update user profile
- `GET /api/users` - List users in company (admin only)

## MFA Setup Flow

1. User logs in with email/password
2. System generates JWT token with `mfa_required: true`
3. User navigates to MFA setup page
4. Backend generates TOTP secret and QR code
5. User scans QR code with authenticator app (Google Authenticator, Authy, etc.)
6. User enters 6-digit code to verify
7. System enables MFA and stores encrypted secret
8. User can generate backup codes

## Security Features

### Multi-Tenancy
- Company-level data isolation using Row-Level Security
- All queries automatically filtered by company_id
- No cross-company data leakage

### Authentication
- Bcrypt password hashing with salt
- JWT tokens with short expiry (30 minutes)
- Refresh tokens with longer expiry (7 days)
- TOTP-based MFA (RFC 6238)

### Authorization
- Role-based access control (Admin, Manager, User)
- Company-scoped permissions
- Endpoint-level permission checks

### Audit Logging
- All authentication events logged
- User actions tracked with IP and timestamp
- Queryable audit trail per company

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Production Deployment

### Security Checklist
- [ ] Change all SECRET_KEY values
- [ ] Use strong database passwords
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable database backups
- [ ] Configure monitoring and alerts
- [ ] Set up log aggregation
- [ ] Implement DDoS protection
- [ ] Regular security audits

### Recommended Infrastructure
- Backend: AWS ECS / Google Cloud Run / Railway
- Database: AWS RDS / Google Cloud SQL
- Frontend: Vercel / Netlify
- CDN: CloudFlare

## Troubleshooting

### Common Issues

1. **Database connection failed**
   - Check PostgreSQL is running
   - Verify DATABASE_URL in .env
   - Ensure database exists

2. **MFA QR code not showing**
   - Check backend logs for errors
   - Verify qrcode library is installed
   - Ensure PIL/Pillow is installed

3. **CORS errors**
   - Verify FRONTEND_URL in backend .env
   - Check CORS middleware configuration

## Support

For issues and questions, please open an issue on GitHub.

## License

MIT License
