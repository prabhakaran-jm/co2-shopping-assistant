class CO2ShoppingAssistant {
    constructor() {
        this.chatInput = document.getElementById('chat-input');
        this.sendButton = document.getElementById('send-button');
        this.chatMessages = document.getElementById('chat-messages');
        this.co2SavingsElement = document.getElementById('co2-savings');
        // Start at 0; do not persist across sessions to avoid stale values
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
            Welcome to the CO2-Aware Shopping Assistant! 🌱<br><br>
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
            console.log('Raw API response:', response);
            const messageText = response.response?.response || response.response || response;
            console.log('Extracted messageText:', messageText);
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
        const sid = this.getCookie ? this.getCookie('assistant_sid') : null;
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ message: message, session_id: sid || undefined })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data.response || 'No response received';
    }

    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }
    
    addMessage(sender, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.innerHTML = this.renderMarkdown(content);
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    renderMarkdown(text) {
        // Convert Markdown images to HTML img tags
        let html = text.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" style="max-width: 200px; height: auto; border-radius: 8px; margin: 5px 0;" />');
        
        // Convert **bold** to <strong>
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert line breaks to <br>
        html = html.replace(/\n/g, '<br>');
        
        return html;
    }
    
    extractAndUpdateCO2Savings(response) {
        // Debug: log the response to see what we're working with
        console.log('=== CO2 Extraction Debug ===');
        console.log('Full response:', response);
        console.log('Response length:', response.length);
        
        // 1) Reset on successful checkout - try multiple patterns
        if (response.includes('Payment Successful') || response.includes('✅') || response.includes('Order Confirmed')) {
            console.log('Detected checkout completion, resetting badge');
            this.totalCO2Saved = 0;
            this.updateCO2Display();
            return;
        }

        // 2) CO2 Impact from cart/checkout: "🌍 CO2 Impact: 44.5 kg CO2" or "🌍 Total CO2: 93.5 kg"
        const co2ImpactMatch = response.match(/🌍\s*(?:CO2\s+Impact|Total\s+CO2):\s*(\d+(?:\.\d+)?)\s*kg/i);
        if (co2ImpactMatch) {
            console.log('Found CO2 impact:', co2ImpactMatch[1]);
            const co2Value = parseFloat(co2ImpactMatch[1]);
            if (!Number.isNaN(co2Value)) {
                this.totalCO2Saved = Math.max(0, co2Value);
                this.updateCO2Display();
                return;
            }
        }

        // 3) Explicit savings statement: "44.5 kg CO₂ saved"
        const savedMatch = response.match(/(\d+(?:\.\d+)?)\s*kg\s*CO[₂2]\s*saved/i);
        if (savedMatch) {
            console.log('Found explicit savings:', savedMatch[1]);
            const saved = parseFloat(savedMatch[1]);
            if (!Number.isNaN(saved)) {
                this.totalCO2Saved = Math.max(0, saved);
                this.updateCO2Display();
                return;
            }
        }

        // 3) Multi-item savings phrasing (ProductDiscoveryAgent):
        //    "Estimated savings choosing efficient options: 1.2kg per item"
        const perItemSavings = response.match(/Estimated\s+savings\s+choosing\s+efficient\s+options:\s*(\d+(?:\.\d+)?)\s*kg\s*per\s*item/i);
        if (perItemSavings) {
            console.log('Found per-item savings:', perItemSavings[1]);
            const perItem = parseFloat(perItemSavings[1]);
            if (!Number.isNaN(perItem)) {
                this.totalCO2Saved = Math.max(0, perItem);
                this.updateCO2Display();
                return;
            }
        }
        
        // 4) Try simpler patterns for multi-item
        const simplePerItem = response.match(/(\d+(?:\.\d+)?)\s*kg\s*per\s*item/i);
        if (simplePerItem) {
            console.log('Found simple per-item:', simplePerItem[1]);
            const perItem = parseFloat(simplePerItem[1]);
            if (!Number.isNaN(perItem)) {
                this.totalCO2Saved = Math.max(0, perItem);
                this.updateCO2Display();
                return;
            }
        }
        
        console.log('No CO2 patterns matched');
        console.log('=== End Debug ===');
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