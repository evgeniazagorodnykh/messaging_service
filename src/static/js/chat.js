let selectedUserId = null;
let socket = null;

// Функция выхода из аккаунта
async function logout() {
    try {
        const response = await fetch('/auth/logout', {
            method: 'POST',
            credentials: 'include'
        });

        if (response.ok) {
            window.location.href = '/auth';
        } else {
            console.error('Ошибка при выходе');
        }
    } catch (error) {
        console.error('Ошибка при выполнении запроса:', error);
    }
}

// Функция выбора пользователя
async function selectUser(userId, userName, event) {
    selectedUserId = userId;
    document.getElementById('chatHeader').innerHTML = `<span>Чат с ${userName}</span><button class="logout-button" id="logoutButton">Выход</button>`;
    document.getElementById('messageInput').disabled = false;
    document.getElementById('sendButton').disabled = false;

    document.querySelectorAll('.user-item').forEach(item => item.classList.remove('active'));
    event.target.classList.add('active');

    const messagesContainer = document.getElementById('messages');
    messagesContainer.innerHTML = '';
    messagesContainer.style.display = 'block';

    document.getElementById('logoutButton').onclick = logout;

    const messages = await loadMessages(userId);

    messages.forEach(async (message) => {
        if (!message.read && message.sender_id == selectedUserId) {
            await markMessageAsRead(message.id);
        }
    });

    connectWebSocket();
}


// Функция для отметки сообщения как прочитанного
async function markMessageAsRead(messageId) {
    try {
        const response = await fetch(`/chat/messages/${messageId}/read`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            throw new Error(`Ошибка HTTP: ${response.status}`);
        }
    } catch (error) {
        console.error('Ошибка при отметке сообщения как прочитанного:', error);
    }
}


// Загрузка сообщений из REST API
async function loadMessages(userId) {
    try {
        const response = await fetch(`/chat/messages/${userId}`);
        
        if (!response.ok) {
            throw new Error(`Ошибка HTTP: ${response.status}`);
        }

        const messages = await response.json();

        if (!Array.isArray(messages)) {
            throw new Error('Полученные данные не являются массивом');
        }

        const messagesContainer = document.getElementById('messages');
        messagesContainer.innerHTML = messages.map(message =>
            createMessageElement(message.content, message.recipient_id)
        ).join('');

        return messages; // Возвращаем сообщения для дальнейшего использования
    } catch (error) {
        console.error('Ошибка загрузки сообщений:', error);
        return []; // Возвращаем пустой массив в случае ошибки
    }
}

// Подключение к WebSocket
function connectWebSocket() {
    if (socket) socket.close();

    socket = new WebSocket(`ws://${window.location.host}/chat/ws/${selectedUserId}`);

    socket.onopen = () => console.log('WebSocket соединение установлено');

    socket.onmessage = (event) => {
        const incomingMessage = JSON.parse(event.data);
        if (incomingMessage.recipient_id === selectedUserId) {
            addMessage(incomingMessage.content, incomingMessage.recipient_id);
        }
    };

    socket.onclose = () => console.log('WebSocket соединение закрыто');
}

// Отправка сообщения
async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();

    if (message && selectedUserId) {
        const payload = {receiver_id: selectedUserId, content: message};

        console.log(JSON.stringify(payload))
        try {
            const response = await fetch('/chat/messages/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response;
                console.error('Ошибка:', errorData);
                throw new Error(`Ошибка HTTP: ${response.status} - ${errorData.detail}`);
            }
        
            // socket.send(JSON.stringify(payload));
            addMessage(message, selectedUserId);
            messageInput.value = '';
        } catch (error) {
            console.error('Ошибка при отправке сообщения:', error);
        }
    }
}

// Добавление сообщения в чат
function addMessage(text, recipient_id) {
    const messagesContainer = document.getElementById('messages');
    messagesContainer.insertAdjacentHTML('beforeend', createMessageElement(text, recipient_id));
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Создание HTML элемента сообщения
function createMessageElement(text, recipient_id) {
    const messageClass = parseInt(selectedUserId, 10) === recipient_id ? 'my-message' : 'other-message';
    return `<div class="message ${messageClass}">${text}</div>`;
}

// Обновление списка пользователей
async function fetchUsers() {
    try {
        const response = await fetch('/users');
        const users = await response.json();
        const userList = document.getElementById('userList');
        userList.innerHTML = '';

        const favoriteElement = document.createElement('div');
        favoriteElement.classList.add('user-item');
        favoriteElement.setAttribute('data-user-id', currentUserId);
        favoriteElement.textContent = 'Избранное';
        userList.appendChild(favoriteElement);

        users.forEach(user => {
            if (user.id !== currentUserId) {
                const userElement = document.createElement('div');
                userElement.classList.add('user-item');
                userElement.setAttribute('data-user-id', user.id);
                userElement.textContent = user.username;
                userList.appendChild(userElement);
            }
        });

        document.querySelectorAll('.user-item').forEach(item => {
            console.log('User ID:', item.getAttribute('data-user-id'), 'Name:', item.textContent); // Вывод данных
            item.onclick = event => selectUser(item.getAttribute('data-user-id'), item.textContent, event);
        });

        // document.querySelectorAll('.user-item').forEach(item => {
        //     item.onclick = event => selectUser(item.getAttribute('data-user-id'), item.textContent, event);
        // });
    } catch (error) {
        console.error('Ошибка при загрузке списка пользователей:', error);
    }
}

document.addEventListener('DOMContentLoaded', fetchUsers);
setInterval(fetchUsers, 10000);

document.getElementById('sendButton').onclick = sendMessage;

document.getElementById('messageInput').onkeypress = async (e) => {
    if (e.key === 'Enter') {
        await sendMessage();
    }
};
