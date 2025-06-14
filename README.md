# 🔗 URL Shortener

A modern, production-ready URL shortener built with Flask and MongoDB.

## ✨ Features

- **URL Shortening**: Convert long URLs into short, memorable codes
- **Click Analytics**: Track click counts and access statistics
- **Custom Short Codes**: Automatic generation of unique short codes using base62 encoding
- **URL Validation**: Proper validation of input URLs
- **Health Monitoring**: Built-in health check endpoints
- **Docker Support**: Full containerization with Docker and Docker Compose
- **Production Ready**: Comprehensive error handling, logging, and security features

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB
- **Frontend**: HTML, CSS, JavaScript
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions

## 🚀 Quick Start

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/robertorincos/urlshort.git
   cd urlshort
   ```

2. **Run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - URL Shortener: http://localhost:5000
   - Health Check: http://localhost:5000/health

### Production Deployment on Ubuntu Server

1. **Run the automated deployment script**:
   ```bash
   ./deploy.sh
   ```

2. **Manual deployment**:
   ```bash
   # Copy environment file and configure
   cp env.example .env
   # Edit .env with your production settings
   
   # Deploy with Docker Compose
   docker-compose up --build -d
   ```

## 📡 API Endpoints

### Shorten URL
```bash
POST /shorten
Content-Type: application/json

{
  "url": "https://example.com"
}
```

**Response**:
```json
{
  "original_url": "https://example.com",
  "short_code": "abc123",
  "short_url": "http://your-domain.com/abc123"
}
```

### Get Statistics
```bash
GET /stats/{short_code}
```

**Response**:
```json
{
  "short_code": "abc123",
  "original_url": "https://example.com",
  "created_at": "2025-01-01T12:00:00Z",
  "click_count": 42,
  "last_accessed": "2025-01-01T15:30:00Z"
}
```

### Health Check
```bash
GET /health
```

## 🔧 Configuration

Create a `.env` file based on `env.example`:

```env
# MongoDB Configuration
MONGO_HOST=mongodb
MONGO_PORT=27017
MONGO_DB_NAME=flask_database

# Application Configuration
APP_HOST=your-domain.com
APP_PORT=5000
APP_PROTOCOL=https
DEBUG=false
```

## 📊 Monitoring

- **Health Check**: `/health` endpoint for monitoring tools
- **Logs**: View logs with `docker-compose logs -f`
- **Statistics**: Built-in click tracking and analytics

## 🔒 Security Features

- Input validation and sanitization
- Non-root Docker container
- Error handling without information disclosure
- Rate limiting ready (can be easily added)

## 🧪 Testing

The project includes comprehensive GitHub Actions CI/CD:

- Automated Docker builds
- Health check testing
- API endpoint testing
- URL redirection testing
- Statistics endpoint testing

## 📈 Production Tips

1. **Use a reverse proxy** (nginx) for SSL termination
2. **Set up monitoring** with tools like Prometheus/Grafana
3. **Configure backups** for MongoDB data
4. **Use environment variables** for all configuration
5. **Monitor logs** regularly for issues

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if needed
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🚨 Support

If you encounter any issues or have questions:

1. Check the [GitHub Issues](https://github.com/robertorincos/urlshort/issues)
2. Review the logs: `docker-compose logs`
3. Verify your environment configuration
4. Ensure all services are running: `docker-compose ps`
