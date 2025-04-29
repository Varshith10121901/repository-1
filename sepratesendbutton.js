document.addEventListener("DOMContentLoaded", function () {
    const sendButton = document.querySelector(".send-button");
    const chatInput = document.querySelector(".chat-input");

    sendButton.addEventListener("click", function () {
        let userMessage = chatInput.value.trim();
        if (userMessage !== "") {
            sendMessage(userMessage);
            chatInput.value = "";
        }
    });

    function sendMessage(message) {
        fetch("http://127.0.0.1:5000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            displayMessage("Bot", data.response);
        })
        .catch(error => console.error("Error:", error));
    }

    function displayMessage(sender, text) {
        const chatBox = document.querySelector(".main-content");
        const messageElement = document.createElement("p");
        messageElement.textContent = `${sender}: ${text}`;
        chatBox.appendChild(messageElement);
    }
});
