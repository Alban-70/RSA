const chatContainer = document.getElementById('chat-container');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');

function addMessage(message, sender='user') {
  const bubble = document.createElement('div');
  bubble.classList.add('chat-bubble', sender);
  bubble.textContent = message;
  chatContainer.appendChild(bubble);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}


chatForm.addEventListener('submit', (e) => {
  e.preventDefault();
  
  if (!chatInput.value.trim()) return;

  chatForm.submit();  // laisser Flask gérer l’historique
});
