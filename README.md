# Face Recognition Service

A production-grade face recognition backend service built with RabbitMQ, PostgreSQL, and face_recognition library.

## Features

- 🎯 Face detection and recognition without cloud AI services
- 👥 Multi-person support with automatic categorization
- 📁 Automatic image organization by person
- 🚀 High-performance with Redis caching
- 🐳 Docker-ready deployment
- 🏗️ Clean architecture with repository pattern

## Features which are yet to implement (時間が足りてなくて実装できませんでした。)
- Publish rabbitmq event from python service
- implement rate limiting
- implement authentication flow
- implement aws S3 storage bucket for storage
- implement CI/CD pipeline
- writing tests code for entire project
- handle message loss in the queue

## Tech Stack

- **Python 3.11+**
- **RabbitMq**
- **PostgreSQL** - Primary database
- **Redis** - Caching layer
- **face_recognition** - Face detection and recognition
- **SQLAlchemy** - ORM
- **Docker** - Containerization

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd face-recognition-service

# Create environment file
cp .env.example .env

# Start services
docker-compose up --build