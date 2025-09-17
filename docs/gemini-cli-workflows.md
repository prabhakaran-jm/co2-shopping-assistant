# 🌟 Gemini CLI Workflows for CO2-Aware Shopping Assistant

This guide demonstrates how to use Google's Gemini CLI to interact with the CO2-Aware Shopping Assistant, perform AI-powered operations, and integrate with the deployment.

## 📋 Prerequisites

### **Install Gemini CLI**
```bash
# Install Gemini CLI
pip install google-generativeai

# Or install from source
git clone https://github.com/google/generative-ai-python.git
cd generative-ai-python
pip install -e .

# Verify installation
python -c "import google.generativeai as genai; print('Gemini CLI installed successfully')"
```

### **Configure API Key**
```bash
# Set up API key
export GOOGLE_AI_API_KEY="your-gemini-api-key"

# Or configure in Python
python -c "
import google.generativeai as genai
genai.configure(api_key='your-gemini-api-key')
print('API key configured successfully')
"
```

## 🚀 Basic Gemini CLI Workflows

### **1. Direct AI Interaction**

#### **Chat with CO2-Aware Assistant**
```bash
# Create a simple chat script
cat > chat_with_assistant.py << 'EOF'
import google.generativeai as genai
import requests
import json

# Configure Gemini
genai.configure(api_key='your-gemini-api-key')
model = genai.GenerativeModel('gemini-2.0-flash')

# CO2-Aware Shopping Assistant endpoint
ASSISTANT_URL = "http://assistant.cloudcarta.com/api/chat"

def chat_with_assistant(message, session_id="cli-session"):
    """Chat with the CO2-Aware Shopping Assistant"""
    try:
        response = requests.post(ASSISTANT_URL, json={
            "message": message,
            "session_id": session_id
        })
        
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "No response received")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error connecting to assistant: {str(e)}"

def main():
    print("🌱 CO2-Aware Shopping Assistant CLI")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
            
        # Get response from assistant
        response = chat_with_assistant(user_input)
        print(f"Assistant: {response}\n")

if __name__ == "__main__":
    main()
EOF

# Run the chat interface
python chat_with_assistant.py
```

#### **Environmental Impact Analysis**
```bash
# Create environmental impact analyzer
cat > analyze_environmental_impact.py << 'EOF'
import google.generativeai as genai
import requests
import json

genai.configure(api_key='your-gemini-api-key')
model = genai.GenerativeModel('gemini-2.0-flash')

def analyze_environmental_impact(product_query):
    """Analyze environmental impact of products"""
    
    # Get products from assistant
    response = requests.post("http://assistant.cloudcarta.com/api/chat", json={
        "message": f"Find eco-friendly {product_query} with CO2 impact data",
        "session_id": "env-analysis"
    })
    
    if response.status_code == 200:
        data = response.json()
        products_info = data.get("response", "")
        
        # Use Gemini to analyze environmental impact
        prompt = f"""
        Analyze the environmental impact of these products and provide insights:
        
        Products: {products_info}
        
        Please provide:
        1. Environmental impact summary
        2. CO2 emission comparison
        3. Sustainability recommendations
        4. Eco-friendly alternatives
        """
        
        analysis = model.generate_content(prompt)
        return analysis.text
    else:
        return f"Error: {response.status_code}"

def main():
    product = input("Enter product to analyze (e.g., 'electronics', 'clothing'): ")
    analysis = analyze_environmental_impact(product)
    print(f"\n🌍 Environmental Impact Analysis for {product}:")
    print(analysis)

if __name__ == "__main__":
    main()
EOF

# Run environmental impact analysis
python analyze_environmental_impact.py
```

### **2. AI Agent Interaction**

