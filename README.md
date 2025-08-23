# SpaceTraders GUI Frontend

A modern, user-friendly graphical user interface for [SpaceTraders.io](https://spacetraders.io/) - the programmable space trading game API.

## About SpaceTraders

[SpaceTraders](https://spacetraders.io/) is a space-themed economic game that provides HTTP endpoints for automating gameplay and building custom tools. It's designed as a learning platform where developers can:

- **Build and manage fleets** of ships
- **Explore the galaxy** for hidden secrets
- **Automate trade routes** using any programming language
- **Join factions** and compete with other players
- **Learn new technologies** through practical application

## Project Overview

This project provides an intuitive GUI frontend that makes SpaceTraders accessible to players who prefer visual interfaces over command-line tools or raw API calls. The frontend includes:

- **Fleet Management Interface** - View and control your ships
- **Market Dashboard** - Monitor prices and plan trade routes
- **Navigation Tools** - Visual system and waypoint exploration
- **Resource Management** - Track cargo, credits, and crew
- **Real-time Updates** - Live game state monitoring

## Technology Stack

- **Backend**: FastAPI (Python) - High-performance async API framework
- **Frontend**: React.js - Modern JavaScript UI library
- **Styling**: CSS3 with modern design patterns
- **API Client**: Axios for HTTP requests
- **Routing**: React Router for navigation

## Features

### Core Gameplay
- Ship fleet overview and management
- Real-time market data visualization
- Interactive system and waypoint maps
- Cargo and resource tracking
- Crew management and morale monitoring

### Trading & Economics
- Price trend analysis and charts
- Route optimization tools
- Automated trading strategy builder
- Profit/loss tracking and analytics

### Exploration & Discovery
- Interactive galaxy map
- Waypoint exploration tools
- Resource extraction monitoring
- Faction relationship tracking

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- SpaceTraders API token

### Configuration

1. **Create environment file**: Copy the example and add your credentials:
   ```bash
   # Create .env file in the root directory
   SPACETRADERS_TOKEN=your_agent_token_here
   SPACETRADERS_CALLSIGN=your_agent_symbol_here
   SPACETRADERS_API_URL=https://api.spacetraders.io/v2
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Running the Application

#### Option 1: Use the startup script (Recommended)
```bash
./start.sh
```

#### Option 2: Manual startup

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Project Structure

```
spacegame/
├── backend/                 # FastAPI backend
│   └── main.py            # Main application file
├── frontend/               # React frontend
│   ├── public/            # Static files
│   ├── src/               # Source code
│   │   ├── components/    # React components
│   │   ├── App.js         # Main app component
│   │   └── index.js       # Entry point
│   └── package.json       # Node.js dependencies
├── requirements.txt        # Python dependencies
├── start.sh               # Startup script
├── .env                   # Environment variables (create this)
└── README.md              # This file
```

## API Endpoints

The backend provides the following endpoints:

- `GET /api/status` - SpaceTraders API status
- `GET /api/agent` - Current agent information
- `GET /api/ships` - All ships for the current agent
- `GET /api/systems` - All systems in the galaxy
- `GET /api/factions` - All factions

## Development

### Backend Development
- FastAPI with automatic API documentation
- Async HTTP client for SpaceTraders API
- Pydantic models for data validation
- CORS middleware for frontend communication

### Frontend Development
- React hooks for state management
- Responsive design with CSS Grid
- Component-based architecture
- Real-time data updates

### Adding New Features
1. Add new endpoints in `backend/main.py`
2. Create corresponding React components
3. Update routing in `frontend/src/App.js`
4. Add styling in CSS files

## Troubleshooting

### Common Issues

1. **Backend won't start**: Check your `.env` file and ensure all required variables are set
2. **Frontend can't connect to backend**: Verify the backend is running on port 8000
3. **API errors**: Check your SpaceTraders token and ensure it's valid
4. **CORS errors**: Backend includes CORS middleware for localhost:3000

### Getting Help

- Check the FastAPI docs at http://localhost:8000/docs
- Review browser console for frontend errors
- Check backend logs for API errors

## Contributing

This is an open-source project welcoming contributions from the SpaceTraders community. Whether you're a seasoned developer or just learning, your help is appreciated!

### How to Contribute
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Resources

- [SpaceTraders Official Website](https://spacetraders.io/)
- [SpaceTraders API Documentation](https://spacetraders.io/docs)
- [Community Discord](https://discord.gg/spacetraders)
- [Community Projects](https://spacetraders.io/projects)
- **OpenAPI Specification**: [`spacetraders_openapi.json`](./spacetraders_openapi.json) - Complete API schema for v2.3.0

## License

*License information to be added*

---

*This project is not affiliated with SpaceTraders.io but is built to enhance the gaming experience for the SpaceTraders community.*
