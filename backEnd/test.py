import openai
import json
import os

key = "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"
output_file_path = "conversation.json"

# Initialize user with a default value
user_input = ""
user = [{"role": "user", "content": user_input}]

# Load existing conversation from JSON file
if os.path.exists(output_file_path) and os.path.getsize(output_file_path) > 0:
    with open(output_file_path, 'r') as json_file:
        chat = json.load(json_file)
else:
    # If the JSON file is empty or doesn't exist, initialize the conversation with general questions
    chat = []
    system = [{"role": "system", "content": "You are a helpful AI assistant. Let's start by getting to know each other. What are your interests?"}]
    user_input = input("\nYou: ")
    user = [{"role": "user", "content": user_input}]
    chat.append(user[0])
    chat.append(system[0])

vclient = openai.OpenAI(api_key=key)

while not user[0]['content'] == "exit":
    # Use the entire chat history for generating the response
    response = vclient.chat.completions.create(
        messages=chat,
        model="gpt-3.5-turbo", stream=True)

    reply = ""
    for delta in response:
        if not delta.choices[0].finish_reason:
            word = delta.choices[0].delta.content
            reply += word
            print(word, end="")

    # Add the user's input and AI's response to the chat history
    user_input = input("\nYou: ")
    user = [{"role": "user", "content": user_input}]
    chat.append(user[0])
    
    chat.append({"role": "system", "content": reply})
    system = [{"role": "system", "content": reply}]

    # Save the updated conversation to the JSON file
    with open(output_file_path, 'w') as json_file:
        json.dump(chat, json_file, indent=2)
