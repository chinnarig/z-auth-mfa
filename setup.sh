#!/bin/bash

# Voice Agent Platform - Setup Script
# This script helps you set up the project quickly

set -e

echo "========================================="
echo "Voice Agent Platform - Setup Script"
echo "========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Create .env file for backend if it doesn't exist
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating backend .env file..."
    cp backend/.env.example backend/.env
    
    # Generate a random secret key
    SECRET_KEY=$(openssl rand -hex 32)
    
    # Update SECRET_KEY in .env
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-super-secret-key-min-32-chars-change-this-in-production/$SECRET_KEY/" backend/.env
    else
        # Linux
        sed -i "s/your-super-secret-key-min-32-chars-change-this-in-production/$SECRET_KEY/" backend/.env
    fi
    
    echo "✅ Backend .env file created with generated SECRET_KEY"
else
    echo "✅ Backend .env file already exists"
fi

# Create .env.local file for frontend if it doesn't exist
if [ ! -f "frontend/.env.local" ]; then
    echo "📝 Creating frontend .env.local file..."
    cp frontend/.env.local.example frontend/.env.local
    echo "✅ Frontend .env.local file created"
else
    echo "✅ Frontend .env.local file already exists"
fi

echo ""
echo "========================================="
echo "Starting Services with Docker Compose"
echo "========================================="
echo ""

# Build and start services
echo "🚀 Building and starting services..."
docker-compose up -d --build

echo ""
echo "⏳ Waiting for database to be ready..."
sleep 10

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "📍 Services are running at:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Documentation: http://localhost:8000/docs"
echo "   - Database: localhost:5432"
echo ""
echo "🔑 Test Credentials (Company: TechCorp):"
echo "   Email: admin@techcorp.com"
echo "   Password: SecurePass123!"
echo ""
echo "📚 View logs with:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop services with:"
echo "   docker-compose down"
echo ""
echo "🗑️  Remove all data with:"
echo "   docker-compose down -v"
echo ""
