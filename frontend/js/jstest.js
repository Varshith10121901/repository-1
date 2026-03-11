fetch('/process_speech', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: chatInput.value })
})
.then(response => response.json())
.then(data => console.log(data.response))
.catch(error => console.error('Error:', error));
