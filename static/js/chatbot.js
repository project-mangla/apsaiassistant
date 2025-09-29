// Enhanced chat functionality for APS Mangla Assistant
document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    const messageInput = document.getElementById('messageInput');
    const chatContainer = document.getElementById('chatContainer');
    const sendBtn = document.getElementById('sendBtn');
    const statusMessage = document.getElementById('statusMessage');
    const suggestionBtns = document.querySelectorAll('.suggestion-btn');
    
    // Focus on input field
    messageInput.focus();
    
    // Handle suggestion button clicks
    suggestionBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const suggestion = this.getAttribute('data-suggestion');
            messageInput.value = suggestion;
            messageInput.focus();
            
            // Auto-submit suggestion
            setTimeout(() => {
                chatForm.dispatchEvent(new Event('submit'));
            }, 100);
        });
    });
    
    // Handle form submission
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = messageInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addMessage(message, 'user');
        
        // Clear input and disable form
        messageInput.value = '';
        setFormState(false);
        
        // Show thinking indicator
        showThinkingIndicator();
        
        // Send message to server
        sendMessage(message);
    });
    
    function addMessage(content, sender, confidence = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (sender === 'bot') {
            contentDiv.innerHTML = `<i class="fas fa-robot me-2"></i>${content}`;
            if (confidence && parseFloat(confidence) > 0) {
                const confidenceFloat = parseFloat(confidence);
                const confidencePercent = Math.round(confidenceFloat * 100);
                let confidenceClass = 'bg-success';
                
                if (confidencePercent < 40) {
                    confidenceClass = 'bg-warning';
                } else if (confidencePercent < 70) {
                    confidenceClass = 'bg-info';
                }
                
                contentDiv.innerHTML += `<br><span class="confidence-badge badge ${confidenceClass}">
                    <i class="fas fa-chart-line me-1"></i>Confidence: ${confidencePercent}%
                </span>`;
            }
        } else {
            contentDiv.innerHTML = `<i class="fas fa-user me-2"></i>${content}`;
        }
        
        messageDiv.appendChild(contentDiv);
        
        // Remove thinking indicator if it exists
        const thinkingIndicator = chatContainer.querySelector('.thinking-message');
        if (thinkingIndicator) {
            thinkingIndicator.remove();
        }
        
        chatContainer.appendChild(messageDiv);
        
        // Scroll to bottom with smooth animation
        scrollToBottom();
    }
    
    function showThinkingIndicator() {
        const thinkingDiv = document.createElement('div');
        thinkingDiv.className = 'chat-message bot-message thinking-message';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = `
            <i class="fas fa-robot me-2"></i>
            <span class="typing-indicator"></span>
            <span class="typing-indicator"></span>
            <span class="typing-indicator"></span>
        `;
        
        thinkingDiv.appendChild(contentDiv);
        chatContainer.appendChild(thinkingDiv);
        scrollToBottom();
    }
    
    function sendMessage(message) {
        const formData = new FormData();
        formData.append('message', message);
        
        updateStatus('processing', 'Processing your question...');
        
        fetch('/chat', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Response data:', data);
            
            if (data.error) {
                addMessage(`Sorry, there was an error: ${data.error}`, 'bot');
                updateStatus('error', 'Error occurred');
            } else {
                addMessage(data.response, 'bot', data.confidence);
                updateStatus('success', 'Response received');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('I apologize, but I encountered a connection error. Please check your internet connection and try again.', 'bot');
            updateStatus('error', 'Connection error');
        })
        .finally(() => {
            // Re-enable form
            setFormState(true);
            messageInput.focus();
        });
    }
    
    function setFormState(enabled) {
        messageInput.disabled = !enabled;
        sendBtn.disabled = !enabled;
        
        // Update suggestion buttons
        suggestionBtns.forEach(btn => {
            btn.disabled = !enabled;
        });
        
        if (enabled) {
            sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send';
            messageInput.placeholder = 'Type your question about APS Mangla...';
        } else {
            sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
            messageInput.placeholder = 'Processing your question...';
        }
    }
    
    function updateStatus(type, message) {
        const icons = {
            'success': 'fas fa-circle text-success',
            'error': 'fas fa-circle text-danger',
            'processing': 'fas fa-spinner fa-spin text-primary',
            'warning': 'fas fa-circle text-warning'
        };
        
        const icon = icons[type] || 'fas fa-circle text-info';
        statusMessage.innerHTML = `<i class="${icon}"></i> ${message}`;
        
        // Reset to ready state after 3 seconds (except for processing)
        if (type !== 'processing') {
            setTimeout(() => {
                statusMessage.innerHTML = '<i class="fas fa-circle text-success"></i> Ready to help with APS Mangla information';
            }, 3000);
        }
    }
    
    function scrollToBottom() {
        chatContainer.scrollTo({
            top: chatContainer.scrollHeight,
            behavior: 'smooth'
        });
    }
    
    // Handle enter key in input
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!sendBtn.disabled) {
                chatForm.dispatchEvent(new Event('submit'));
            }
        }
    });
    
    // Auto-resize textarea
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });
    
    // Handle suggestion button hover effects
    suggestionBtns.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Initialize status
    updateStatus('success', 'Ready to help with APS Mangla information');
    
    // Add welcome animation to initial bot message
    setTimeout(() => {
        const initialMessage = chatContainer.querySelector('.bot-message');
        if (initialMessage) {
            initialMessage.style.animation = 'fadeInUp 0.6s ease-out';
        }
    }, 100);
});
