from flask import Flask, request, jsonify, render_template
import re
# Make sure to import the correct OpenAI client library
# Replace 'from openai import OpenAI' with the appropriate import based on your setup
from openai import OpenAI  # Adjust this import as needed

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI()

# Assistant and thread setup
assistant_id = "asst_v8d2PBayDOHEgLFbefkcoxdL"
thread = client.beta.threads.create()
printed_message_ids = set()  # Track message IDs that have already been printed

# Define a function to add a user message to the thread
def add_message(user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message
    )

# Define the main route for the web app
@app.route('/')
def index():
    return render_template('index.html')

# Define the route to handle user messages
@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.json.get("message")
    add_message(user_message)  # Add user's message to the thread

    # Start a new run to get the assistant's response
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant_id,
        instructions="Answer the user's query, using information from the Data Base."
    )

    # Check for completed run and retrieve response
    if run.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        response_text = ""

        # Find the last unprinted assistant response
        for msg in messages.data:
            if msg.role == "assistant" and msg.id not in printed_message_ids:
                # Clean and format the response text
                assistant_text = msg.content[0].text.value
                clean_text = re.sub(r"【.*?】", "", assistant_text)  # Remove annotations
                response_text = clean_text  # Keep the original formatting
                printed_message_ids.add(msg.id)  # Mark as printed
                break

        return jsonify({"response": response_text})

    return jsonify({"response": "I'm processing your request, please wait..."})

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
