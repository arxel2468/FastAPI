import os
import dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from groq import Groq

# Load environment variables
dotenv.load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Groq API Client
groq_client = Groq(api_key=GROQ_API_KEY)

# Database setup (SQLite)
DATABASE_URL = "sqlite:///./chat.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# User Model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)

# Chat Message Model
class ChatMessage(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String)
    sender = Column(String)  # "user" or "ai"

# Create tables
Base.metadata.create_all(bind=engine)

# Serve frontend
@app.get("/")
def serve_home():
    return FileResponse("static/index.html")

# Store connected users
connected_users = {}

@app.websocket("/ws/{username}")
async def chat_websocket(websocket: WebSocket, username: str):
    await websocket.accept()
    connected_users[username] = websocket
    db = SessionLocal()

    # Ensure user exists
    user = db.query(User).filter(User.username == username).first()
    if not user:
        user = User(username=username)
        db.add(user)
        db.commit()

    try:
        while True:
            user_message = await websocket.receive_text()

            # Store user message in DB
            db.add(ChatMessage(user_id=user.id, message=user_message, sender="user"))
            db.commit()

            # Get AI response (streaming in chunks)
            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": user_message}],
                temperature=0.7,
                max_completion_tokens=50,  # Shorter responses for conversation-like flow
                top_p=1,
                stream=True,
                stop=None,
            )

            ai_response = ""
            async for chunk in completion:
                delta = chunk.choices[0].delta.content
                if delta:
                    ai_response += delta
                    await websocket.send_text(delta)  # Send AI response in small parts

            # Store AI response in DB
            db.add(ChatMessage(user_id=user.id, message=ai_response, sender="ai"))
            db.commit()

    except WebSocketDisconnect:
        del connected_users[username]
        await websocket.close()
