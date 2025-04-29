<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini Code Analyzer</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #4285f4;
            --secondary-color: #1a73e8;
            --accent-color: #34a853;
            --text-color: #202124;
            --bg-color: #f8f9fa;
            --card-bg: #ffffff;
            --border-radius: 8px;
            --box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            --highlight-color: #e8f0fe;
            --error-color: #ea4335;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Google Sans', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px 0;
        }

        .logo {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 15px;
        }

        .logo i {
            font-size: 36px;
            margin-right: 12px;
            color: var(--primary-color);
        }

        .logo h1 {
            font-size: 28px;
            font-weight: 500;
            color: var(--text-color);
        }

        header p {
            color: #5f6368;
            max-width: 700px;
            margin: 0 auto;
        }

        .api-key-container {
            background-color: var(--card-bg);
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            padding: 20px;
            margin-bottom: 30px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
        }

        input[type="text"], 
        textarea {
            width: 100%;
            padding: 12px 15px;
            border: 1px solid #dadce0;
            border-radius: var(--border-radius);
            font-size: 16px;
            transition: border 0.3s;
        }

        input[type="text"]:focus, 
        textarea:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 2px rgba(66, 133, 244, 0.2);
        }

        .submit-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        button {
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: var(--border-radius);
            padding: 12px 24px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: background-color 0.3s;
            display: flex;
            align-items: center;
        }

        button:hover {
            background-color: var(--secondary-color);
        }

        button i {
            margin-right: 8px;
        }

        .api-status {
            display: inline-flex;
            align-items: center;
            margin-left: 15px;
            font-size: 14px;
        }

        .status-indicator {
            height: 10px;
            width: 10px;
            border-radius: 50%;
            background-color: #dadce0;
            margin-right: 8px;
        }

        .active {
            background-color: var(--accent-color);
        }

        .error {
            background-color: var(--error-color);
        }

        .code-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }

        @media (max-width: 768px) {
            .code-container {
                grid-template-columns: 1fr;
            }
        }

        .code-input, 
        .analysis-output {
            background-color: var(--card-bg);
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            padding: 20px;
            height: 500px;
            display: flex;
            flex-direction: column;
        }

        .code-input h2, 
        .analysis-output h2 {
            font-size: 18px;
            margin-bottom: 15px;
            color: var(--text-color);
            font-weight: 500;
            display: flex;
            align-items: center;
        }

        .code-input h2 i, 
        .analysis-output h2 i {
            margin-right: 10px;
            color: var(--primary-color);
        }

        textarea {
            flex-grow: 1;
            resize: none;
            font-family: 'Courier New', monospace;
            line-height: 1.5;
            padding: 15px;
        }

        .analysis-content {
            flex-grow: 1;
            overflow-y: auto;
            background-color: #f5f5f5;
            border-radius: var(--border-radius);
            padding: 15px;
            font-size: 15px;
            white-space: pre-wrap;
        }

        .loading {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
        }

        .spinner {
            border: 4px solid rgba(0, 0, 0, 0.1);
            border-radius: 50%;
            border-top: 4px solid var(--primary-color);
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin-bottom: 15px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .settings-panel {
            background-color: var(--card-bg);
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            padding: 20px;
            margin-bottom: 30px;
        }

        .settings-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            cursor: pointer;
        }

        .settings-header h2 {
            font-size: 18px;
            font-weight: 500;
            display: flex;
            align-items: center;
        }

        .settings-header h2 i {
            margin-right: 10px;
            color: var(--primary-color);
        }

        .settings-content {
            display: none;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
            padding-top: 15px;
            border-top: 1px solid #dadce0;
        }

        .settings-option {
            margin-bottom: 15px;
        }

        select {
            width: 100%;
            padding: 10px;
            border: 1px solid #dadce0;
            border-radius: var(--border-radius);
            background-color: white;
            font-size: 15px;
        }

        footer {
            text-align: center;
            padding: 20px 0;
            color: #5f6368;
            font-size: 14px;
            margin-top: 30px;
        }

        .error-message {
            color: var(--error-color);
            font-size: 14px;
            margin-top: 5px;
            display: none;
        }

        .highlight {
            background-color: var(--highlight-color);
            padding: 2px 0;
        }

        .analysis-section {
            margin-bottom: 15px;
        }

        .section-title {
            font-weight: bold;
            margin-bottom: 5px;
            color: var(--secondary-color);
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">
                <i class="fas fa-code"></i>
                <h1>Gemini Code Analyzer</h1>
            </div>
            <p>Use Google's Gemini AI to analyze, explain, and improve your code with advanced suggestions and insights.</p>
        </header>

        <div class="api-key-container">
            <div class="form-group">
                <label for="api-key">Gemini API Key</label>
                <input type="text" id="api-key" placeholder="Enter your Gemini API key...">
                <div class="error-message" id="api-key-error">Please enter a valid API key</div>
            </div>
            <div class="submit-container">
                <button id="verify-api-key"><i class="fas fa-key"></i>Verify API Key</button>
                <div class="api-status">
                    <span class="status-indicator" id="status-indicator"></span>
                    <span id="status-text">Not verified</span>
                </div>
            </div>
        </div>

        <div class="settings-panel">
            <div class="settings-header" id="settings-toggle">
                <h2><i class="fas fa-cog"></i>Analysis Settings</h2>
                <i class="fas fa-chevron-down"></i>
            </div>
            <div class="settings-content" id="settings-content">
                <div class="settings-option">
                    <label for="analysis-type">Analysis Type</label>
                    <select id="analysis-type">
                        <option value="comprehensive">Comprehensive Analysis</option>
                        <option value="security">Security Audit</option>
                        <option value="performance">Performance Optimization</option>
                        <option value="readability">Code Readability</option>
                        <option value="bugs">Bug Detection</option>
                    </select>
                </div>
                <div class="settings-option">
                    <label for="code-language">Programming Language</label>
                    <select id="code-language">
                        <option value="auto">Auto-detect</option>
                        <option value="python">Python</option>
                        <option value="javascript">JavaScript</option>
                        <option value="java">Java</option>
                        <option value="csharp">C#</option>
                        <option value="cpp">C++</option>
                        <option value="php">PHP</option>
                        <option value="go">Go</option>
                        <option value="ruby">Ruby</option>
                        <option value="swift">Swift</option>
                    </select>
                </div>
                <div class="settings-option">
                    <label for="detail-level">Detail Level</label>
                    <select id="detail-level">
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                        <option value="low">Low</option>
                    </select>
                </div>
            </div>
        </div>

        <div class="code-container">
            <div class="code-input">
                <h2><i class="fas fa-pencil-alt"></i>Your Code</h2>
                <textarea id="code-editor" placeholder="Paste your code here..."></textarea>
            </div>
            <div class="analysis-output">
                <h2><i class="fas fa-search"></i>Analysis Results</h2>
                <div class="analysis-content" id="analysis-content">
                    <div class="placeholder">
                        Enter your API key, paste your code, and click "Analyze Code" to get started.
                    </div>
                </div>
            </div>
        </div>

        <div class="submit-container" style="justify-content: center;">
            <button id="analyze-btn"><i class="fas fa-magic"></i>Analyze Code</button>
        </div>

        <footer>
            <p>Gemini Code Analyzer &copy; 2025 | This tool uses Google's Gemini API to analyze code</p>
            <p>Not affiliated with Google. You are responsible for your API usage and associated costs.</p>
        </footer>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Elements
            const apiKeyInput = document.getElementById('api-key');
            const verifyButton = document.getElementById('verify-api-key');
            const statusIndicator = document.getElementById('status-indicator');
            const statusText = document.getElementById('status-text');
            const codeEditor = document.getElementById('code-editor');
            const analyzeButton = document.getElementById('analyze-btn');
            const analysisContent = document.getElementById('analysis-content');
            const apiKeyError = document.getElementById('api-key-error');
            const settingsToggle = document.getElementById('settings-toggle');
            const settingsContent = document.getElementById('settings-content');
            
            // Analysis settings
            const analysisType = document.getElementById('analysis-type');
            const codeLanguage = document.getElementById('code-language');
            const detailLevel = document.getElementById('detail-level');
            
            // Toggle settings panel
            settingsToggle.addEventListener('click', function() {
                if (settingsContent.style.display === 'grid') {
                    settingsContent.style.display = 'none';
                    settingsToggle.querySelector('.fas.fa-chevron-down').className = 'fas fa-chevron-down';
                } else {
                    settingsContent.style.display = 'grid';
                    settingsToggle.querySelector('.fas.fa-chevron-down').className = 'fas fa-chevron-up';
                }
            });
            
            // Store API key in session storage
            function saveApiKey(key) {
                sessionStorage.setItem('geminiApiKey', key);
            }
            
            // Get API key from session storage
            function getApiKey() {
                return sessionStorage.getItem('geminiApiKey');
            }
            
            // Check for saved API key on page load
            const savedApiKey = getApiKey();
            if (savedApiKey) {
                apiKeyInput.value = savedApiKey;
                verifyApiKey(savedApiKey);
            }
            
            // Verify API key
            verifyButton.addEventListener('click', function() {
                const apiKey = apiKeyInput.value.trim();
                if (!apiKey) {
                    apiKeyError.style.display = 'block';
                    return;
                }
                
                apiKeyError.style.display = 'none';
                verifyApiKey(apiKey);
            });
            
            // Function to verify API key
            function verifyApiKey(apiKey) {
                // Show verifying status
                statusIndicator.className = 'status-indicator';
                statusText.textContent = 'Verifying...';
                
                // Simple verification endpoint - in production use proper verification
                const endpoint = `https://generativelanguage.googleapis.com/v1beta/models?key=${apiKey}`;
                
                fetch(endpoint)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Invalid API key');
                        }
                        return response.json();
                    })
                    .then(data => {
                        // API key verified successfully
                        statusIndicator.className = 'status-indicator active';
                        statusText.textContent = 'Verified';
                        saveApiKey(apiKey);
                    })
                    .catch(error => {
                        console.error('API Key verification failed:', error);
                        statusIndicator.className = 'status-indicator error';
                        statusText.textContent = 'Invalid key';
                        apiKeyError.style.display = 'block';
                        apiKeyError.textContent = 'API key verification failed';
                    });
            }
            
            // Analyze code
            analyzeButton.addEventListener('click', function() {
                const apiKey = apiKeyInput.value.trim();
                const code = codeEditor.value.trim();
                
                // Validate inputs
                if (!apiKey) {
                    apiKeyError.style.display = 'block';
                    return;
                }
                
                if (!code) {
                    alert('Please enter some code to analyze');
                    return;
                }
                
                // Show loading state
                analysisContent.innerHTML = `
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>Analyzing your code...</p>
                    </div>
                `;
                
                // Get analysis settings
                const type = analysisType.value;
                const language = codeLanguage.value;
                const detail = detailLevel.value;
                
                // Call Gemini API
                analyzeWithGemini(apiKey, code, type, language, detail);
            });
            
            // Function to analyze code using Gemini API
            function analyzeWithGemini(apiKey, code, type, language, detail) {
                // Gemini API endpoint
                const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=${apiKey}`;
                
                // Build the prompt based on analysis type
                let prompt = `Analyze the following code`;
                
                if (language !== 'auto') {
                    prompt += ` written in ${language}`;
                }
                
                switch (type) {
                    case 'security':
                        prompt += `. Focus on security vulnerabilities, potential exploits, and security best practices.`;
                        break;
                    case 'performance':
                        prompt += `. Focus on performance issues, optimizations, and efficiency improvements.`;
                        break;
                    case 'readability':
                        prompt += `. Focus on code readability, style, naming conventions, and organization.`;
                        break;
                    case 'bugs':
                        prompt += `. Focus on identifying bugs, potential errors, edge cases, and logical issues.`;
                        break;
                    default:
                        prompt += `. Provide a comprehensive analysis including security, performance, readability, and potential bugs.`;
                }
                
                // Add detail level instructions
                switch (detail) {
                    case 'high':
                        prompt += ` Provide detailed explanations with specific examples and recommended fixes.`;
                        break;
                    case 'medium':
                        prompt += ` Provide balanced explanations with key examples and suggested improvements.`;
                        break;
                    case 'low':
                        prompt += ` Provide concise overview of the most important issues and brief suggestions.`;
                        break;
                }
                
                prompt += `\n\nFormat your analysis with clear sections for Issues Found, Code Quality, and Recommendations. Here's the code:\n\n${code}`;
                
                // Request body
                const requestBody = {
                    contents: [{
                        parts: [{
                            text: prompt
                        }]
                    }],
                    generationConfig: {
                        temperature: 0.2,
                        topK: 40,
                        topP: 0.95,
                        maxOutputTokens: 8192,
                    }
                };
                
                // Make the API request
                fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(requestBody)
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('API request failed');
                    }
                    return response.json();
                })
                .then(data => {
                    // Extract and display the analysis
                    try {
                        const analysisText = data.candidates[0].content.parts[0].text;
                        displayAnalysis(analysisText);
                    } catch (e) {
                        throw new Error('Failed to parse API response');
                    }
                })
                .catch(error => {
                    console.error('Analysis failed:', error);
                    analysisContent.innerHTML = `
                        <div class="error-message" style="display:block; text-align:center; margin-top:20px;">
                            <i class="fas fa-exclamation-circle" style="font-size:24px; margin-bottom:10px;"></i>
                            <p>Analysis failed: ${error.message}</p>
                            <p style="margin-top:10px;">Please check your API key and try again.</p>
                        </div>
                    `;
                });
            }
            
            // Function to display the analysis result
            function displayAnalysis(text) {
                // Format and display the analysis
                let formattedText = text;
                
                // Simple Markdown-like formatting
                formattedText = formattedText
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    .replace(/\*(.*?)\*/g, '<em>$1</em>')
                    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
                    .replace(/`(.*?)`/g, '<code>$1</code>')
                    .replace(/^# (.*?)$/gm, '<h3 class="section-title">$1</h3>')
                    .replace(/^## (.*?)$/gm, '<h4 class="section-title">$1</h4>')
                    .replace(/^### (.*?)$/gm, '<h5 class="section-title">$1</h5>');
                
                // Add section styling
                const sections = ['Issues Found', 'Code Quality', 'Recommendations', 'Security', 'Performance', 'Readability', 'Bugs'];
                
                sections.forEach(section => {
                    const regex = new RegExp(`(${section}:?)`, 'g');
                    formattedText = formattedText.replace(regex, '<div class="section-title">$1</div>');
                });
                
                analysisContent.innerHTML = formattedText;
            }
            
            // Initialize from query params if present
            const urlParams = new URLSearchParams(window.location.search);
            const codeParam = urlParams.get('code');
            if (codeParam) {
                try {
                    codeEditor.value = decodeURIComponent(codeParam);
                } catch (e) {
                    console.error('Failed to decode URL parameter');
                }
            }
        });
    </script>
</body>
</html>