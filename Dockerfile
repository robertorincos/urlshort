FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Expose port 5000
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]