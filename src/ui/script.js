class CO2ShoppingAssistant {
    constructor() {
        this.chatInput = document.getElementById('chat-input');
        this.sendButton = document.getElementById('send-button');
        this.chatMessages = document.getElementById('chat-messages');
        this.co2SavingsElement = document.getElementById('co2-savings');
        this.agentLog = document.getElementById('agent-log');
        this.productGrid = document.getElementById('product-grid');
        this.shippingPanel = document.getElementById('shipping-impact');
        this.shippingOptionsEl = document.getElementById('shipping-options');
        this.shippingSummaryEl = document.getElementById('shipping-summary');
        // Start at 0; do not persist across sessions to avoid stale values
        this.totalCO2Saved = 0;
        this.co2Label = 'CO₂';
        this.productCO2 = 0;  // Track product CO2 separately
        this.shippingCO2 = 0; // Track shipping CO2 separately
        this.selectedShippingOption = null; // Track selected shipping option name
        this.lastUserMessage = '';
        this.retry = { count: 0, max: 3, cooldownMs: 250, inFlight: false };
        
        this.initializeEventListeners();
        this.addWelcomeMessage();
        this.renderSampleProducts();
        this.initializeStaticShippingOptions();
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
        
        // Demo agent activity on load
        setTimeout(() => {
            this.logAgent('Host Agent: System initialized');
            this.logAgent('Product Discovery Agent: Ready to search catalog');
            this.logAgent('CO2 Calculator Agent: Monitoring environmental impact');
        }, 1000);
    }
    
    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message) return;
        
        this.addMessage('user', message);
        this.lastUserMessage = message;
        this.chatInput.value = '';
        this.sendButton.disabled = true;
        
        // Check if this is a payment request with selected shipping
        const isPaymentRequest = /pay|payment|credit card|payment_token|billing/.test(message.toLowerCase());
        const hasSelectedShipping = this.shippingCO2 > 0 && this.selectedShippingOption;
        
        // Don't modify payment messages - they were working before
        let processedMessage = message;
        
        try {
            const response = await this.callAPI(processedMessage);
            const messageText = response.response?.response || response.response || response;
            const assistantEl = this.addMessage('assistant', messageText);
            this.updateUIFromAssistant(messageText);
            // Auto-retry transient empty-cart states for checkout/payment flows
            if (this.autoRetryIfCartEmpty(messageText, assistantEl)) {
                return; // Skip further handling; retry will render the next response
            }
            this.extractAndUpdateCO2Savings(messageText);
        } catch (error) {
            this.addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
            // swallow console noise in production UI
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

    logAgent(activity) {
        if (!this.agentLog) return;
        const entry = document.createElement('div');
        entry.textContent = activity;
        this.agentLog.appendChild(entry);
        this.agentLog.scrollTop = this.agentLog.scrollHeight;
    }

    routeToSpecializedAgents(userMessage) {
        const message = userMessage.toLowerCase();
        
        // Cart management (check first to avoid conflicts with product search)
        if (/add.*cart|remove.*cart|cart|shopping cart|add.*to.*cart/.test(message)) {
            setTimeout(() => this.logAgent('Cart Management Agent: Managing cart operations...'), 200);
            setTimeout(() => this.logAgent('CO2 Calculator Agent: Calculating cart environmental impact...'), 400);
        }
        
        // Product search/discovery
        else if (/find|search|show|get|look for|products?|items?|laptop|watch|shoes|clothes/.test(message)) {
            setTimeout(() => this.logAgent('Product Discovery Agent: Searching product catalog...'), 200);
            setTimeout(() => this.logAgent('CO2 Calculator Agent: Analyzing environmental impact...'), 400);
        }
        
        // Checkout process
        else if (/checkout|proceed|order|purchase|buy/.test(message)) {
            setTimeout(() => this.logAgent('Checkout Agent: Processing checkout workflow...'), 200);
            setTimeout(() => this.logAgent('CO2 Calculator Agent: Calculating order environmental impact...'), 400);
        }
        
        // Payment processing
        else if (/pay|payment|credit card|payment_token|billing/.test(message)) {
            // If shipping has been selected but no explicit checkout, apply shipping to payment
            if (this.shippingCO2 > 0) {
                setTimeout(() => this.logAgent('Checkout Agent: Applying selected shipping option...'), 200);
                setTimeout(() => this.logAgent('Checkout Agent: Processing payment with shipping...'), 400);
                setTimeout(() => this.logAgent('CO2 Calculator Agent: Calculating total order impact...'), 600);
            } else {
                setTimeout(() => this.logAgent('Checkout Agent: Processing payment...'), 200);
                setTimeout(() => this.logAgent('Checkout Agent: Validating payment token...'), 400);
            }
        }
        
        // Shipping options
        else if (/shipping|delivery|express|ground|eco.*shipping/.test(message)) {
            setTimeout(() => this.logAgent('Cart Management Agent: Retrieving shipping options...'), 200);
            setTimeout(() => this.logAgent('CO2 Calculator Agent: Calculating shipping environmental impact...'), 400);
        }
        
        // Product comparison
        else if (/compare|alternative|better|vs|versus|difference/.test(message)) {
            setTimeout(() => this.logAgent('Comparison Agent: Analyzing product alternatives...'), 200);
            setTimeout(() => this.logAgent('CO2 Calculator Agent: Comparing environmental impacts...'), 400);
        }
        
        // CO2 analysis
        else if (/co2|carbon|environmental|eco|green|sustainable/.test(message)) {
            setTimeout(() => this.logAgent('CO2 Calculator Agent: Analyzing environmental impact...'), 200);
            setTimeout(() => this.logAgent('CO2 Calculator Agent: Generating sustainability recommendations...'), 400);
        }
        
        // General queries
        else {
            setTimeout(() => this.logAgent('Host Agent: Analyzing user intent...'), 200);
            setTimeout(() => this.logAgent('Host Agent: Routing to appropriate specialized agent...'), 400);
        }
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

    // Enriched UI hooks for agent log, shipping selector, and product badges
    updateUIFromAssistant(text) {
        const normalized = text.replace(/\*\*/g, '');

        // Agent coordination log
        const agentLines = normalized.match(/^(Host|Product Discovery|CO2 Calculator|Cart Management|Comparison) Agent:.*$/gmi);
        if (agentLines && agentLines.length) {
            agentLines.forEach(line => this.logAgent(line.trim()));
        }

        // Smart agent routing based on user intent
        if (this.lastUserMessage) {
            setTimeout(() => {
                this.logAgent(`Host Agent: Processing "${this.lastUserMessage}"`);
                this.routeToSpecializedAgents(this.lastUserMessage);
            }, 500);
        }

        // Shipping options block - also trigger on shipping-related keywords
        if (/Shipping\s+Options/i.test(normalized) || /shipping|delivery|express/i.test(this.lastUserMessage || '')) {
            this.renderShippingOptionsFromText(normalized);
        }
    }

    renderShippingOptionsFromText(text) {
        if (!this.shippingPanel || !this.shippingOptionsEl) return;
        this.shippingPanel.style.display = 'block';

        // Parse bullet-like options with CO2 lines
        const optionRegex = /([A-Za-z\-\s]+)\(([^)]+)\)\s*-\s*\$([0-9.]+)[\s\S]*?CO[₂2]:\s*(\d+(?:\.\d+)?)\s*kg/gi;
        const options = [];
        let match;
        while ((match = optionRegex.exec(text)) !== null) {
            options.push({
                name: match[1].trim(),
                eta: match[2].trim(),
                price: parseFloat(match[3]),
                co2: parseFloat(match[4])
            });
        }

        // If no options found in text, show demo options
        if (options.length === 0) {
            options.push(
                { name: 'Eco-Friendly', eta: '7 days', price: 7.99, co2: 150.0 },
                { name: 'Standard', eta: '5 days', price: 12.99, co2: 280.0 },
                { name: 'Express', eta: '2 days', price: 19.99, co2: 450.0 }
            );
        }

        this.shippingOptionsEl.innerHTML = '';
        const minCo2 = Math.min(...options.map(o => o.co2));
        options.forEach(o => {
            const row = document.createElement('div');
            row.className = 'shipping-impact__option';
            row.innerHTML = `
                <div>
                    <div><strong>${o.name}</strong> • ${o.eta}</div>
                    <div>CO₂: ${o.co2.toFixed(1)} kg</div>
                </div>
                <div>$${o.price.toFixed(2)}</div>
            `;
            row.onclick = () => {
                const delta = o.co2 - minCo2;
                this.shippingSummaryEl.textContent = delta > 0
                    ? `Selecting this adds +${delta.toFixed(1)} kg CO₂ vs eco option`
                    : `Best choice: lowest CO₂ option`;
                this.shippingCO2 = Math.max(0, o.co2);
                this.selectedShippingOption = o.name; // Track selected option name
                this.totalCO2Saved = this.productCO2 + this.shippingCO2;
                this.co2Label = 'Shipping CO₂';
                this.updateCO2Display();
            };
            this.shippingOptionsEl.appendChild(row);
        });
        this.shippingSummaryEl.textContent = 'Select an option to compare impact.';
    }

    renderSampleProducts() {
        if (!this.productGrid) return;
        const samples = [
            { name: 'Sunglasses', price: 19.99, co2: 49.0, eco: 9, img: '/ob-images/static/img/products/sunglasses.jpg' },
            { name: 'Watch', price: 109.99, co2: 44.5, eco: 8, img: '/ob-images/static/img/products/watch.jpg' },
            { name: 'Loafers', price: 89.99, co2: 45.5, eco: 9, img: '/ob-images/static/img/products/loafers.jpg' }
        ];
        this.productGrid.innerHTML = '';
        samples.forEach(p => this.productGrid.appendChild(this.createProductCard(p)));
    }

    createProductCard(product) {
        const card = document.createElement('div');
        card.className = 'product-card';
        const impactClass = product.co2 > 50 ? 'badge--high' : product.co2 > 30 ? 'badge--medium' : 'badge--low';
        card.innerHTML = `
            <img class="product-card__img" src="${product.img}" alt="${product.name}" />
            <div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px;">
                <div style="font-weight:700;">${product.name}</div>
                <div>$${product.price.toFixed(2)}</div>
            </div>
            <div style="margin-top:6px;display:flex;gap:6px;align-items:center;">
                <span class="badge ${impactClass}">CO₂: ${product.co2.toFixed(1)}kg</span>
                <span class="badge badge--eco">Eco ${product.eco}/10</span>
            </div>
        `;
        return card;
    }
    
    extractAndUpdateCO2Savings(response) {
        // Normalize: remove markdown bold so regex matches labels like **Total CO2**
        const text = response.replace(/\*\*/g, '');
        

        // 1) Reset after payment confirmation
        if (/Payment\s+Successful/i.test(text) || /Order\s+Confirmed/i.test(text)) {
            this.totalCO2Saved = 0;
            this.productCO2 = 0;
            this.shippingCO2 = 0;
            this.selectedShippingOption = null;
            this.co2Label = 'CO₂';
            this.updateCO2Display();
            return;
        }

        // 2) Handle different CO2 scenarios with proper accumulation
        
        // 2a) Total CO2 (from checkout) - ONLY handle if NOT a cart add operation
        const totalCo2Match = text.match(/(?:🌍\s*)?Total\s+CO[₂2]\s*:\s*(\d+(?:\.\d+)?)\s*kg/i);
        if (totalCo2Match && !/add.*cart|cart.*add/i.test(this.lastUserMessage || '')) {
            const co2Value = parseFloat(totalCo2Match[1]);
            if (!Number.isNaN(co2Value)) {
                this.totalCO2Saved = Math.max(0, co2Value);
                this.co2Label = 'Total CO₂';
                this.updateCO2Display();
                return;
            }
        }

        // 2b) Bullet lines: Shipping CO2 ("• CO2: 150.0 kg") and Cart total ("• Total CO2: 89.0 kg")
        const shippingCo2Match = text.match(/\u2022\s*CO[₂2]\s*:\s*(\d+(?:\.\d+)?)\s*kg/i);
        const bulletTotalMatch = text.match(/\u2022\s*Total\s+CO[₂2]\s*:\s*(\d+(?:\.\d+)?)\s*kg/i);
        if (shippingCo2Match) {
            const co2Value = parseFloat(shippingCo2Match[1]);
            if (!Number.isNaN(co2Value)) {
                this.shippingCO2 = Math.max(0, co2Value);
                this.totalCO2Saved = this.productCO2 + this.shippingCO2;
                this.co2Label = 'Shipping CO₂';
                this.updateCO2Display();
                return;
            }
        }
        // Only process bullet total if it's NOT from a cart operation (to avoid overwriting accumulation)
        if (bulletTotalMatch && !/add.*cart|cart.*add/i.test(this.lastUserMessage || '')) {
            const co2Value = parseFloat(bulletTotalMatch[1]);
            if (!Number.isNaN(co2Value)) {
                this.totalCO2Saved = Math.max(0, co2Value);
                this.co2Label = 'Total CO₂';
                this.updateCO2Display();
                return;
            }
        }

        // 2c) Product CO2 Impact - accumulate with existing shipping CO2
        const impactCo2Match = text.match(/(?:🌍\s*)?CO[₂2]\s*Impact\s*:\s*(\d+(?:\.\d+)?)\s*kg/i);
        if (impactCo2Match) {
            const co2Value = parseFloat(impactCo2Match[1]);
            if (!Number.isNaN(co2Value)) {
                this.productCO2 = Math.max(0, co2Value);
                // Accumulate: product CO2 + shipping CO2
                this.totalCO2Saved = this.productCO2 + this.shippingCO2;
                this.co2Label = this.shippingCO2 > 0 ? 'Total CO₂' : 'Product CO₂';
                this.updateCO2Display();
                return;
            }
        }

        // 2d) Product CO2 from cart operations - accumulate with existing shipping CO2
        const cartCo2Patterns = [
            /🌍\s*CO[₂2]\s*Impact\s*:\s*(\d+(?:\.\d+)?)\s*kg\s*CO[₂2]/i,  // Match "🌍 CO2 Impact: 44.5 kg CO2"
            /CO[₂2]\s*Impact\s*:\s*(\d+(?:\.\d+)?)\s*kg\s*CO[₂2]/i,       // Match "CO2 Impact: 44.5 kg CO2"
            /🌍\s*CO[₂2]\s*Impact\s*:\s*(\d+(?:\.\d+)?)\s*kg/i,           // Match "🌍 CO2 Impact: 44.5 kg"
            /CO[₂2]\s*Impact\s*:\s*(\d+(?:\.\d+)?)\s*kg/i,                // Match "CO2 Impact: 44.5 kg"
            /(\d+(?:\.\d+)?)\s*kg\s*CO[₂2]/i,                             // Match "44.5 kg CO2" anywhere
            /(\d+(?:\.\d+)?)\s*kg/i                                       // Match "44.5 kg" anywhere (fallback)
        ];
        
        for (const pattern of cartCo2Patterns) {
            const productCo2Match = text.match(pattern);
            if (productCo2Match && /add.*cart|cart.*add/i.test(this.lastUserMessage || '')) {
                const co2Value = parseFloat(productCo2Match[1]);
                if (!Number.isNaN(co2Value)) {
                    this.productCO2 = Math.max(0, co2Value);
                    // Accumulate: product CO2 + shipping CO2
                    this.totalCO2Saved = this.productCO2 + this.shippingCO2;
                    this.co2Label = this.shippingCO2 > 0 ? 'Total CO₂' : 'Product CO₂';
                    this.updateCO2Display();
                    return;
                }
            }
        }
        
        // 2e) Handle "Total CO2" from cart responses - only if no shipping selected to avoid overwriting
        const cartTotalMatch = text.match(/Total\s+CO[₂2]\s*:\s*(\d+(?:\.\d+)?)\s*kg/i);
        if (cartTotalMatch && /add.*cart|cart.*add/i.test(this.lastUserMessage || '')) {
            const co2Value = parseFloat(cartTotalMatch[1]);
            if (!Number.isNaN(co2Value)) {
                this.productCO2 = Math.max(0, co2Value);
                // Always accumulate: product CO2 + shipping CO2
                this.totalCO2Saved = this.productCO2 + this.shippingCO2;
                this.co2Label = this.shippingCO2 > 0 ? 'Total CO₂' : 'Product CO₂';
                this.updateCO2Display();
                return;
            }
        }

        // 3) Explicit savings statement: "44.5 kg CO₂ saved"
        const savedMatch = response.match(/(\d+(?:\.\d+)?)\s*kg\s*CO[₂2]\s*saved/i);
        if (savedMatch) {
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
            const perItem = parseFloat(simplePerItem[1]);
            if (!Number.isNaN(perItem)) {
                this.totalCO2Saved = Math.max(0, perItem);
                this.updateCO2Display();
                return;
            }
        }
        
    }
    
    updateCO2Display() {
        if (this.co2SavingsElement) {
            const label = this.co2Label || 'CO₂';
            this.co2SavingsElement.textContent = `${label}: ${this.totalCO2Saved.toFixed(1)} kg`;
            this.co2SavingsElement.style.transform = 'scale(1.1)';
            setTimeout(() => {
                this.co2SavingsElement.style.transform = 'scale(1)';
            }, 200);
        }
    }

    initializeStaticShippingOptions() {
        const shippingOptions = document.querySelectorAll('.shipping-option');
        shippingOptions.forEach(option => {
            option.addEventListener('click', () => {
                // Remove previous selection
                shippingOptions.forEach(opt => opt.classList.remove('selected'));
                
                // Add selection to clicked option
                option.classList.add('selected');
                
                // Update CO2 display
                const co2 = parseFloat(option.dataset.co2);
                const price = parseFloat(option.dataset.price);
                const days = option.dataset.days;
                const name = option.querySelector('.shipping-option__name').textContent;
                
                this.shippingCO2 = co2;
                this.selectedShippingOption = name; // Track selected option name
                this.totalCO2Saved = this.productCO2 + this.shippingCO2;
                this.co2Label = 'Shipping CO₂';
                this.updateCO2Display();
                
                // Log the selection
                this.logAgent(`User selected: ${name} shipping (${days}, $${price}, ${co2}kg CO₂)`);
                
                // Send selection to backend to update checkout state
                this.sendShippingSelectionToBackend(name);
            });
        });
    }
    
    async sendShippingSelectionToBackend(shippingOption) {
        try {
            // Send a message to the backend to set the shipping option
            const response = await this.callAPI(`set shipping to ${shippingOption}`);
        } catch (error) {
        }
    }
}

// Initialize the assistant when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new CO2ShoppingAssistant();
});