#### **Direct Agent Communication**
```bash
# Create agent communication script
cat > communicate_with_agents.py << 'EOF'
import google.generativeai as genai
import requests
import json

genai.configure(api_key='your-gemini-api-key')
model = genai.GenerativeModel('gemini-2.0-flash')

def communicate_with_agent(agent_name, task):
    """Communicate directly with specific AI agents"""
    
    response = requests.post("http://assistant.cloudcarta.com/api/a2a/send", json={
        "agent_name": agent_name,
        "task": {"message": task},
        "message_type": "task_request",
        "timeout": 30.0
    })
    
    if response.status_code == 200:
        data = response.json()
        return data.get("response", "No response received")
    else:
        return f"Error: {response.status_code} - {response.text}"

def get_agent_status():
    """Get status of all AI agents"""
    
    response = requests.get("http://assistant.cloudcarta.com/api/a2a/agents")
    
    if response.status_code == 200:
        data = response.json()
        agents = data.get("agents", [])
        
        print("🤖 AI Agent Status:")
        for agent in agents:
            print(f"  {agent['name']}: {agent['status']} ({agent['health']})")
        
        return agents
    else:
        print(f"Error getting agent status: {response.status_code}")
        return []

def main():
    print("🤖 CO2-Aware Shopping Assistant - Agent Communication")
    
    # Show available agents
    agents = get_agent_status()
    
    while True:
        print("\nAvailable agents:")
        for i, agent in enumerate(agents):
            print(f"  {i+1}. {agent['name']}")
        print("  0. Exit")
        
        choice = input("\nSelect agent (number): ")
        
        if choice == '0':
            break
            
        try:
            agent_index = int(choice) - 1
            if 0 <= agent_index < len(agents):
                agent_name = agents[agent_index]['name']
                task = input(f"Task for {agent_name}: ")
                
                response = communicate_with_agent(agent_name, task)
                print(f"\n{agent_name} Response: {response}")
            else:
                print("Invalid selection")
        except ValueError:
            print("Please enter a valid number")

if __name__ == "__main__":
    main()
EOF

# Run agent communication
python communicate_with_agents.py
```

### **3. MCP Transport Interaction**

#### **MCP Tool Discovery and Execution**
```bash
# Create MCP interaction script
cat > mcp_interaction.py << 'EOF'
import google.generativeai as genai
import requests
import json

genai.configure(api_key='your-gemini-api-key')
model = genai.GenerativeModel('gemini-2.0-flash')

def list_mcp_tools(server_name):
    """List available MCP tools"""
    
    response = requests.get(f"http://assistant.cloudcarta.com/api/mcp/{server_name}/tools")
    
    if response.status_code == 200:
        data = response.json()
        tools = data.get("tools", [])
        
        print(f"🛠️ Available tools in {server_name} MCP server:")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
        
        return tools
    else:
        print(f"Error: {response.status_code}")
        return []

def execute_mcp_tool(server_name, tool_name, arguments):
    """Execute MCP tool"""
    
    response = requests.post(
        f"http://assistant.cloudcarta.com/api/mcp/{server_name}/tools/{tool_name}",
        json=arguments
    )
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return f"Error: {response.status_code} - {response.text}"

def get_mcp_resources(server_name):
    """Get MCP resources"""
    
    response = requests.get(f"http://assistant.cloudcarta.com/api/mcp/{server_name}/resources")
    
    if response.status_code == 200:
        data = response.json()
        resources = data.get("resources", [])
        
        print(f"📚 Available resources in {server_name} MCP server:")
        for resource in resources:
            print(f"  - {resource['uri']}: {resource['description']}")
        
        return resources
    else:
        print(f"Error: {response.status_code}")
        return []

def main():
    print("🛠️ CO2-Aware Shopping Assistant - MCP Interaction")
    
    servers = ["boutique", "co2"]
    
    while True:
        print("\nAvailable MCP servers:")
        for i, server in enumerate(servers):
            print(f"  {i+1}. {server}")
        print("  0. Exit")
        
        choice = input("\nSelect server (number): ")
        
        if choice == '0':
            break
            
        try:
            server_index = int(choice) - 1
            if 0 <= server_index < len(servers):
                server_name = servers[server_index]
                
                print(f"\nServer: {server_name}")
                print("1. List tools")
                print("2. List resources")
                print("3. Execute tool")
                print("0. Back")
                
                action = input("Select action: ")
                
                if action == '1':
                    list_mcp_tools(server_name)
                elif action == '2':
                    get_mcp_resources(server_name)
                elif action == '3':
                    tools = list_mcp_tools(server_name)
                    if tools:
                        tool_name = input("Enter tool name: ")
                        # Simple argument input (can be enhanced)
                        arguments = {}
                        print("Enter arguments (press Enter to finish):")
                        while True:
                            key = input("Key: ")
                            if not key:
                                break
                            value = input("Value: ")
                            arguments[key] = value
                        
                        result = execute_mcp_tool(server_name, tool_name, arguments)
                        print(f"Result: {json.dumps(result, indent=2)}")
            else:
                print("Invalid selection")
        except ValueError:
            print("Please enter a valid number")

if __name__ == "__main__":
    main()
EOF

# Run MCP interaction
python mcp_interaction.py
```

