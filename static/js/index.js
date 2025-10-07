$(document).ready(function() {
    const messagesContainer = $('#messages');
    const messageInput = $('#message-input');
    const sendButton = $('#send-btn');
    const modelOptions = $('#model-options');
    const defaultModel = "qwen3-coder";

    let isTyping = false;
    let last_data = null;
    let selectedModel = defaultModel;

    // Добавление сообщения в чат
    function addMessage(message, type) {
        const now = new Date();
        const timeString = now.toLocaleTimeString('ru-RU', {
            hour: '2-digit',
            minute: '2-digit'
        });

        const messageClass = type === 'user' ? 'user' : 'ai';
        const messageContentHTML = message.replace(/\n/g, '<br>');
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

    // Добавление интерактивного сообщения в чат
    function addInteractiveMessage(response, type) {
        const now = new Date();
        const timeString = now.toLocaleTimeString('ru-RU', {
            hour: '2-digit',
            minute: '2-digit'
        });

        id = response.id
        let data = null;
        if (typeof response.answer === "string") {
            json_str = response.answer.replaceAll('\n', '').replaceAll('\\"', '"')
            data = JSON.parse(json_str)
            response.answer = data;
        } else {
            data = response.answer;
        }

        last_data = response;

        const messageClass = type === 'user' ? 'user' : 'ai';

        let container = createTableContainer(id, data);
        const messageHTML = `
            <div class="message ${messageClass}">
                <div class="message-content">
                    ${container}
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

    function onChangeModel() {
        const text = modelOptions.val();
        if (text === '') {
            selectedModel = defaultModel;
        } else {
            selectedModel = text;
        }
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
            url: '/completion',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ question: message, model_name: selectedModel }),
            success: function(data) {
                hideTypingIndicator();
                console.log(data)
                if (!data.moderator_decision) {
                    addMessage(data.answer, 'ai');
                } else {
                    addInteractiveMessage(data, 'ai');
                }
            },
            error: function() {
                hideTypingIndicator();
                addMessage('Извините, произошла ошибка при обращении к серверу.', 'ai');
            }
        });
    }

    modelOptions.change(onChangeModel)

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

    function createTable(data) {
        const x_title = data.x.title;
        const x_values = data.x.values;
        const y_items = data.y;
        let table = `<table class="ai-table"><thead><tr><th>${x_title}</th>`;
        for (let i = 0; i < y_items.length; i++) {
            table += `<th>${y_items[i].title}</th>`;
        }
        table += '</tr></thead>';

        table += '<tbody>';
        for (let i = 0; i < x_values.length; i++) {
            table += `<tr><td>${x_values[i]}</td>`;
            for (let j = 0; j < y_items.length; j++) {
                table += `<td>${y_items[j].values[i]}</td>`;
            }
            table += '</tr>';
        }
        table += '</tbody></table>';
        return table;
    }

    function createTableContainer(id, data) {
        let table = createTable(data)
        return `
        <div class="ai-table-container" id="${id}">
            <div class="ai-table-header">
                <h3 class="ai-table-header-title">${data.title}</h3>
                <button class="ai-table-header-button">
                    <img src="/static/image/chart.png" alt="Построить график" style="width: 20px; height: 20px;">
                </button>
            </div>
            ${table}
        </div>`
    }

    $('#messages').on('click', '.ai-table-header-button', function() {
        let $container = $(this).closest('.ai-table-container');
        let id = $container.attr('id');
        const canvas_id = `canvas-${id}`
        $container.append(`<div class="chart-container"><canvas id="${canvas_id}"></canvas>`)
        const ctx = document.getElementById(canvas_id).getContext('2d');
        let chart_type = last_data.chart_type == null || last_data.chart_type == undefined
          ? "bar"
          : last_data.chart_type;
        if (chart_type === "time series") {
            chart_type = "line"
        }
        const data = last_data.answer;
        const labels = data.x.values;
        const datasets = [];
        for (let i=0; i<data.y.length; i++) {
            datasets.push({
                label: data.y[i].title,
                data: data.y[i].values,
                borderWidth: 1
            })
        }

        // Убираем предыдущий график, если он есть
        if (window.aiChart) {
            window.aiChart.destroy();
            window.aiChart = null;
        }
        // Создаём новый график
        window.aiChart = new Chart(ctx, {
            type: chart_type,
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: data.title
                    }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    });

    onChangeModel();

});