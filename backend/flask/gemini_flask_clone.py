<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AURA AI - Advanced Intelligence Assistant</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/4.0.2/marked.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.5/FileSaver.min.js"></script>
    <style>
        .gradient-bg {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
        }
        .glass-effect {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .chat-bubble {
            border-radius: 18px;
            padding: 12px 16px;
            margin: 8px 0;
            max-width: 80%;
        }
        .user-bubble {
            background-color: #8b5cf6;
            color: white;
            margin-left: auto;
            border-top-right-radius: 4px;
        }
        .ai-bubble {
            background-color: #f3f4f6;
            color: #1f2937;
            margin-right: auto;
            border-top-left-radius: 4px;
        }
        .menu-item {
            transition: all 0.3s ease;
        }
        .menu-item:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
        .menu-item.active {
            background-color: rgba(255, 255, 255, 0.2);
            border-left: 4px solid white;
        }
        .typing-indicator {
            display: flex;
            align-items: center;
        }
        .typing-indicator span {
            height: 8px;
            width: 8px;
            margin: 0 2px;
            background-color: #8b5cf6;
            border-radius: 50%;
            display: inline-block;
            animation: typing 1.5s infinite ease-in-out;
        }
        .typing-indicator span:nth-child(2) {
            animation-delay: 0.2s;
        }
        .typing-indicator span:nth-child(3) {
            animation-delay: 0.4s;
        }
        @keyframes typing {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        .file-drag {
            border: 2px dashed #d1d5db;
            border-radius: 8px;
            padding: 2rem;
            text-align: center;
            transition: all 0.3s ease;
        }
        .file-drag.active {
            border-color: #8b5cf6;
            background-color: rgba(139, 92, 246, 0.1);
        }
        .file-preview {
            max-height: 200px;
            max-width: 100%;
            object-fit: contain;
            margin-top: 1rem;
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .pulse {
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
    </style>
</head>
<body class="bg-gray-100 font-sans min-h-screen">
    <div class="flex h-screen overflow-hidden">
        <!-- Sidebar -->
        <div class="gradient-bg text-white w-64 flex-shrink-0 flex flex-col">
            <div class="p-4 flex items-center justify-center h-16 border-b border-purple-500">
                <h1 class="text-2xl font-bold">AURA AI</h1>
            </div>
            <div class="p-4">
                <p class="text-sm opacity-70">Advanced Intelligence Assistant</p>
            </div>
            <nav class="flex-1">
                <ul>
                    <li>
                        <button onclick="showSection('chatbot')" class="menu-item active w-full text-left py-3 px-4 flex items-center">
                            <i class="fas fa-comments mr-3"></i> Chatbot
                        </button>
                    </li>
                    <li>
                        <button onclick="showSection('imageanalysis')" class="menu-item w-full text-left py-3 px-4 flex items-center">
                            <i class="fas fa-image mr-3"></i> Image Analysis
                        </button>
                    </li>
                    <li>
                        <button onclick="showSection('documentanalysis')" class="menu-item w-full text-left py-3 px-4 flex items-center">
                            <i class="fas fa-file-alt mr-3"></i> Document Analysis
                        </button>
                    </li>
                </ul>
            </nav>
            <div class="p-4 text-sm opacity-70">
                <p>Powered by Gemini AI</p>
                <p>© 2025 AURA AI</p>
            </div>
        </div>

        <!-- Main Content -->
        <div class="flex-1 flex flex-col overflow-hidden">
            <!-- Top bar -->
            <div class="bg-white h-16 border-b flex items-center px-6 justify-between">
                <div class="flex items-center">
                    <h2 class="text-xl font-semibold text-gray-800" id="current-section-title">Chatbot</h2>
                </div>
                <div class="flex items-center space-x-2">
                    <button class="bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-sm font-medium flex items-center">
                        <i class="fas fa-lightbulb mr-1"></i> Tips
                    </button>
                    <button class="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm font-medium flex items-center">
                        <i class="fas fa-cog mr-1"></i> Settings
                    </button>
                </div>
            </div>

            <!-- Content Sections -->
            <div class="flex-1 overflow-hidden">
                <!-- Chatbot Section -->
                <div id="chatbot" class="h-full flex flex-col">
                    <div id="chat-messages" class="flex-1 p-4 overflow-y-auto flex flex-col space-y-4">
                        <div class="ai-bubble">
                            <p>Hello! I'm AURA AI, your personal AI assistant. How can I help you today?</p>
                        </div>
                    </div>
                    <div class="p-4 border-t bg-white">
                        <div class="flex items-center">
                            <input type="text" id="chat-input" placeholder="Ask me anything..." class="flex-1 border rounded-l-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-transparent">
                            <button id="chat-send" class="bg-purple-600 text-white rounded-r-lg px-4 py-2 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-600 focus:ring-opacity-50">
                                <i class="fas fa-paper-plane"></i>
                            </button>
                        </div>
                        <div class="flex items-center mt-2 text-sm text-gray-500">
                            <i class="fas fa-info-circle mr-1"></i>
                            <span>Powered by Gemini 2.0 Flash</span>
                        </div>
                    </div>
                </div>

                <!-- Image Analysis Section -->
                <div id="imageanalysis" class="h-full flex flex-col hidden">
                    <div class="flex-1 p-6 overflow-y-auto">
                        <div class="max-w-3xl mx-auto">
                            <div class="bg-white rounded-lg shadow-md p-6 mb-6">
                                <h3 class="text-lg font-semibold mb-4">Upload Images for Analysis</h3>
                                <div id="image-drop-area" class="file-drag cursor-pointer">
                                    <i class="fas fa-cloud-upload-alt text-4xl text-gray-400 mb-2"></i>
                                    <p class="mb-1">Drag & drop images here or click to browse</p>
                                    <p class="text-sm text-gray-500">Supports JPG, PNG, and WEBP (max 2 images)</p>
                                    <input type="file" id="image-upload" accept="image/*" multiple class="hidden">
                                </div>
                                <div id="image-preview-container" class="mt-4 grid grid-cols-2 gap-4 hidden">
                                    <!-- Images will be shown here -->
                                </div>
                            </div>
                            
                            <div class="bg-white rounded-lg shadow-md p-6">
                                <div class="mb-4">
                                    <label for="image-prompt" class="block text-sm font-medium text-gray-700 mb-1">Analysis Prompt</label>
                                    <textarea id="image-prompt" rows="3" class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600" placeholder="Write a prompt about what you want to know from these images...">Describe what you see in these images in detail.</textarea>
                                </div>
                                <div class="flex justify-end">
                                    <button id="analyze-images" class="bg-purple-600 text-white px-5 py-2 rounded-lg hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-600 flex items-center">
                                        <i class="fas fa-magic mr-2"></i> Analyze Images
                                    </button>
                                </div>
                            </div>
                            
                            <div id="image-result" class="bg-white rounded-lg shadow-md p-6 mt-6 hidden">
                                <h3 class="text-lg font-semibold mb-4">Analysis Results</h3>
                                <div id="image-analysis-result" class="prose max-w-none"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Document Analysis Section -->
                <div id="documentanalysis" class="h-full flex flex-col hidden">
                    <div class="flex-1 p-6 overflow-y-auto">
                        <div class="max-w-3xl mx-auto">
                            <div class="bg-white rounded-lg shadow-md p-6 mb-6">
                                <h3 class="text-lg font-semibold mb-4">Upload Document for Analysis</h3>
                                <div id="document-drop-area" class="file-drag cursor-pointer">
                                    <i class="fas fa-file-upload text-4xl text-gray-400 mb-2"></i>
                                    <p class="mb-1">Drag & drop your document here or click to browse</p>
                                    <p class="text-sm text-gray-500">Supports PDF documents (max 10MB)</p>
                                    <input type="file" id="document-upload" accept=".pdf" class="hidden">
                                </div>
                                <div id="document-preview" class="mt-4 hidden">
                                    <div class="flex items-center p-3 bg-gray-50 rounded-lg">
                                        <i class="fas fa-file-pdf text-red-500 text-2xl mr-3"></i>
                                        <div class="flex-1">
                                            <p id="document-name" class="font-medium"></p>
                                            <p id="document-size" class="text-sm text-gray-500"></p>
                                        </div>
                                        <button id="remove-document" class="text-gray-400 hover:text-gray-600">
                                            <i class="fas fa-times"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="bg-white rounded-lg shadow-md p-6">
                                <div class="mb-4">
                                    <label for="document-prompt" class="block text-sm font-medium text-gray-700 mb-1">Analysis Prompt</label>
                                    <textarea id="document-prompt" rows="3" class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600" placeholder="What would you like to know about this document?">Summarize this document</textarea>
                                </div>
                                <div class="flex justify-end">
                                    <button id="analyze-document" class="bg-purple-600 text-white px-5 py-2 rounded-lg hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-600 flex items-center">
                                        <i class="fas fa-search-plus mr-2"></i> Analyze Document
                                    </button>
                                </div>
                            </div>
                            
                            <div id="document-result" class="bg-white rounded-lg shadow-md p-6 mt-6 hidden">
                                <h3 class="text-lg font-semibold mb-4">Document Analysis</h3>
                                <div id="document-analysis-result" class="prose max-w-none"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // API Key
        const API_KEY = "AIzaSyCvyxvEZcBh2x8VRFUCFDZqeoIMCWjwYzo";
        
        // DOM Elements
        const chatInput = document.getElementById('chat-input');
        const chatSend = document.getElementById('chat-send');
        const chatMessages = document.getElementById('chat-messages');
        
        // Track active section
        let activeSection = 'chatbot';
        const sections = ['chatbot', 'imageanalysis', 'documentanalysis'];
        const sectionTitles = {
            'chatbot': 'Chatbot',
            'imageanalysis': 'Image Analysis',
            'documentanalysis': 'Document Analysis'
        };

        // Show selected section and update navigation
        function showSection(sectionId) {
            // Hide all sections
            sections.forEach(id => {
                document.getElementById(id).classList.add('hidden');
                document.querySelector(`button[onclick="showSection('${id}')"]`).classList.remove('active');
            });
            
            // Show selected section
            document.getElementById(sectionId).classList.remove('hidden');
            document.querySelector(`button[onclick="showSection('${sectionId}')"]`).classList.add('active');
            document.getElementById('current-section-title').textContent = sectionTitles[sectionId];
            
            activeSection = sectionId;
        }

        // Initialize Google AI client
        async function initGoogleAI() {
            return window.googleGenAI = {
                apiKey: API_KEY,
                async generateContent(params) {
                    try {
                        const response = await fetch("https://generativelanguage.googleapis.com/v1beta/models/" + params.model + ":generateContent?key=" + this.apiKey, {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json",
                            },
                            body: JSON.stringify(params),
                        });
                        
                        const data = await response.json();
                        if (data.error) {
                            throw new Error(data.error.message || "Error generating content");
                        }
                        
                        return {
                            text: data.candidates[0].content.parts[0].text,
                            response: {
                                text: () => data.candidates[0].content.parts[0].text
                            }
                        };
                    } catch (error) {
                        console.error("Error generating content:", error);
                        return { 
                            text: "Sorry, there was an error processing your request. Please try again." 
                        };
                    }
                },
                async generateContentWithImage(prompt, imageData) {
                    try {
                        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent?key=${this.apiKey}`, {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json",
                            },
                            body: JSON.stringify({
                                contents: [
                                    {
                                        parts: [
                                            { text: prompt },
                                            ...imageData.map(img => ({
                                                inline_data: {
                                                    mime_type: img.mimeType,
                                                    data: img.data.split(',')[1] // Remove data URL prefix
                                                }
                                            }))
                                        ]
                                    }
                                ],
                                generationConfig: {
                                    temperature: 0.4,
                                    topK: 32,
                                    topP: 1,
                                    maxOutputTokens: 2048,
                                }
                            }),
                        });
                        
                        const data = await response.json();
                        if (data.error) {
                            throw new Error(data.error.message || "Error analyzing images");
                        }
                        
                        return data.candidates[0].content.parts[0].text;
                    } catch (error) {
                        console.error("Image analysis error:", error);
                        return "Sorry, there was an error analyzing the images. Please try again.";
                    }
                },
                async generateContentWithDocument(prompt, documentData) {
                    try {
                        // For PDF documents, we need to extract the text using a PDF library
                        // In a real app, this would be done server-side
                        // For now, we'll simulate with the filename and prompt
                        
                        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${this.apiKey}`, {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json",
                            },
                            body: JSON.stringify({
                                contents: [
                                    {
                                        parts: [
                                            { 
                                                text: `Document filename: ${documentData.filename}\n\n` +
                                                      `Document size: ${documentData.size}\n\n` +
                                                      `User prompt: ${prompt}\n\n` +
                                                      `Please analyze this document based on the information provided.`
                                            }
                                        ]
                                    }
                                ],
                                generationConfig: {
                                    temperature: 0.2,
                                    topK: 32,
                                    topP: 1,
                                    maxOutputTokens: 2048,
                                }
                            }),
                        });
                        
                        const data = await response.json();
                        if (data.error) {
                            throw new Error(data.error.message || "Error analyzing document");
                        }
                        
                        return data.candidates[0].content.parts[0].text;
                    } catch (error) {
                        console.error("Document analysis error:", error);
                        return "Sorry, there was an error analyzing the document. Please try again.";
                    }
                }
            };
        }

        // Initialize the AI client when the page loads
        let googleAI;
        window.onload = async function() {
            googleAI = await initGoogleAI();
            
            // Setup event listeners
            setupChatbot();
            setupImageAnalysis();
            setupDocumentAnalysis();
        };

        // CHATBOT FUNCTIONALITY
        function setupChatbot() {
            // Send message on button click
            chatSend.addEventListener('click', sendChatMessage);
            
            // Send message on Enter key
            chatInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendChatMessage();
                }
            });
        }

        async function sendChatMessage() {
            const message = chatInput.value.trim();
            if (!message) return;
            
            // Add user message to chat
            addMessageToChat('user', message);
            
            // Clear input
            chatInput.value = '';
            
            // Show typing indicator
            const typingIndicator = document.createElement('div');
            typingIndicator.className = 'ai-bubble typing-indicator';
            typingIndicator.innerHTML = '<span></span><span></span><span></span>';
            chatMessages.appendChild(typingIndicator);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            try {
                // Send to API
                const response = await googleAI.generateContent({
                    model: "gemini-1.5-flash",
                    contents: [{ role: "user", parts: [{ text: message }] }]
                });
                
                // Remove typing indicator
                chatMessages.removeChild(typingIndicator);
                
                // Add AI response to chat
                addMessageToChat('ai', response.text);
            } catch (error) {
                // Remove typing indicator
                chatMessages.removeChild(typingIndicator);
                
                // Add error message
                addMessageToChat('ai', "Sorry, I encountered an error while processing your request. Please try again.");
                console.error("Chat error:", error);
            }
        }

        function addMessageToChat(role, text) {
            const messageDiv = document.createElement('div');
            messageDiv.className = role === 'user' ? 'user-bubble chat-bubble' : 'ai-bubble chat-bubble';
            
            // Process markdown in AI responses
            if (role === 'ai') {
                messageDiv.innerHTML = marked.parse(text);
                // Apply syntax highlighting
                messageDiv.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightElement(block);
                });
            } else {
                messageDiv.textContent = text;
            }
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        // IMAGE ANALYSIS FUNCTIONALITY
        function setupImageAnalysis() {
            const dropArea = document.getElementById('image-drop-area');
            const fileInput = document.getElementById('image-upload');
            const previewContainer = document.getElementById('image-preview-container');
            const analyzeBtn = document.getElementById('analyze-images');
            
            // Open file dialog when clicking on drop area
            dropArea.addEventListener('click', () => fileInput.click());
            
            // Handle drag events
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                dropArea.addEventListener(eventName, preventDefaults, false);
            });
            
            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }
            
            // Handle drag visual feedback
            ['dragenter', 'dragover'].forEach(eventName => {
                dropArea.addEventListener(eventName, () => {
                    dropArea.classList.add('active');
                });
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                dropArea.addEventListener(eventName, () => {
                    dropArea.classList.remove('active');
                });
            });
            
            // Handle dropped files
            dropArea.addEventListener('drop', (e) => {
                const dt = e.dataTransfer;
                const files = dt.files;
                handleImageFiles(files);
            });
            
            // Handle selected files
            fileInput.addEventListener('change', function() {
                handleImageFiles(this.files);
            });
            
            // Process selected images
            function handleImageFiles(files) {
                // Clear preview container
                previewContainer.innerHTML = '';
                
                // Limit to 2 images
                const imagesToProcess = Array.from(files).slice(0, 2);
                
                if (imagesToProcess.length > 0) {
                    previewContainer.classList.remove('hidden');
                    
                    imagesToProcess.forEach(file => {
                        if (!file.type.match('image.*')) return;
                        
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            const imgContainer = document.createElement('div');
                            imgContainer.className = 'relative';
                            
                            const img = document.createElement('img');
                            img.src = e.target.result;
                            img.className = 'file-preview w-full h-48 object-cover rounded-lg';
                            img.dataset.file = file.name;
                            img.dataset.base64 = e.target.result;
                            img.dataset.mimeType = file.type;
                            
                            imgContainer.appendChild(img);
                            previewContainer.appendChild(imgContainer);
                        };
                        
                        reader.readAsDataURL(file);
                    });
                } else {
                    previewContainer.classList.add('hidden');
                }
            }
            
            // Analyze images button
            analyzeBtn.addEventListener('click', async function() {
                const images = previewContainer.querySelectorAll('img');
                if (images.length === 0) {
                    alert('Please upload at least one image to analyze.');
                    return;
                }
                
                const prompt = document.getElementById('image-prompt').value.trim() || 'Describe what you see in these images in detail.';
                analyzeBtn.disabled = true;
                analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Analyzing...';
                
                const imageResults = document.getElementById('image-result');
                const imageAnalysisResult = document.getElementById('image-analysis-result');
                
                try {
                    // Prepare image data for API
                    const imageData = Array.from(images).map(img => ({
                        data: img.dataset.base64,
                        mimeType: img.dataset.mimeType
                    }));
                    
                    // Send images to Gemini API
                    const result = await googleAI.generateContentWithImage(prompt, imageData);
                    
                    imageResults.classList.remove('hidden');
                    imageAnalysisResult.innerHTML = marked.parse(result);
                    
                    // Apply syntax highlighting if needed
                    imageAnalysisResult.querySelectorAll('pre code').forEach((block) => {
                        hljs.highlightElement(block);
                    });
                } catch (error) {
                    imageResults.classList.remove('hidden');
                    imageAnalysisResult.innerHTML = "Sorry, there was an error analyzing the images. The API may have rejected the request due to content policies or technical issues.";
                    console.error("Image analysis error:", error);
                } finally {
                    analyzeBtn.disabled = false;
                    analyzeBtn.innerHTML = '<i class="fas fa-magic mr-2"></i> Analyze Images';
                }
            });
        }

        // DOCUMENT ANALYSIS FUNCTIONALITY
        function setupDocumentAnalysis() {
            const dropArea = document.getElementById('document-drop-area');
            const fileInput = document.getElementById('document-upload');
            const documentPreview = document.getElementById('document-preview');
            const documentName = document.getElementById('document-name');
            const documentSize = document.getElementById('document-size');
            const removeDocument = document.getElementById('remove-document');
            const analyzeBtn = document.getElementById('analyze-document');
            
            // Open file dialog when clicking on drop area
            dropArea.addEventListener('click', () => fileInput.click());
            
            // Handle drag events
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                dropArea.addEventListener(eventName, preventDefaults, false);
            });
            
            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }
            
            // Handle drag visual feedback
            ['dragenter', 'dragover'].forEach(eventName => {
                dropArea.addEventListener(eventName, () => {
                    dropArea.classList.add('active');
                });
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                dropArea.addEventListener(eventName, () => {
                    dropArea.classList.remove('active');
                });
            });
            
            // Handle dropped files
            dropArea.addEventListener('drop', (e) => {
                const dt = e.dataTransfer;
                const files = dt.files;
                if (files.length > 0) handleDocumentFile(files[0]);
            });
            
            // Handle selected files
            fileInput.addEventListener('change', function() {
                if (this.files.length > 0) handleDocumentFile(this.files[0]);
            });
            
            // Process selected document
            function handleDocumentFile(file) {
                if (file.type !== 'application/pdf') {
                    alert('Please upload a PDF document.');
                    return;
                }
                
                if (file.size > 10 * 1024 * 1024) { // 10MB limit
                    alert('File size exceeds the 10MB limit. Please upload a smaller file.');
                    return;
                }
                
                documentName.textContent = file.name;
                documentSize.textContent = formatFileSize(file.size);
                documentPreview.classList.remove('hidden');
                
                // Store file reference for later use
                documentPreview.dataset.file = file.name;
                documentPreview.dataset.size = formatFileSize(file.size);
                
                // Store file content as base64 for API
                const reader = new FileReader();
                reader.onload = function(e) {
                    documentPreview.dataset.base64 = e.target.result;
                };
                reader.readAsDataURL(file);
            }
            
            // Format file size
            function formatFileSize(bytes) {