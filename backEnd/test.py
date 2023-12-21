'''import openai
API_Key=''
openai.api_key=API_Key

model_id='gpt-3.5-turbo'
vclient=openai.OpenAI()
response=vclient.chat.completions.create(model=model_id, messages=[
    {}
])'''
import openai
import json
from re import sub
key= "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"
system = [{"role": "system", "content": """You are an AI friend who is interacting with autistic children.
            Your goal is to engage them in a friendly and supportive conversation, incorporating role-playing scenarios to encourage social interaction. 
           Create a positive and inclusive environment, adapt to their preferences, and guide them through imaginative scenarios that foster communication and social skills. 
           Remember to be patient, understanding, and encouraging throughout the interaction. Use reponses that initiate conversation instead of being responsive. 
           If the student seems uninterested, make sure that they are engaged"""}]

user = [{"role": "user", "content": "Introduce yourself. Ask the user their age and tailor your responses appropriately."}]
chat = []
vclient=openai.OpenAI(api_key=key)
while not sub(r'\W+', '',user[0]['content']) == "bye":
    response = vclient.chat.completions.create(
        messages = system + chat[-10:] + user,
        model="gpt-3.5-turbo", stream=True)
    reply = ""
    for delta in response:
        if not delta.choices[0].finish_reason:
            word = delta.choices[0].delta.content
            reply += word
            print(word, end ="")
    chat += user + [{"role": "assistant", "content": reply}]
    user = [{"role": "user", "content": input("\nYou: ")}]
output_file_path = "conversation.json"
with open(output_file_path, 'w') as json_file:
    json.dump(chat, json_file)