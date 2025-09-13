class CO2ShoppingAssistant {
    constructor() {
        this.chatInput = document.getElementById('chat-input');
        this.sendButton = document.getElementById('send-button');
        this.chatMessages = document.getElementById('chat-messages');
        this.co2SavingsElement = document.getElementById('co2-savings');
        this.totalCO2Saved = 0;
        
        this.initializeEventListeners();
        this.addWelcomeMessage();
    }
    
    initializeEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
    }
    
    addWelcomeMessage() {
        const welcomeMessage = `
            Welcome to the CO2-Aware Shopping Assistant! ���<br><br>
            I can help you:<br>
            • Find products with lower carbon footprint<br>
            • Suggest sustainable alternatives<br>
            • Calculate CO2 savings<br>
            • Get eco-friendly recommendations<br><br>
            Try asking: "Show me eco-friendly laptops" or "What's the CO2 impact of this product?"
        `;
        this.addMessage('assistant', welcomeMessage);
    }
    
    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message) return;
        
        this.addMessage('user', message);
        this.chatInput.value = '';
        this.sendButton.disabled = true;
        
        try {
            const response = await this.callAPI(message);
            const messageText = response.response?.response || response.response || response;
            this.addMessage('assistant', messageText);
            this.extractAndUpdateCO2Savings(messageText);
        } catch (error) {
            this.addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
            console.error('Error:', error);
        } finally {
            this.sendButton.disabled = false;
        }
    }
    
    async callAPI(message) {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data.response || 'No response received';
    }
    
    addMessage(sender, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.innerHTML = content;
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    extractAndUpdateCO2Savings(response) {
        const co2Match = response.match(/(\d+(?:\.\d+)?)\s*kg\s*CO[₂2]/i);
        if (co2Match) {
            const co2Amount = parseFloat(co2Match[1]);
            this.totalCO2Saved += co2Amount;
            this.updateCO2Display();
        }
    }
    
    updateCO2Display() {
        if (this.co2SavingsElement) {
            this.co2SavingsElement.textContent = `${this.totalCO2Saved.toFixed(1)} kg CO₂ saved`;
            this.co2SavingsElement.style.transform = 'scale(1.1)';
            setTimeout(() => {
                this.co2SavingsElement.style.transform = 'scale(1)';
            }, 200);
        }
    }
}

// Initialize the assistant when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new CO2ShoppingAssistant();
});
