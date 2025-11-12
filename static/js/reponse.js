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

const codedMessageSpan = document.getElementById('encrypted_message');
const codedMessage = codedMessageSpan ? codedMessageSpan.textContent : null;

// Afficher le message crypté côté bot au chargement
if (codedMessage && codedMessage !== 'Aucun message crypté') {
  addMessage(codedMessage, 'bot');
}

chatForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;

  // Ajouter le message de l'utilisateur
  addMessage(message, 'user');

  // Réponse automatique simulée
  setTimeout(() => {
    if (codedMessage && codedMessage !== 'Aucun message crypté') {
      addMessage(codedMessage, 'bot');
    } else {
      addMessage(`Réponse automatique: ${message.split('').reverse().join('')}`, 'bot');
    }
  }, 600);

  chatInput.value = '';
});