## 🔧 Advanced Gemini CLI Workflows

### **1. Intelligent Product Recommendations**

#### **AI-Powered Product Search**
```bash
# Create intelligent product search
cat > intelligent_product_search.py << 'EOF'
import google.generativeai as genai
import requests
import json

genai.configure(api_key='your-gemini-api-key')
model = genai.GenerativeModel('gemini-2.0-flash')

def intelligent_product_search(user_query):
    """Use Gemini to enhance product search"""
    
    # First, get basic products from assistant
    response = requests.post("http://assistant.cloudcarta.com/api/chat", json={
        "message": f"Find products for: {user_query}",
        "session_id": "intelligent-search"
    })
    
    if response.status_code == 200:
        data = response.json()
        basic_results = data.get("response", "")
        
        # Use Gemini to enhance the results
        prompt = f"""
        User query: {user_query}
        
        Basic product results: {basic_results}
        
        Please enhance these results by:
        1. Providing more detailed product descriptions
        2. Adding environmental impact analysis
        3. Suggesting eco-friendly alternatives
        4. Providing sustainability tips
        5. Ranking products by environmental friendliness
        
        Format the response in a user-friendly way with clear sections.
        """
        
        enhanced_results = model.generate_content(prompt)
        return enhanced_results.text
    else:
        return f"Error: {response.status_code}"

def main():
    print("🔍 Intelligent Product Search with Gemini")
    
    while True:
        query = input("\nWhat are you looking for? (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
            
        print("\n🔍 Searching...")
        results = intelligent_product_search(query)
        print(f"\n{results}")

if __name__ == "__main__":
    main()
EOF

# Run intelligent product search
python intelligent_product_search.py
```

### **2. Environmental Impact Analysis**

#### **CO2 Impact Calculator**
```bash
# Create CO2 impact calculator
cat > co2_impact_calculator.py << 'EOF'
import google.generativeai as genai
import requests
import json

genai.configure(api_key='your-gemini-api-key')
model = genai.GenerativeModel('gemini-2.0-flash')

def calculate_co2_impact(product_data):
    """Calculate CO2 impact using MCP tools and Gemini analysis"""
    
    # Use CO2 MCP tool
    response = requests.post(
        "http://assistant.cloudcarta.com/api/mcp/co2/tools/calculate_co2_impact",
        json=product_data
    )
    
    if response.status_code == 200:
        co2_data = response.json()
        
        # Use Gemini to analyze and explain the results
        prompt = f"""
        CO2 Impact Data: {json.dumps(co2_data, indent=2)}
        
        Please provide a comprehensive analysis including:
        1. Environmental impact summary
        2. Comparison to industry averages
        3. Environmental equivalencies (e.g., "equivalent to X miles driven")
        4. Sustainability recommendations
        5. Ways to reduce environmental impact
        6. Eco-friendly alternatives
        
        Make the analysis easy to understand for consumers.
        """
        
        analysis = model.generate_content(prompt)
        return {
            "co2_data": co2_data,
            "analysis": analysis.text
        }
    else:
        return f"Error: {response.status_code}"

def main():
    print("🌍 CO2 Impact Calculator with Gemini Analysis")
    
    while True:
        print("\nEnter product information:")
        product_type = input("Product type (e.g., electronics, clothing): ")
        price = float(input("Price ($): "))
        quantity = int(input("Quantity: "))
        
        product_data = {
            "product_type": product_type,
            "price": price,
            "quantity": quantity
        }
        
        print("\nCalculating CO2 impact...")
        result = calculate_co2_impact(product_data)
        
        if isinstance(result, dict):
            print(f"\n📊 CO2 Impact Data:")
            print(json.dumps(result["co2_data"], indent=2))
            print(f"\n🌍 Environmental Analysis:")
            print(result["analysis"])
        else:
            print(f"Error: {result}")
        
        continue_search = input("\nCalculate another product? (y/n): ")
        if continue_search.lower() != 'y':
            break

if __name__ == "__main__":
    main()
EOF

# Run CO2 impact calculator
python co2_impact_calculator.py
```

### **3. Shopping Assistant Integration**

