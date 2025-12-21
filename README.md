# Gantt Scheduler

A modern, interactive Gantt chart task scheduler built with **Vue.js 3** and **Python Flask**.

![Gantt Scheduler](https://img.shields.io/badge/Vue.js-3.4-4FC08D?logo=vue.js)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask)

## ✨ Features

- **Draggable Tasks** - Drag tasks horizontally to change dates, vertically to reorder
- **Resizable Tasks** - Resize tasks from left/right edges to adjust start/end dates
- **Task Connections** - Connect tasks with customizable arrows showing dependencies
- **Multiple Time Scales** - Switch between Hour, Day, Week, and Month views
- **Connection Types** - Support for Finish-to-Start, Start-to-Start, Finish-to-Finish, Start-to-Finish
- **Arrow Customization** - Customize arrow colors and styles (solid, dashed, dotted)
- **Progress Tracking** - Visual progress bars on each task
- **Modern UI** - Dark theme with industrial aesthetic

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

## 📖 Usage

### Creating Tasks

1. Click the **"Add Task"** button in the header
2. Fill in the task details (title, dates, color, progress)
3. Click **"Create Task"**

### Dragging Tasks

- **Move horizontally**: Click and drag a task bar to change its dates
- **Move vertically**: Drag up/down to reorder tasks
- **Resize**: Drag the left/right edges of a task to adjust start/end dates

### Creating Connections

1. Hover over a task bar to see connection handles (circles on left/right)
2. Click and drag from a handle to another task
3. Release to create the connection

### Editing Connections

- **Click** on a connection arrow to edit its properties (color, style, type)
- **Right-click** on a connection arrow to delete it

### Time Scale

Use the scale selector (Hour/Day/Week/Month) in the header to change the timeline granularity.

### Demo Data

Click **"Load Demo"** to populate the chart with sample tasks and connections.

## 🔌 API Endpoints

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | Get all tasks |
| GET | `/api/tasks/{id}` | Get task by ID |
| POST | `/api/tasks` | Create new task |
| PUT | `/api/tasks/{id}` | Update task |
| DELETE | `/api/tasks/{id}` | Delete task |

### Connections

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/connections` | Get all connections |
| POST | `/api/connections` | Create connection |
| PUT | `/api/connections/{id}` | Update connection |
| DELETE | `/api/connections/{id}` | Delete connection |

### Utility

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tasks/seed` | Load demo data |

## 📁 Project Structure

```
My_Gantt/
├── backend/
│   ├── main.py          # Flask application
│   ├── models.py        # SQLAlchemy models
│   ├── database.py      # Database configuration
│   └── requirements.txt # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── GanttChart.vue  # Main Gantt component
│   │   ├── styles/
│   │   │   └── main.css        # Global styles
│   │   ├── api.js              # API client
│   │   ├── App.vue             # Root component
│   │   └── main.js             # Entry point
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
└── README.md
```

## 🎨 Customization

### Task Colors

Tasks support any valid CSS color. Common colors used:
- `#4CAF50` - Green (completed/planning)
- `#2196F3` - Blue (design)
- `#9C27B0` - Purple (development)
- `#FF9800` - Orange (frontend)
- `#F44336` - Red (testing)
- `#607D8B` - Gray (deployment)

### Arrow Styles

- **Solid** - Default continuous line
- **Dashed** - Long dashes (8px dash, 4px gap)
- **Dotted** - Short dashes (2px dash, 4px gap)

### Connection Types

- **Finish-to-Start** - Task B starts after Task A finishes (default)
- **Start-to-Start** - Task B starts when Task A starts
- **Finish-to-Finish** - Task B finishes when Task A finishes
- **Start-to-Finish** - Task B finishes when Task A starts

## 🛠 Tech Stack

**Frontend:**
- Vue.js 3 (Composition API)
- Vite
- date-fns
- Axios

**Backend:**
- Python 3.10+
- Flask
- Flask-CORS
- SQLAlchemy
- SQLite

## 📄 License

MIT License - feel free to use this project for personal or commercial purposes.

