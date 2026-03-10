// Screening form submit

document.getElementById("screeningForm")?.addEventListener("submit",function(e){

e.preventDefault()

let mood=document.getElementById("mood").value
let text=document.getElementById("text").value

let risk="Low"

if(mood=="sad" || text.includes("sad"))
risk="Moderate"

if(text.includes("hopeless") || text.includes("depressed"))
risk="High"

localStorage.setItem("risk",risk)

window.location.href="result.html"

})


// show result

if(document.getElementById("riskLevel")){

let risk=localStorage.getItem("risk")

document.getElementById("riskLevel").innerText="Risk Level: "+risk

}


// chatbot

function sendMessage(){

let message=document.getElementById("message").value

let chatbox=document.getElementById("chatbox")

chatbox.innerHTML+="<p>You: "+message+"</p>"

let reply="I'm here to support you."

if(message.includes("sad"))
reply="I'm sorry you're feeling sad. Talking to someone may help."

if(message.includes("stress"))
reply="Try taking some deep breaths and resting."

chatbox.innerHTML+="<p>Bot: "+reply+"</p>"

}