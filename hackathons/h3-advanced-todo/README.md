# H3: Advanced Todo Application

## Overview
Advanced todo application with event-driven architecture, real-time synchronization, and AI-powered task prioritization.

## Architecture
- Event-driven microservices using Kafka
- Real-time sync with Redis and Socket.IO
- AI-powered task prioritization
- Multi-channel notifications

## Services
- Task Service: Core task management
- Notification Service: Multi-channel notifications
- AI Service: Intelligent task prioritization
- Analytics Service: Productivity insights
- Gateway: API gateway

## Getting Started
1. Install Docker and Docker Compose
2. Run `docker-compose up` to start all services
3. Access the application at http://localhost:3000

## Development
- Each service is located in the `/services` directory
- Shared components are in the `/shared` directory
- Tests are in the `/tests` directory