const socket = io();

socket.on('connect', () => {
  console.log('Connecté au serveur');
});

socket.on('message', (data) => {
  const chatContainer = document.getElementById('chat-container'); // ou chat-box
  const msg = document.createElement('div');
  msg.classList.add('chat-bubble', 'bot');
  msg.textContent = data;
  chatContainer.appendChild(msg);
});


function sendMessage() {
  const input = document.getElementById('msg');
  const text = input.value;
  socket.send(text);
  input.value = '';
}


