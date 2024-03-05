import streamlit as st
from openai import OpenAI

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="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",
                                   type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("💬 AI Scenario Assistant")

# Initialize session state if not already done
if "messages" not in st.session_state:
    st.session_state.messages = []

# Define additional training examples related to school interactions
additional_training_data = [
    {"prompt": "You're discussing the upcoming school dance with your friend.\nYou: Are you going to the school dance this Friday?", "response": "Friend: Yeah, I'm planning to go with a group of friends. Are you going too?"},
    {"prompt": "You're asking your classmate about an assignment.\nYou: Do you know when the history essay is due?", "response": "Classmate: It's due next Monday. I've already started researching for it."},
    {"prompt": "You're talking to your teacher after class.\nYou: Can you help me understand the concept we covered in today's lecture?", "response": "Teacher: Of course! Let's go over it together."},
    {"prompt": "You're catching up with your friend between classes.\nYou: How was the science experiment in the lab today?", "response": "Friend: It was fun! We got to see some cool chemical reactions."},
    {"prompt": "You're discussing the school play with your drama club members.\nYou: Do you think we need more rehearsals before the performance?", "response": "Drama Club Member: Yeah, I think we should run through the scenes one more time to polish our performance."},
    {"prompt": "You're asking your classmate for help with a difficult homework problem.\nYou: Can you explain how to solve question number 5? I'm stuck.", "response": "Classmate: Sure, let's go over it together."},
    # Add more training examples related to school interactions...
]

# Combine the original and additional training data
training_data = [
    {"prompt": "You and your classmate are discussing the upcoming school project.\nYou: Hey, have you started working on the project yet?", "response": "Classmate: Yeah, I've done some research on our topic. Have you decided on our approach?"},
    {"prompt": "You're talking to your friend during lunch break.\nYou: Did you understand today's math lesson?", "response": "Friend: No, I'm so confused! Can you help me understand it better?"},
    {"prompt": "You're studying with a group of classmates for an upcoming exam.\nYou: Do you think we should focus more on studying theory or practicing problems?", "response": "Classmate: I think a balance of both would be ideal. Let's review the theory first and then solve some practice questions."},
    # Add more original training examples related to school interactions...
]
training_data += additional_training_data

if st.session_state.messages:
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    client = OpenAI(api_key=openai_api_key)

    # Initialize messages list if not already done
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
