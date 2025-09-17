#!/usr/bin/env python3

"""
🔍 CO2-Aware Shopping Assistant - Intelligent Product Search
This script demonstrates intelligent product search using Google's Gemini CLI
"""

import google.generativeai as genai
import requests
import json
import os
import sys
from typing import Dict, Any, List

# Configuration
ASSISTANT_URL = os.getenv('ASSISTANT_URL', 'http://assistant.cloudcarta.com/api/chat')
MCP_URL = os.getenv('MCP_URL', 'http://assistant.cloudcarta.com/api/mcp')
GEMINI_API_KEY = os.getenv('GOOGLE_AI_API_KEY')

class IntelligentProductSearch:
    def __init__(self):
        """Initialize the intelligent product search"""
        if not GEMINI_API_KEY:
            print("❌ GOOGLE_AI_API_KEY environment variable is not set")
            print("Please set it with: export GOOGLE_AI_API_KEY='your-gemini-api-key'")
            sys.exit(1)
        
        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        print("🔍 Intelligent Product Search initialized!")
        print("Using Gemini 2.0 Flash for enhanced search capabilities")
    
    def search_products(self, query: str, filters: Dict[str, Any] = None) -> str:
        """Search for products using the assistant"""
        try:
            # Build search message with filters
            search_message = f"Find eco-friendly {query}"
            if filters:
                if 'max_price' in filters:
                    search_message += f" under ${filters['max_price']}"
                if 'category' in filters:
                    search_message += f" in {filters['category']} category"
                if 'min_eco_score' in filters:
                    search_message += f" with eco-score above {filters['min_eco_score']}"
            
            response = requests.post(ASSISTANT_URL, json={
                "message": search_message,
                "session_id": "intelligent-search"
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "No products found")
            else:
                return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Search failed: {str(e)}"
    
    def enhance_search_results(self, products: str, user_query: str, user_preferences: str = "") -> str:
        """Enhance search results using Gemini"""
        try:
            prompt = f"""
            User Query: {user_query}
            User Preferences: {user_preferences}
            Product Results: {products}
            
            Please enhance these search results by:
            1. Providing detailed product descriptions
            2. Adding environmental impact analysis
            3. Suggesting eco-friendly alternatives
            4. Providing sustainability tips
            5. Ranking products by environmental friendliness
            6. Adding price vs. sustainability analysis
            7. Suggesting complementary products
            
            Format the response in a user-friendly way with clear sections.
            Make it informative and actionable for sustainable shopping.
            """
            
            enhanced_results = self.model.generate_content(prompt)
            return enhanced_results.text
        except Exception as e:
            return f"Enhancement failed: {str(e)}"
    
    def get_sustainability_recommendations(self, products: str) -> str:
        """Get sustainability recommendations for products"""
        try:
            prompt = f"""
            Products: {products}
            
            Provide sustainability recommendations including:
            1. Environmental impact summary
            2. Carbon footprint analysis
            3. Sustainable alternatives
            4. Eco-friendly usage tips
            5. Recycling and disposal guidance
            6. Long-term environmental benefits
            
            Focus on actionable advice for sustainable consumption.
            """
            
            recommendations = self.model.generate_content(prompt)
            return recommendations.text
        except Exception as e:
            return f"Recommendations failed: {str(e)}"
    
    def compare_products(self, products: str) -> str:
        """Compare products for sustainability"""
        try:
            prompt = f"""
            Products to compare: {products}
            
            Provide a comprehensive comparison including:
            1. Environmental impact comparison
            2. Carbon footprint analysis
            3. Sustainability score ranking
            4. Price vs. environmental value
            5. Long-term environmental benefits
            6. Recommendation based on sustainability
            
            Present the comparison in a clear, easy-to-understand format.
            """
            
            comparison = self.model.generate_content(prompt)
            return comparison.text
        except Exception as e:
            return f"Comparison failed: {str(e)}"
    
    def get_eco_friendly_alternatives(self, product_query: str) -> str:
        """Get eco-friendly alternatives for products"""
        try:
            prompt = f"""
            Product query: {product_query}
            
            Suggest eco-friendly alternatives including:
            1. Sustainable product options
            2. Environmentally conscious brands
            3. Green alternatives with lower carbon footprint
            4. Recycled or upcycled options
            5. Local and sustainable alternatives
            6. Tips for making existing products more eco-friendly
            
            Provide specific, actionable alternatives.
            """
            
            alternatives = self.model.generate_content(prompt)
            return alternatives.text
        except Exception as e:
            return f"Alternatives failed: {str(e)}"
    
    def analyze_shopping_trends(self, search_history: List[str]) -> str:
        """Analyze shopping trends for sustainability insights"""
        try:
            prompt = f"""
            Shopping search history: {', '.join(search_history)}
            
            Analyze shopping trends and provide insights:
            1. Environmental impact trends
            2. Sustainability preferences
            3. Areas for improvement
            4. Eco-friendly shopping patterns
            5. Recommendations for more sustainable choices
            6. Carbon footprint reduction opportunities
            
            Provide actionable insights for sustainable shopping.
            """
            
            analysis = self.model.generate_content(prompt)
            return analysis.text
        except Exception as e:
            return f"Trend analysis failed: {str(e)}"
    
    def run_interactive_search(self):
        """Run the interactive product search interface"""
        print("\n🔍 Intelligent Product Search - CO2-Aware Shopping Assistant")
        print("=" * 60)
        print("Search for eco-friendly products with AI-enhanced results!")
        print("Type 'help' for commands, 'quit' to exit")
        print("")
        
        search_history = []
        
        while True:
            try:
                user_input = input("Search for: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("🔍 Thank you for using Intelligent Product Search!")
                    break
                
                if user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                if user_input.lower() == 'trends':
                    if search_history:
                        print("\n📊 Shopping Trend Analysis:")
                        analysis = self.analyze_shopping_trends(search_history)
                        print(analysis)
                    else:
                        print("No search history to analyze yet.")
                    continue
                
                # Store search history
                search_history.append(user_input)
                
                # Get user preferences
                preferences = input("Any preferences? (price range, category, eco-score, or press Enter): ").strip()
                
                # Parse filters
                filters = {}
                if preferences:
                    if 'under' in preferences.lower() or '$' in preferences:
                        # Extract price
                        import re
                        price_match = re.search(r'\$?(\d+)', preferences)
                        if price_match:
                            filters['max_price'] = int(price_match.group(1))
                    
                    if 'category' in preferences.lower():
                        # Extract category
                        category_match = re.search(r'category[:\s]+(\w+)', preferences.lower())
                        if category_match:
                            filters['category'] = category_match.group(1)
                
                print(f"\n🔍 Searching for: {user_input}")
                if filters:
                    print(f"Filters: {filters}")
                
                # Search for products
                products = self.search_products(user_input, filters)
                print(f"\n📦 Search Results:")
                print(products)
                
                # Enhance results with Gemini
                print(f"\n🌟 AI-Enhanced Results:")
                enhanced_results = self.enhance_search_results(products, user_input, preferences)
                print(enhanced_results)
                
                # Get sustainability recommendations
                print(f"\n🌍 Sustainability Recommendations:")
                recommendations = self.get_sustainability_recommendations(products)
                print(recommendations)
                
                # Ask if user wants to compare products
                compare = input("\nCompare these products? (y/n): ").strip().lower()
                if compare == 'y':
                    print(f"\n⚖️ Product Comparison:")
                    comparison = self.compare_products(products)
                    print(comparison)
                
                # Ask if user wants eco-friendly alternatives
                alternatives = input("\nGet eco-friendly alternatives? (y/n): ").strip().lower()
                if alternatives == 'y':
                    print(f"\n🌱 Eco-Friendly Alternatives:")
                    eco_alternatives = self.get_eco_friendly_alternatives(user_input)
                    print(eco_alternatives)
                
                print("")
                
            except KeyboardInterrupt:
                print("\n\n🔍 Search interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Please try again or type 'quit' to exit.")
    
    def show_help(self):
        """Show help information"""
        print("\n📚 Available Commands:")
        print("  help     - Show this help message")
        print("  trends   - Analyze your shopping trends")
        print("  quit     - Exit the search")
        print("")
        print("💡 Search Examples:")
        print("  - 'laptops under $1000'")
        print("  - 'eco-friendly clothing'")
        print("  - 'sustainable home products'")
        print("  - 'green electronics'")
        print("  - 'organic food products'")
        print("")
        print("🎯 Filter Examples:")
        print("  - 'under $500'")
        print("  - 'category electronics'")
        print("  - 'eco-score above 8'")
        print("")

def main():
    """Main function"""
    print("🚀 Starting Intelligent Product Search...")
    
    try:
        search = IntelligentProductSearch()
        search.run_interactive_search()
    except Exception as e:
        print(f"❌ Failed to start search: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
