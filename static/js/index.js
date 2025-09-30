$(document).ready(function() {
    const messagesContainer = $('#messages');
    const messageInput = $('#message-input');
    const sendButton = $('#send-btn');
    let isTyping = false;

    // Добавление сообщения в чат
    function addMessage(content, type) {
        const now = new Date();
        const timeString = now.toLocaleTimeString('ru-RU', {
            hour: '2-digit',
            minute: '2-digit'
        });

        const messageClass = type === 'user' ? 'user' : 'ai';
        const messageContentHTML = content.replace(/\n/g, '<br>');
        const messageHTML = `
            <div class="message ${messageClass}">
                <div class="message-content">
                    <p>${messageContentHTML}</p>
                    <span class="timestamp">${timeString}</span>
                </div>
            </div>
        `;

        messagesContainer.append(messageHTML);
        messagesContainer.scrollTop(messagesContainer[0].scrollHeight);
    }

    // Показать индикатор "Ассистент думает..."
    function showTypingIndicator() {
        isTyping = true;
        const indicatorHTML = `
            <div class="message ai" id="typing-indicator">
                <div class="typing-indicator">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span style="margin-left: 8px; color: #6b7280;">Ассистент думает...</span>
                </div>
            </div>
        `;

        messagesContainer.append(indicatorHTML);
        messagesContainer.scrollTop(messagesContainer[0].scrollHeight);
        sendButton.prop('disabled', true);
    }

    // Скрыть индикатор
    function hideTypingIndicator() {
        $('#typing-indicator').remove();
        isTyping = false;
        sendButton.prop('disabled', !messageInput.val().trim());
    }

    // Отправка сообщения
    function sendMessage() {
        const message = messageInput.val().trim();
        if (!message) return;

        // Добавить сообщение пользователя
        addMessage(message, 'user');
        messageInput.val('');
        sendButton.prop('disabled', true);

        // Показать индикатор
        showTypingIndicator();

        // AJAX запрос к API
        $.ajax({
            url: 'http://localhost:8000/completion',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ question: message }),
            success: function(data) {
                hideTypingIndicator();
                addMessage(data.answer, 'ai');
            },
            error: function() {
                hideTypingIndicator();
                addMessage('Извините, произошла ошибка при обращении к серверу.', 'ai');
            }
        });
    }

    // Обработчик кнопки отправки
    sendButton.click(sendMessage);

    // Обработчик нажатия Enter
    messageInput.on('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Отслеживание ввода для активации/деактивации кнопки
    messageInput.on('input', function() {
        sendButton.prop('disabled', !this.value.trim() && !isTyping);
    });
});