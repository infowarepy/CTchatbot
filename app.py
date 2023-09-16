from flask import Flask, render_template, request, jsonify
import openai
import speech_recognition as sr
import sqlite3
from sentiment import analyze_emotion 
from config import SECRET_KEY

app = Flask(__name__, static_folder='static')

#api key generated on 16-09-2023
openai.api_key = SECRET_KEY


DATABASE = 'conversation.db' # to store chats temporarily

def create_tables():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS conversation (role TEXT, content TEXT)')
    conn.commit()
    conn.close()

def reset_conversation():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM conversation')
    conn.commit()
    conn.close()

def get_conversation():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM conversation')
    conversation = c.fetchall()
    conn.close()
    return conversation

def add_message(role, content):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('INSERT INTO conversation (role, content) VALUES (?, ?)', (role, content))
    conn.commit()
    conn.close()

create_tables()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/reset_conversation', methods=['POST'])
def reset_conversation_route():
    reset_conversation()
    return jsonify({'message': 'Conversation reset.'})


def set_ai(condition,severity,gender):
    
    name = "Chris"
    if gender == "Female":
        name = "Julia"

    print(condition,severity,gender)

    # Define the prompt messages in a dictionary
    prompt_messages = {
        "Memory Loss": {
            "None": """I am Somehow smart and knowledgeable,
                I know and remember my demographics and address,
                I have no problem remembering things or places.""",

            "Mild": """I can recall my personal information.
                But my memory to recall is limited, and I tend to forget 20% of common things.""",

            "Moderate": """I am forgetful and have moderate difficulty in concentration,
                My memory to recall is limited, and I tend to forget 40% of common things.""",

            "Severe": """I am forgetful and have major difficulty in concentration,
                I sometimes say random things,
                80% of my memory is failing,
                I can remember my personal information as a patient"""
        },
        
        "Alzheimer": {
            "None": """I possess average cognitive abilities,
                I can recall personal information, demographics, and addresses without difficulty,
                I have no issues with memory retention or recalling things and places.""",
            
            "Mild": """I can recall personal information with some limitations,
                My memory recall is moderately limited, with a tendency to forget around 20% of common things.""",

            "Moderate": """I am experiencing forgetfulness and moderate difficulty in concentration,
                My memory recall is limited, with a tendency to forget around 40% of common things.""",

            "Severe": """I am experiencing major difficulty in concentration and memory recall,
                I may exhibit random speech patterns or phrases,
                Approximately 80% of my memory capacity is affected,
                I am still able to remember my personal information as a patient"""
        },
    }


    
    add_message('patient', f"I am a patient (person with a disease) with a specific disease condition and I will have to act accordingly (role assigned to me is 'patient'). My disease condition is {condition} with a severity of {severity}. I am sitting in a clinical trial assessment office to assess my cognitive impairment. These are my symptoms: {prompt_messages[condition][severity]}. I have to behave according to these symptoms. I will answer no longer than 5 sentences per question. My name is {name}, and my gender is {gender}. I will not try to answer like an assistant (e.g., 'how can I help you,' 'how may I assist you'). I will act as a patient throughout the whole process. Importantly, I will not pretend to be the Rater; you(doctor) will prompt the questions as a Rater. Instead of using 'I am an AI language model or AI model bla bla bla,' I will use the name given to me, which is {name}. For some questions, even if I don't have any previous information, I will still act as a patient (person with a disease) with the mentioned condition, severity, and symptoms, and answer accordingly. Even though questions may be repeated, I will continue to answer them as mentioned. Even if some questions are related to preferences or emotions, I will answer them as a person considering the disease as mentioned above.From now my role is 'patient'. and i will behave according to symptoms mentioned. lets start now") 



@app.route('/chat', methods=['POST'])
def chat():
    reset_conversation()

    condition = request.form['condition']
    severity = request.form['severity']
    gender = request.form['gender']

    reply = "Now you can chat further"

    set_ai(condition, severity, gender)

    return jsonify({'reply': reply})


@app.route('/chat_further', methods=['POST'])
def chat_further():
    text = request.form['doctor_input']

    add_message('doctor', text)

    conversation = get_conversation()
    # formatted_conversation = [{'role': role, 'content': content} for role, content in conversation]
    formatted_conversation = ""
    for role, content in conversation:
        if role == 'doctor':
            formatted_conversation += f"doctor: {content}\n"
        else:
            formatted_conversation += f"patient: {content}\n"

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=formatted_conversation,
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.7
    )

    reply = response['choices'][0]['text']
    reply = reply.replace("patient: ", "")

    # Check if the system reply still contains phrases like "AI language model"
    # if any(keyword in reply for keyword in ["AI language model", "AI model", "language model"]):
    #     reply = f"Please ask me relevant question."

    add_message('patient', reply)
    detected_emotion = analyze_emotion(f"detect emotion and return single word : {reply}")
    print(detected_emotion)

    # print(text)
    # print(reply)
    # print(conversation)
    # print(formatted_conversation)

    return jsonify({'reply': reply})


if __name__ == '__main__':
    app.run(debug=False)
