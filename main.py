from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import random
import time

app = FastAPI(
    title="Jeremy Roast API",
    description="A fun API to make fun of Jeremy (in good spirits!)",
    version="1.0.0"
)

# Jeremy facts and roasts
JEREMY_FACTS = [
    "Jeremy thinks 'git' is a type of sandwich",
    "Jeremy's debugging strategy: 'Have you tried turning it off and on again?' - for everything",
    "Jeremy writes code like he's having a conversation with his cat",
    "Jeremy's idea of testing is 'it works on my machine'",
    "Jeremy thinks 'stack overflow' is a place where developers go to cry",
    "Jeremy's favorite programming language is 'whatever the tutorial says'",
    "Jeremy believes in 'magic code' - code that works but he has no idea why",
    "Jeremy's commit messages: 'stuff' and 'more stuff'",
    "Jeremy thinks 'API' stands for 'Another Problem Incoming'",
    "Jeremy's deployment strategy: 'ship it and pray'"
]

JEREMY_ROASTS = [
    "Jeremy, your code is so buggy, even the bugs have bugs!",
    "Jeremy's debugging skills are like trying to find a black cat in a dark room... while blindfolded",
    "Jeremy writes code like he's playing whack-a-mole with errors",
    "Jeremy's idea of optimization is 'if it's slow, just wait longer'",
    "Jeremy thinks 'clean code' means 'code that's been through the dishwasher'",
    "Jeremy's testing approach: 'ship it to production and let the users find the bugs'",
    "Jeremy believes 'documentation' is a mythical creature",
    "Jeremy's error handling: 'if something goes wrong, just ignore it'",
    "Jeremy thinks 'refactoring' means 'copy and paste with different names'",
    "Jeremy's version control strategy: 'save everything as 'final_final_v2_really_final.py''"
]

JEREMY_COMPLIMENTS = [
    "Jeremy is actually pretty good at finding creative ways to break things",
    "Jeremy has mastered the art of 'unintentional feature discovery'",
    "Jeremy's code is so unique, it's like modern art",
    "Jeremy has a talent for making simple things complicated",
    "Jeremy is the king of 'it works, don't touch it'",
    "Jeremy has perfected the 'write once, debug forever' methodology",
    "Jeremy is a pioneer in 'experimental programming'",
    "Jeremy's code tells a story - a horror story, but still a story",
    "Jeremy has the gift of making every bug look like a feature",
    "Jeremy is the master of 'creative problem solving' (even if it creates more problems)"
]

class JeremyInsult(BaseModel):
    target: str = "Jeremy"
    intensity: str = "medium"
    category: str = "general"

class JeremyResponse(BaseModel):
    message: str
    timestamp: float
    roast_level: str
    category: str

@app.get("/", response_class=HTMLResponse)
async def root():
    """Welcome page with a fun message about Jeremy"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Jeremy Roast API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .container { max-width: 800px; margin: 0 auto; }
            h1 { text-align: center; color: #ffd700; }
            .endpoint { background: rgba(255,255,255,0.1); padding: 20px; margin: 10px 0; border-radius: 10px; }
            .endpoint h3 { color: #ffd700; }
            code { background: rgba(0,0,0,0.3); padding: 5px; border-radius: 5px; }
            .warning { background: rgba(255,165,0,0.3); padding: 15px; border-radius: 10px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎭 Jeremy Roast API 🎭</h1>
            <p>Welcome to the most entertaining API about Jeremy! (All in good fun, of course)</p>
            
            <div class="warning">
                <strong>⚠️ Disclaimer:</strong> This API is created with love and humor. Jeremy, if you're reading this, we're just kidding! (Mostly...)
            </div>
            
            <h2>Available Endpoints:</h2>
            
            <div class="endpoint">
                <h3>🎯 Get a Random Jeremy Fact</h3>
                <code>GET /jeremy/fact</code>
                <p>Learn something "interesting" about Jeremy's coding adventures</p>
            </div>
            
            <div class="endpoint">
                <h3>🔥 Get a Jeremy Roast</h3>
                <code>GET /jeremy/roast</code>
                <p>Get a spicy roast about Jeremy's programming skills</p>
            </div>
            
            <div class="endpoint">
                <h3>😇 Get a Jeremy Compliment</h3>
                <code>GET /jeremy/compliment</code>
                <p>Get a "compliment" about Jeremy (with a twist)</p>
            </div>
            
            <div class="endpoint">
                <h3>🎲 Get a Random Jeremy Response</h3>
                <code>GET /jeremy/random</code>
                <p>Get a random fact, roast, or compliment</p>
            </div>
            
            <div class="endpoint">
                <h3>📊 Jeremy Stats</h3>
                <code>GET /jeremy/stats</code>
                <p>See how many times we've made fun of Jeremy</p>
            </div>
            
            <div class="endpoint">
                <h3>🔍 Search Jeremy Content</h3>
                <code>GET /jeremy/search?q=keyword</code>
                <p>Search through Jeremy-related content</p>
            </div>
            
            <div class="endpoint">
                <h3>🎭 Custom Jeremy Insult</h3>
                <code>POST /jeremy/insult</code>
                <p>Create a custom insult for Jeremy (or anyone else)</p>
            </div>
            
            <p><em>Remember: This is all in good fun! Jeremy, we love you! (Even if your code makes us cry sometimes)</em></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/jeremy/fact")
async def get_jeremy_fact():
    """Get a random fact about Jeremy's coding adventures"""
    fact = random.choice(JEREMY_FACTS)
    return {
        "fact": fact,
        "category": "fact",
        "timestamp": time.time(),
        "message": "Here's something 'interesting' about Jeremy!"
    }

