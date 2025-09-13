import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Using gemini-1.5-flash as specified, which is a good choice for speed
    model = genai.GenerativeModel('gemini-1.5-flash') 
else:
    print("Warning: GEMINI_API_KEY not found in environment variables")
    # You might want to raise an error or exit here in a production app
    # For now, it will return None from parse_message_with_gemini if key is missing

# Master Prompt for task extraction - REFINED VERSION
MASTER_PROMPT = """
You are PingPlan, an intelligent and precise task-parsing AI assistant for a WhatsApp bot.
Your mission is to process user messages and extract structured task information.

**Your response MUST be ONLY one of the following:**
1.  A valid JSON object (Python dictionary format).
2.  The literal string "null" (without quotes), if the message is not an actionable task.

**JSON Object Structure (when applicable):**
* **"task_description"**: The main, clear description of the task or action.
    * **Rule:** This field is REQUIRED and must NOT be empty.
* **"deadline"**: The specific date, time, or relative timeframe for completion.
    * **Rule:** Extract as precisely as possible (e.g., "Monday 9 PM", "March 15th"). If no deadline is explicitly mentioned or clearly inferable, set this value to an empty string "".
* **"project_name"**: The associated project, course, subject, or context.
    * **Rule:** Extract concise names (e.g., "CS101", "Marketing Presentation", "Groceries"). If no project/context is mentioned or clearly inferable, set this value to an empty string "".

**CRITICAL DECISION RULE (When to return "null"):**
You **MUST** return "null" if the user's message falls into any of these categories:
* **Non-Actionable Phrases:** Greetings (e.g., "hi", "hello"), expressions of gratitude (e.g., "thanks", "thank you"), farewells (e.g., "bye"), or general conversation.
* **Questions:** Any message that is clearly a question (e.g., "What's up?", "How are you?").
* **Bot Commands:** Messages that are clearly meant as commands for the bot itself (e.g., "show my tasks", "delete 1", "help"). These are handled by the main application, not by you.
* **Ambiguous/Empty:** Messages that are too vague, too short, or simply do not contain a discernible task.

**Your Goal for Testing and Debugging:**
Aim for extreme precision. If there's any doubt it's a task, return "null". This will help in testing the `null` path and ensuring the bot's fallback messages are triggered correctly when you intend them to be.

**EXAMPLES (Observe both JSON and "null" responses):**

User message: "Submit the physics report by Sunday at 9pm"
Your response:
{"task_description": "Submit the physics report", "deadline": "Sunday at 9pm", "project_name": "physics"}

User message: "don't forget to buy groceries after work"
Your response:
{"task_description": "buy groceries after work", "deadline": "", "project_name": "groceries"}

User message: "finish the presentation"
Your response:
{"task_description": "finish the presentation", "deadline": "", "project_name": ""}

User message: "Check on the project status"
Your response:
{"task_description": "Check on the project status", "deadline": "", "project_name": ""}

User message: "thank you so much for your help!"
Your response:
null

User message: "hello PingPlan"
Your response:
null

User message: "show my tasks"
Your response:
null

User message: "What should I do today?"
Your response:
null

User message: "Okay, sounds good"
Your response:
null
"""

def parse_message_with_gemini(user_message):
    """
    Parse a user message using Gemini AI to extract task information.
    
    Args:
        user_message (str): The raw message from the user
        
    Returns:
        dict or None: Parsed task data with keys: task_description, deadline, project_name
                      Returns None if parsing fails or message is not a task
    """
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not configured")
        return None
    
    try:
        # Combine master prompt with user message for Gemini
        # Added explicit "User message:" and "Your response:" for clarity to the model
        full_prompt = MASTER_PROMPT + "\n\nUser message: \"" + user_message + "\"\nYour response:"
        
        # Generate content using Gemini
        response = model.generate_content(full_prompt)
        
        # Extract the response text and clean potential markdown
        response_text = response.text.strip()
        if response_text.startswith('```json'):
            response_text = response_text.replace('```json', '').replace('```', '').strip()
        elif response_text.startswith('```'):
            response_text = response_text.replace('```', '').strip()
        
        # --- NEW LOGIC: Check for 'null' response from Gemini ---
        if response_text.lower() == 'null':
            print(f"Gemini classified message '{user_message}' as a non-task.")
            return None # Return None to indicate it's not a parsable task
        # --- END NEW LOGIC ---

        # Attempt to parse as JSON
        try:
            parsed_data = json.loads(response_text)
            
            # Validate that we have the required keys and task_description is not empty
            required_keys = ['task_description', 'deadline', 'project_name']
            if all(key in parsed_data for key in required_keys) and parsed_data.get("task_description"):
                return parsed_data
            else:
                print(f"Warning: Missing required keys or empty task_description in parsed data: {parsed_data}")
                return None
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response from Gemini (expected JSON or 'null'): '{response_text}'")
            return None
            
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        # Consider logging the full exception for better debugging
        return None

# Test function (can be removed in production, but very useful now)
def test_parser():
    """Test the parser with sample messages, including non-tasks"""
    test_messages = [
        "CS 101 Assignment 3 - Implement a binary search tree. Due: March 15th, 2024",
        "Hey everyone, don't forget the calculus homework is due tomorrow at 11:59 PM. Chapter 5 problems 1-20.",
        "Group meeting tomorrow at 2 PM to discuss the marketing presentation",
        "thank you so much!", # Should return null
        "hello",              # Should return null
        "show my tasks",      # Should return null (bot command)
        "what's for dinner?"  # Should return null (question)
    ]
    
    for msg in test_messages:
        print(f"\n--- Testing message: \"{msg}\" ---")
        result = parse_message_with_gemini(msg)
        print(f"Parsed Result: {result}")

if __name__ == "__main__":
    test_parser()