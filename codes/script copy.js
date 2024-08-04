const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('sendButton');
const recordButton = document.getElementById('recordButton');
const stopButton = document.getElementById('stopButton');

let mediaRecorder = null;
let audioChunks = [];

recordButton.addEventListener('click', async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.addEventListener('dataavailable', event => {
            audioChunks.push(event.data);
        });

        mediaRecorder.start();
        recordButton.disabled = true;
        stopButton.disabled = false;

        // Attach the stop event listener after the recorder has started
        mediaRecorder.addEventListener('stop', handleStopRecording); 
    } catch (err) {
        console.error('Error accessing microphone:', err);
    }
});

stopButton.addEventListener('click', () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        recordButton.disabled = false;
        stopButton.disabled = true;
    }
});

async function handleStopRecording() {
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    audioChunks = [];

    // Convert audioBlob to ArrayBuffer
    const arrayBuffer = await new Response(audioBlob).arrayBuffer();

    sendAudioMessage(arrayBuffer); // Pass ArrayBuffer instead of Blob
}

sendButton.addEventListener('click', () => {
    const messageText = messageInput.value.trim();
    if (messageText) {
        sendMessage(messageText);
        messageInput.value = '';
    }
});

function sendMessage(message) {
    displayMessage(message, 'outgoing');

    const formData = new FormData();
    formData.append('ask', message);

    fetch('http://localhost:8888/hear', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const [responseText, sources] = data; 
        displayMessage(responseText, 'incoming');
        
        // Format and display sources as hyperlinks
        if (sources && sources.length > 0) {
            const formattedSources = sources
                .map(source => `<a href="${source}" target="_blank">${source}</a>`)
                .join('<br>');
            displayMessage(`Sources:\n${formattedSources}`, 'incoming');
        }
    })
    .catch(error => console.error('API Error:', error));
}

async function sendAudioMessage(arrayBuffer) {
    displayAudioMessage(arrayBuffer, 'outgoing');
    
    const audioBlob = new Blob([arrayBuffer], { type: 'audio/webm' }); 
    const audioFile = new File([audioBlob], 'recorded_audio.webm', { type: 'audio/webm' });

    const formData = new FormData();
    formData.append('audioForm', audioFile);  // Send the File object

    try {
        const response = await fetch('http://localhost:8888/hear', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        const [responseText, sources] = data; 
        displayMessage(responseText, 'incoming');

        if (sources && sources.length > 0) {
            const formattedSources = sources.map(source => `<a href="${source}" target="_blank">${source}</a>`).join('<br>');
            displayMessage(`Sources:\n${formattedSources}`, 'incoming');
        }
    } catch (error) {
        console.error('API Error:', error);
    }
}


function displayMessage(text, type) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', type);

    // // Create a <pre> element to preserve formatting (Option 1)
    // const preElement = document.createElement('pre'); 
    // preElement.textContent = text;
    // messageElement.appendChild(preElement);

    // OR Replace with HTML elements (Option 2 - more flexible styling)
    const formattedText = text.replace(/\n/g, '<br>').replace(/\t/g, '&nbsp;&nbsp;&nbsp;&nbsp;');
    messageElement.innerHTML = formattedText; 

    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight; 
}

function displayAudioMessage(arrayBuffer, type) { // Accept ArrayBuffer
    // Convert the ArrayBuffer back to a Blob
    const audioBlob = new Blob([arrayBuffer], { type: 'audio/webm' }); 

    const messageElement = document.createElement('div');
    messageElement.classList.add('message', type);

    const audioElement = document.createElement('audio');
    audioElement.src = URL.createObjectURL(audioBlob); // Use the Blob
    audioElement.controls = true;
    messageElement.appendChild(audioElement);

    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight; 
}
