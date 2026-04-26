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
            background: #111;
            color: white;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }

        header {
            padding: 15px;
            text-align: center;
            font-weight: bold;
            border-bottom: 1px solid #222;
            background: black;
            position: relative;
        }

        #logoutBtn {
            position: absolute;
            right: 15px;
            top: 10px;
            padding: 6px 12px;
            border-radius: 10px;
            border: none;
            background: #ff4d4d;
            color: white;
            cursor: pointer;
            display: none;
        }

        #chat {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: none;
            flex-direction: column;
            gap: 12px;
            background: rgba(255,255,255,0.05);
        }

        .msg {
            padding: 12px;
            border-radius: 12px;
            max-width: 70%;
        }

        .me { background: #3897F0; margin-left: auto; }
        .other { background: #333; }

        .input-area {
            display: none;
            padding: 12px;
            background: black;
            gap: 10px;
        }

        input {
            flex: 1;
            padding: 12px;
            border-radius: 20px;
            border: none;
            background: #222;
            color: white;
        }

        button {
            padding: 10px 15px;
            border-radius: 20px;
            border: none;
            background: #3897F0;
            color: white;
            cursor: pointer;
        }

        #auth {
            padding: 20px;
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
