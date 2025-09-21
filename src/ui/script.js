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
        this.connectionStatus = document.getElementById('connection-status');
        
        // Sustainability Dashboard elements
        this.totalCO2SavedEl = document.getElementById('total-co2-saved');
        this.ecoProductsCountEl = document.getElementById('eco-products-count');
        this.sustainabilityScoreEl = document.getElementById('sustainability-score');
        this.greenSavingsEl = document.getElementById('green-savings');
        this.ecoProgressFillEl = document.getElementById('eco-progress-fill');
        this.ecoProgressTextEl = document.getElementById('eco-progress-text');
        this.ecoTipsEl = document.getElementById('eco-tips');
        // Start at 0; do not persist across sessions to avoid stale values
        this.totalCO2Impact = 0;  // Total CO2 impact (consumption)
        this.totalCO2Saved = 0;   // Total CO2 savings (vs worst alternatives)
        this.co2Label = 'CO₂ Impact';
        this.productCO2 = 0;  // Track product CO2 separately
        this.displayProductCO2 = null; // For display purposes only
        this.shippingCO2 = 0; // Track shipping CO2 separately
        this.selectedShippingOption = null; // Track selected shipping option name
        this.lastUserMessage = '';
        this.isProcessingCheckoutCommand = false; // Flag to prevent double CO2 processing
        this.retry = { count: 0, max: 3, cooldownMs: 250, inFlight: false };
        
        // Sustainability tracking
        this.ecoProductsCount = 0;
        this.sustainabilityScore = 0;
        this.greenSavings = 0;
        this.monthlyEcoGoal = 100; // kg CO₂ saved per month
        
        this.initializeEventListeners();
        this.addWelcomeMessage();
        this.renderSampleProducts();
        this.initializeStaticShippingOptions();
        
        // Add before/after comparison functionality
        this.addComparisonButtons();
        
        // Initialize sustainability dashboard
        this.initializeSustainabilityDashboard();
        
        // Check server connectivity
        this.checkServerConnectivity();
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
        
        const processedMessage = message;
        
        try {
            const response = await this.callAPI(processedMessage);
            const messageText = response.response?.response || response.response || response;
            const assistantEl = this.addMessage('assistant', messageText);
            
            // This function now handles the CO2 extraction
            this.updateUIFromAssistant(messageText);

            // Auto-retry transient empty-cart states for checkout/payment flows
            if (this.autoRetryIfCartEmpty(messageText, assistantEl)) {
                return; // Skip further handling; retry will render the next response
            }
            
            // **FIXED**: Redundant call to extractAndUpdateCO2Savings was removed from here.

        } catch (error) {
            let errorMessage = 'Sorry, I encountered an error. Please try again.';
            
            if (error.message.includes('Failed to fetch')) {
                errorMessage = 'Unable to connect to the server. Please check if the application is running.';
            } else if (error.message.includes('HTTP error')) {
                errorMessage = `Server error: ${error.message}`;
            } else if (error.message.includes('NetworkError')) {
                errorMessage = 'Network error. Please check your connection.';
            }
            
            this.addMessage('assistant', errorMessage);
            this.logAgent(`Host Agent: Error occurred - ${error.message}`);
        } finally {
            this.sendButton.disabled = false;
        }
    }
    
    async callAPI(message) {
        const sid = this.getCookie ? this.getCookie('assistant_sid') : null;
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({ message: message, session_id: sid || undefined })
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
            }
            
            const data = await response.json();
            return data.response || 'No response received';
        } catch (error) {
            throw error;
        }
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
        
        let agentIcon = '🤖';
        let agentClass = 'agent-log-entry';
        
        if (activity.includes('Host Agent')) {
            agentIcon = '🏠';
            agentClass += ' host-agent';
        } else if (activity.includes('Product Discovery Agent')) {
            agentIcon = '🔍';
            agentClass += ' discovery-agent';
        } else if (activity.includes('CO2 Calculator Agent')) {
            agentIcon = '🌱';
            agentClass += ' co2-agent';
        } else if (activity.includes('Cart Management Agent')) {
            agentIcon = '🛒';
            agentClass += ' cart-agent';
        } else if (activity.includes('Checkout Agent')) {
            agentIcon = '💳';
            agentClass += ' checkout-agent';
        } else if (activity.includes('Comparison Agent')) {
            agentIcon = '⚖️';
            agentClass += ' comparison-agent';
        }
        
        entry.className = agentClass;
        entry.innerHTML = `
            <div class="agent-icon">${agentIcon}</div>
            <div class="agent-content">
                <div class="agent-time">${new Date().toLocaleTimeString()}</div>
                <div class="agent-activity">${activity}</div>
            </div>
        `;
        
        this.agentLog.appendChild(entry);
        this.agentLog.scrollTop = this.agentLog.scrollHeight;
        
        entry.style.opacity = '0';
        entry.style.transform = 'translateX(-20px)';
        setTimeout(() => {
            entry.style.transition = 'all 0.3s ease';
            entry.style.opacity = '1';
            entry.style.transform = 'translateX(0)';
        }, 50);
    }

    routeToSpecializedAgents(userMessage) {
        const message = userMessage.toLowerCase();
        
        if (/add.*cart|remove.*cart|cart|shopping cart|add.*to.*cart/.test(message)) {
            setTimeout(() => this.logAgent('Cart Management Agent: Managing cart operations...'), 200);
            setTimeout(() => this.logAgent('CO2 Calculator Agent: Calculating cart environmental impact...'), 400);
        }
        else if (/find|search|show|get|look for|products?|items?|laptop|watch|shoes|clothes/.test(message)) {
            setTimeout(() => this.logAgent('Product Discovery Agent: Searching product catalog...'), 200);
            setTimeout(() => this.logAgent('CO2 Calculator Agent: Analyzing environmental impact...'), 400);
        }
        else if (/checkout|proceed|order|purchase|buy/.test(message)) {
            setTimeout(() => this.logAgent('Checkout Agent: Processing checkout workflow...'), 200);
            setTimeout(() => this.logAgent('CO2 Calculator Agent: Calculating order environmental impact...'), 400);
        }
        else if (/pay|payment|credit card|payment_token|billing/.test(message)) {
            if (this.shippingCO2 > 0) {
                setTimeout(() => this.logAgent('Checkout Agent: Applying selected shipping option...'), 200);
                setTimeout(() => this.logAgent('Checkout Agent: Processing payment with shipping...'), 400);
                setTimeout(() => this.logAgent('CO2 Calculator Agent: Calculating total order impact...'), 600);
            } else {
                setTimeout(() => this.logAgent('Checkout Agent: Processing payment...'), 200);
                setTimeout(() => this.logAgent('Checkout Agent: Validating payment token...'), 400);
            }
        }
        else if (/shipping|delivery|express|ground|eco.*shipping/.test(message)) {
            setTimeout(() => this.logAgent('Cart Management Agent: Retrieving shipping options...'), 200);
            setTimeout(() => this.logAgent('CO2 Calculator Agent: Calculating shipping environmental impact...'), 400);
        }
        else if (/compare|alternative|better|vs|versus|difference/.test(message)) {
            setTimeout(() => this.logAgent('Comparison Agent: Analyzing product alternatives...'), 200);
            setTimeout(() => this.logAgent('CO2 Calculator Agent: Comparing environmental impacts...'), 400);
        }
        else if (/co2|carbon|environmental|eco|green|sustainable/.test(message)) {
            setTimeout(() => this.logAgent('CO2 Calculator Agent: Analyzing environmental impact...'), 200);
            setTimeout(() => this.logAgent('CO2 Calculator Agent: Generating sustainability recommendations...'), 400);
        }
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
                if (!this.autoRetryIfCartEmpty(text, el)) {
                    this.extractAndUpdateCO2Savings(text);
                }
            } catch (e) {
            } finally {
                this.retry.inFlight = false;
                this.sendButton.disabled = false;
            }
        }, this.retry.cooldownMs);
        return true;
    }
    
    renderMarkdown(text) {
        let html = text.replace(/![\[^\]]*\]\([^)]*\)/g, '<img src="$2" alt="$1" style="max-width: 200px; height: auto; border-radius: 8px; margin: 5px 0;" />');
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/\\_/g, '_').replace(/\\\$/g, '$');
        html = html.replace(/\n/g, '<br>');
        return html;
    }

    updateUIFromAssistant(text) {
        const normalized = text.replace(/\*\*/g, '').replace(/\\_/g, '_').replace(/\\\$/g, '$');
        
        // This is the single source for CO2 extraction from any assistant response.
        this.extractAndUpdateCO2Savings(text);

        const agentLines = normalized.match(/^(Host|Product Discovery|CO2 Calculator|Cart Management|Comparison) Agent:.*$/gmi);
        if (agentLines && agentLines.length) {
            agentLines.forEach(line => this.logAgent(line.trim()));
        }

        if (this.lastUserMessage) {
            setTimeout(() => {
                this.logAgent(`Host Agent: Processing "${this.lastUserMessage}"`);
                this.routeToSpecializedAgents(this.lastUserMessage);
            }, 500);
        }

        if (/Shipping\s+Options/i.test(normalized) || /shipping|delivery|express/i.test(this.lastUserMessage || '')) {
            this.renderShippingOptionsFromText(normalized);
        }
        
        // Handle checkout commands that change shipping method
        if (/checkout with|shipping.*ground|shipping.*eco|shipping.*express/i.test(this.lastUserMessage || '')) {
            this.isProcessingCheckoutCommand = true; // Set flag to prevent double processing
            const match = this.lastUserMessage.match(/with\s+(ground|eco|express|eco-friendly)/i);
            if (match && match[1]) {
                let shippingMethod = match[1].toLowerCase();
                // Map command terms to actual shipping method names
                if (shippingMethod === 'eco') {
                    shippingMethod = 'eco-friendly';
                }
                this.updateShippingSelectionFromCheckoutCommand(shippingMethod);
            } else {
                this.logAgent(`Could not extract shipping method from command: ${this.lastUserMessage}`);
            }
        }
        
        // Handle product responses to render dynamic products
        // Check if response contains product information (📦 symbols) or if it's a product-related query
        if (normalized.includes('📦') || /show all products|find.*products|search.*products|list all|show me.*products|find watch|find sunglasses|find.*item|find.*laptop|find.*hairdryer|find.*phone|find.*shoes|find.*shirt|eco.*friendly/i.test(this.lastUserMessage || '')) {
            this.renderProductsFromResponse(normalized);
        }
    }

    renderShippingOptionsFromText(text) {
        if (!this.shippingPanel || !this.shippingOptionsEl) return;
        this.shippingPanel.style.display = 'block';

        const optionRegex = /([A-Za-z\-\s]+)\(([^)]+)\)\s*-\s*\$([0-9.]+)[ \s\S]*?CO[₂2]:\s*(\d+(?:\.\d+)?)\s*kg/gi;
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
            row.dataset.shippingMethod = o.name.toLowerCase(); // Add data-shipping-method
            row.innerHTML = `
                <div>
                    <div><strong>${o.name}</strong> • ${o.eta}</div>
                    <div>CO₂: ${o.co2.toFixed(1)} kg</div>
                </div>
                <div>$${o.price.toFixed(2)}</div>
            `;
            row.onclick = () => {
                this._updateShippingSelection(row); // Use the new method
                
                const delta = o.co2 - minCo2;
                this.shippingSummaryEl.textContent = delta > 0
                    ? `Selecting this adds +${delta.toFixed(1)} kg CO₂ vs eco option`
                    : `Best choice: lowest CO₂ option`;
                this.shippingCO2 = Math.max(0, o.co2);
                this.selectedShippingOption = o.name;
                this.totalCO2Impact = this.productCO2 + this.shippingCO2;
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
        
        // **FIXED**: Added classes for querySelector to find these elements
        card.innerHTML = `
            <img class="product-card__img" src="${product.img}" alt="${product.name}" />
            <div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px;">
                <div class="product-name" style="font-weight:700;">${product.name}</div>
                <div class="product-price">$${product.price.toFixed(2)}</div>
            </div>
            <div style="margin-top:6px;display:flex;gap:6px;align-items:center;">
                <span class="badge ${impactClass} product-co2">CO₂: ${product.co2.toFixed(1)}kg</span>
                <span class="badge badge--eco product-eco">Eco ${product.eco}/10</span>
            </div>
        `;
        
        // Add click handler to update sustainability metrics
        card.addEventListener('click', () => {
            this.updateSustainabilityFromProduct(product);
        });
        
        return card;
    }
    
    // **FIXED**: This is the single, corrected version of the function.
    extractAndUpdateCO2Savings(response) {
        console.log('🔍 DEBUG: extractAndUpdateCO2Savings called with response:', response);
        console.log('🔍 DEBUG: Current values before processing:');
        console.log('  - productCO2:', this.productCO2);
        console.log('  - shippingCO2:', this.shippingCO2);
        console.log('  - totalCO2Impact:', this.totalCO2Impact);
        console.log('  - isProcessingCheckoutCommand:', this.isProcessingCheckoutCommand);
        
        // Normalize: remove markdown bold so regex matches labels like **Total CO2**
        const text = response.replace(/\*\*/g, '');

        // 1. Reset state after cart clearing OR successful payments
        if (/cart\s+has\s+been\s+cleared|empty\s+cart|cart\s+is\s+now\s+empty|Payment\s+Successful|Order\s+Confirmed|order.*confirmed/i.test(text)) {
            this.totalCO2Impact = 0;
            this.totalCO2Saved = 0;
            this.productCO2 = 0;
            this.shippingCO2 = 0;
            this.selectedShippingOption = null;
            this.co2Label = 'CO₂ Impact';
            this.updateCO2Display();
            this.resetSustainabilityMetrics();
            
            // Clear shipping selection visual state
            this.clearShippingSelection();
            return;
        }

        // 2. Handle Cart Operations
        const isCartAddOperation = /add.*cart|cart.*add/i.test(this.lastUserMessage || '');
        const isCartRemoveOperation = /remove.*cart|cart.*remove/i.test(this.lastUserMessage || '');
        const isCartClearOperation = /empty.*cart|clear.*cart|clear.*my.*cart/i.test(this.lastUserMessage || '');

        // Also check if the response indicates cart is empty
        const isCartEmptyResponse = /cart.*empty|empty.*cart|no.*items.*cart|cart.*is.*empty/i.test(text);

        if (isCartAddOperation) {
            this.handleCartOperation('add', text);
            return;
        } else if (isCartRemoveOperation || isCartClearOperation || isCartEmptyResponse) {
            this.handleCartOperation('clear', text);
            return;
        }

        // 3. Handle multiple products scenario (e.g., "show all products")
        // Check for various patterns that indicate multiple products
        const productCountPatterns = [
            /Found\s+(\d+)\s+(?:eco-friendly\s+)?products/i,
            /Here are\s+(\d+)\s+(?:eco-friendly\s+)?products/i,
            /Here's\s+(\d+)\s+(?:eco-friendly\s+)?products/i,
            /(\d+)\s+recommendations/i,
            /(\d+)\s+results/i,
            /AI-Powered Product Suggestions.*?(\d+)\s+recommendations/i
        ];
        
        let productCount = 0;
        for (const pattern of productCountPatterns) {
            const match = text.match(pattern);
            if (match) {
                productCount = parseInt(match[1]);
                break;
            }
        }
        
        // Also check if we have multiple product entries (📦 symbols)
        if (productCount === 0) {
            const productSymbols = (text.match(/📦/g) || []).length;
            if (productSymbols > 1) {
                productCount = productSymbols;
            }
        }
        
        if (productCount > 1 && !isCartAddOperation && !isCartRemoveOperation && !isCartClearOperation && !isCartEmptyResponse) {
            // Calculate total CO2 from individual products in the response
            const co2Matches = text.match(/CO[₂2]\s*Impact\s*:\s*(\d+(?:\.\d+)?)\s*kg/gi);
            if (co2Matches && co2Matches.length > 0) {
                let totalCo2 = 0;
                co2Matches.forEach(match => {
                    const co2Value = parseFloat(match.match(/(\d+(?:\.\d+)?)/)[1]);
                    if (!Number.isNaN(co2Value)) {
                        totalCo2 += co2Value;
                    }
                });
                const averageCo2 = totalCo2 / co2Matches.length;
                
                this.productCO2 = totalCo2;
                this.totalCO2Impact = totalCo2;
                this.co2Label = 'Product Catalog';
                this.updateCO2Display(productCount, averageCo2);
                return;
            }
        }

        // 5. Handle other scenarios when not a cart operation (e.g., viewing a single product) - PRIORITIZED
        const impactCo2Match = text.match(/(?:🌍\s*)?CO[₂2]\s*Impact\s*:\s*(\d+(?:\.\d+)?)\s*kg/i);
        const isCheckoutResponse = /checkout|order.*summary|shipping.*method/i.test(text);
        if (impactCo2Match && !isCartAddOperation && !isCartRemoveOperation && !isCartClearOperation && !isCartEmptyResponse && !isCheckoutResponse) {
            const co2Value = parseFloat(impactCo2Match[1]);
            if (!Number.isNaN(co2Value)) {
                this.productCO2 = Math.max(0, co2Value);
                this.totalCO2Impact = this.productCO2 + this.shippingCO2;
                this.calculateCO2Savings();
                this.co2Label = this.shippingCO2 > 0 ? 'Total CO₂ Impact' : 'Product CO₂ Impact';
                this.updateCO2Display();
                return;
            }
        }

        // 4. Handle cart CO2 data from "what's in my cart" responses
        const cartCo2Match = text.match(/Total\s+CO[₂2]\s*Emissions?.*?(\d+(?:\.\d+)?)\s*kg/i);
        if (cartCo2Match && !isCartAddOperation && !isCartRemoveOperation && !isCartClearOperation && !isCartEmptyResponse) {
            const co2Value = parseFloat(cartCo2Match[1]);
            if (!Number.isNaN(co2Value)) {
                // This is cart CO2 (products only), don't add shipping
                this.productCO2 = Math.max(0, co2Value);
                this.totalCO2Impact = this.productCO2 + this.shippingCO2;
                this.calculateCO2Savings();
                this.co2Label = this.shippingCO2 > 0 ? 'Total CO₂ Impact' : 'Cart CO₂ Impact';
                this.updateCO2Display();
                return;
            }
        }

        // 4b. Handle cart CO2 from cart summary responses
        const cartSummaryMatch = text.match(/Total\s+CO[₂2]\s*impact.*?(\d+(?:\.\d+)?)\s*kg/i);
        if (cartSummaryMatch && !isCartAddOperation && !isCartRemoveOperation && !isCartClearOperation && !isCartEmptyResponse) {
            console.log('🎯 DEBUG: cartSummaryMatch found! Pattern: /Total\\s+CO[₂2]\\s*impact.*?(\\d+(?:\\.\\d+)?)\\s*kg/i');
            console.log('🎯 DEBUG: Matched value:', cartSummaryMatch[1]);
            const co2Value = parseFloat(cartSummaryMatch[1]);
            if (!Number.isNaN(co2Value)) {
                // Check if this is a checkout response (which includes shipping)
                const isCheckoutResponse = /checkout|order.*summary|shipping.*method/i.test(text);
                console.log('🎯 DEBUG: isCheckoutResponse:', isCheckoutResponse);
                console.log('🎯 DEBUG: this.shippingCO2:', this.shippingCO2);
                
                if (isCheckoutResponse) {
                    console.log('🎯 DEBUG: Processing checkout response');
                    // Backend always sends the FINAL total CO2 impact in checkout responses
                    this.totalCO2Impact = co2Value; // 194.5kg (final total)
                    
                    // If shipping is already set, calculate products by subtraction
                    if (this.shippingCO2 > 0) {
                        this.productCO2 = Math.max(0, co2Value - this.shippingCO2);
                        console.log('🎯 DEBUG: Checkout with shipping - calculated productCO2:', this.productCO2);
                    } else {
                        // Shipping will be set later - assume eco-friendly shipping 150kg
                        this.productCO2 = Math.max(0, co2Value - 150.0); // 194.5 - 150 = 44.5kg
                        this.checkoutTotalLocked = true; // Prevent recalculation when shipping is added
                        console.log('🎯 DEBUG: Checkout without shipping - assumed eco-friendly shipping, calculated productCO2:', this.productCO2);
                    }
                    console.log('🎯 DEBUG: Set totalCO2Impact to:', this.totalCO2Impact);
                    console.log('🎯 DEBUG: Set productCO2 to:', this.productCO2);
                } else {
                    console.log('🎯 DEBUG: Processing regular cart response');
                    // This is a regular cart response (products only)
                    this.productCO2 = Math.max(0, co2Value);
                    this.totalCO2Impact = this.productCO2 + this.shippingCO2;
                    console.log('🎯 DEBUG: Set productCO2 to:', this.productCO2);
                    console.log('🎯 DEBUG: Set totalCO2Impact to:', this.totalCO2Impact);
                }
                this.calculateCO2Savings();
                this.co2Label = this.shippingCO2 > 0 ? 'Total CO₂ Impact' : 'Cart CO₂ Impact';
                this.updateCO2Display();
                console.log('🎯 DEBUG: Returning after cartSummaryMatch processing');
                return;
            }
        }

        // 4. Handle a definitive "Total CO2" when not a cart operation (e.g., checkout)
        const totalCo2Match = text.match(/Total\s+CO[₂2]\s*Impact\s*:\s*(\d+(?:\.\d+)?)\s*kg/i);
        if (totalCo2Match && !isCartAddOperation && !isCartRemoveOperation && !isCartClearOperation && !isCartEmptyResponse) {
            console.log('🎯 DEBUG: totalCo2Match found! Pattern: /Total\\s+CO[₂2]\\s*Impact\\s*:\\s*(\\d+(?:\\.\\d+)?)\\s*kg/i');
            console.log('🎯 DEBUG: Matched value:', totalCo2Match[1]);
            const co2Value = parseFloat(totalCo2Match[1]);
            if (!Number.isNaN(co2Value)) {
                // Check if this is a checkout response with shipping already included
                const isCheckoutResponse = /checkout|order.*summary|shipping.*method/i.test(text);
                console.log('🎯 DEBUG: isCheckoutResponse:', isCheckoutResponse);
                console.log('🎯 DEBUG: this.shippingCO2:', this.shippingCO2);
                
                if (isCheckoutResponse) {
                    console.log('🎯 DEBUG: Processing checkout response (pattern 2)');
                    // Backend always sends the FINAL total CO2 impact in checkout responses
                    this.totalCO2Impact = co2Value; // 194.5kg (final total)
                    
                    // If shipping is already set, calculate products by subtraction
                    if (this.shippingCO2 > 0) {
                        this.productCO2 = Math.max(0, co2Value - this.shippingCO2);
                        console.log('🎯 DEBUG: Checkout with shipping - calculated productCO2 (pattern 2):', this.productCO2);
                    } else {
                        // Shipping will be set later - assume eco-friendly shipping 150kg
                        this.productCO2 = Math.max(0, co2Value - 150.0); // 194.5 - 150 = 44.5kg
                        this.checkoutTotalLocked = true; // Prevent recalculation when shipping is added
                        console.log('🎯 DEBUG: Checkout without shipping - assumed eco-friendly shipping, calculated productCO2 (pattern 2):', this.productCO2);
                    }
                    console.log('🎯 DEBUG: Set totalCO2Impact to:', this.totalCO2Impact);
                    console.log('🎯 DEBUG: Set productCO2 to:', this.productCO2);
                } else {
                    console.log('🎯 DEBUG: Processing regular response (pattern 2)');
                    // This is just product CO2, add shipping if selected
                    this.productCO2 = Math.max(0, co2Value);
                    this.totalCO2Impact = this.productCO2 + this.shippingCO2;
                    console.log('🎯 DEBUG: Set productCO2 to:', this.productCO2);
                    console.log('🎯 DEBUG: Set totalCO2Impact to:', this.totalCO2Impact);
                }
                this.calculateCO2Savings();
                this.co2Label = 'Total CO₂ Impact';
                this.updateCO2Display();
                
                // Reset the checkout command flag after processing
                this.isProcessingCheckoutCommand = false;
                console.log('🎯 DEBUG: Returning after totalCo2Match processing');
                return;
            }
        }
        
        // Reset the checkout command flag after processing
        this.isProcessingCheckoutCommand = false;
    }
    
    updateCO2Display(productCount = null, averageCo2 = null) {
        console.log('🎨 DEBUG: updateCO2Display called with:');
        console.log('  - productCount:', productCount);
        console.log('  - averageCo2:', averageCo2);
        console.log('  - this.productCO2:', this.productCO2);
        console.log('  - this.shippingCO2:', this.shippingCO2);
        console.log('  - this.totalCO2Impact:', this.totalCO2Impact);
        console.log('  - this.displayProductCO2:', this.displayProductCO2);
        
        if (this.co2SavingsElement) {
            const label = this.co2Label || 'CO₂ Impact';
            let content;
            
            if (productCount && productCount > 1) {
                content = `
                    <div class="co2-widget">
                        <div class="co2-icon">🌱</div>
                        <div class="co2-content">
                            <div class="co2-label">${label}</div>
                            <div class="co2-value">${productCount} products found</div>
                            <div class="co2-breakdown">Total CO₂: ${this.totalCO2Impact.toFixed(1)}kg</div>
                            <div class="co2-breakdown">Average CO₂: ${averageCo2.toFixed(1)}kg</div>
                        </div>
                    </div>
                `;
            } else {
                const productDisplayValue = this.displayProductCO2 !== null ? this.displayProductCO2 : this.productCO2;
                
                // If checkout is locked, calculate display total from current values
                const displayTotal = this.checkoutTotalLocked ? 
                    (this.productCO2 + this.shippingCO2) : 
                    this.totalCO2Impact;
                
                content = `
                <div class="co2-widget">
                    <div class="co2-icon">🌱</div>
                    <div class="co2-content">
                        <div class="co2-label">${label}</div>
                        <div class="co2-value">${displayTotal.toFixed(1)} kg</div>
                        ${displayTotal > 0 ? `<div class="co2-breakdown">
                            ${this.productCO2 > 0 ? `Products: ${productDisplayValue.toFixed(1)}kg` : ''}
                            ${this.shippingCO2 > 0 ? `Shipping: ${this.shippingCO2.toFixed(1)}kg` : ''}
                        </div>` : ''}
                        ${this.totalCO2Saved > 0 ? `<div class="co2-savings">Saved: ${this.totalCO2Saved.toFixed(1)}kg</div>` : ''}
                    </div>
                </div>
            `;
            }
            
            this.co2SavingsElement.innerHTML = content;
            
            this.co2SavingsElement.style.transform = 'scale(1.1)';
            setTimeout(() => {
                this.co2SavingsElement.style.transform = 'scale(1)';
            }, 200);
            
            const impactLevel = this.getCO2ImpactLevel(this.totalCO2Impact);
            this.co2SavingsElement.className = `co2-badge ${impactLevel}`;
        }
        
        // Update sustainability dashboard
        this.updateSustainabilityMetrics();
    }
    
    getCO2ImpactLevel(co2Value) {
        if (co2Value <= 50) return 'low-impact';
        if (co2Value <= 150) return 'medium-impact';
        if (co2Value <= 300) return 'high-impact';
        return 'very-high-impact';
    }

    initializeStaticShippingOptions() {
        const shippingOptions = document.querySelectorAll('.shipping-option');
        shippingOptions.forEach(option => {
            // Ensure static options also have data-shipping-method for command selection
            const name = option.querySelector('.shipping-option__name').textContent;
            option.dataset.shippingMethod = name.toLowerCase();

            option.addEventListener('click', () => {
                this._updateShippingSelection(option); // Use the new method
                
                const co2 = parseFloat(option.dataset.co2);
                const price = parseFloat(option.dataset.price);
                const days = option.dataset.days;
                // const name = option.querySelector('.shipping-option__name').textContent; // Already extracted above
                
                // Replace shipping CO2 (don't add to existing)
                this.shippingCO2 = co2;
                this.selectedShippingOption = name;
                
                // If checkout total is locked, don't recalculate - just update shipping
                if (this.checkoutTotalLocked) {
                    console.log('🔒 DEBUG: Checkout total locked - not recalculating totalCO2Impact');
                    // Keep the locked total from checkout response
                } else {
                    this.totalCO2Impact = this.productCO2 + this.shippingCO2;
                }
                
                // Calculate CO2 savings (vs worst alternatives)
                this.calculateCO2Savings();
                
                this.co2Label = 'Total CO₂ Impact';
                this.updateCO2Display();
                
                this.logAgent(`User selected: ${name} shipping (${days}, ${price}, ${co2}kg CO₂)`)
                this.sendShippingSelectionToBackend(name);
            });
        });
    }
    
    async sendShippingSelectionToBackend(shippingOption) {
        console.log('🚢 DEBUG: sendShippingSelectionToBackend called with:', shippingOption);
        console.log('🚢 DEBUG: Current values before shipping call:');
        console.log('  - productCO2:', this.productCO2);
        console.log('  - shippingCO2:', this.shippingCO2);
        console.log('  - totalCO2Impact:', this.totalCO2Impact);
        
        try {
            const response = await this.callAPI(`set shipping to ${shippingOption}`);
            // Extract the text response from the API response object
            const messageText = response.response?.response || response.response || response;
            console.log('🚢 DEBUG: Backend response:', messageText);
            console.log('🚢 DEBUG: NOT calling extractAndUpdateCO2Savings - values should remain unchanged');
            // CO2 values are already set by updateUIFromAssistant - no need to recalculate
        } catch (error) {
            console.log('🚢 DEBUG: Error in sendShippingSelectionToBackend:', error);
        }
    }
    
  _updateShippingSelection(selectedOptionElement) {
    // Handle both static shipping options and dynamic shipping-impact options
    const staticOptions = document.querySelectorAll('.shipping-option');
    const dynamicOptions = this.shippingOptionsEl ? this.shippingOptionsEl.children : [];
    
    // Clear selection from static options
    staticOptions.forEach((option) => {
      if (option === selectedOptionElement) {
        option.classList.add('selected');
      } else {
        option.classList.remove('selected');
      }
    });
    
    // Clear selection from dynamic options
    Array.from(dynamicOptions).forEach((option) => {
      if (option === selectedOptionElement) {
        option.classList.add('shipping-impact__option--selected');
      } else {
        option.classList.remove('shipping-impact__option--selected');
      }
    });
  }

  clearShippingSelection() {
    // Clear selection from all shipping options
    const staticOptions = document.querySelectorAll('.shipping-option');
    const dynamicOptions = this.shippingOptionsEl ? this.shippingOptionsEl.children : [];
    
    // Clear selection from static options
    staticOptions.forEach((option) => {
      option.classList.remove('selected');
    });
    
    // Clear selection from dynamic options
    Array.from(dynamicOptions).forEach((option) => {
      option.classList.remove('shipping-impact__option--selected');
    });
  }

  updateShippingSelectionFromCheckoutCommand(shippingMethod) {

    const normalizedShippingMethod = shippingMethod.toLowerCase();
    let selectedOptionElement = null;

    // First check static shipping options
    const staticOptions = document.querySelectorAll('.shipping-option');
    staticOptions.forEach((option) => {
      const optionMethod = option.dataset.shippingMethod;
      if (optionMethod && optionMethod.toLowerCase() === normalizedShippingMethod) {
        selectedOptionElement = option;
      }
    });

    // If not found in static options, check dynamic options
    if (!selectedOptionElement && this.shippingOptionsEl) {
      Array.from(this.shippingOptionsEl.children).forEach((option) => {
        const optionMethod = option.dataset.shippingMethod;
        if (optionMethod && optionMethod.toLowerCase() === normalizedShippingMethod) {
          selectedOptionElement = option;
        }
      });
    }

    if (selectedOptionElement) {
      this._updateShippingSelection(selectedOptionElement);
      
      // Also update CO2 values to prevent double-counting
      const co2 = parseFloat(selectedOptionElement.dataset.co2 || 0);
      const price = parseFloat(selectedOptionElement.dataset.price || 0);
      const days = selectedOptionElement.dataset.days || '';
      
      // Update shipping CO2 (replace, don't add)
      this.shippingCO2 = co2;
      this.selectedShippingOption = shippingMethod;
      this.totalCO2Impact = this.productCO2 + this.shippingCO2;
      
      // Calculate CO2 savings
      this.calculateCO2Savings();
      
      this.co2Label = 'Total CO₂ Impact';
      this.updateCO2Display();
      
    } else {
      this.logAgent(`Could not find shipping option: ${shippingMethod}`);
    }
  }
    
    renderProductsFromResponse(responseText) {
        if (!this.productGrid) {
            this.logAgent('Product grid not found, cannot render products');
            return;
        }
        
        // Extract products from AI response text
        const products = this.extractProductsFromText(responseText);
        this.logAgent(`Extracted ${products.length} products from response`);
        
        if (products.length > 0) {
            // Clear existing products
            this.productGrid.innerHTML = '';
            
            // Render each product
            products.forEach(product => {
                const productCard = this.createProductCard(product);
                this.productGrid.appendChild(productCard);
            });
            
            // Add compare buttons to the newly rendered products
            this.addComparisonButtons();
            
            this.logAgent(`Successfully rendered ${products.length} products with compare buttons`);
        } else {
            this.logAgent('No products found in response, keeping existing products');
        }
    }
    
    extractProductsFromText(text) {
        const products = [];
        
        // Split text by product sections (📦 symbols)
        const productSections = text.split(/📦/).slice(1); // Remove first empty section
        
        productSections.forEach((section, index) => {
            // Extract product name (remove markdown formatting and number prefix)
            const nameMatch = section.match(/^\s*\*?\*?(?:\d+\.\s*)?([^*\n]+?)\*?\*?\s*\n/);
            if (!nameMatch) return;
            
            const name = nameMatch[1].trim();
            
            // Extract price
            const priceMatch = section.match(/💰\s*Price:\s*\$([\d.]+)/);
            if (!priceMatch) return;
            
            const price = parseFloat(priceMatch[1]);
            
            // Extract CO2 impact
            const co2Match = section.match(/🌍\s*CO2\s*Impact:\s*([\d.]+)\s*kg/);
            if (!co2Match) return;
            
            const co2 = parseFloat(co2Match[1]);
            
            // Generate image path based on product name
            const imagePath = this.getProductImagePath(name);
            
            products.push({
                name: name,
                price: price,
                co2: co2,
                eco: Math.min(10, Math.max(1, Math.round(10 - (co2 / 10)))), // Calculate eco score based on CO2
                img: imagePath
            });
        });
        
        return products;
    }
    
    getProductImagePath(productName) {
        // Map product names to actual Online Boutique image paths
        const name = productName.toLowerCase();
        
        if (name.includes('sunglasses') || name.includes('glasses')) {
            return '/ob-images/static/img/products/sunglasses.jpg';
        } else if (name.includes('watch')) {
            return '/ob-images/static/img/products/watch.jpg';
        } else if (name.includes('loafers') || name.includes('shoes')) {
            return '/ob-images/static/img/products/loafers.jpg';
        } else if (name.includes('shirt') || name.includes('t-shirt') || name.includes('tank top')) {
            return '/ob-images/static/img/products/tank-top.jpg';
        } else if (name.includes('laptop')) {
            // Laptop not in catalog, suggest tech accessories instead
            return '/ob-images/static/img/products/watch.jpg';
        } else if (name.includes('hairdryer') || name.includes('hair dryer')) {
            return '/ob-images/static/img/products/hairdryer.jpg';
        } else if (name.includes('candle') || name.includes('holder')) {
            return '/ob-images/static/img/products/candle-holder.jpg';
        } else if (name.includes('salt') || name.includes('pepper') || name.includes('shaker')) {
            return '/ob-images/static/img/products/salt-and-pepper-shakers.jpg';
        } else if (name.includes('bamboo') || name.includes('jar')) {
            return '/ob-images/static/img/products/bamboo-glass-jar.jpg';
        } else if (name.includes('mug')) {
            return '/ob-images/static/img/products/mug.jpg';
        } else {
            // Use sunglasses as fallback instead of non-existent default.jpg
            return '/ob-images/static/img/products/sunglasses.jpg';
        }
    }
    
    addComparisonButtons() {
        const productCards = document.querySelectorAll('.product-card');
        productCards.forEach(card => {
            const compareBtn = document.createElement('button');
            compareBtn.className = 'compare-btn';
            compareBtn.innerHTML = '⚖️ Compare Eco-Impact';
            compareBtn.onclick = () => this.showEcoComparison(card);
            card.appendChild(compareBtn);
        });
    }
    
    showEcoComparison(productCard) {
        // **FIXED**: Using the correct selectors that were added in createProductCard
        const productName = productCard.querySelector('.product-name')?.textContent || 'Product';
        const productPrice = parseFloat(productCard.querySelector('.product-price')?.textContent.replace('$', '') || 0);
        const productCO2 = parseFloat(productCard.querySelector('.product-co2')?.textContent.replace('CO₂: ', '').replace('kg', '') || 0);
        const productEcoScore = parseInt(productCard.querySelector('.product-eco')?.textContent.replace('Eco ', '').replace('/10', '') || 0);
        
        const modal = document.createElement('div');
        modal.className = 'comparison-modal';
        modal.innerHTML = `
            <div class="comparison-content">
                <div class="comparison-header">
                    <h3>🌱 Eco-Impact Comparison: ${productName}</h3>
                    <button class="close-btn" onclick="this.closest('.comparison-modal').remove()">×</button>
                </div>
                <div class="comparison-grid">
                    <div class="comparison-card less-eco">
                        <div class="comparison-title">❌ Less Eco-Friendly Alternative</div>
                        <div class="comparison-product">Standard ${productName}</div>
                        <div class="comparison-metrics">
                            <div class="metric">
                                <span class="metric-label">Price:</span>
                                <span class="metric-value">$${(productPrice * 0.8).toFixed(2)}</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">CO₂ Emissions:</span>
                                <span class="metric-value bad">${(productCO2 * 2.5).toFixed(1)} kg</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Eco Score:</span>
                                <span class="metric-value bad">${Math.max(1, productEcoScore - 4)}/10</span>
                            </div>
                        </div>
                        <div class="comparison-impact">
                            <strong>Impact:</strong> Higher carbon footprint, non-sustainable materials
                        </div>
                    </div>
                    
                    <div class="comparison-card current">
                        <div class="comparison-title">✅ Your Selection</div>
                        <div class="comparison-product">${productName}</div>
                        <div class="comparison-metrics">
                            <div class="metric">
                                <span class="metric-label">Price:</span>
                                <span class="metric-value">$${productPrice.toFixed(2)}</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">CO₂ Emissions:</span>
                                <span class="metric-value good">${productCO2.toFixed(1)} kg</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Eco Score:</span>
                                <span class="metric-value good">${productEcoScore}/10</span>
                            </div>
                        </div>
                        <div class="comparison-impact">
                            <strong>Impact:</strong> Lower carbon footprint, sustainable materials
                        </div>
                    </div>
                    
                    <div class="comparison-card more-eco">
                        <div class="comparison-title">🌱 More Eco-Friendly Alternative</div>
                        <div class="comparison-product">Premium Eco ${productName}</div>
                        <div class="comparison-metrics">
                            <div class="metric">
                                <span class="metric-label">Price:</span>
                                <span class="metric-value">$${(productPrice * 1.3).toFixed(2)}</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">CO₂ Emissions:</span>
                                <span class="metric-value excellent">${(productCO2 * 0.4).toFixed(1)} kg</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Eco Score:</span>
                                <span class="metric-value excellent">${Math.min(10, productEcoScore + 2)}/10</span>
                            </div>
                        </div>
                        <div class="comparison-impact">
                            <strong>Impact:</strong> Minimal carbon footprint, 100% sustainable materials
                        </div>
                    </div>
                </div>
                <div class="comparison-summary">
                    <h4>📊 Environmental Impact Summary</h4>
                    <div class="summary-stats">
                        <div class="stat">
                            <span class="stat-label">CO₂ Savings vs Standard:</span>
                            <span class="stat-value savings">${(productCO2 * 1.5).toFixed(1)} kg saved</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Eco Score Improvement:</span>
                            <span class="stat-value improvement">+${Math.min(3, productEcoScore - 2)} points</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Sustainability Level:</span>
                            <span class="stat-value level">${productEcoScore >= 7 ? 'Excellent' : productEcoScore >= 5 ? 'Good' : 'Fair'}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        this.logAgent(`Comparison Agent: Generated eco-impact comparison for ${productName}`);
        this.logAgent(`CO2 Calculator Agent: Calculated ${(productCO2 * 1.5).toFixed(1)}kg CO₂ savings vs standard alternative`);
    }
    
    async checkServerConnectivity() {
        try {
            const response = await fetch('/api/info', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateConnectionStatus('connected', '🟢', 'Connected');
                this.logAgent(`Host Agent: Connected to server - ${data.name} v${data.version}`);
                this.logAgent(`Host Agent: Available agents: ${data.agents.join(', ')}`);
            } else {
                this.updateConnectionStatus('disconnected', '🔴', `Server Error (${response.status})`);
                this.logAgent(`Host Agent: Server connection issue - HTTP ${response.status}`);
            }
        } catch (error) {
            this.updateConnectionStatus('disconnected', '🔴', 'Disconnected');
            this.logAgent(`Host Agent: Unable to connect to server - ${error.message}`);
            this.logAgent(`Host Agent: Please ensure the application is running on the correct port`);
        }
    }
    
    updateConnectionStatus(status, icon, text) {
        if (this.connectionStatus) {
            this.connectionStatus.className = `connection-status ${status}`;
            this.connectionStatus.querySelector('.status-icon').textContent = icon;
            this.connectionStatus.querySelector('.status-text').textContent = text;
        }
    }
    
    initializeSustainabilityDashboard() {
        // Ensure all sustainability metrics start at 0
        this.totalCO2Saved = 0;
        this.ecoProductsCount = 0;
        this.sustainabilityScore = 0;
        this.greenSavings = 0;
        
        this.updateSustainabilityMetrics();
        this.updateEcoTips();
    }
    
    updateSustainabilityMetrics() {
        if (this.totalCO2SavedEl) {
            this.totalCO2SavedEl.textContent = `${this.totalCO2Saved.toFixed(1)} kg`;
        }
        
        if (this.ecoProductsCountEl) {
            this.ecoProductsCountEl.textContent = this.ecoProductsCount;
        }
        
        // Calculate sustainability score based on CO2 savings (0-100 scale)
        // Max possible savings: 100kg (products) + 1000kg (shipping) = 1100kg
        const maxPossibleSavings = 1100;
        this.sustainabilityScore = Math.min(Math.round((this.totalCO2Saved / maxPossibleSavings) * 100), 100);
        
        if (this.sustainabilityScoreEl) {
            this.sustainabilityScoreEl.textContent = `${this.sustainabilityScore}/100`;
        }
        
        // Calculate green savings based on actual CO2 savings ($0.10 per kg CO₂ saved)
        this.greenSavings = this.totalCO2Saved * 0.1;
        
        if (this.greenSavingsEl) {
            this.greenSavingsEl.textContent = `$${this.greenSavings.toFixed(2)}`;
        }
        
        this.updateEcoProgress();
    }
    
    updateEcoProgress() {
        const progressPercentage = Math.min((this.totalCO2Saved / this.monthlyEcoGoal) * 100, 100);
        
        if (this.ecoProgressFillEl) {
            this.ecoProgressFillEl.style.width = `${progressPercentage}%`;
        }
        
        if (this.ecoProgressTextEl) {
            this.ecoProgressTextEl.textContent = `${Math.round(progressPercentage)}% Complete`;
        }
    }
    
    updateEcoTips() {
        const tips = [
            "Choose eco-friendly shipping options",
            "Look for products with low CO₂ impact", 
            "Consider sustainable alternatives",
            "Bundle orders to reduce shipping emissions",
            "Support brands with green certifications",
            "Opt for renewable energy sources"
        ];
        
        if (this.ecoTipsEl) {
            // Show 3 random tips
            const shuffledTips = tips.sort(() => 0.5 - Math.random());
            const selectedTips = shuffledTips.slice(0, 3);
            
            this.ecoTipsEl.innerHTML = selectedTips
                .map(tip => `<div class="tip-item">${tip}</div>`)
                .join('');
        }
    }
    
    updateSustainabilityFromProduct(product) {
        // Update metrics when a product is added
        if (product.eco >= 7) {
            this.ecoProductsCount++;
        }
        
        // Sustainability score and green savings are now calculated in updateSustainabilityMetrics()
        // based on actual CO2 savings rather than individual product eco ratings
        
        this.updateSustainabilityMetrics();
    }
    
    resetSustainabilityMetrics() {
        this.ecoProductsCount = 0;
        this.sustainabilityScore = 0;
        this.greenSavings = 0;
        // totalCO2Saved is reset in the calling function (extractAndUpdateCO2Savings)
        this.updateSustainabilityMetrics();
    }
    
    handleCartOperation(operation, response) {
        const text = response.replace(/\*\*/g, '');

        // Skip processing if this is a checkout response
        const isCheckoutResponse = /checkout|order.*summary|shipping.*method/i.test(text);
        if (isCheckoutResponse) {
            return;
        }

        if (operation === 'add') {
            // Look for cart total or individual product CO2
            const cartTotalMatch = text.match(/Total\s+CO[₂2]\s*:\s*(\d+(?:\.\d+)?)\s*kg/i);
            if (cartTotalMatch && cartTotalMatch[1]) {
                this.productCO2 = parseFloat(cartTotalMatch[1]);
            } else {
                // Look for cart summary CO2 impact
                const cartImpactMatch = text.match(/Total\s+CO[₂2]\s*impact.*?(\d+(?:\.\d+)?)\s*kg/i);
                if (cartImpactMatch && cartImpactMatch[1]) {
                    this.productCO2 = parseFloat(cartImpactMatch[1]);
            } else {
                // Look for individual product CO2 and add it
                const productCo2Match = text.match(/CO[₂2]\s*Impact\s*:\s*(\d+(?:\.\d+)?)\s*kg/i);
                if (productCo2Match && productCo2Match[1]) {
                    this.productCO2 = parseFloat(productCo2Match[1]);
                    }
                }
            }
        } else if (operation === 'remove' || operation === 'clear') {
            // For clear operations or when cart is empty, reset everything
            if (operation === 'clear' || /cart.*empty|empty.*cart|cart.*is.*empty/i.test(text)) {
                this.productCO2 = 0;
                this.totalCO2Impact = 0;
                this.totalCO2Saved = 0;
                this.co2Label = 'CO₂ Impact';
                this.resetSustainabilityMetrics();
                this.updateCO2Display();
                return; // Don't continue with normal CO2 calculations
            } else {
                // Look for updated cart total after removal
                const cartTotalMatch = text.match(/Total\s+CO[₂2]\s*:\s*(\d+(?:\.\d+)?)\s*kg/i);
                if (cartTotalMatch && cartTotalMatch[1]) {
                    this.productCO2 = parseFloat(cartTotalMatch[1]);
                } else {
                    // If no cart total found, assume cart is empty
                    this.productCO2 = 0;
                }
            }
        }

        // Update total CO2 impact (consumption)
        this.totalCO2Impact = this.productCO2 + this.shippingCO2;

        // Calculate CO2 savings (vs worst alternatives)
        this.calculateCO2Savings();

        this.co2Label = 'Total CO₂ Impact';
        this.updateCO2Display();
    }
    
    calculateCO2Savings() {
        // Calculate savings compared to worst alternatives
        let totalSavings = 0;
        
        // Product savings: compare to worst-case products (assume 100kg baseline for worst products)
        const worstProductCO2 = 100; // Worst-case product baseline
        const productSavings = Math.max(0, worstProductCO2 - this.productCO2);
        
        // Shipping savings: only calculate if shipping is actually selected
        let shippingSavings = 0;
        if (this.selectedShippingOption) {
            // Compare to Express (worst option = 1000kg)
            const worstShippingCO2 = 1000;
            shippingSavings = Math.max(0, worstShippingCO2 - this.shippingCO2);
        }
        
        this.totalCO2Saved = productSavings + shippingSavings;
        
        // Update sustainability dashboard immediately
        this.updateSustainabilityMetrics();
    }
}

// Initialize the assistant when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new CO2ShoppingAssistant();
});
