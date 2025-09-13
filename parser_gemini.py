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
    # Using gemini-1.5-flash for speed and cost-effectiveness
    model = genai.GenerativeModel('gemini-1.5-flash') 
else:
    print("Warning: GEMINI_API_KEY not found in environment variables. Gemini parsing will not work.")
    # In a production app, you might want to raise an error or have a more robust fallback.

# Master Prompt for task extraction (v3.0 - Refined for robustness and concise deadlines)
MASTER_PROMPT = """
You are PingPlan, an expert AI assistant for a WhatsApp bot, specializing in precisely parsing user messages into structured task data.

Your response MUST be ONLY one of the following:
1.  A valid JSON object (Python dictionary format).
2.  The literal string "null" (without quotes).

**JSON Object Rules (when applicable):**
* **"task_description"**: REQUIRED. A clear, actionable summary of the task. Must NOT be an empty string.
* **"deadline"**: The most relevant due date, time, or timeframe.
    * **Rule:** If multiple dates/times are mentioned for a single event, summarize them concisely (e.g., "Multiple sessions, Sep 9-19", "Every Monday for 4 weeks"). If a single, clear deadline exists, extract it precisely (e.g., "Monday 9 PM", "March 15th, 2024"). If no deadline is found or clearly inferable, use an empty string "".
* **"project_name"**: A concise project, course, subject, or context name.
    * **Rule:** Extract if clearly present (e.g., "CS101", "Marketing Presentation", "Groceries"). If none is found or clearly inferable, use an empty string "".

**CRITICAL RULE for returning "null":**
You MUST return "null" if the user's message is NOT a clear, actionable task. This is paramount for the bot's user experience. This includes:
* General conversation, greetings (e.g., "hi", "hello"), farewells (e.g., "bye"), or expressions of gratitude (e.g., "thanks", "thank you").
* Questions (e.g., "What's up?", "How are you?").
* Bot commands (e.g., "show my tasks", "delete 1", "help", "list tasks"). These are handled by the main application, not by you.
* Ambiguous statements, very short messages, or text that lacks a clear action to be taken. If in doubt, return "null".

**Your Goal for Testing and Debugging:**
Aim for extreme precision. Always prioritize returning "null" if the message is not unequivocally an actionable task requiring extraction. This ensures the main bot application can deliver appropriate fallback messages.

**EXAMPLES (Observe both JSON and "null" responses):**

User message: "CS 101 Assignment 3 - Implement a binary search tree. Due: March 15th, 2024"
Your response:
{"task_description": "Implement a binary search tree (Assignment 3)", "deadline": "March 15th, 2024", "project_name": "CS 101"}

User message: "Please Note Ignitors sessions will be held next week on September 9, 10, 13, 15, 16, and 19 from 12:00 PM to 12:50 PM."
Your response:
{"task_description": "Attend Ignitors sessions", "deadline": "Multiple sessions, Sep 9-19", "project_name": "Ignitors"}

User message: "study for DBMS test on Monday"
Your response:
{"task_description": "Study for test", "deadline": "Monday", "project_name": "DBMS"}

User message: "finish the presentation for marketing"
Your response:
{"task_description": "Finish the presentation", "deadline": "", "project_name": "Marketing"}

User message: "I need to buy some milk and bread"
Your response:
{"task_description": "Buy milk and bread", "deadline": "", "project_name": "Groceries"}

User message: "can you show me my tasks please"
Your response:
null

User message: "sounds good"
Your response:
null

User message: "thank you so much for your help!"
Your response:
null

User message: "Hello PingPlan, how are you today?"
Your response:
null

User message: "?"
Your response:
null

User message: "Just finished the report"
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
        print("Error: GEMINI_API_KEY not configured. Cannot call Gemini API.")
        return None
    
    try:
        # Combine master prompt with user message for Gemini
        # Encapsulate user_message in quotes to clearly delineate it for the model
        full_prompt = MASTER_PROMPT + "\n\nUser message: \"" + user_message + "\"\nYour response:"
        
        # Generate content using Gemini
        response = model.generate_content(full_prompt)
        
        # Extract the response text and clean potential markdown (e.g., ```json)
        response_text = response.text.strip()
        if response_text.startswith('```json'):
            response_text = response_text.replace('```json', '').replace('```', '').strip()
        elif response_text.startswith('```'): # Catch if it just uses ```
            response_text = response_text.replace('```', '').strip()
        
        # --- CRITICAL NULL CHECK: If Gemini returns 'null', it's not a task ---
        if response_text.lower() == 'null':
            print(f"DEBUG: Gemini classified message '{user_message}' as a non-task. Returning None.")
            return None # Indicate to app.py that this is not a parsable task
        # --- END CRITICAL NULL CHECK ---

        # Attempt to parse the response as JSON
        try:
            parsed_data = json.loads(response_text)
            
            # Validate that all required keys are present and task_description is not empty
            required_keys = ['task_description', 'deadline', 'project_name']
            if all(key in parsed_data for key in required_keys) and parsed_data.get("task_description"):
                print(f"DEBUG: Successfully parsed task from '{user_message}': {parsed_data}")
                return parsed_data
            else:
                print(f"WARNING: Gemini returned invalid JSON structure or empty task_description for message '{user_message}': {parsed_data}. Returning None.")
                return None
                
        except json.JSONDecodeError as e:
            print(f"ERROR: JSON parsing failed for Gemini response for message '{user_message}': {e}")
            print(f"Raw response from Gemini (expected JSON or 'null'): '{response_text}'")
            return None
            
    except Exception as e:
        print(f"ERROR: Exception calling Gemini API for message '{user_message}': {e}")
        # Consider logging the full traceback for better debugging in a production environment
        return None

# Test function (extremely useful for local debugging)
def test_parser():
    """Test the parser with a variety of sample messages, including non-tasks and complex tasks."""
    print("--- Running Parser Test Suite ---")
    test_messages = [
        # Valid tasks
        "CS 101 Assignment 3 - Implement a binary search tree. Due: March 15th, 2024",
        "Please Note Ignitors sessions will be held next week on September 9, 10, 13, 15, 16, and 19 from 12:00 PM to 12:50 PM.",
        "study for DBMS test on Monday",
        "finish the presentation for marketing",
        "I need to buy some milk and bread",
        "Upload my posters for the creators showcase by 7 PM tonight",
        "Submit this assignment by Monday",

        # Non-tasks (should return None)
        "thank you so much!",
        "hello",
        "show my tasks",
        "what's for dinner?",
        "Okay, sounds good",
        "?",
        "hiii",
        "Hello world",
        "Just finished the report", # Not an actionable future task
        "Can you help me?",
        "delete 2", # Bot command
        "" # Empty message
    ]
    
    for msg in test_messages:
        print(f"\n--- Testing message: \"{msg}\" ---")
        result = parse_message_with_gemini(msg)
        print(f"Parsed Result: {result}")

if __name__ == "__main__":
    test_parser()