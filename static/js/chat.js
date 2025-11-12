const socket = io();

socket.on('connect', () => {
  console.log('Connecté au serveur');
});

socket.on('message', (data) => {
  const chatBox = document.getElementById('chat-box');
  const msg = document.createElement('p');
  msg.textContent = data;
  chatBox.appendChild(msg);
});

function sendMessage() {
  const input = document.getElementById('msg');
  const text = input.value;
  socket.send(text);
  input.value = '';
}