#### **Complete Shopping Workflow**
```bash
# Create complete shopping workflow
cat > complete_shopping_workflow.py << 'EOF'
import google.generativeai as genai
import requests
import json

genai.configure(api_key='your-gemini-api-key')
model = genai.GenerativeModel('gemini-2.0-flash')

class ShoppingWorkflow:
    def __init__(self):
        self.session_id = "gemini-cli-session"
        self.cart_items = []
    
    def search_products(self, query):
        """Search for products"""
        response = requests.post("http://assistant.cloudcarta.com/api/chat", json={
            "message": f"Find eco-friendly {query}",
            "session_id": self.session_id
        })
        
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "")
        else:
            return f"Error: {response.status_code}"
    
    def analyze_with_gemini(self, products_info, user_preferences):
        """Use Gemini to analyze products"""
        prompt = f"""
        Products found: {products_info}
        User preferences: {user_preferences}
        
        Please analyze these products and provide:
        1. Top 3 recommendations with reasons
        2. Environmental impact comparison
        3. Price vs. sustainability analysis
        4. Personalized recommendations based on preferences
        """
        
        analysis = model.generate_content(prompt)
        return analysis.text
    
    def add_to_cart(self, product_id, quantity=1):
        """Add product to cart"""
        response = requests.post("http://assistant.cloudcarta.com/api/chat", json={
            "message": f"Add product {product_id} with quantity {quantity} to cart",
            "session_id": self.session_id
        })
        
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "")
        else:
            return f"Error: {response.status_code}"
    
    def get_cart_summary(self):
        """Get cart summary with CO2 impact"""
        response = requests.post("http://assistant.cloudcarta.com/api/chat", json={
            "message": "Show me my cart with CO2 impact",
            "session_id": self.session_id
        })
        
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "")
        else:
            return f"Error: {response.status_code}"
    
    def checkout(self, address, payment_info):
        """Complete checkout"""
        response = requests.post("http://assistant.cloudcarta.com/api/chat", json={
            "message": f"Checkout with address: {address}, payment: {payment_info}",
            "session_id": self.session_id
        })
        
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "")
        else:
            return f"Error: {response.status_code}"

def main():
    print("🛒 Complete Shopping Workflow with Gemini")
    
    workflow = ShoppingWorkflow()
    
    # Get user preferences
    print("Let's personalize your shopping experience!")
    preferences = input("Tell me your preferences (e.g., 'eco-friendly', 'budget-conscious', 'premium quality'): ")
    
    while True:
        print("\n🛒 Shopping Options:")
        print("1. Search products")
        print("2. View cart")
        print("3. Checkout")
        print("0. Exit")
        
        choice = input("Select option: ")
        
        if choice == '1':
            query = input("What are you looking for? ")
            print("\n🔍 Searching for products...")
            products = workflow.search_products(query)
            print(f"\nProducts found:\n{products}")
            
            # Use Gemini to analyze
            print("\n🤖 Gemini Analysis:")
            analysis = workflow.analyze_with_gemini(products, preferences)
            print(analysis)
            
            # Option to add to cart
            add_to_cart = input("\nAdd any products to cart? (y/n): ")
            if add_to_cart.lower() == 'y':
                product_id = input("Enter product ID: ")
                quantity = int(input("Enter quantity: "))
                result = workflow.add_to_cart(product_id, quantity)
                print(f"Cart update: {result}")
        
        elif choice == '2':
            print("\n🛒 Your Cart:")
            cart_summary = workflow.get_cart_summary()
            print(cart_summary)
        
        elif choice == '3':
            print("\n💳 Checkout")
            address = input("Enter shipping address: ")
            payment_info = input("Enter payment info: ")
            result = workflow.checkout(address, payment_info)
            print(f"Checkout result: {result}")
            break
        
        elif choice == '0':
            break
        
        else:
            print("Invalid option")

if __name__ == "__main__":
    main()
EOF

# Run complete shopping workflow
python complete_shopping_workflow.py
```

## 🎯 Specialized Workflows

### **1. Sustainability Advisor**