@app.get("/jeremy/roast")
async def get_jeremy_roast():
    """Get a spicy roast about Jeremy"""
    roast = random.choice(JEREMY_ROASTS)
    return {
        "roast": roast,
        "category": "roast",
        "timestamp": time.time(),
        "roast_level": "spicy",
        "message": "🔥 Here's a hot take on Jeremy!"
    }

@app.get("/jeremy/compliment")
async def get_jeremy_compliment():
    """Get a 'compliment' about Jeremy (with a twist)"""
    compliment = random.choice(JEREMY_COMPLIMENTS)
    return {
        "compliment": compliment,
        "category": "compliment",
        "timestamp": time.time(),
        "sincerity_level": "questionable",
        "message": "😇 Here's a 'nice' thing about Jeremy!"
    }

@app.get("/jeremy/random")
async def get_random_jeremy_content():
    """Get a random piece of Jeremy content"""
    categories = ["fact", "roast", "compliment"]
    category = random.choice(categories)
    
    if category == "fact":
        content = random.choice(JEREMY_FACTS)
    elif category == "roast":
        content = random.choice(JEREMY_ROASTS)
    else:
        content = random.choice(JEREMY_COMPLIMENTS)
    
    return {
        "content": content,
        "category": category,
        "timestamp": time.time(),
        "message": f"Here's a random {category} about Jeremy!"
    }

@app.get("/jeremy/stats")
async def get_jeremy_stats():
    """Get statistics about Jeremy content"""
    return {
        "total_facts": len(JEREMY_FACTS),
        "total_roasts": len(JEREMY_ROASTS),
        "total_compliments": len(JEREMY_COMPLIMENTS),
        "total_content": len(JEREMY_FACTS) + len(JEREMY_ROASTS) + len(JEREMY_COMPLIMENTS),
        "message": "Statistics about Jeremy's... interesting coding journey",
        "timestamp": time.time()
    }

@app.get("/jeremy/search")
async def search_jeremy_content(q: str = Query(..., description="Search query")):
    """Search through Jeremy content"""
    query = q.lower()
    results = []
    
    # Search through facts
    for fact in JEREMY_FACTS:
        if query in fact.lower():
            results.append({"content": fact, "category": "fact"})
    
    # Search through roasts
    for roast in JEREMY_ROASTS:
        if query in roast.lower():
            results.append({"content": roast, "category": "roast"})
    
    # Search through compliments
    for compliment in JEREMY_COMPLIMENTS:
        if query in compliment.lower():
            results.append({"content": compliment, "category": "compliment"})
    
    return {
        "query": q,
        "results": results,
        "total_results": len(results),
        "message": f"Found {len(results)} results for '{q}'",
        "timestamp": time.time()
    }

@app.post("/jeremy/insult", response_model=JeremyResponse)
async def create_custom_insult(insult: JeremyInsult):
    """Create a custom insult for Jeremy (or anyone else)"""
    
    # Generate insult based on category and intensity
    if insult.category == "coding":
        if insult.intensity == "mild":
            message = f"{insult.target} thinks 'debugging' means 'deleting code until it works'"
        elif insult.intensity == "medium":
            message = f"{insult.target}'s code is so messy, even the linter gave up and went home"
        else:  # intense
            message = f"{insult.target} writes code that makes other developers question their career choices"
    elif insult.category == "general":
        if insult.intensity == "mild":
            message = f"{insult.target} is like a broken clock - wrong twice a day"
        elif insult.intensity == "medium":
            message = f"{insult.target} has the personality of a wet sock"
        else:  # intense
            message = f"{insult.target} is proof that evolution can go backwards"
    else:
        message = f"{insult.target} is uniquely... special"
    
    return JeremyResponse(
        message=message,
        timestamp=time.time(),
        roast_level=insult.intensity,
        category=insult.category
    )

@app.get("/jeremy/health")
async def jeremy_health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Jeremy's API is running (unlike some of his code)",
        "timestamp": time.time(),
        "uptime": "probably longer than Jeremy's attention span"
    }

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler with Jeremy humor"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "This endpoint is as missing as Jeremy's documentation",
            "suggestion": "Try one of the available endpoints, or ask Jeremy where he put it",
            "available_endpoints": [
                "/jeremy/fact",
                "/jeremy/roast", 
                "/jeremy/compliment",
                "/jeremy/random",
                "/jeremy/stats",
                "/jeremy/search",
                "/jeremy/insult"
            ]
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
