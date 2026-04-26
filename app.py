from flask import Flask, render_template_string
import os

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://hvaujoxdpowcvbcgoefk.supabase.co")
SUPABASE_KEY = os.getenv(
    "SUPABASE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh2YXVqb3hkcG93Y3ZiY2dvZWZrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY4Mzk0NzMsImV4cCI6MjA5MjQxNTQ3M30.TXL8M0LIXUTiOc_-GeEIcTPPpVUPLwon2qCDzuMyApg"
)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Mini ShatterChat</title>
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>

    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        body {
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: url("https://images.unsplash.com/photo-1506744038136-46273834b3fb") no-repeat center center fixed;
            background-size: cover;
            color: white;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        body::before {
            content: "";
            position: fixed;
            inset: 0;
            background: linear-gradient(
                120deg,
                rgba(245,133,41,0.3),
                rgba(221,42,123,0.3),
                rgba(129,52,175,0.3),
                rgba(81,91,212,0.3)
            );
            filter: blur(120px);
            z-index: -1;
        }

        header {
            padding: 15px;
            text-align: center;
            font-weight: bold;
            border-bottom: 1px solid #222;
            background: black;
        }

        #chat {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(20px);
            border-top: 1px solid rgba(255,255,255,0.1);
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }

        .msg {
            padding: 12px 16px;
            border-radius: 20px;
            max-width: 70%;
            font-size: 14px;
            line-height: 1.4;
            backdrop-filter: blur(15px);
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.15);
        }
        
        .me {
            margin-left: auto;
            background: linear-gradient(
                45deg,
                rgba(245,133,41,0.6),
                rgba(221,42,123,0.6),
                rgba(129,52,175,0.6),
                rgba(81,91,212,0.6)
            );
            border-bottom-right-radius: 5px;
        }
        
        .other {
            border-bottom-left-radius: 5px;
        }

        .username {
            font-size: 12px;
            opacity: 0.7;
        }

        .input-area {
            display: flex;
            padding: 12px;
            gap: 10px;
            background: black;
        }

        input {
            flex: 1;
            padding: 12px 15px;
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.2);
            background: rgba(255,255,255,0.08);
            color: white;
            outline: none;
        }

        button {
            margin-left: 10px;
            padding: 10px 15px;
            border-radius: 20px;
            border: none;
            background: #3897F0;
            colour: black;
            cursor: pointer;            
        }
    </style>
</head>

<body>

<header>
    ✨ ShatterChat
    <button id="logoutBtn" onclick="logout()">Logout</button>
</header>

<div id="auth">
    <input type="text" id="username" placeholder="Username">
    <input type="password" id="password" placeholder="Password">
    <button onclick="register()">Register</button>
    <button onclick="login()">Login</button>
</div>

<div id="chat"></div>

<div class="input-area" id="chatInput">
    <input type="text" id="msgInput" placeholder="Message...">
    <button onclick="send()">Send</button>
</div>

<script>

const client = supabase.createClient("{{ url }}", "{{ key }}");

let currentUser = localStorage.getItem("username");

if (currentUser) startChat();

/* =========================
   REGISTER
========================= */
async function register() {
    const username = username.value;
    const password = password.value;

    await client.from("users").insert([{ username, password }]);
    alert("Registered!");
}

/* =========================
   LOGIN
========================= */
async function login() {
    const usernameVal = username.value;
    const passwordVal = password.value;

    const { data } = await client
        .from("users")
        .select("*")
        .eq("username", usernameVal)
        .eq("password", passwordVal)
        .maybeSingle();

    if (!data) return alert("Invalid login!");

    localStorage.setItem("username", usernameVal);
    currentUser = usernameVal;

    startChat();
}

/* =========================
   START CHAT
========================= */
function startChat() {
    auth.style.display = "none";
    chat.style.display = "flex";
    chatInput.style.display = "flex";
    logoutBtn.style.display = "block";

    fetchHistory();

    client.channel("room1")
        .on("postgres_changes",
            { event: "INSERT", schema: "public", table: "messages" },
            payload => renderMsg(payload.new)
        )
        .subscribe();
}

/* =========================
   LOGOUT (NEW)
========================= */
function logout() {
    if (!confirm("Are you sure you want to logout?")) return;

    localStorage.removeItem("username");
    currentUser = null;

    chat.innerHTML = "";

    auth.style.display = "block";
    chat.style.display = "none";
    chatInput.style.display = "none";
    logoutBtn.style.display = "none";
}

/* =========================
   LOAD MESSAGES
========================= */
async function fetchHistory() {
    const { data } = await client
        .from("messages")
        .select("*")
        .order("created_at", { ascending: true });

    data.forEach(renderMsg);
}

/* =========================
   RENDER MESSAGE
========================= */
function renderMsg(msg) {
    const div = document.createElement("div");
    div.className = "msg " + (msg.username === currentUser ? "me" : "other");

    div.textContent = msg.username + ": " + msg.content;

    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

/* =========================
   SEND MESSAGE
========================= */
async function send() {
    if (!msgInput.value) return;

    await client.from("messages").insert([{
        username: currentUser,
        content: msgInput.value
    }]);

    msgInput.value = "";
}

</script>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(
        HTML_TEMPLATE,
        url=SUPABASE_URL,
        key=SUPABASE_KEY
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