#### **Personal Sustainability Advisor**
```bash
# Create sustainability advisor
cat > sustainability_advisor.py << 'EOF'
import google.generativeai as genai
import requests
import json

genai.configure(api_key='your-gemini-api-key')
model = genai.GenerativeModel('gemini-2.0-flash')

def get_sustainability_recommendations(user_profile):
    """Get personalized sustainability recommendations"""
    
    prompt = f"""
    User Profile: {user_profile}
    
    Please provide personalized sustainability recommendations including:
    1. Shopping habits to reduce environmental impact
    2. Product categories to prioritize for eco-friendly options
    3. Lifestyle changes for sustainability
    4. Carbon footprint reduction strategies
    5. Sustainable shopping tips
    6. Environmental impact education
    
    Make recommendations specific to the user's profile and lifestyle.
    """
    
    recommendations = model.generate_content(prompt)
    return recommendations.text

def analyze_shopping_patterns(cart_history):
    """Analyze shopping patterns for sustainability"""
    
    prompt = f"""
    Shopping History: {cart_history}
    
    Analyze this shopping history for:
    1. Environmental impact trends
    2. Sustainability score
    3. Areas for improvement
    4. Eco-friendly alternatives
    5. Carbon footprint reduction opportunities
    
    Provide actionable insights and recommendations.
    """
    
    analysis = model.generate_content(prompt)
    return analysis.text

def main():
    print("🌱 Personal Sustainability Advisor")
    
    # Get user profile
    print("Let's create your sustainability profile!")
    lifestyle = input("Describe your lifestyle (e.g., 'busy professional', 'eco-conscious', 'budget-focused'): ")
    interests = input("What are your interests? (e.g., 'technology', 'fashion', 'home improvement'): ")
    sustainability_goals = input("What are your sustainability goals? (e.g., 'reduce carbon footprint', 'support eco-friendly brands'): ")
    
    user_profile = f"Lifestyle: {lifestyle}, Interests: {interests}, Goals: {sustainability_goals}"
    
    print("\n🤖 Generating personalized recommendations...")
    recommendations = get_sustainability_recommendations(user_profile)
    print(f"\n🌍 Your Personalized Sustainability Recommendations:")
    print(recommendations)
    
    # Analyze shopping patterns
    print("\n📊 Shopping Pattern Analysis")
    print("Enter your recent shopping history (or 'skip' to skip):")
    cart_history = input("Shopping history: ")
    
    if cart_history.lower() != 'skip':
        analysis = analyze_shopping_patterns(cart_history)
        print(f"\n📈 Shopping Pattern Analysis:")
        print(analysis)

if __name__ == "__main__":
    main()
EOF

# Run sustainability advisor
python sustainability_advisor.py
```

### **2. Environmental Education**

#### **Environmental Learning Assistant**
```bash
# Create environmental learning assistant
cat > environmental_learning.py << 'EOF'
import google.generativeai as genai
import requests
import json

genai.configure(api_key='your-gemini-api-key')
model = genai.GenerativeModel('gemini-2.0-flash')

def explain_environmental_concept(concept):
    """Explain environmental concepts in simple terms"""
    
    prompt = f"""
    Explain the environmental concept: {concept}
    
    Please provide:
    1. Simple, easy-to-understand explanation
    2. Real-world examples
    3. Impact on daily life
    4. How to make a positive difference
    5. Related concepts to learn about
    
    Make it educational and engaging for someone new to environmental topics.
    """
    
    explanation = model.generate_content(prompt)
    return explanation.text

def calculate_environmental_equivalencies(co2_amount):
    """Convert CO2 amounts to understandable equivalencies"""
    
    prompt = f"""
    CO2 Amount: {co2_amount} kg
    
    Convert this CO2 amount to understandable equivalencies such as:
    1. Miles driven in a car
    2. Trees needed to offset
    3. Energy consumption
    4. Other relatable comparisons
    
    Make it easy to understand the environmental impact.
    """
    
    equivalencies = model.generate_content(prompt)
    return equivalencies.text

def main():
    print("📚 Environmental Learning Assistant")
    
    while True:
        print("\n📖 Learning Options:")
        print("1. Learn about environmental concepts")
        print("2. Calculate environmental equivalencies")
        print("3. Get sustainability tips")
        print("0. Exit")
        
        choice = input("Select option: ")
        
        if choice == '1':
            concept = input("What environmental concept would you like to learn about? ")
            print("\n🤖 Explaining concept...")
            explanation = explain_environmental_concept(concept)
            print(f"\n📚 {concept}:")
            print(explanation)
        
        elif choice == '2':
            co2_amount = input("Enter CO2 amount in kg: ")
            print("\n🤖 Calculating equivalencies...")
            equivalencies = calculate_environmental_equivalencies(co2_amount)
            print(f"\n🌍 Environmental Equivalencies:")
            print(equivalencies)
        
        elif choice == '3':
            # Get sustainability tips
            response = requests.post("http://assistant.cloudcarta.com/api/chat", json={
                "message": "Give me 5 sustainability tips for daily life",
                "session_id": "learning-session"
            })
            
            if response.status_code == 200:
                data = response.json()
                tips = data.get("response", "")
                print(f"\n💡 Sustainability Tips:")
                print(tips)
            else:
                print(f"Error: {response.status_code}")
        
        elif choice == '0':
            break
        
        else:
            print("Invalid option")

if __name__ == "__main__":
    main()
EOF

# Run environmental learning assistant
python environmental_learning.py
```

