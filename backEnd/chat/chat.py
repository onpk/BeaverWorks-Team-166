import openai
import json
import os
from re import sub
from voicetotextalt import VTT
from random import choice
key = "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"
output_file_path = "conversation.json"

scenarios=["""You're in the cafeteria during lunch break when 
           a classmate from your science class, walks over. He asks if he can sit with you and mentions he's curious about your opinion on the latest physics 
           experiment""",""" You're studying in the library when an art enthusiast approaches. She asks if the seat next to you is taken and mentions 
           she's been experimenting with watercolor techniques lately and would love to share her progress.""", """You're working on a group project in the classroom when Alex, a classmate known for their musical talents, comes over. They ask if they can join your group and 
           suggest incorporating music into the presentation since they recently composed a piece inspired by the topic.""","""You're waiting for the bus after school when Maya, a student you recognize from the drama club, approaches. She asks if she can sit next to you and mentions 
           she's excited about the upcoming school play auditions and wonders if you plan to try out too.""",""" You're in the game room during free period when Michael, a fellow gamer, walks over. He asks if he can join your game and mentions he's been practicing a new strategy 
           in his favorite game and is eager to test it out.""","""You're at the outdoor hangout spot after school when Sarah, a classmate you've seen around, comes over. She asks if she can sit at your table and mentions she's 
           been feeling stressed lately and could use a friendly chat to unwind.""", """ You're in the gym during your workout session when Daniel, a classmate who's into fitness, approaches. He asks if he can share the equipment with you and mentions he's been following a new 
           exercise routine and wants to know if you have any tips.""", """ You're in the music room practicing piano when Lily, a fellow musician, walks in. She asks if she can use the piano next to you and mentions she's been working on a 
           new song and would love your feedback.""", """You're in the library reading zone when Ethan, a classmate you've seen around, approaches. He asks if he can join you and mentions he's been struggling to find a good book to read 
           and wonders if you have any recommendations. """, """ You're at the art studio working on your project when Sophia, a classmate known for her creativity, comes over. She asks if she can work alongside you and mentions she's been experimenting with a 
           new painting technique and would love to share it with you."""]
# Initialize user with a default value
user = ""
assistant=""
name=""
intromessage="""You are an AI friend who is interacting with autistic children.
            Your goal is to engage them in a friendly and supportive conversation, incorporating role-playing scenarios to encourage social interaction. 
           Create a positive and inclusive environment, adapt to their preferences, and guide them through imaginative scenarios that foster communication and social skills. 
           Remember to be patient, understanding, and encouraging throughout the interaction."""
#user = [{"role": "user", "content": user_input}]
intromessage+="""Your role-playing scenario is this: """+choice(scenarios)+". Please make your responses and messages based around this scenario."

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
            cont=chat[c]["content"]
            temp=cont.split()
            for i in temp:
                if i=="I'm":
                    name=sub(r'\W+', '',temp[temp.index(i)+1])
            if ("apologize" or "sorry") in  cont:
                   pass
            else:
                assistant+=cont

    intromessage+="These are previous messages you sent. Remember them as you write your responses. "+assistant+" These are the messages that the user sent. Remember these as well when you write your responses. "+user
    system = [{"role": "system", "content":intromessage}]
    user = [{"role": "user", "content":"Reintroduce yourself as "+name+". Start a conversation with the user."}]
    chat=[]

else:
    # If the JSON file is empty or doesn't exist, initialize the conversation with general questions
    #print("nay")
    system = [{"role": "assistant", "content":intromessage.strip()}]

    user = [{"role": "user", "content": "Introduce yourself with a name. Ask the user their age and tailor your responses appropriately."}]
    chat = []

vclient = openai.OpenAI(api_key=key)

while "Bye" not in user[0]['content'].strip() or "bye" not in user[0]['content'].strip():
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
    user_input = VTT(outfile="outfile.txt").speak()
    user = [{"role": "user", "content": user_input}]
    print("\nYou: ",end="")
    print(user[0]['content'])
    chat.append(user[0])
    print("\nSystem: ")
    
    chat.append({"role": "assistant", "content": reply})
    system = [{"role": "assistant", "content": reply}]
    with open(output_file_path, 'w') as json_file:
        json.dump(chat, json_file, indent=2)
    # Save the updated conversation to the JSON file
#chats.update(chat)

