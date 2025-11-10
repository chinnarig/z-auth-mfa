# 🚀 Quick Start Guide

## Prerequisites
- Docker & Docker Compose
- 5 minutes of your time!

## Installation (3 Easy Steps)

### Step 1: Extract the Project
```bash
# If you downloaded the tar.gz file
tar -xzf voice-agent-auth.tar.gz
cd voice-agent-auth

# Or if you have the folder directly
cd voice-agent-auth
```

### Step 2: Run the Setup Script
```bash
chmod +x setup.sh
./setup.sh
```

That's it! The script will:
- ✅ Check Docker installation
- ✅ Create environment files
- ✅ Generate secure secret keys
- ✅ Start all services (Database, Backend, Frontend)
- ✅ Load test data

### Step 3: Access the Application

**Frontend:** http://localhost:3000
**Backend API:** http://localhost:8000
**API Docs:** http://localhost:8000/docs

## Test Login Credentials

### Company: TechCorp
- **Admin User**
  - Email: `admin@techcorp.com`
  - Password: `SecurePass123!`
  - Role: Admin

- **Manager User**
  - Email: `manager@techcorp.com`
  - Password: `SecurePass123!`
  - Role: Manager

- **Regular User**
  - Email: `user@techcorp.com`
  - Password: `SecurePass123!`
  - Role: User

### Company: StartupXYZ
- **Admin User**
  - Email: `admin@startupxyz.com`
  - Password: `SecurePass123!`
  - Role: Admin

## Testing MFA Setup

1. Login with any test account
2. Go to Dashboard
3. Click "Enable MFA"
4. Scan QR code with Google Authenticator or Authy
5. Enter the 6-digit code
6. Save your backup codes
7. Logout and login again to test MFA

## Manual Setup (Without Docker)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure .env file
cp .env.example .env
# Edit .env with your database credentials

# Setup database (requires PostgreSQL running)
psql -U postgres -d voice_agent_db -f ../database/init.sql
psql -U postgres -d voice_agent_db -f ../database/test_data.sql

# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install

# Configure .env.local
cp .env.local.example .env.local

# Start development server
npm run dev
```

## Common Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

### Remove All Data (Fresh Start)
```bash
docker-compose down -v
./setup.sh
```

### Access Database
```bash
docker-compose exec db psql -U postgres -d voice_agent_db
```

## Testing the API

### Using the Interactive Docs
Visit http://localhost:8000/docs for Swagger UI

### Using cURL

**Register a new user:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@mycompany.com",
    "password": "SecurePass123!",
    "full_name": "New User",
    "company_name": "My Company",
    "company_domain": "mycompany.com"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@techcorp.com",
    "password": "SecurePass123!"
  }'
```

## Troubleshooting

### Port Already in Use
If ports 3000, 8000, or 5432 are already in use:

1. Stop the conflicting services
2. Or modify `docker-compose.yml` to use different ports

### Database Connection Error
```bash
# Wait for database to be ready
docker-compose logs db

# Manually restart backend after database is ready
docker-compose restart backend
```

### Frontend Can't Connect to Backend
- Check that backend is running: http://localhost:8000/health
- Verify CORS settings in `backend/app/main.py`
- Check `frontend/.env.local` has correct API URL

### Permission Denied on setup.sh
```bash
chmod +x setup.sh
```

## Features to Explore

1. **Multi-Factor Authentication**
   - Enable MFA on your account
   - Test with Google Authenticator
   - Try backup codes

2. **Multi-Tenancy**
   - Register multiple companies
   - Notice data isolation between companies
   - Try cross-company access (should fail)

3. **Role-Based Access**
   - Login as different roles (admin, manager, user)
   - Test permission differences

4. **Audit Logging**
   - All actions are logged
   - Check database: `SELECT * FROM audit_logs;`

## Next Steps

1. **Production Deployment**
   - See `README.md` for production checklist
   - Change all secret keys
   - Set up proper database
   - Enable HTTPS

2. **Customization**
   - Add your own features
   - Modify UI/branding
   - Add more user roles
   - Integrate with your existing systems

3. **Security**
   - Enable rate limiting
   - Set up monitoring
   - Regular security audits
   - Implement DDoS protection

## Support

- 📖 Full documentation: `README.md`
- 🔐 Security details: `SECURITY_ARCHITECTURE.md`
- 📡 API reference: `API_DOCUMENTATION.md`
- 🐛 Issues: Check logs with `docker-compose logs -f`

## Success Indicators

✅ All services running: `docker-compose ps`
✅ Backend healthy: http://localhost:8000/health
✅ Frontend accessible: http://localhost:3000
✅ Can login with test credentials
✅ MFA setup works
✅ API docs accessible: http://localhost:8000/docs

**Congratulations! Your secure multi-tenant authentication system is ready!** 🎉
