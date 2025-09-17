#!/bin/bash

# 🔌 CO2-Aware Shopping Assistant - cURL API Examples
# This script demonstrates how to interact with the CO2-Aware Shopping Assistant using cURL

set -e

# Configuration
ASSISTANT_URL="http://assistant.cloudcarta.com"
API_BASE="$ASSISTANT_URL/api"

echo "🔌 CO2-Aware Shopping Assistant - cURL API Examples"
echo "=================================================="

# Function to make API calls with error handling
make_api_call() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    local description="$4"
    
    echo "🔍 $description"
    echo "Endpoint: $method $endpoint"
    if [ -n "$data" ]; then
        echo "Data: $data"
    fi
    echo "---"
    
    if [ "$method" = "GET" ]; then
        curl -s -X GET "$endpoint" | jq '.' 2>/dev/null || curl -s -X GET "$endpoint"
    else
        curl -s -X "$method" "$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" | jq '.' 2>/dev/null || curl -s -X "$method" "$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data"
    fi
    
    echo ""
    echo "Press Enter to continue..."
    read -r
    echo ""
}

# 1. Health Check
echo "🏥 1. Health Check"
echo "=================="

make_api_call "GET" "$API_BASE/health" "" "Check system health"

# 2. Main Chat Interface
echo "💬 2. Main Chat Interface"
echo "========================"

make_api_call "POST" "$API_BASE/chat" '{"message": "Find eco-friendly laptops under $1000", "session_id": "curl-demo"}' "Chat with the assistant"

make_api_call "POST" "$API_BASE/chat" '{"message": "What is the CO2 impact of a smartphone?", "session_id": "curl-demo"}' "Ask about CO2 impact"

make_api_call "POST" "$API_BASE/chat" '{"message": "Add a sustainable laptop to my cart", "session_id": "curl-demo"}' "Add product to cart"

# 3. A2A Protocol Endpoints
echo "🤖 3. A2A Protocol Endpoints"
echo "==========================="

make_api_call "GET" "$API_BASE/a2a/status" "" "Get A2A protocol status"

make_api_call "GET" "$API_BASE/a2a/agents" "" "List all registered agents"

make_api_call "GET" "$API_BASE/a2a/agents/ProductDiscoveryAgent/status" "" "Get Product Discovery Agent status"

make_api_call "POST" "$API_BASE/a2a/send" '{"agent_name": "ProductDiscoveryAgent", "task": {"message": "Find eco-friendly products"}, "message_type": "task_request", "timeout": 30.0}' "Send message to specific agent"

make_api_call "POST" "$API_BASE/a2a/broadcast" '{"message_type": "health_check", "payload": {"check": "status"}, "exclude_agents": []}' "Send broadcast message"

make_api_call "GET" "$API_BASE/a2a/health" "" "Get A2A protocol health"

# 4. MCP Transport Endpoints
echo "🔗 4. MCP Transport Endpoints"
echo "============================="

make_api_call "GET" "$API_BASE/mcp" "" "Get MCP server information"

make_api_call "GET" "$API_BASE/mcp/boutique/tools" "" "List Boutique MCP tools"

make_api_call "GET" "$API_BASE/mcp/co2/tools" "" "List CO2 MCP tools"

make_api_call "POST" "$API_BASE/mcp/co2/tools/calculate_co2_impact" '{"product_type": "electronics", "price": 500, "quantity": 1, "manufacturing_location": "global", "transport_distance": 1000}' "Calculate CO2 impact"

make_api_call "POST" "$API_BASE/mcp/boutique/tools/product_search" '{"query": "laptops", "category": "electronics", "max_price": 1000, "limit": 5}' "Search products"

make_api_call "GET" "$API_BASE/mcp/boutique/resources" "" "List Boutique MCP resources"

make_api_call "GET" "$API_BASE/mcp/boutique/resources/catalog" "" "Read product catalog"

make_api_call "GET" "$API_BASE/mcp/co2/resources" "" "List CO2 MCP resources"

make_api_call "GET" "$API_BASE/mcp/co2/resources/emission_factors" "" "Read emission factors"

make_api_call "GET" "$API_BASE/mcp/boutique/prompts" "" "List Boutique MCP prompts"

make_api_call "POST" "$API_BASE/mcp/boutique/prompts/product_search_prompt" '{"user_request": "Find eco-friendly laptops"}' "Render product search prompt"

