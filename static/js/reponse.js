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

chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;

  // Ajouter le message utilisateur dans le chat
  addMessage(message, 'user');

  // Préparer les données à envoyer
  const formData = new FormData(chatForm);

  // Envoyer au serveur via fetch
  const response = await fetch(chatForm.action, {
    method: 'POST',
    body: formData
  });

  // Récupérer la réponse JSON du serveur
  const data = await response.json();

  // Afficher le message crypté côté bot
  if (data.coded_message) {
    addMessage(data.coded_message, 'bot');
  }

  chatInput.value = '';
});
