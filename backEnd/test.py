import openai
import json
import os
from re import sub
key = "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"
output_file_path = "conversation.json"

# Initialize user with a default value
user = ""
assistant=""
name=""
intromessage="""You are an AI friend who is interacting with autistic children.
            Your goal is to engage them in a friendly and supportive conversation, incorporating role-playing scenarios to encourage social interaction. 
           Create a positive and inclusive environment, adapt to their preferences, and guide them through imaginative scenarios that foster communication and social skills. 
           Remember to be patient, understanding, and encouraging throughout the interaction. Use reponses that initiate conversation instead of being responsive. 
           If the student seems uninterested, make sure that they are engaged"""
#user = [{"role": "user", "content": user_input}]

# Load existing conversation from JSON file
if os.path.exists(output_file_path) and os.path.getsize(output_file_path) > 0:
   # print("aye")
    with open(output_file_path, 'r') as json_file:
        chat = json.load(json_file)
    for c in range(2,len(chat)):
        if chat[c]["role"]=="user":
            if "python -u" in chat[c]["content"]:
                pass
            else:
                user+=chat[c]["content"]
        elif chat[c]["role"]=="assistant":
            assistant+=chat[c]["content"]
        else:
            temp=chat[c]["content"].split()
            for i in temp:
                if i=="I'm":
                    name=sub(r'\W+', '',temp[temp.index(i)+1])
    intromessage+="These are previous messages you sent. Remember them as you write your responses. "+assistant+" These are the messages that the user sent. Remember these as well when you write your responses. "+user
    system = [{"role": "system", "content":intromessage}]
    user = [{"role": "user", "content":"Reintroduce yourself as "+name+". Start a conversation with the user."}]
    chat=[]

else:
    # If the JSON file is empty or doesn't exist, initialize the conversation with general questions
    #print("nay")
    system = [{"role": "system", "content": """You are an AI friend who is interacting with autistic children.
            Your goal is to engage them in a friendly and supportive conversation, incorporating role-playing scenarios to encourage social interaction. 
           Create a positive and inclusive environment, adapt to their preferences, and guide them through imaginative scenarios that foster communication and social skills. 
           Remember to be patient, understanding, and encouraging throughout the interaction. Use reponses that initiate conversation instead of being responsive. 
           If the student seems uninterested, make sure that they are engaged"""}]

    user = [{"role": "user", "content": "Introduce yourself. Ask the user their age and tailor your responses appropriately."}]
    chat = []

vclient = openai.OpenAI(api_key=key)

while not user[0]['content'] == sub(r'\W+', '',"bye"):
    # Use the entire chat history for generating the response
    response = vclient.chat.completions.create(
        messages=system + chat[-10:] + user,
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