# 5. ADK Integration Endpoints
echo "🌟 5. ADK Integration Endpoints"
echo "==============================="

make_api_call "POST" "$API_BASE/adk-chat" '{"message": "Hello ADK agent, help me find sustainable products", "session_id": "adk-demo"}' "Chat with ADK agent"

# 6. Advanced Examples
echo "⚡ 6. Advanced Examples"
echo "======================"

# Complex product search with filters
make_api_call "POST" "$API_BASE/chat" '{"message": "Find eco-friendly electronics under $800 with high sustainability rating", "session_id": "advanced-demo"}' "Advanced product search"

# Cart management workflow
make_api_call "POST" "$API_BASE/chat" '{"message": "Show me my cart with CO2 impact", "session_id": "advanced-demo"}' "View cart with CO2 impact"

# Checkout process
make_api_call "POST" "$API_BASE/chat" '{"message": "Checkout with eco-friendly shipping", "session_id": "advanced-demo"}' "Eco-friendly checkout"

# Product comparison
make_api_call "POST" "$API_BASE/chat" '{"message": "Compare the environmental impact of these laptops", "session_id": "advanced-demo"}' "Product comparison"

# 7. Error Handling Examples
echo "🛠️ 7. Error Handling Examples"
echo "============================="

make_api_call "POST" "$API_BASE/chat" '{"message": "", "session_id": "error-demo"}' "Empty message (should handle gracefully)"

make_api_call "GET" "$API_BASE/nonexistent" "" "Non-existent endpoint (should return 404)"

make_api_call "POST" "$API_BASE/a2a/send" '{"agent_name": "NonExistentAgent", "task": {"message": "test"}}' "Non-existent agent (should handle gracefully)"

# 8. Performance Testing
echo "📊 8. Performance Testing"
echo "========================"

echo "Testing response times..."
for i in {1..5}; do
    echo "Request $i:"
    time curl -s -X POST "$API_BASE/chat" \
        -H "Content-Type: application/json" \
        -d '{"message": "Quick test", "session_id": "perf-test"}' > /dev/null
done

# 9. Batch Operations
echo "📦 9. Batch Operations"
echo "====================="

echo "Running batch operations..."
for query in "laptops" "smartphones" "headphones" "tablets" "smartwatches"; do
    echo "Searching for: $query"
    make_api_call "POST" "$API_BASE/chat" "{\"message\": \"Find eco-friendly $query\", \"session_id\": \"batch-demo\"}" "Batch search: $query"
done

# 10. Integration Examples
echo "🔗 10. Integration Examples"
echo "=========================="

# Complete shopping workflow
echo "Complete shopping workflow:"
echo "1. Search for products"
make_api_call "POST" "$API_BASE/chat" '{"message": "Find sustainable laptops", "session_id": "workflow-demo"}' "Step 1: Search products"

echo "2. Add to cart"
make_api_call "POST" "$API_BASE/chat" '{"message": "Add the most eco-friendly laptop to my cart", "session_id": "workflow-demo"}' "Step 2: Add to cart"

echo "3. View cart"
make_api_call "POST" "$API_BASE/chat" '{"message": "Show my cart with CO2 impact", "session_id": "workflow-demo"}' "Step 3: View cart"

echo "4. Checkout"
make_api_call "POST" "$API_BASE/chat" '{"message": "Checkout with sustainable shipping", "session_id": "workflow-demo"}' "Step 4: Checkout"

echo "🎉 cURL API examples completed!"
echo ""
echo "📚 Next steps:"
echo "   - Try the Python API client: python python-api-client.py"
echo "   - Import the Postman collection: postman-collection.json"
echo "   - Check the JavaScript client: javascript-api-client.js"
echo ""
echo "🔗 Useful resources:"
echo "   - Live demo: https://assistant.cloudcarta.com/"
echo "   - API documentation: $API_BASE/docs"
echo "   - Repository: https://github.com/prabhakaran-jm/co2-shopping-assistant"
echo ""
echo "💡 Tips:"
echo "   - Use jq for better JSON formatting: curl ... | jq '.'"
echo "   - Add -v flag for verbose output: curl -v ..."
echo "   - Use -w flag for timing: curl -w '@curl-format.txt' ..."
echo "   - Save responses: curl ... > response.json"
