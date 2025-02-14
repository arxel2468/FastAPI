import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from groq import Groq

# Set up Groq API Key
os.environ["GROQ_API_KEY"] = "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"

# Initialize FastAPI
app = FastAPI()

# Groq API client
groq_client = Groq()

# Database setup (SQLite for simplicity)
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

Base.metadata.create_all(bind=engine)

# Serve frontend
@app.get("/")
def serve_home():
    return FileResponse("static/index.html")

# WebSocket connections
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

            # Store user message
            db.add(ChatMessage(user_id=user.id, message=user_message, sender="user"))
            db.commit()

            # Get AI response
            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": user_message}],
                temperature=1,
                max_completion_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
            )

            ai_response = ""
            for chunk in completion:
                ai_response += chunk.choices[0].delta.content or ""

            # Store AI response
            db.add(ChatMessage(user_id=user.id, message=ai_response, sender="ai"))
            db.commit()

            await websocket.send_text(ai_response)

    except WebSocketDisconnect:
        del connected_users[username]
        await websocket.close()
