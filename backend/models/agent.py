from pydantic import BaseModel

class Agent(BaseModel):
    symbol: str
    headquarters: str
    credits: int
    startingFaction: str