let isDarkMode = false;

const clickSound = new Audio("assets/click.wav");
const waitingSound = new Audio("assets/waiting.wav");
waitingSound.loop = true;
waitingSound.volume = 0.5;

function toggleTheme() {
  clickSound.play();
  isDarkMode = !isDarkMode;
  document.body.className = isDarkMode ? 'dark-mode' : 'light-mode';
  localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
  document.getElementById('theme-toggle-icon').textContent = isDarkMode ? '🌙' : '☀️';
}

window.onload = () => {
  const theme = localStorage.getItem('theme');
  isDarkMode = theme === 'dark';
  document.body.className = isDarkMode ? 'dark-mode' : 'light-mode';
  document.getElementById('theme-toggle-icon').textContent = isDarkMode ? '🌙' : '☀️';

  // Attach click listeners to suggestion buttons
  const suggestionButtons = document.querySelectorAll(".suggestion");
  suggestionButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const suggestion = button.textContent.trim();
      if (suggestion) {
        sendSuggestion(suggestion);
      }
    });
  });
};

function login() {
  clickSound.play();
  const name = document.getElementById('username').value.trim();
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value.trim();

  if (!name || !email || !password) {
    alert("Please fill all fields.");
    return;
  }

  document.getElementById('login').style.display = 'none';
  document.getElementById('chat').style.display = 'block';
  document.getElementById('greeting').textContent = `Hello ${name}`;
  document.getElementById('suggestions').style.display = 'block';
}

function handleKeyPress(event) {
  if (event.key === 'Enter') {
    clickSound.play();
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    if (message) {
      sendMessage(message);
      input.value = '';
    }
  }
}

function sendMessage(message) {
  const chatBox = document.getElementById('chatBox');
  const username = document.getElementById('username').value.trim();

  const userMessage = `<div><strong>You:</strong> ${message}</div>`;
  chatBox.innerHTML += userMessage;
  chatBox.scrollTop = chatBox.scrollHeight;

  const thinkingDiv = document.getElementById("thinking");
  thinkingDiv.style.display = 'block';
  waitingSound.play();

  fetch('http://127.0.0.1:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: message, username: username })
  })
  .then(res => res.json())
  .then(data => {
    thinkingDiv.style.display = 'none';
    waitingSound.pause();
    waitingSound.currentTime = 0;

    const botReply = document.createElement('div');
    if (data.response) {
      botReply.innerHTML = `<strong>Mintor:</strong> ${data.response}`;
    } else if (data.error) {
      botReply.innerHTML = `<strong>Mintor:</strong> ⚠️ ${data.error}`;
    } else {
      botReply.innerHTML = `<strong>Mintor:</strong> ⚠️ Unexpected response.`;
    }
    chatBox.appendChild(botReply);
    chatBox.scrollTop = chatBox.scrollHeight;
  })
  .catch(() => {
    thinkingDiv.style.display = 'none';
    waitingSound.pause();
    waitingSound.currentTime = 0;

    const errorMessage = document.createElement('div');
    errorMessage.innerHTML = `<strong>Error:</strong> Could not connect to Mintor.`;
    chatBox.appendChild(errorMessage);
    chatBox.scrollTop = chatBox.scrollHeight;
  });
}

// Handle suggestion click as real message
function sendSuggestion(suggestion) {
  clickSound.play(); // Optional: play sound on click
  const chatBox = document.getElementById('chatBox');
  const username = document.getElementById('username').value.trim();

  // Show user message
  const userMessage = `<div><strong>You:</strong> ${suggestion}</div>`;
  chatBox.innerHTML += userMessage;
  chatBox.scrollTop = chatBox.scrollHeight;

  const thinkingDiv = document.getElementById("thinking");
  thinkingDiv.style.display = 'block';
  waitingSound.play();

  // Send to backend
  fetch('http://127.0.0.1:8000/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message: suggestion, username: username })
  })
  .then(res => res.json())
  .then(data => {
    thinkingDiv.style.display = 'none';
    waitingSound.pause();
    waitingSound.currentTime = 0;

    const botReply = document.createElement('div');
    if (data.response) {
      botReply.innerHTML = `<strong>Mintor:</strong> ${data.response}`;
    } else if (data.error) {
      botReply.innerHTML = `<strong>Mintor:</strong> ⚠️ ${data.error}`;
    } else {
      botReply.innerHTML = `<strong>Mintor:</strong> ⚠️ Unexpected response.`;
    }
    chatBox.appendChild(botReply);
    chatBox.scrollTop = chatBox.scrollHeight;
  })
  .catch(error => {
    thinkingDiv.style.display = 'none';
    waitingSound.pause();
    waitingSound.currentTime = 0;
    const errorMessage = document.createElement('div');
    errorMessage.innerHTML = `<strong>Error:</strong> Could not connect to Mintor.`;
    chatBox.appendChild(errorMessage);
    chatBox.scrollTop = chatBox.scrollHeight;
  });
}

