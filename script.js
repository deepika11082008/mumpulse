// LOGIN PAGE
document.getElementById("loginForm")?.addEventListener("submit", function(e){

e.preventDefault();

let name = document.getElementById("name").value;
let weeks = document.getElementById("weeks").value;

localStorage.setItem("name", name);
localStorage.setItem("weeks", weeks);

window.location = "screening.html";

});


// VOICE QUESTIONS
let questions = [
"What is your name?",
"How is your life going?",
"How is your baby health?",
"How are you feeling emotionally today?",
"Are you feeling stressed or tired?"
];

function startDay(day){

let q = questions[Math.floor(Math.random()*questions.length)];

let questionElement = document.getElementById("question");

if(questionElement){
questionElement.innerText = "Day " + day + " Question: " + q;
}

}


// VOICE RECORDING
function recordVoice(){

alert("Voice recording started (demo)");

}


// QUESTIONNAIRE SUBMIT
document.getElementById("questionnaire")?.addEventListener("submit", function(e){

e.preventDefault();

let text =
(document.getElementById("q1")?.value || "") +
(document.getElementById("q2")?.value || "");

let risk = "Low";

if(text.toLowerCase().includes("sad") || text.toLowerCase().includes("tired"))
risk = "Moderate";

if(text.toLowerCase().includes("hopeless") || text.toLowerCase().includes("depressed"))
risk = "High";

localStorage.setItem("risk", risk);

window.location = "result.html";

});


// RESULT PAGE
if(document.getElementById("riskLevel")){

let risk = localStorage.getItem("risk") || "Low";

document.getElementById("riskLevel").innerText = "Risk Level: " + risk;

let msg = "You are emotionally stable.";

if(risk === "Moderate")
msg = "You may be experiencing emotional stress.";

if(risk === "High")
msg = "Please consult a healthcare professional.";

document.getElementById("message").innerText = msg;

}


// DASHBOARD
if(document.getElementById("dName")){

document.getElementById("dName").innerText = localStorage.getItem("name");
document.getElementById("dWeeks").innerText = localStorage.getItem("weeks");
document.getElementById("dRisk").innerText = localStorage.getItem("risk");

}


// CHATBOT
function sendMessage(){

let msgInput = document.getElementById("message");
let box = document.getElementById("chatbox");

if(!msgInput || !box) return;

let msg = msgInput.value;

box.innerHTML += "<p><b>You:</b> " + msg + "</p>";

let reply = "I'm here to support you.";

if(msg.toLowerCase().includes("sad"))
reply = "It's okay to feel sad. Try talking to someone you trust.";

if(msg.toLowerCase().includes("stress"))
reply = "Take some rest and breathing exercises.";

box.innerHTML += "<p><b>Bot:</b> " + reply + "</p>";

msgInput.value = "";

}


// VOICE CHAT
function voiceChat(){

alert("Voice chatbot activated (demo)");

}