#!/usr/bin/env python3

"""
🌱 CO2-Aware Shopping Assistant - Interactive Chat Interface
This script provides an interactive chat interface using Google's Gemini CLI
"""

import google.generativeai as genai
import requests
import json
import os
import sys
from typing import Dict, Any

# Configuration
ASSISTANT_URL = os.getenv('ASSISTANT_URL', 'http://assistant.cloudcarta.com/api/chat')
GEMINI_API_KEY = os.getenv('GOOGLE_AI_API_KEY')

class CO2ShoppingAssistant:
    def __init__(self):
        """Initialize the CO2-Aware Shopping Assistant"""
        if not GEMINI_API_KEY:
            print("❌ GOOGLE_AI_API_KEY environment variable is not set")
            print("Please set it with: export GOOGLE_AI_API_KEY='your-gemini-api-key'")
            sys.exit(1)
        
        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Session management
        self.session_id = "gemini-cli-session"
        self.conversation_history = []
        
        print("🌱 CO2-Aware Shopping Assistant initialized!")
        print("Using Gemini 2.0 Flash for enhanced AI capabilities")
    
    def chat_with_assistant(self, message: str) -> str:
        """Chat with the CO2-Aware Shopping Assistant"""
        try:
            response = requests.post(ASSISTANT_URL, json={
                "message": message,
                "session_id": self.session_id
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "No response received")
            else:
                return f"Error: {response.status_code} - {response.text}"
        except requests.exceptions.Timeout:
            return "Request timeout - the assistant is taking too long to respond"
        except requests.exceptions.ConnectionError:
            return "Connection error - cannot reach the assistant"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    def enhance_with_gemini(self, response: str, user_message: str) -> str:
        """Enhance the assistant's response using Gemini"""
        try:
            prompt = f"""
            User message: {user_message}
            Assistant response: {response}
            
            Please enhance this response by:
            1. Adding more detailed environmental impact information
            2. Providing additional sustainability tips
            3. Suggesting eco-friendly alternatives
            4. Explaining the environmental benefits
            5. Adding educational content about sustainability
            
            Make the response more informative and engaging while maintaining the original information.
            """
            
            enhanced_response = self.model.generate_content(prompt)
            return enhanced_response.text
        except Exception as e:
            return f"Gemini enhancement failed: {str(e)}"
    
    def get_environmental_tips(self) -> str:
        """Get environmental tips using Gemini"""
        try:
            prompt = """
            Provide 5 practical environmental tips for sustainable shopping:
            1. Focus on eco-friendly products
            2. Consider carbon footprint
            3. Support sustainable brands
            4. Reduce packaging waste
            5. Choose local products
            
            Make each tip actionable and explain the environmental impact.
            """
            
            tips = self.model.generate_content(prompt)
            return tips.text
        except Exception as e:
            return f"Failed to get environmental tips: {str(e)}"
    
    def analyze_shopping_behavior(self, user_input: str) -> str:
        """Analyze user's shopping behavior for sustainability insights"""
        try:
            prompt = f"""
            User shopping request: {user_input}
            
            Analyze this shopping request for sustainability insights:
            1. Environmental impact assessment
            2. Eco-friendly alternatives
            3. Sustainability recommendations
            4. Carbon footprint considerations
            5. Green shopping tips
            
            Provide actionable insights for making more sustainable choices.
            """
            
            analysis = self.model.generate_content(prompt)
            return analysis.text
        except Exception as e:
            return f"Analysis failed: {str(e)}"
    
    def run_interactive_chat(self):
        """Run the interactive chat interface"""
        print("\n🌱 CO2-Aware Shopping Assistant - Interactive Chat")
        print("=" * 50)
        print("Type 'help' for commands, 'quit' to exit")
        print("Ask me about eco-friendly products, CO2 impact, or sustainability!")
        print("")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("🌱 Thank you for using the CO2-Aware Shopping Assistant!")
                    print("Remember: Every sustainable choice makes a difference! 🌍")
                    break
                
                if user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                if user_input.lower() == 'tips':
                    print("\n🌍 Environmental Tips:")
                    tips = self.get_environmental_tips()
                    print(tips)
                    continue
                
                if user_input.lower() == 'analyze':
                    if self.conversation_history:
                        print("\n📊 Shopping Behavior Analysis:")
                        analysis = self.analyze_shopping_behavior(" ".join(self.conversation_history[-3:]))
                        print(analysis)
                    else:
                        print("No conversation history to analyze yet.")
                    continue
                
                # Store conversation history
                self.conversation_history.append(user_input)
                
                print("\n🤖 Assistant: ", end="", flush=True)
                
                # Get response from assistant
                response = self.chat_with_assistant(user_input)
                print(response)
                
                # Enhance with Gemini
                print("\n🌟 Enhanced with Gemini:")
                enhanced_response = self.enhance_with_gemini(response, user_input)
                print(enhanced_response)
                
                print("")
                
            except KeyboardInterrupt:
                print("\n\n🌱 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Please try again or type 'quit' to exit.")
    
    def show_help(self):
        """Show help information"""
        print("\n📚 Available Commands:")
        print("  help     - Show this help message")
        print("  tips     - Get environmental shopping tips")
        print("  analyze  - Analyze your shopping behavior")
        print("  quit     - Exit the chat")
        print("")
        print("💡 Example Questions:")
        print("  - 'Find eco-friendly laptops under $1000'")
        print("  - 'What's the CO2 impact of this smartphone?'")
        print("  - 'Show me sustainable clothing options'")
        print("  - 'Compare the environmental impact of these products'")
        print("  - 'Add this eco-friendly product to my cart'")
        print("")

def main():
    """Main function"""
    print("🚀 Starting CO2-Aware Shopping Assistant Chat Interface...")
    
    try:
        assistant = CO2ShoppingAssistant()
        assistant.run_interactive_chat()
    except Exception as e:
        print(f"❌ Failed to start assistant: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
