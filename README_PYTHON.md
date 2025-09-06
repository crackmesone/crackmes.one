# crackmes.one - Python Version

This is the Python rewrite of the original Go-based crackmes.one website. The application has been fully converted from Go to Python using Flask while maintaining all the original functionality.

## Original vs Python Implementation

### Technology Stack Comparison

| Component | Original Go | Python Version |
|-----------|-------------|----------------|
| Web Framework | httprouter + custom | Flask with blueprints |
| Database Driver | MongoDB Go driver | pymongo |
| Templates | Go templates | Jinja2 |
| Session Management | Gorilla sessions | Flask-Session |
| CSRF Protection | csrfbanana | Flask-WTF |
| Password Hashing | bcrypt | bcrypt |
| File Upload | Native Go | Werkzeug |
| Routing | httprouter | Flask blueprints |

### Features Implemented

✅ **Complete Feature Parity:**
- User authentication (registration, login, logout)
- Crackme upload and management
- Solution upload and management  
- Comment system
- Rating system (difficulty and quality)
- Notifications system
- User profiles with statistics
- Search functionality
- RSS feeds
- File upload with moderation
- Responsive web design

## Installation and Setup

### Prerequisites
- Python 3.8+
- MongoDB
- pip (Python package installer)

### Installation Steps

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up MongoDB:**
   - Install MongoDB for your operating system
   - Start MongoDB service
   - The application will connect to `mongodb://127.0.0.1:27017` by default

3. **Create required directories:**
```bash
mkdir -p tmp/{crackme,solution}
mkdir -p static/{crackme,solution}
```

4. **Optional - Create configuration file:**
```bash
mkdir config
# Copy your config.json file to config/config.json
# Or use the default development configuration
```

5. **Run the application:**
```bash
python3 crackmesone.py
```

The application will be available at `http://localhost:8080`

## Configuration

The application supports configuration via `config/config.json`. If no configuration file is provided, it will use default development settings.

Example configuration structure:
```json
{
  "Database": {
    "MongoDB": {
      "URL": "mongodb://127.0.0.1:27017",
      "Database": "crackmesone"
    }
  },
  "Session": {
    "Key": "your-secret-key"
  }
}
```

## Application Structure

```
crackmesone.py          # Main application entry point
requirements.txt        # Python dependencies
app/
  ├── __init__.py
  ├── routes.py         # Flask routes and blueprints
  ├── models/           # Database models
  │   ├── user.py       # User authentication and management
  │   ├── crackme.py    # Crackme model and operations
  │   ├── solution.py   # Solution model and operations
  │   ├── comment.py    # Comment system
  │   ├── rating.py     # Rating system (difficulty/quality)
  │   └── notification.py # Notification system
  ├── shared/           # Shared utilities
  │   └── database.py   # Database connection and utilities
  └── templates/        # Jinja2 templates
      ├── base.html     # Base template
      ├── index.html    # Homepage
      ├── auth/         # Authentication templates
      ├── user/         # User profile templates
      ├── crackme/      # Crackme templates
      └── errors/       # Error page templates
static/
  └── css/
      └── style.css     # Application styles
```

## API Endpoints

The Python version maintains the same URL structure as the original Go version:

- `GET /` - Homepage
- `GET /login` - Login page
- `POST /login` - Login form submission
- `GET /register` - Registration page
- `POST /register` - Registration form submission
- `GET /logout` - Logout
- `GET /user/<username>` - User profile
- `GET /crackme/<hex_id>` - Crackme detail page
- `GET /upload/crackme` - Upload crackme form
- `POST /upload/crackme` - Upload crackme submission
- `GET /upload/solution/<hex_id>` - Upload solution form
- `POST /upload/solution/<hex_id>` - Upload solution submission
- `POST /comment/<hex_id>` - Post comment
- `GET /search` - Search page
- `GET /notifications` - User notifications
- `POST /api/rate-difficulty/<hex_id>` - Rate difficulty
- `POST /api/rate-quality/<hex_id>` - Rate quality
- `GET /rss/crackme` - RSS feed

## Database Schema

The Python version uses the same MongoDB collections and document structure as the original Go version:

- `user` - User accounts and authentication
- `crackme` - Crackme challenges
- `solution` - Solution submissions
- `comment` - User comments
- `rating_difficulty` - Difficulty ratings
- `rating_quality` - Quality ratings
- `notifications` - User notifications

## Development

### Running in Development Mode

For development, you can enable debug mode by modifying `crackmesone.py`:

```python
app.run(host='0.0.0.0', port=8080, debug=True)
```

### Code Organization

The application follows Flask best practices:
- **Blueprints** for organizing routes
- **Models** for database operations
- **Templates** with inheritance and components
- **Context processors** for global template variables
- **Decorators** for authentication and authorization

## Migration from Go Version

If you're migrating from the Go version:

1. **Database**: No migration needed - the Python version uses the same MongoDB schema
2. **Files**: Existing crackme and solution files in `static/` directory are compatible
3. **Configuration**: Convert your Go configuration to the JSON format expected by the Python version
4. **Templates**: The Python version includes equivalent templates with the same functionality

## Features Comparison

| Feature | Go Version | Python Version | Status |
|---------|------------|----------------|---------|
| User Authentication | ✓ | ✓ | Complete |
| File Upload | ✓ | ✓ | Complete |
| Crackme Management | ✓ | ✓ | Complete |
| Solution Management | ✓ | ✓ | Complete |
| Comment System | ✓ | ✓ | Complete |
| Rating System | ✓ | ✓ | Complete |
| Notifications | ✓ | ✓ | Complete |
| Search | ✓ | ✓ | Complete |
| RSS Feeds | ✓ | ✓ | Complete |
| User Profiles | ✓ | ✓ | Complete |
| CSRF Protection | ✓ | ✓ | Complete |
| Session Management | ✓ | ✓ | Complete |
| Responsive Design | ✓ | ✓ | Complete |

## Contributing

The Python version maintains the same functionality as the original Go version while providing a more accessible codebase for Python developers. Contributions are welcome!

## License

This project maintains the same license as the original crackmes.one project.