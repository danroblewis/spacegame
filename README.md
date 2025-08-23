# 🎭 Jeremy Roast API 🎭

A fun and humorous FastAPI server dedicated to making fun of Jeremy (in good spirits, of course!). This API provides various endpoints to get facts, roasts, and "compliments" about Jeremy's coding adventures.

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

3. Open your browser and visit:
   - **Main page**: http://localhost:8000/
   - **API docs**: http://localhost:8000/docs
   - **Alternative docs**: http://localhost:8000/redoc

## 🎯 Available Endpoints

### 🏠 Root
- `GET /` - Beautiful HTML welcome page with all endpoint information

### 📚 Jeremy Content
- `GET /jeremy/fact` - Get a random fact about Jeremy's coding adventures
- `GET /jeremy/roast` - Get a spicy roast about Jeremy
- `GET /jeremy/compliment` - Get a "compliment" about Jeremy (with a twist)
- `GET /jeremy/random` - Get random fact, roast, or compliment

### 📊 Information
- `GET /jeremy/stats` - Get statistics about available content
- `GET /jeremy/search?q=keyword` - Search through Jeremy content
- `GET /jeremy/health` - Health check with Jeremy humor

### 🎭 Custom Content
- `POST /jeremy/insult` - Create custom insults (for Jeremy or anyone else)

## 🔧 API Examples

### Get a Random Jeremy Fact
```bash
curl http://localhost:8000/jeremy/fact
```

### Get a Jeremy Roast
```bash
curl http://localhost:8000/jeremy/roast
```

### Search for Content
```bash
curl "http://localhost:8000/jeremy/search?q=debugging"
```

### Create Custom Insult
```bash
curl -X POST "http://localhost:8000/jeremy/insult" \
  -H "Content-Type: application/json" \
  -d '{"target": "Jeremy", "intensity": "intense", "category": "coding"}'
```

## 🎨 Features

- **Beautiful HTML welcome page** with gradient background and styling
- **Random content generation** for endless entertainment
- **Search functionality** to find specific Jeremy content
- **Custom insult generator** with different intensities and categories
- **Humorous error handling** with Jeremy-themed 404 pages
- **Interactive API documentation** via Swagger UI
- **Health check endpoint** with Jeremy humor

## 😄 Content Categories

### Facts
Humorous "facts" about Jeremy's coding practices, debugging strategies, and development approach.

### Roasts
Spicy takes on Jeremy's programming skills, code quality, and development methodology.

### Compliments
"Compliments" that are actually thinly veiled roasts (all in good fun!).

## ⚠️ Disclaimer

This API is created with love and humor. Jeremy, if you're reading this, we're just kidding! (Mostly...) It's all in good spirits and meant to bring laughter to the development team.

## 🛠️ Development

### Project Structure
```
spacegame/
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Adding New Content
To add more Jeremy facts, roasts, or compliments, simply edit the arrays in `main.py`:
- `JEREMY_FACTS`
- `JEREMY_ROASTS` 
- `JEREMY_COMPLIMENTS`

### Running Tests
The server includes built-in error handling and validation. Test different endpoints to see the humorous responses!

## 🌟 Have Fun!

Remember, this is all in good fun! Jeremy, we love you! (Even if your code makes us cry sometimes) 

Enjoy the API and may your debugging sessions be as entertaining as Jeremy's coding adventures! 🎉
