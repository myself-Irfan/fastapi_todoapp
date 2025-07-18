# Task Management API with JWT Authentication

A FastAPI-based task management API with JWT authentication and Argon2 password hashing.

## Features

- **JWT Authentication**: Secure token-based authentication
- **Argon2 Password Hashing**: Industry-standard password hashing
- **Protected Routes**: All task endpoints require authentication
- **User Management**: User registration and login
- **Task CRUD Operations**: Create, read, update, delete tasks
- **SQLAlchemy ORM**: Database operations with SQLAlchemy
- **Pydantic Validation**: Request/response validation
- **Comprehensive Logging**: Structured logging with rotation

## Authentication Implementation

### Password Security
- Uses **Argon2** algorithm for password hashing
- Secure password verification
- Configurable password complexity requirements (minimum 8 characters)

### JWT Token System
- **HS256** algorithm for token signing
- Configurable token expiration (default: 30 minutes)
- Bearer token authentication
- Secure token validation

### Protected Endpoints
All task-related endpoints require authentication:
- `GET /api/tasks/` - Get all tasks
- `GET /api/tasks/{task_id}` - Get specific task
- `POST /api/tasks/` - Create new task
- `PUT /api/tasks/{task_id}` - Update task
- `DELETE /api/tasks/{task_id}` - Delete task

## API Endpoints

### Authentication Endpoints

#### Register User
```bash
POST /api/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "securepassword123"
}
```

#### Login User
```bash
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=testuser&password=securepassword123
```

Returns:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Get Current User
```bash
GET /api/auth/me
Authorization: Bearer <token>
```

### Task Endpoints (All require authentication)

#### Get All Tasks
```bash
GET /api/tasks/
Authorization: Bearer <token>
```

#### Create Task
```bash
POST /api/tasks/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Task Title",
  "description": "Task description",
  "due_date": "2024-12-31",
  "is_complete": false
}
```

#### Get Task by ID
```bash
GET /api/tasks/{task_id}
Authorization: Bearer <token>
```

#### Update Task
```bash
PUT /api/tasks/{task_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated Title",
  "is_complete": true
}
```

#### Delete Task
```bash
DELETE /api/tasks/{task_id}
Authorization: Bearer <token>
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd task-management-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the application:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
SQLALCHEMY_DB_URL=sqlite:///./todo.db

# JWT Configuration
SECRET_KEY=your-super-secret-key-here-change-in-production-at-least-32-characters-long
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
DEBUG=False

# Logging Configuration (optional)
LOG_DIR=logs
LOG_FILE=app.log
```

## Security Considerations

### Production Setup
1. **Change the SECRET_KEY**: Use a strong, random secret key
2. **Use HTTPS**: Always use HTTPS in production
3. **Database Security**: Use a production database with proper credentials
4. **Environment Variables**: Never commit sensitive data to version control
5. **Token Expiration**: Configure appropriate token expiration times
6. **Rate Limiting**: Implement rate limiting for authentication endpoints

### Password Requirements
- Minimum 8 characters
- Passwords are hashed using Argon2
- Email validation enforced

## Testing the API

### Using cURL

1. **Register a user**:
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

2. **Login and get token**:
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpassword123"
```

3. **Access protected endpoint**:
```bash
curl -X GET "http://localhost:8000/api/tasks/" \
  -H "Authorization: Bearer <your-token-here>"
```

### Using the Interactive API Documentation

Visit `http://localhost:8000/docs` to access the Swagger UI documentation where you can:
- Test all endpoints interactively
- View request/response schemas
- Authenticate using the built-in authorization

## Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application setup
│   ├── auth.py              # Authentication utilities
│   ├── auth_routes.py       # Authentication endpoints
│   ├── task_routes.py       # Task CRUD endpoints (protected)
│   ├── task_views.py        # Task view endpoints
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # Database configuration
│   └── logger.py            # Logging configuration
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .env                    # Environment variables (create this)
└── README.md              # This file
```

## Key Dependencies

- **FastAPI**: Web framework
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation
- **python-jose[cryptography]**: JWT token handling
- **passlib[argon2]**: Password hashing with Argon2
- **python-multipart**: Form data handling
- **email-validator**: Email validation
- **uvicorn**: ASGI server

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

## Logging

The application includes comprehensive logging:
- Console output for development
- File logging with rotation
- Structured log format with timestamps
- Configurable log levels

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.