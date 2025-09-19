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
        
        // Add before/after comparison functionality
        this.addComparisonButtons();
        
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
                console.error('Retry error:', e);
            } finally {
                this.retry.inFlight = false;
                this.sendButton.disabled = false;
            }
        }, this.retry.cooldownMs);
        return true;
    }
    
    renderMarkdown(text) {
        let html = text.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" style="max-width: 200px; height: auto; border-radius: 8px; margin: 5px 0;" />');
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/\n/g, '<br>');
        return html;
    }

    updateUIFromAssistant(text) {
        const normalized = text.replace(/\*\*/g, '');
        
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
    }

    renderShippingOptionsFromText(text) {
        if (!this.shippingPanel || !this.shippingOptionsEl) return;
        this.shippingPanel.style.display = 'block';

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
                this.selectedShippingOption = o.name;
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
        return card;
    }
    
    // **FIXED**: This is the single, corrected version of the function.
    extractAndUpdateCO2Savings(response) {
        // Normalize: remove markdown bold so regex matches labels like **Total CO2**
        const text = response.replace(/\*\*/g, '');

        // 1. Reset state after a successful payment or cart clearing
        if (/Payment\s+Successful|Order\s+Confirmed|cart\s+has\s+been\s+cleared/i.test(text)) {
            this.totalCO2Saved = 0;
            this.productCO2 = 0;
            this.shippingCO2 = 0;
            this.selectedShippingOption = null;
            this.co2Label = 'CO₂';
            this.updateCO2Display();
            return;
        }

        const isCartAddOperation = /add.*cart|cart.*add/i.test(this.lastUserMessage || '');

        // 2. Handle Product Addition to Cart (PRIORITY 1)
        if (isCartAddOperation) {
            // First, look for the "Total CO2" from the cart summary. This is the accumulated value.
            const cartTotalMatch = text.match(/Total\s+CO[₂2]\s*:\s*(\d+(?:\.\d+)?)\s*kg/i);
            
            if (cartTotalMatch && cartTotalMatch[1]) {
                const totalProductCO2 = parseFloat(cartTotalMatch[1]);
                if (!Number.isNaN(totalProductCO2)) {
                    // Set the productCO2 state to the new ACCUMULATED total from the cart.
                    this.productCO2 = totalProductCO2;
                    
                    // Add the accumulated product CO2 to the existing shipping CO2.
                    this.totalCO2Saved = this.productCO2 + this.shippingCO2;
                    
                    this.co2Label = 'Total CO₂';
                    this.updateCO2Display();
                    return; // The correct value has been found and updated.
                }
            }
        }

        // 3. Handle other scenarios when not adding to cart (e.g., viewing a single product)
        // This part of the logic now runs only if it's NOT a cart addition.
        const impactCo2Match = text.match(/(?:🌍\s*)?CO[₂2]\s*Impact\s*:\s*(\d+(?:\.\d+)?)\s*kg/i);
        if (impactCo2Match && !isCartAddOperation) {
            const co2Value = parseFloat(impactCo2Match[1]);
            if (!Number.isNaN(co2Value)) {
                this.productCO2 = Math.max(0, co2Value);
                this.totalCO2Saved = this.productCO2 + this.shippingCO2;
                this.co2Label = this.shippingCO2 > 0 ? 'Total CO₂' : 'Product CO₂';
                this.updateCO2Display();
                return;
            }
        }

        // 4. Handle a definitive "Total CO2" when not adding to cart (e.g., checkout)
        const totalCo2Match = text.match(/Total\s+CO[₂2]\s*:\s*(\d+(?:\.\d+)?)\s*kg/i);
        if (totalCo2Match && !isCartAddOperation) {
            const co2Value = parseFloat(totalCo2Match[1]);
            if (!Number.isNaN(co2Value)) {
                // Overwrite the total, as this is a definitive summary from the backend
                this.totalCO2Saved = Math.max(0, co2Value);
                this.co2Label = 'Total CO₂';
                this.updateCO2Display();
                return;
            }
        }
    }
    
    updateCO2Display() {
        if (this.co2SavingsElement) {
            const label = this.co2Label || 'CO₂';
            this.co2SavingsElement.innerHTML = `
                <div class="co2-widget">
                    <div class="co2-icon">🌱</div>
                    <div class="co2-content">
                        <div class="co2-label">${label}</div>
                        <div class="co2-value">${this.totalCO2Saved.toFixed(1)} kg</div>
                        ${this.totalCO2Saved > 0 ? `<div class="co2-breakdown">
                            ${this.productCO2 > 0 ? `Products: ${this.productCO2.toFixed(1)}kg` : ''}
                            ${this.shippingCO2 > 0 ? `Shipping: ${this.shippingCO2.toFixed(1)}kg` : ''}
                        </div>` : ''}
                    </div>
                </div>
            `;
            
            this.co2SavingsElement.style.transform = 'scale(1.1)';
            setTimeout(() => {
                this.co2SavingsElement.style.transform = 'scale(1)';
            }, 200);
            
            const impactLevel = this.getCO2ImpactLevel(this.totalCO2Saved);
            this.co2SavingsElement.className = `co2-badge ${impactLevel}`;
        }
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
            option.addEventListener('click', () => {
                shippingOptions.forEach(opt => opt.classList.remove('selected'));
                option.classList.add('selected');
                
                const co2 = parseFloat(option.dataset.co2);
                const price = parseFloat(option.dataset.price);
                const days = option.dataset.days;
                const name = option.querySelector('.shipping-option__name').textContent;
                
                this.shippingCO2 = co2;
                this.selectedShippingOption = name;
                this.totalCO2Saved = this.productCO2 + this.shippingCO2;
                this.co2Label = 'Total CO₂';
                this.updateCO2Display();
                
                this.logAgent(`User selected: ${name} shipping (${days}, $${price}, ${co2}kg CO₂)`);
                this.sendShippingSelectionToBackend(name);
            });
        });
    }
    
    async sendShippingSelectionToBackend(shippingOption) {
        try {
            await this.callAPI(`set shipping to ${shippingOption}`);
        } catch (error) {
            console.error("Failed to send shipping selection to backend:", error);
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
}

// Initialize the assistant when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new CO2ShoppingAssistant();
});