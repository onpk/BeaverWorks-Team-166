'''import openai
API_Key=''
openai.api_key=API_Key

model_id='gpt-3.5-turbo'
vclient=openai.OpenAI()
response=vclient.chat.completions.create(model=model_id, messages=[
    {}
])'''
import openai
import os
key= "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"
system = [{"role": "system", "content": "You are a peer support companion to an autistic student to help them learn social skills."}]
user = [{"role": "user", "content": "Introduce yourself."}]
chat = []
vclient=openai.OpenAI(api_key=key)
while not user[0]['content'] == "exit":
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
    user = [{"role": "user", "content": input("\nPrompt: ")}]