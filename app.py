from flask import Flask, render_template_string
import os

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://hvaujoxdpowcvbcgoefk.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh2YXVqb3hkcG93Y3ZiY2dvZWZrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY4Mzk0NzMsImV4cCI6MjA5MjQxNTQ3M30.TXL8M0LIXUTiOc_-GeEIcTPPpVUPLwon2qCDzuMyApg")

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>ShatterChat X</title>
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body { margin:0; font-family:sans-serif; background:#111; color:white; display:flex; flex-direction:column; height:100vh;}
header { padding:10px; background:black; text-align:center; position:relative;}
#logoutBtn { position:absolute; right:10px; top:8px; display:none;}
#notifBell { position:absolute; left:10px; top:8px; cursor:pointer;}
#chat { flex:1; overflow-y:auto; padding:10px; display:none;}
.msg { padding:8px; border-radius:12px; margin-bottom:8px; max-width:70%;}
.me { background:#3897F0; margin-left:auto;}
.other { background:#333;}
.input-area { display:none; padding:10px; background:black;}
input, button { padding:8px; border-radius:8px; border:none;}
button { background:#3897F0; color:white; cursor:pointer;}
#auth { padding:20px;}
#profileBox, #suggestions { padding:10px; display:none; background:#000;}
@media(max-width:768px){ .msg{max-width:90%; font-size:14px;} }
</style>
</head>
<body>

<header>
<span id="notifBell">🔔 <span id="notifCount">0</span></span>
ShatterChat X
<button id="logoutBtn" onclick="logout()">Logout</button>
</header>

<div id="auth">
<input id="username" placeholder="Username">
<input id="password" type="password" placeholder="Password">
<button onclick="register()">Register</button>
<button onclick="login()">Login</button>
</div>

<div id="profileBox">
<img id="avatar" width="50" height="50" style="border-radius:50%">
<div id="bio"></div>
<div>Followers: <span id="followers">0</span></div>
<input type="file" id="avatarUpload">
</div>

<div id="suggestions"></div>

<div id="chat"></div>
<div id="typing"></div>

<div class="input-area" id="chatInput">
<input id="msgInput" placeholder="Message">
<button onclick="send()">Send</button>
<button id="recordBtn">🎤</button>
</div>

<script>
const { createClient } = supabase;
const client = createClient("{{url}}", "{{key}}");

let currentUser = localStorage.getItem("username");

if(currentUser) start();

async function register(){
 await client.from("users").insert([{username:username.value,password:password.value}]);
 alert("Registered");
}

async function login(){
 const {data} = await client.from("users")
  .select("*")
  .eq("username",username.value)
  .eq("password",password.value)
  .maybeSingle();
 if(!data) return alert("Invalid");
 localStorage.setItem("username",username.value);
 currentUser=username.value;
 start();
}

async function start(){
 auth.style.display="none";
 chat.style.display="block";
 chatInput.style.display="flex";
 logoutBtn.style.display="block";
 profileBox.style.display="block";
 suggestions.style.display="block";
 await setOnline();
 loadProfile();
 loadSuggestions();
 loadNotifications();
 loadMessages();
 subscribe();
}

function logout(){
 if(!confirm("Logout?")) return;
 localStorage.removeItem("username");
 location.reload();
}

async function setOnline(){
 await client.from("online_users").upsert({username:currentUser});
}

async function loadProfile(){
 const {data} = await client.from("profiles")
  .select("*").eq("username",currentUser).maybeSingle();
 if(!data) return;
 bio.textContent=data.bio||"No bio";
 avatar.src=data.avatar_url||"https://via.placeholder.com/50";
 followers.textContent=data.followers||0;
}

avatarUpload.onchange=async(e)=>{
 const file=e.target.files[0];
 const path=currentUser+"-"+Date.now();
 await client.storage.from("avatars").upload(path,file);
 const {data}=client.storage.from("avatars").getPublicUrl(path);
 await client.from("profiles")
  .update({avatar_url:data.publicUrl})
  .eq("username",currentUser);
 loadProfile();
};

async function loadSuggestions(){
 const {data}=await client.from("profiles")
  .select("username").neq("username",currentUser).limit(5);
 suggestions.innerHTML="<h4>People You May Know</h4>";
 data.forEach(u=>{
  const div=document.createElement("div");
  div.textContent=u.username;
  div.onclick=()=>follow(u.username);
  suggestions.appendChild(div);
 });
}

async function follow(user){
 await client.from("follows").insert([{follower:currentUser,following:user}]);
 await client.from("notifications").insert([{
  username:user,
  message:currentUser+" followed you"
 }]);
 alert("Followed");
}

async function loadNotifications(){
 const {data}=await client.from("notifications")
  .select("*").eq("username",currentUser).eq("is_read",false);
 notifCount.textContent=data.length;
}

async function loadMessages(){
 const {data}=await client.from("messages")
  .select("*").order("created_at",{ascending:true});
 data.forEach(render);
}

function render(msg){
 const div=document.createElement("div");
 div.className="msg "+(msg.username===currentUser?"me":"other");
 if(msg.parent_id) div.style.marginLeft="20px";
 if(msg.content.endsWith(".webm")){
  const audio=document.createElement("audio");
  audio.controls=true;
  audio.src=msg.content;
  div.appendChild(audio);
 }else{
  div.textContent=msg.username+": "+msg.content;
 }
 chat.appendChild(div);
 chat.scrollTop=chat.scrollHeight;
}

async function send(parent=null){
 if(!msgInput.value) return;
 await client.from("messages").insert([{
  username:currentUser,
  content:msgInput.value,
  parent_id:parent
 }]);
 msgInput.value="";
}

msgInput.addEventListener("input",async()=>{
 await client.from("typing").upsert({username:currentUser,is_typing:true});
 setTimeout(async()=>{
  await client.from("typing").upsert({username:currentUser,is_typing:false});
 },1000);
});

function subscribe(){
 client.channel("room")
  .on("postgres_changes",{event:"INSERT",schema:"public",table:"messages"},
   p=>render(p.new))
  .subscribe();

 client.channel("typing")
  .on("postgres_changes",{event:"*",schema:"public",table:"typing"},
   p=>{
    if(p.new.username!==currentUser && p.new.is_typing)
     typing.textContent=p.new.username+" is typing...";
    else typing.textContent="";
   }).subscribe();
}

let mediaRecorder;
let chunks=[];
recordBtn.onclick=async()=>{
 const stream=await navigator.mediaDevices.getUserMedia({audio:true});
 mediaRecorder=new MediaRecorder(stream);
 mediaRecorder.start();
 mediaRecorder.ondataavailable=e=>chunks.push(e.data);
 mediaRecorder.onstop=async()=>{
  const blob=new Blob(chunks);
  const path=currentUser+"-"+Date.now()+".webm";
  await client.storage.from("voice").upload(path,blob);
  const {data}=client.storage.from("voice").getPublicUrl(path);
  await client.from("messages").insert([{
   username:currentUser,
   content:data.publicUrl
  }]);
  chunks=[];
 };
 setTimeout(()=>mediaRecorder.stop(),4000);
};
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML, url=SUPABASE_URL, key=SUPABASE_KEY)

if __name__ == "__main__":
    app.run(debug=True)
