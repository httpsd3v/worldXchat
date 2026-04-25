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
            font-family: -apple-system, sans-serif;
            background: #000;
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
        }

        #chat {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .msg {
            padding: 10px 15px;
            border-radius: 18px;
            max-width: 70%;
        }

        .me {
            align-self: flex-end;
            background: linear-gradient(45deg, #f58529, #dd2a7b, #8134af, #515bd4);
        }

        .other {
            align-self: flex-start;
            background: #262626;
        }

        .username {
            font-size: 12px;
            opacity: 0.7;
        }

        .input-area {
            display: flex;
            padding: 10px;
            border-top: 1px solid #222;
        }

        input {
            flex: 1;
            padding: 10px;
            border-radius: 20px;
            border: none;
            outline: none;
        }

        button {
            margin-left: 10px;
            padding: 10px 15px;
            border-radius: 20px;
            border: none;
            background: #f3f6f4;
            colour: black;
            cursor: pointer;            
        }
    </style>
</head>
<body>

<header>✨ShatterChat</header>

<div id="auth">
    <input type="text" id="username" placeholder="Username">
    <input type="password" id="password" placeholder="Password">
    <button onclick="register()">Register</button>
    <button onclick="login()">Login</button>
</div>

<div id="chat" style="display:none;"></div>

<div class="input-area" id="chatInput" style="display:none;">
    <input type="text" id="msgInput" placeholder="Message...">
    <button onclick="send()">send</button>
</div>

<script>
/* =========================
   SAFE SUPABASE INIT
========================= */

if (!window.supabase) {
    alert("Supabase failed to load!");
}

const client = supabase.createClient(
    "{{ url }}",
    "{{ key }}"
);

let currentUser = localStorage.getItem("username");

/* =========================
   START CHAT
========================= */

if (currentUser) startChat();

/* =========================
   REGISTER
========================= */

async function register() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const { error } = await client.from("users").insert([
        { username, password }
    ]);

    if (error) {
        alert(error.message);
        return;
    }

    alert("Registered! Now login.");
}

/* =========================
   LOGIN
========================= */

async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const { data, error } = await client
        .from("users")
        .select("*")
        .eq("username", username)
        .eq("password", password)
        .maybeSingle();

    if (error || !data) {
        alert("Invalid login!");
        return;
    }

    localStorage.setItem("username", username);
    currentUser = username;
    startChat();
}

/* =========================
   CHAT START
========================= */

function startChat() {
    document.getElementById("auth").style.display = "none";
    document.getElementById("chat").style.display = "flex";
    document.getElementById("chatInput").style.display = "flex";

    fetchHistory();

    client.channel("room1")
        .on(
            "postgres_changes",
            { event: "INSERT", schema: "public", table: "messages" },
            payload => renderMsg(payload.new)
        )
        .subscribe();
}

/* =========================
   LOAD MESSAGES
========================= */

async function fetchHistory() {
    const { data, error } = await client
        .from("messages")
        .select("*")
        .order("created_at", { ascending: true });

    if (error) {
        console.log(error);
        return;
    }

    data.forEach(renderMsg);
}

/* =========================
   RENDER MESSAGE
========================= */

function renderMsg(msg) {
    const div = document.createElement("div");
    div.className = "msg " + (msg.username === currentUser ? "me" : "other");

    div.innerHTML = `
        <div class="username">${msg.username || "unknown"}</div>
        <div>${msg.content}</div>
    `;

    document.getElementById("chat").appendChild(div);
    document.getElementById("chat").scrollTop = 999999;
}

/* =========================
   SEND MESSAGE
========================= */

async function send() {
    const input = document.getElementById("msgInput");
    if (!input.value) return;

    const { error } = await client.from("messages").insert([
        {
            content: input.value,
            username: currentUser
        }
    ]);

    if (error) {
        alert(error.message);
        return;
    }

    input.value = "";
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
