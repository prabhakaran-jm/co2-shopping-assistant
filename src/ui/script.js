class CO2ShoppingAssistant {
    constructor() {
        console.log('UI script version: v2.1');
        this.chatInput = document.getElementById('chat-input');
        this.sendButton = document.getElementById('send-button');
        this.chatMessages = document.getElementById('chat-messages');
        this.co2SavingsElement = document.getElementById('co2-savings');
        // Start at 0; do not persist across sessions to avoid stale values
        this.totalCO2Saved = 0;
        this.lastUserMessage = '';
        this.retry = { count: 0, max: 3, cooldownMs: 250, inFlight: false };
        
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
        this.lastUserMessage = message;
        this.chatInput.value = '';
        this.sendButton.disabled = true;
        
        try {
            const response = await this.callAPI(message);
            console.log('Raw API response:', response);
            const messageText = response.response?.response || response.response || response;
            console.log('Extracted messageText:', messageText);
            const assistantEl = this.addMessage('assistant', messageText);
            // Auto-retry transient empty-cart states for checkout/payment flows
            if (this.autoRetryIfCartEmpty(messageText, assistantEl)) {
                return; // Skip further handling; retry will render the next response
            }
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
        return messageDiv;
    }

    autoRetryIfCartEmpty(messageText, assistantEl) {
        const isCartEmpty = /your cart is empty/i.test(messageText);
        const isCheckoutOrPay = /(checkout|pay)/i.test(this.lastUserMessage || '');
        if (!isCartEmpty || !isCheckoutOrPay) return false;
        if (this.retry.inFlight || this.retry.count >= this.retry.max) return false;

        // Suppress the noisy assistant message and retry silently
        if (assistantEl && assistantEl.parentNode) {
            assistantEl.parentNode.removeChild(assistantEl);
        }
        this.retry.inFlight = true;
        this.retry.count += 1;
        setTimeout(async () => {
            try {
                const response = await this.callAPI(this.lastUserMessage);
                console.log('Retry response:', response);
                const text = response.response?.response || response.response || response;
                const el = this.addMessage('assistant', text);
                // If still empty, try again (bounded by max)
                if (!this.autoRetryIfCartEmpty(text, el)) {
                    this.extractAndUpdateCO2Savings(text);
                }
            } catch (e) {
                console.error('Retry error:', e);
            } finally {
                this.retry.inFlight = false;
                this.sendButton.disabled = false;
            }
        }, this.retry.cooldownMs);
        return true;
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

        // Normalize: remove markdown bold so regex matches labels like **Total CO2**
        const text = response.replace(/\*\*/g, '');

        // 1) Reset after payment confirmation
        if (/Payment\s+Successful/i.test(text) || /Order\s+Confirmed/i.test(text)) {
            console.log('Detected payment completion, resetting badge to 0');
            this.totalCO2Saved = 0;
            this.updateCO2Display();
            return;
        }

        // 2) Prefer Total CO2 if present, then Shipping CO2, then CO2 Impact
        const totalCo2Match = text.match(/(?:🌍\s*)?Total\s+CO[₂2]\s*:\s*(\d+(?:\.\d+)?)\s*kg/i);
        if (totalCo2Match) {
            console.log('Found Total CO2:', totalCo2Match[1]);
            const co2Value = parseFloat(totalCo2Match[1]);
            if (!Number.isNaN(co2Value)) {
                this.totalCO2Saved = Math.max(0, co2Value);
                this.updateCO2Display();
                return;
            }
        }

        // 2b) Bullet lines: Shipping CO2 ("• CO2: 150.0 kg") and Cart total ("• Total CO2: 89.0 kg")
        const shippingCo2Match = text.match(/\u2022\s*CO[₂2]\s*:\s*(\d+(?:\.\d+)?)\s*kg/i);
        const bulletTotalMatch = text.match(/\u2022\s*Total\s+CO[₂2]\s*:\s*(\d+(?:\.\d+)?)\s*kg/i);
        if (shippingCo2Match) {
            console.log('Found shipping CO2:', shippingCo2Match[1]);
            const co2Value = parseFloat(shippingCo2Match[1]);
            if (!Number.isNaN(co2Value)) {
                this.totalCO2Saved = Math.max(0, co2Value);
                this.updateCO2Display();
                return;
            }
        }
        if (bulletTotalMatch) {
            console.log('Found bullet Total CO2:', bulletTotalMatch[1]);
            const co2Value = parseFloat(bulletTotalMatch[1]);
            if (!Number.isNaN(co2Value)) {
                this.totalCO2Saved = Math.max(0, co2Value);
                this.updateCO2Display();
                return;
            }
        }

        // 2c) Fallback: CO2 Impact line
        const impactCo2Match = text.match(/(?:🌍\s*)?CO[₂2]\s*Impact\s*:\s*(\d+(?:\.\d+)?)\s*kg/i);
        if (impactCo2Match) {
            console.log('Found CO2 Impact:', impactCo2Match[1]);
            const co2Value = parseFloat(impactCo2Match[1]);
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