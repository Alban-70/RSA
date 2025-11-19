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

<<<<<<< HEAD
chatForm.addEventListener('submit', async (e) => {
=======

chatForm.addEventListener('submit', (e) => {
>>>>>>> 9373e396b6074b0092fc51bd437b9c335e7ea9f2
  e.preventDefault();
  
  if (!chatInput.value.trim()) return;

<<<<<<< HEAD
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
=======
  chatForm.submit();  // laisser Flask gérer l’historique
>>>>>>> 9373e396b6074b0092fc51bd437b9c335e7ea9f2
});
