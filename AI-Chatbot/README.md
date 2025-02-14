# 🧠 AI Chatbot with FastAPI + Groq

A real-time chatbot using **FastAPI**, **Groq API**, **WebSockets**, and **SQLite**. It supports **user authentication**, **chat history storage**, and has a **modern UI** built with **Tailwind CSS**.

## 🚀 Features
✅ **Real-time chat using WebSockets**  
✅ **Uses Groq API (LLaMA-3.3-70B model)**  
✅ **Stores chat history per user in SQLite**  
✅ **Simple username-based authentication**  
✅ **Modern, responsive UI with Tailwind CSS**  

---

## 🛠️ Tech Stack
- **Backend:** FastAPI, WebSockets, Groq API
- **Database:** SQLite + SQLAlchemy
- **Frontend:** HTML, Tailwind CSS, JavaScript
- **Deployment:** Uvicorn (local), Railway/Vercel (future)

---

## ⚡ Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/fastapi-groq-chatbot.git
cd fastapi-groq-chatbot
```

2️⃣ Install Dependencies
```bash
pip install fastapi uvicorn groq sqlite3 sqlalchemy websockets pydantic
```
3️⃣ Set Up Your API Key
Replace "your-groq-api-key" in main.py:
```python
os.environ["GROQ_API_KEY"] = "your-groq-api-key"
```
4️⃣ Run the Server
```bash
uvicorn main:app --reload
```
Server runs on http://127.0.0.1:8000/

📌 Usage
1️⃣ Open the app in a browser:

Go to http://127.0.0.1:8000/
2️⃣ Enter a username and start chatting!

3️⃣ Messages are stored, and the AI responds using Groq's LLaMA-3.3-70B model.

📈 Future Enhancements
✅ User authentication (JWT-based login/logout)
✅ Chat history retrieval feature
✅ Deploy on Railway/Vercel
✅ More interactive UI/UX with chat bubbles
