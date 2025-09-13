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
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    print("Warning: GEMINI_API_KEY not found in environment variables")

# Master Prompt for task extraction
MASTER_PROMPT = """
You are an AI assistant that extracts structured task information from WhatsApp messages. 
Your job is to parse forwarded messages and extract ONLY the following information in JSON format:

1. task_description: The main task or assignment description
2. deadline: The due date or deadline (extract from text or infer if not explicitly stated)
3. project_name: The subject, course, or project this task belongs to

IMPORTANT RULES:
- Return ONLY valid JSON format, no additional text or explanations
- If information is missing, use "Not specified" as the value
- For deadlines, try to extract dates in YYYY-MM-DD format if possible
- If no clear deadline exists, use "Not specified"
- Project names should be concise (e.g., "CS101", "Math Assignment", "Group Project")

EXAMPLES:

Input: "Hey everyone, don't forget the calculus homework is due tomorrow at 11:59 PM. Chapter 5 problems 1-20."
Output: {"task_description": "Chapter 5 problems 1-20", "deadline": "Not specified", "project_name": "Calculus"}

Input: "CS 101 Assignment 3 - Implement a binary search tree. Due: March 15th, 2024"
Output: {"task_description": "Implement a binary search tree", "deadline": "2024-03-15", "project_name": "CS 101"}

Input: "Group meeting tomorrow at 2 PM to discuss the marketing presentation"
Output: {"task_description": "Group meeting to discuss the marketing presentation", "deadline": "Not specified", "project_name": "Marketing"}

Input: "Physics lab report due next Friday. Include graphs and analysis."
Output: {"task_description": "Physics lab report with graphs and analysis", "deadline": "Not specified", "project_name": "Physics"}

Now parse this message:
"""

def parse_message_with_gemini(user_message):
    """
    Parse a user message using Gemini AI to extract task information.
    
    Args:
        user_message (str): The raw message from the user
        
    Returns:
        dict or None: Parsed task data with keys: task_description, deadline, project_name
                     Returns None if parsing fails
    """
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not configured")
        return None
    
    try:
        # Combine master prompt with user message
        full_prompt = MASTER_PROMPT + user_message
        
        # Generate content using Gemini
        response = model.generate_content(full_prompt)
        
        # Extract the response text
        response_text = response.text.strip()
        
        # Try to parse as JSON
        try:
            # Remove any markdown formatting if present
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            # Parse JSON
            parsed_data = json.loads(response_text)
            
            # Validate that we have the required keys
            required_keys = ['task_description', 'deadline', 'project_name']
            if all(key in parsed_data for key in required_keys):
                return parsed_data
            else:
                print(f"Warning: Missing required keys in parsed data: {parsed_data}")
                return None
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response: {response_text}")
            return None
            
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None

# Test function (can be removed in production)
def test_parser():
    """Test the parser with sample messages"""
    test_messages = [
        "CS 101 Assignment 3 - Implement a binary search tree. Due: March 15th, 2024",
        "Hey everyone, don't forget the calculus homework is due tomorrow at 11:59 PM. Chapter 5 problems 1-20.",
        "Group meeting tomorrow at 2 PM to discuss the marketing presentation"
    ]
    
    for msg in test_messages:
        print(f"\nTesting: {msg}")
        result = parse_message_with_gemini(msg)
        print(f"Result: {result}")

if __name__ == "__main__":
    test_parser()
