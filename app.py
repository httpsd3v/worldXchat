from flask import Flask, render_template_string
import os

app = Flask(__name__)

SUPABASE_URL = os.getenv("MY_SUPEBASE_URL")
SUPABASE_KEY = os.getenv("MY_ANON_KEY")

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
    ✨ShatterChat
    <button id="logoutBtn" onclick="logout()" style="
        position:absolute;
        right:15px;
        top:10px;
        display:none;
        padding:6px 12px;
        border:none;
        border-radius:10px;
        background:red;
        color:white;
        cursor:pointer;
    ">
        Logout
    </button>
</header>

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

    document.getElementById("logoutBtn").style.display = "block";

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
   LOG OUT
========================= */
function logout() {
    if (!confirm("Logout?")) return;

    // 1. clear session
    localStorage.removeItem("username");
    currentUser = null;

    // 2. clear chat UI
    document.getElementById("chat").innerHTML = "";

    // 3. reset UI
    document.getElementById("auth").style.display = "block";
    document.getElementById("chat").style.display = "none";
    document.getElementById("chatInput").style.display = "none";
    document.getElementById("logoutBtn").style.display = "none";

    // 4. optional hard reset of page state
    location.hash = "";
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
