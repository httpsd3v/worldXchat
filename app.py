from flask import Flask, render_template_string, os

app = Flask(__name__)

# --- CONFIGURATION ---
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-anon-key")

# --- HTML TEMPLATE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Mini Text Realtime</title>
    <script src="https://jsdelivr.net"></script>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: -apple-system, sans-serif; background: #f0f2f5; display: flex; flex-direction: column; height: 100vh; margin: 0; }
        #chat { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 10px; }
        .msg { background: white; padding: 10px 15px; border-radius: 18px; width: fit-content; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
        .input-area { background: white; padding: 20px; display: flex; gap: 10px; border-top: 1px solid #ddd; }
        input { flex: 1; padding: 12px; border: 1px solid #ccc; border-radius: 25px; outline: none; }
        button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 25px; cursor: pointer; }
    </style>
</head>
<body>
    <div id="chat"></div>
    <div class="input-area">
        <input type="text" id="msgInput" placeholder="Write a message..." onkeypress="if(event.key==='Enter') send()">
        <button onclick="send()">Send</button>
    </div>

    <script>
        const supabase = supabase.createClient("{{ url }}", "{{ key }}");
        const chatDiv = document.getElementById('chat');

        // 1. Fetch initial history
        async function fetchHistory() {
            const { data } = await supabase.from('messages').select('*').order('created_at', { ascending: true });
            if (data) data.forEach(m => renderMsg(m.content));
        }

        // 2. Realtime listener
        supabase.channel('room1')
            .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'messages' }, payload => {
                renderMsg(payload.new.content);
            })
            .subscribe();

        // 3. UI Helpers
        function renderMsg(text) {
            const div = document.createElement('div');
            div.className = 'msg';
            div.innerText = text;
            chatDiv.appendChild(div);
            chatDiv.scrollTop = chatDiv.scrollHeight;
        }

        async function send() {
            const el = document.getElementById('msgInput');
            if (!el.value) return;
            const content = el.value;
            el.value = '';
            await supabase.from('messages').insert([{ content }]);
        }

        fetchHistory();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, url=SUPABASE_URL, key=SUPABASE_KEY)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))