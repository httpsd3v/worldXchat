# ✨ Mini ShatterChat

Mini ShatterChat is a simple real-time chat application built using:

- 🐍 Flask (Backend)
- ⚡ Supabase (Database + Realtime)
- 🌐 HTML/CSS/JavaScript
- ☁️ Deployable on Render

It allows users to:

- ✅ Register  
- ✅ Login  
- ✅ Send messages  
- ✅ Receive real-time messages  
- ✅ Logout  

---

# 🚀 Features

- Real-time chat using Supabase Realtime
- Simple username/password authentication (custom table)
- Modern glassmorphism UI
- Mobile responsive
- Persistent login using localStorage

---

# 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask |
| Database | Supabase (PostgreSQL) |
| Realtime | Supabase Channels |
| Frontend | Vanilla JS |
| Deployment | Render |

---

# 📦 Installation (Local Setup)

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/mini-shatterchat.git
cd mini-shatterchat
```

---

## 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

---

## 3️⃣ Install Dependencies

```bash
pip install flask
```

---

## 4️⃣ Set Environment Variables

Create a `.env` file or set manually:

```
MY_SUPEBASE_URL=your_supabase_url
MY_ANON_KEY=your_supabase_anon_key
```

On Linux/macOS:
```bash
export MY_SUPEBASE_URL=your_url
export MY_ANON_KEY=your_key
```

On Windows:
```bash
set MY_SUPEBASE_URL=your_url
set MY_ANON_KEY=your_key
```

---

## 5️⃣ Run the App

```bash
python app.py
```

Then visit:

```
http://localhost:5000
```

---

# 🗄 Supabase Setup

## 1️⃣ Create a New Project

Go to Supabase dashboard and create a new project.

---

## 2️⃣ Create Tables

### 🔹 users table

| Column | Type |
|--------|------|
| id | bigint (primary key, auto-increment) |
| username | text |
| password | text |

---

### 🔹 messages table

| Column | Type |
|--------|------|
| id | bigint (primary key, auto-increment) |
| content | text |
| username | text |
| created_at | timestamp (default: now()) |

---

## 3️⃣ Enable Realtime

- Go to Database → Replication
- Enable Realtime for `messages` table

---

# 🌍 Deploying to Render

1. Push project to GitHub  
2. Create new Web Service on Render  
3. Connect repository  
4. Add environment variables:
   - `MY_SUPEBASE_URL`
   - `MY_ANON_KEY`
5. Start command:

```bash
python app.py
```

---

# ⚠️ Security Notice

This project stores passwords in plain text and is **NOT production-ready**.

For production:
- Use Supabase Auth instead of custom users table
- Hash passwords
- Add JWT authentication
- Enable Row Level Security (RLS)

---

# 🔮 Future Improvements

- 🔔 Push notifications
- 🟢 Online status indicator
- 📷 Image sending
- 🧠 Typing indicator
- 🔒 Secure authentication
- 🎨 Theme switcher

---

# 👑 Author

Made by CYshatter
