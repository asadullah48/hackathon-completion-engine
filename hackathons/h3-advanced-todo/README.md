# H3 Advanced Todo Application

## Overview
The H3 Advanced Todo Application is a sophisticated task management system featuring team collaboration, analytics, and advanced productivity tools. Built with Next.js, Tailwind CSS, and FastAPI, it provides a comprehensive solution for personal and team task management.

## Features

### Core Features
- **Task Management**: Create, update, delete, and track tasks with categories, priorities, and deadlines
- **Constitutional AI**: Built-in content validation to prevent inappropriate or harmful content
- **Recurring Tasks**: Set up repeating tasks with customizable patterns (daily, weekly, monthly)
- **Templates**: Create and reuse task templates for common workflows

### Team Collaboration
- **Team Management**: Create and manage teams with role-based permissions
- **Team Tasks**: Assign tasks to team members with detailed tracking
- **Comments**: Collaborate on tasks with threaded comments
- **Notifications**: Real-time notifications for team activities

### Analytics & Reporting
- **Dashboard**: Visualize task completion rates, categories, and trends
- **Charts**: Interactive bar and pie charts showing task distributions
- **Timeline**: Track task activity over time

### Productivity Enhancements
- **Keyboard Shortcuts**: Quick access to common actions (Ctrl+N for new task, etc.)
- **Offline Support**: Service worker enables offline access to cached data
- **Export/Import**: Backup and restore tasks in JSON/CSV formats
- **Search & Filter**: Quickly find tasks by various criteria

### Technical Features
- **Zero-Backend-LLM Architecture**: AI processing runs entirely on the client side
- **PWA Support**: Installable as a progressive web app
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Type Safety**: Full TypeScript support throughout the application

## Architecture

### Frontend (Next.js)
- **Components**: Modular, reusable UI components
- **State Management**: Zustand for global state management
- **API Client**: Comprehensive API abstraction layer
- **Types**: Strict TypeScript interfaces for all data structures
- **Styling**: Tailwind CSS with custom configurations

### Backend (FastAPI)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: User management system
- **API Routes**: RESTful endpoints for all features
- **Validation**: Pydantic models for request/response validation
- **Security**: Input sanitization and content validation

## Getting Started

### Prerequisites
- Node.js (v16 or later)
- Python (v3.8 or later)
- pip package manager

### Installation

#### Backend Setup
```bash
cd hackathons/h3-advanced-todo/backend
pip install -r requirements.txt
```

#### Frontend Setup
```bash
cd hackathons/h3-advanced-todo/frontend
npm install
```

### Running the Application

#### Backend Server
```bash
cd hackathons/h3-advanced-todo/backend
uvicorn main:app --reload
```

#### Frontend Server
```bash
cd hackathons/h3-advanced-todo/frontend
npm run dev
```

The application will be accessible at `http://localhost:3000`.

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl + N | Create new todo |
| Ctrl + Shift + N | Create new team |
| Ctrl + E | Edit selected todo |
| Ctrl + D | Delete selected todo |
| Ctrl + K | Show keyboard shortcuts |

## API Endpoints

### Todos
- `GET /api/todos` - Get all todos
- `POST /api/todos` - Create a new todo
- `PUT /api/todos/{id}` - Update a todo
- `DELETE /api/todos/{id}` - Delete a todo

### Teams
- `GET /api/teams` - Get all teams
- `POST /api/teams` - Create a new team
- `GET /api/teams/{id}` - Get team details
- `PUT /api/teams/{id}` - Update a team
- `DELETE /api/teams/{id}` - Delete a team

### Team Members
- `GET /api/teams/{team_id}/members` - Get team members
- `POST /api/teams/{team_id}/members` - Add a member to team
- `DELETE /api/teams/{team_id}/members/{user_id}` - Remove member from team

### Team Todos
- `GET /api/teams/{team_id}/todos` - Get team todos
- `POST /api/teams/{team_id}/todos` - Create team todo
- `PUT /api/teams/{team_id}/todos/{todo_id}` - Update team todo
- `DELETE /api/teams/{team_id}/todos/{todo_id}` - Delete team todo

### Comments
- `GET /api/teams/{team_id}/todos/{todo_id}/comments` - Get comments for a todo
- `POST /api/teams/{team_id}/todos/{todo_id}/comments` - Add a comment to a todo
- `DELETE /api/teams/{team_id}/todos/{todo_id}/comments/{comment_id}` - Delete a comment

## Project Structure

```
hackathons/h3-advanced-todo/
├── backend/
│   ├── models/           # Database models
│   ├── routers/          # API route handlers
│   ├── services/         # Business logic
│   ├── seeds/            # Initial data
│   ├── database.py       # Database configuration
│   └── main.py           # Application entry point
├── frontend/
│   ├── app/              # Next.js pages
│   ├── components/       # Reusable UI components
│   ├── lib/              # Utilities and hooks
│   ├── public/           # Static assets
│   └── styles/           # Global styles
└── tests/                # Test files
```

## Testing

Run all tests:
```bash
cd hackathons/h3-advanced-todo
python -m pytest tests/
```

## Deployment

### Production Build
```bash
cd hackathons/h3-advanced-todo/frontend
npm run build
```

### Environment Variables
Create a `.env` file in the backend directory:
```
DATABASE_URL=sqlite:///./todos.db
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built for the H3 Hackathon
- Inspired by modern productivity applications
- Uses open-source libraries and frameworks