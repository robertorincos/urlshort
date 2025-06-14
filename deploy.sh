#!/bin/bash

# URL Shortener Deployment Script for Ubuntu Server
# This script automates the deployment process

set -e  # Exit on any error

echo "🚀 Starting URL Shortener deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    echo "Run: curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    echo "Run: sudo curl -L \"https://github.com/docker/compose/releases/download/1.29.2/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose"
    echo "Then: sudo chmod +x /usr/local/bin/docker-compose"
    exit 1
fi

print_status "Docker and Docker Compose are installed ✅"

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from example..."
    cp env.example .env
    print_warning "Please edit .env file with your production settings before running docker-compose up"
    
    # Prompt for basic configuration
    read -p "Enter your domain or IP address (e.g., your-domain.com or 192.168.1.100): " HOST
    read -p "Will you use HTTPS? (y/n): " USE_HTTPS
    
    if [ "$USE_HTTPS" = "y" ] || [ "$USE_HTTPS" = "Y" ]; then
        PROTOCOL="https"
    else
        PROTOCOL="http"
    fi
    
    # Update .env file
    sed -i "s/APP_HOST=your-domain.com/APP_HOST=$HOST/" .env
    sed -i "s/APP_PROTOCOL=https/APP_PROTOCOL=$PROTOCOL/" .env
    
    print_status ".env file configured with HOST=$HOST and PROTOCOL=$PROTOCOL"
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Pull latest changes (if this is a git repo)
if [ -d ".git" ]; then
    print_status "Pulling latest changes from Git..."
    git pull origin main || print_warning "Could not pull from git (maybe not a git repo or no internet)"
fi

# Build and start services
print_status "Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    print_status "✅ Services are running successfully!"
    
    # Show service status
    print_status "Service status:"
    docker-compose ps
    
    # Get the APP_HOST from .env
    APP_HOST=$(grep APP_HOST .env | cut -d '=' -f2)
    APP_PROTOCOL=$(grep APP_PROTOCOL .env | cut -d '=' -f2)
    
    echo ""
    print_status "🎉 Deployment completed successfully!"
    print_status "Your URL shortener is now available at: ${APP_PROTOCOL}://${APP_HOST}:5000"
    print_status "Health check endpoint: ${APP_PROTOCOL}://${APP_HOST}:5000/health"
    echo ""
    print_status "To view logs: docker-compose logs -f"
    print_status "To stop: docker-compose down"
    print_status "To restart: docker-compose restart"
    
else
    print_error "❌ Services failed to start properly"
    print_error "Check logs with: docker-compose logs"
    exit 1
fi 