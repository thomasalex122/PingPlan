from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """
    Webhook endpoint to receive messages from Twilio WhatsApp integration
    """
    # Get the incoming message from Twilio
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')
    
    # Create Twilio response object
    resp = MessagingResponse()
    
    # Simple response for now - just echo back the message
    response_text = f"Pong! Your message was: {incoming_msg}"
    
    # Add the response message
    resp.message(response_text)
    
    return str(resp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
