<!DOCTYPE html>
<html>
<head>
    <title>Basic Chatbot</title>
    <style>
        #chat-container {
            width: 400px;
            height: 500px;
            border: 1px solid #ccc;
            overflow-y: scroll;
            padding: 10px;
        }
        #user-input {
            width: 380px;
            padding: 5px;
        }
    </style>
</head>
<body>
    <div id="chat-container"></div>
    <input type="text" id="user-input" placeholder="Type your message...">
    <script>
        const chatContainer = document.getElementById('chat-container');
        const userInput = document.getElementById('user-input');

        function appendMessage(sender, message) {
            const messageDiv = document.createElement('div');
            messageDiv.textContent = `${sender}: ${message}`;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight; // Auto-scroll
        }

        function getBotResponse(userMessage) {
            // This is where you would integrate with an AI service like Gemini API or use some simple logic.
            // For this basic example, we'll use a simple hardcoded response.
            const responses = {
                'hello': 'Hi there!',
                'how are you?': 'I am doing well, thank you!',
                'what is your name?': 'I am a basic chatbot.',
                'default': 'I do not understand. Please try again.'
            };

            const lowerMessage = userMessage.toLowerCase();
            return responses[lowerMessage] || responses['default'];
        }

        userInput.addEventListener('keyup', function(event) {
            if (event.key === 'Enter') {
                const message = userInput.value;
                appendMessage('You', message);
                userInput.value = '';

                // Simulate bot response (replace with actual API call)
                setTimeout(() => {
                    const botResponse = getBotResponse(message);
                    appendMessage('Bot', botResponse);
                }, 500); // Simulate delay
            }
        });

        //Initial Bot message
        appendMessage('Bot', 'Hello, how can I help you?');
    </script>
</body>
</html>