document.addEventListener('DOMContentLoaded', function () {
    // DOM Elements
    const chatInput = document.querySelector('.chat-input');
    const sendButton = document.querySelector('.send-button');
    const micButton = document.querySelector('.mic-button');
    const chatbox = document.querySelector('.chatbox');
    const welcomeMessage = document.querySelector('.welcome-message');
    const auraModeBtn = document.querySelector('.aura-mode-btn');

    // Check if elements exist before using them
    if (!chatInput || !sendButton || !chatbox) {
        console.error('Critical chat elements not found. Check your HTML structure.');
        return; // Stop execution if critical elements are missing
    }

    let auraMode = false;
    let isBotResponding = false; // Flag to track if the bot is currently responding

    // Speech Recognition Setup
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition;
    let isListening = false;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
    } else {
        console.error("Your browser doesn't support speech recognition. Try Chrome or Edge.");
        if (micButton) micButton.classList.add("disabled");
    }

    // Function to safely append messages to the chatbox
    function appendMessage(text, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);
        const textNode = document.createTextNode(text);
        messageElement.appendChild(textNode);
        chatbox.appendChild(messageElement);
        requestAnimationFrame(() => {
            chatbox.scrollTop = chatbox.scrollHeight;
        });
        if (welcomeMessage) {
            welcomeMessage.style.display = 'none';
        }
    }

    // Function to get bot response
    function getBotResponse(userMessage) {
        const responses = {
            'hello': 'Hey there! How can I help you?',
            'hi': 'Hello! What can I do for you today?',
            'how are you?': 'I\'m doing great! Thanks for asking.',
            'what is your name?': 'I\'m your friendly chatbot.',
            'tell me a joke': 'Why don\'t scientists trust atoms? Because they make up everything!',
            'tell me another joke': 'Sure, here\'s one: What do you call a lazy kangaroo? Pouch potato!',
            'tell me a funny story': 'I would, but they all involve punchlines I can\'t quite process yet. Maybe ask me again later?',
            'what time is it?': 'I don\'t have access to the current time, but you can check your device!',
            'what day is it?': 'I cant retrieve date information, but you can always check your device.',
            'what is the weather?': 'I\'m not able to provide weather information at the moment.',
            'who are you?': 'I\'m a chatbot designed to assist with your questions and provide helpful information.',
            'what can you do?': 'I can answer questions, tell jokes, and have conversations. I\'m still learning, though!',
            'thank you': 'You\'re welcome! Feel free to ask if you have any more questions.',
            'thanks': 'No problem! I\'m here to help.',
            'goodbye': 'Goodbye! Have a great day!',
            'bye': 'See you later!',
            'how does this work?': 'I process your messages and try to provide relevant responses. Think of me as a digital assistant!',
            'what is the meaning of life?': 'That\'s a big question! Many people believe the meaning of life is to find happiness and purpose.',
            'are you a robot?': 'I\'m a computer program, but I like to think I\'m a friendly one!',
            'what is the capital of France?': 'The capital of France is Paris.',
            'what is the capital of japan?': 'The capital of Japan is Tokyo.',
            'what is the capital of germany?': 'The capital of Germany is Berlin.',
            'what is the biggest planet?': 'Jupiter is the biggest planet in our solar system.',
            'what is the smallest planet?': 'Mercury is the smallest planet in our solar system.',
            'who is yuvaraj?': 'yuvaraj was a chutya beacuse he never pics the call.',
            'tell me a fact': 'Did you know honey never spoils',
            'tell me a riddle': 'What has an eye but cannot see A needle',
            'sing me a song': 'I can\'t sing, but I can recite some lyrics',
            'tell me a poem': 'Roses are red, violets are blue, I\'m a chatbot, how are you',
            'what is your favorite color': 'As a chatbot, I don\'t have preferences, but blue is a calming color',
            'what is your favorite food': 'I don\'t eat, but I hear pizza is popular',
            'how old are you': 'I don\'t have an age, I\'m a computer program',
            'what is your name': 'Hey AURA here ',
            'where are you from': 'I exist in the digital realm',
            'what is the weather in London': 'I can\'t provide real-time weather information',
            'what is the capital of Australia': 'The capital of Australia is Canberra',
            'what is the capital of Canada': 'The capital of Canada is Ottawa',
            'what is the capital of Brazil': 'The capital of Brazil is Brasília',
            'what is the largest ocean': 'The Pacific Ocean is the largest',
            'what is the longest river': 'The Nile is often considered the longest river',
            'who wrote hamlet': 'William Shakespeare wrote Hamlet',
            'who painted the mona lisa': 'Leonardo da Vinci painted the Mona Lisa',
            'what is pi': 'Pi is a mathematical constant approximately equal to 3.14159',
            'what is e': 'e is a mathematical constant approximately equal to 2.71828',
            'what is the speed of light': 'The speed of light in a vacuum is approximately 299,792,458 meters per second',
            'what is a black hole': 'A black hole is a region of spacetime where gravity is so strong that nothing, not even light, can escape it',
            'what is photosynthesis': 'Photosynthesis is the process by which plants convert light energy into chemical energy',
            'what is gravity': 'Gravity is the force that attracts a body toward the center of the earth, or toward any other physical body having mass',
            'what is a neuron': 'A neuron is a nerve cell that is the basic building block of the nervous system',
            'what is DNA': 'DNA is deoxyribonucleic acid, a molecule that carries the genetic instructions used in the growth, development, functioning and reproduction of all known living organisms',
            'what is the periodic table': 'The periodic table is a tabular display of the chemical elements, which are arranged by atomic number, electron configuration, and recurring chemical properties',
            'what is a calorie': 'A calorie is a unit of energy',
            'what is a light year': 'A light-year is a unit of distance equal to the distance light travels in one year',
            'what is a constellation': 'A constellation is a group of stars that forms a recognizable pattern',
            'what is a comet': 'A comet is an icy small Solar System body that, when passing close to the Sun, heats up and begins to outgas, displaying a visible atmosphere or coma, and sometimes also a tail',
            'what is a galaxy': 'A galaxy is a huge collection of gas, dust, and billions of stars and their solar systems, all held together by gravity',
            'what is a volcano': 'A volcano is a rupture in the crust of a planetary-mass object, such as Earth, that allows hot lava, volcanic ash, and gases to escape from a magma chamber below the surface',
            'what is a tsunami': 'A tsunami is a series of large waves caused by an underwater earthquake, volcanic eruption, or other disturbance',
            'what is a hurricane': 'A hurricane is a type of tropical cyclone, a severe storm that forms over warm ocean waters',
            'what is a desert': 'A desert is a barren area of landscape where little precipitation occurs and, consequently, living conditions are hostile for plant and animal life',
            'what is a rainforest': 'A rainforest is a forest with high rainfall',
            'what is an ecosystem': 'An ecosystem is a geographic area where plants, animals, and other organisms, as well as weather and landscape, work together to form a bubble of life',
            'what is evolution': 'Evolution is the process by which different kinds of living organisms are thought to have developed and diversified from earlier forms during the history of the earth',
            'what is a mammal': 'A mammal is a warm-blooded vertebrate animal of a class that is distinguished by the possession of hair or fur, females secrete milk for the nourishment of the young, and typically the young are born live',
            'what is a reptile': 'A reptile is a vertebrate animal of a class that includes snakes, lizards, crocodiles, turtles, and tortoises',
            'what is an amphibian': 'An amphibian is a cold-blooded vertebrate animal that is born in water and breathes with gills, and as an adult, lives on land and breathes with lungs',
            'what is an insect': 'An insect is a small arthropod animal that has six legs and generally one or two pairs of wings',
            'what is a fish': 'A fish is a limbless cold-blooded vertebrate animal with gills and fins and living wholly in water',
            'what is a bird': 'A bird is a warm-blooded vertebrate animal with feathers, wings, and a beak',
            'what is a plant': 'A plant is a living organism of the kind exemplified by trees, shrubs, herbs, grasses, ferns, and mosses, typically growing in a permanent site, absorbing water and inorganic substances through its roots, and manufacturing nutrients in its leaves by photosynthesis',
            'what is a fungus': 'A fungus is any member of the group of eukaryotic organisms that includes microorganisms such as yeasts and molds, as well as the more familiar mushrooms',
            'what is a bacteria': 'Bacteria are microscopic single-celled organisms that thrive in diverse environments',
            'what is a virus': 'A virus is a microscopic infectious agent capable of replicating only in living cells of other organisms',
            'what is an atom': 'An atom is the basic unit of a chemical element',
            'what is a molecule': 'A molecule is a group of atoms bonded together',
            'what is a cell': 'A cell is the basic structural and functional unit of all living organisms',
            'what is a tissue': 'A tissue is a group of cells that have similar structure and that function together as a unit',
            'what is an organ': 'An organ is a collection of tissues joined in a structural unit to serve a common function',
            'what is a system': 'A system is a set of connected things or parts forming a complex whole',
            'what is a human': 'A human is a bipedal primate mammal',
            'what is a dog': 'A dog is a domesticated carnivorous mammal that typically has a long snout, an acute sense of smell, and a barking, howling, or whining voice',
            'what is a cat': 'A cat is a small domesticated carnivorous mammal with soft fur, a short snout, and retractile claws',
            'what is a horse': 'A horse is a large plant-eating domesticated mammal with solid hoofs and a flowing mane and tail, used for riding, racing, or to carry and pull loads',
            'what is a cow': 'A cow is a domesticated bovine animal that is kept for its milk or meat',
            'what is a sheep': 'A sheep is a domesticated ruminant animal with a thick woolly fleece',
            'what is a pig': 'A pig is a domesticated omnivorous mammal with a stout body and a short upturned snout',
            'what is a chicken': 'A chicken is a domesticated fowl, especially a young one',
            'what is a duck': 'A duck is a waterbird with a broad flat beak, webbed feet, and a waddling gait',
            'what is a snake': 'A snake is a long, limbless reptile with no eyelids, a short tail, and a wide mouth that it can open extremely wide',
            'what is a spider': 'A spider is an eight-legged predatory arachnid with an unsegmented body divided into two sections and silk-spinning organs at the rear end',
            'default': 'Sorry, I didn\'t catch that. Could you rephrase?'
        };

        const lowerMessage = userMessage.toLowerCase().trim();
        return responses[lowerMessage] || responses['default'];
    }

    // Function to handle user input
    function handleUserInput() {
        if (isBotResponding) return;
        const userText = chatInput.value.trim();
        if (!userText) return;
        appendMessage(userText, 'user');
        chatInput.value = '';
        isBotResponding = true;
        setTimeout(() => {
            const botText = getBotResponse(userText);
            appendMessage(botText, 'bot');
            isBotResponding = false;
            chatInput.focus();
        }, 600);
    }

    // Event listeners
    sendButton.addEventListener('click', function (e) {
        e.preventDefault();
        handleUserInput();
    });

    chatInput.addEventListener('keypress', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            handleUserInput();
        }
    });

    // Voice recognition events
    if (recognition && micButton) {
        micButton.addEventListener('click', function (e) {
            e.preventDefault();
            if (isListening) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });

        recognition.onstart = function () {
            if (micButton) micButton.classList.add("active");
            isListening = true;
        };

        recognition.onresult = function (event) {
            let transcript = event.results[0][0].transcript;
            chatInput.value = transcript;
            handleUserInput();
        };

        recognition.onend = function () {
            if (micButton) micButton.classList.remove("active");
            isListening = false;
        };

        recognition.onerror = function (event) {
            console.error('Speech recognition error:', event.error);
            if (micButton) micButton.classList.remove("active");
            isListening = false;
        };
    }

    // AURA Mode toggle
    if (auraModeBtn) {
        auraModeBtn.addEventListener('click', function (e) {
            e.preventDefault();
            auraMode = !auraMode;
            if (auraMode) {
                document.body.style.background = 'linear-gradient(45deg, #000000, #1a0000)';
                auraModeBtn.textContent = 'NORMAL MODE';
                auraModeBtn.style.background = 'linear-gradient(45deg, rgb(212, 255, 0), rgb(255, 255, 0))';
                auraModeBtn.style.boxShadow = '0 0 15px rgb(255, 255, 0), 0 0 25px rgb(255, 255, 0)';
                auraModeBtn.style.border = '2px solid rgb(255, 255, 0)';
            } else {
                document.body.style.background = 'black';
                auraModeBtn.textContent = 'AURA MODE';
                auraModeBtn.style.background = 'linear-gradient(45deg, #ff7e00, #ff4d00)';
                auraModeBtn.style.boxShadow = '0 0 15px #ff4500, 0 0 25px #ff7700';
                auraModeBtn.style.border = '2px solid #ff4500';
            }
        });
    }

    chatInput.focus();
    console.log("Chat interface initialized successfully!");
});