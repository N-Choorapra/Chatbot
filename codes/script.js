"use strict";
const inputEl = document.querySelector(".input-chat");
const btnEl = document.querySelector(".fa-paper-plane");
const cardBodyEl = document.querySelector(".card-body");
let userMessage;
const URL = "http://localhost:8888/hear";

const chatGenerator = (robotMessageEl) => {
  const formData = new FormData();
  formData.append("ask", userMessage);

  const requestOption = {
    method: "POST",
    body: formData,
  };

  fetch(URL, requestOption)
    .then((res) => res.json())
    .then((data) => {
      robotMessageEl.querySelector(".robot").textContent = data.response;
    })
    .catch((error) => {
      robotMessageEl.querySelector(".robot").textContent = "An error occurred.";
      console.error("Error:", error);
    });
};

// manage chat
function manageChat() {
  userMessage = inputEl.value.trim();
  if (!userMessage) return;
  inputEl.value = "";
  cardBodyEl.appendChild(messageEl(userMessage, "user"));

  const robotMessageEl = messageEl("Thinking...........", "chat-bot");
  cardBodyEl.append(robotMessageEl);

  chatGenerator(robotMessageEl);
}

// messages
const messageEl = (message, className) => {
  const chatEl = document.createElement("div");
  chatEl.classList.add("chat", className);
  let chatContent =
    className === "chat-bot"
      ? `<span class="user-icon"><i class="fa fa-robot"></i></span>
         <p class='robot'>${message}</p>`
      : `<span class="user-icon"><i class="fa fa-user"></i></span>
         <p>${message}</p>`;
  chatEl.innerHTML = chatContent;
  return chatEl;
};

btnEl.addEventListener("click", manageChat);
inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    manageChat();
  }
});