## 🔧 Integration Examples

### **1. CI/CD Integration**

#### **Automated Testing with Gemini**
```bash
# Create automated testing script
cat > automated_testing.py << 'EOF'
import google.generativeai as genai
import requests
import json
import time

genai.configure(api_key='your-gemini-api-key')
model = genai.GenerativeModel('gemini-2.0-flash')

def test_assistant_functionality():
    """Test CO2-Aware Shopping Assistant functionality"""
    
    test_cases = [
        "Find eco-friendly electronics under $200",
        "Add a laptop to my cart",
        "Show me my cart with CO2 impact",
        "Calculate CO2 impact for a smartphone",
        "Get sustainability recommendations"
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"Testing: {test_case}")
        
        response = requests.post("http://assistant.cloudcarta.com/api/chat", json={
            "message": test_case,
            "session_id": f"test-{int(time.time())}"
        })
        
        if response.status_code == 200:
            data = response.json()
            success = data.get("success", False)
            results.append({
                "test": test_case,
                "success": success,
                "response": data.get("response", "")[:100] + "..." if len(data.get("response", "")) > 100 else data.get("response", "")
            })
        else:
            results.append({
                "test": test_case,
                "success": False,
                "response": f"Error: {response.status_code}"
            })
    
    return results

def analyze_test_results(results):
    """Use Gemini to analyze test results"""
    
    prompt = f"""
    Test Results: {json.dumps(results, indent=2)}
    
    Analyze these test results and provide:
    1. Overall system health assessment
    2. Identified issues or problems
    3. Recommendations for improvement
    4. Performance insights
    5. Suggestions for additional testing
    
    Focus on actionable insights for improving the system.
    """
    
    analysis = model.generate_content(prompt)
    return analysis.text

def main():
    print("🧪 Automated Testing with Gemini Analysis")
    
    print("Running functionality tests...")
    results = test_assistant_functionality()
    
    print("\n📊 Test Results:")
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status}: {result['test']}")
        print(f"    Response: {result['response']}")
    
    print("\n🤖 Gemini Analysis:")
    analysis = analyze_test_results(results)
    print(analysis)

if __name__ == "__main__":
    main()
EOF

# Run automated testing
python automated_testing.py
```

### **2. Monitoring Integration**

#### **Intelligent Monitoring**
```bash
# Create intelligent monitoring script
cat > intelligent_monitoring.py << 'EOF'
import google.generativeai as genai
import requests
import json
import time

genai.configure(api_key='your-gemini-api-key')
model = genai.GenerativeModel('gemini-2.0-flash')

def get_system_metrics():
    """Get system metrics"""
    
    metrics = {}
    
    # Get A2A status
    try:
        response = requests.get("http://assistant.cloudcarta.com/api/a2a/status")
        if response.status_code == 200:
            metrics["a2a_status"] = response.json()
    except:
        metrics["a2a_status"] = "Error"
    
    # Get MCP status
    try:
        response = requests.get("http://assistant.cloudcarta.com/api/mcp")
        if response.status_code == 200:
            metrics["mcp_status"] = response.json()
    except:
        metrics["mcp_status"] = "Error"
    
    # Get health status
    try:
        response = requests.get("http://assistant.cloudcarta.com/api/health")
        if response.status_code == 200:
            metrics["health_status"] = response.json()
    except:
        metrics["health_status"] = "Error"
    
    return metrics

def analyze_system_health(metrics):
    """Use Gemini to analyze system health"""
    
    prompt = f"""
    System Metrics: {json.dumps(metrics, indent=2)}
    
    Analyze the system health and provide:
    1. Overall system status assessment
    2. Identified issues or anomalies
    3. Performance insights
    4. Recommendations for optimization
    5. Alerts or warnings if needed
    
    Focus on actionable insights for system maintenance.
    """
    
    analysis = model.generate_content(prompt)
    return analysis.text

def main():
    print("📊 Intelligent System Monitoring with Gemini")
    
    while True:
        print(f"\n🔄 Monitoring cycle at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        metrics = get_system_metrics()
        analysis = analyze_system_health(metrics)
        
        print("📈 System Analysis:")
        print(analysis)
        
        # Wait for next cycle
        print("\n⏰ Waiting 60 seconds for next monitoring cycle...")
        time.sleep(60)

if __name__ == "__main__":
    main()
EOF

# Run intelligent monitoring
python intelligent_monitoring.py
```

## 📚 Best Practices

### **1. Error Handling**
```python
# Always handle errors gracefully
try:
    response = requests.post(url, json=data, timeout=30)
    if response.status_code == 200:
        return response.json()
    else:
        return f"HTTP Error: {response.status_code}"
except requests.exceptions.Timeout:
    return "Request timeout"
except requests.exceptions.ConnectionError:
    return "Connection error"
except Exception as e:
    return f"Unexpected error: {str(e)}"
```

### **2. Rate Limiting**
```python
# Implement rate limiting for API calls
import time

def rate_limited_request(url, data, delay=1):
    time.sleep(delay)  # Wait between requests
    return requests.post(url, json=data)
```

### **3. Configuration Management**
```python
# Use environment variables for configuration
import os

API_KEY = os.getenv('GOOGLE_AI_API_KEY')
ASSISTANT_URL = os.getenv('ASSISTANT_URL', 'http://assistant.cloudcarta.com/api/chat')
```

## 🚀 Advanced Use Cases

### **1. Batch Processing**
```bash
# Process multiple requests in batch
cat > batch_processing.py << 'EOF'
import google.generativeai as genai
import requests
import json
import concurrent.futures

genai.configure(api_key='your-gemini-api-key')
model = genai.GenerativeModel('gemini-2.0-flash')

def process_request(request_data):
    """Process a single request"""
    response = requests.post("http://assistant.cloudcarta.com/api/chat", json=request_data)
    return response.json() if response.status_code == 200 else {"error": response.status_code}

def batch_process_requests(requests_list):
    """Process multiple requests in parallel"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_request, req) for req in requests_list]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    return results

# Example usage
requests_list = [
    {"message": "Find eco-friendly laptops", "session_id": "batch-1"},
    {"message": "Calculate CO2 impact for smartphones", "session_id": "batch-2"},
    {"message": "Get sustainability tips", "session_id": "batch-3"}
]

results = batch_process_requests(requests_list)
print(json.dumps(results, indent=2))
EOF
```

### **2. Data Analysis**
```bash
# Analyze shopping data with Gemini
cat > data_analysis.py << 'EOF'
import google.generativeai as genai
import requests
import json
import pandas as pd

genai.configure(api_key='your-gemini-api-key')
model = genai.GenerativeModel('gemini-2.0-flash')

def analyze_shopping_data(data):
    """Analyze shopping data with Gemini"""
    
    prompt = f"""
    Shopping Data: {json.dumps(data, indent=2)}
    
    Analyze this shopping data and provide:
    1. Shopping pattern insights
    2. Environmental impact trends
    3. Cost vs. sustainability analysis
    4. Recommendations for improvement
    5. Predictive insights
    
    Provide actionable business insights.
    """
    
    analysis = model.generate_content(prompt)
    return analysis.text

# Example usage with sample data
sample_data = {
    "products": [
        {"name": "Eco Laptop", "price": 1200, "co2_impact": 45},
        {"name": "Green Phone", "price": 800, "co2_impact": 32},
        {"name": "Sustainable Headphones", "price": 200, "co2_impact": 8}
    ],
    "total_co2": 85,
    "total_cost": 2200
}

analysis = analyze_shopping_data(sample_data)
print(analysis)
EOF
```

This comprehensive guide demonstrates how to use Google's Gemini CLI to interact with the CO2-Aware Shopping Assistant, providing AI-powered insights, analysis, and automation capabilities for enhanced user experience and system management.
