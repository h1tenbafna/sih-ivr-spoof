import audioop
import base64
import json
import os
from flask import Flask, request
from flask_sock import Sock, ConnectionClosed
from twilio.twiml.voice_response import VoiceResponse, Start
from twilio.rest import Client
import vosk
import time
from flask import url_for, jsonify
from flask import render_template
import flask
import pickle
import joblib
from spam_lookup import lookup
from number_validity import isValid
import unicodedata

app = Flask(__name__)
sock = Sock(app)
twilio_account_sid = "ACb570e0d0321934733824f7c7f8c88c5c"
twilio_auth_token = "9f20b219969c3ad2b6ce0da45db9dac9"
twilio_client = Client(twilio_account_sid, twilio_auth_token)
model = vosk.Model('model')

database = ""
cursor = ""
def connect_database():
    global database, cursor
    import psycopg2
    db_url = "postgresql://srikanth:5zx_u0fv14b4BLPnCs4_8A@free-tier12.aws-ap-south-1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&options=--cluster%3Ddread-macaw-1079"
    database = psycopg2.connect(db_url, application_name="$ docs_simplecrud_psycopg2") 
    cursor = database.cursor()    

def add_to_database(temp_msg, selected_option, number, prediction):
    # message1 = unicodedata.normalize('NFKD', temp_msg).encode('ascii', 'ignore')
    message1 = temp_msg
    # temp_msg.replace("\'", "\\'")
    message2 = ""
    for i in range(len(message1)):
        if message1[i] == "\'":
            message2 += "\\" + "\'"
        else:
            message2 += message1[i]
    sql_query = f'INSERT INTO call_reports (mobile_number, transcript, selected_option, prediction) values(\'{number[3:]}\', \'{message2}\', \'{selected_option}\', \'{prediction}\');'
    cursor.execute(sql_query)
    database.commit()

CL = '\x1b[0K'
BS = '\x08'

number = ""

temp_msg = ""

should_stream = True

selected_option = ""

def classify(text):
    #load classifier
    clf_filename='naive_bayes_classifier.pkl'
    nb_clf = pickle.load(open(clf_filename,'rb'))
    #vectorize the new text
    vec_filename='count_vectorizer.pkl'
    vectorizer = pickle.load(open(vec_filename,'rb'))
                          
    pred= nb_clf.predict(vectorizer.transform([text]))
    # print(pred[0])
    return pred[0]

def twiml(resp):
    resp = flask.Response(str(resp))
    resp.headers['Content-Type'] = 'text/xml'
    return resp

@app.route('/home', methods=['GET'])
def home():
    global selected_option, number, temp_msg
    return render_template("ivrs.html")

@app.route('/get-call-details', methods=['GET'])
def get_details():
    global temp_msg, selected_option, number
    response = {
        'message': temp_msg,
        'mob_number': number,
        'selected_option': selected_option
    }
    return jsonify(response)

@app.route('/call', methods=['POST'])
def call():
    """Accept a phone call."""
    global number, should_stream, temp_msg
    temp_msg = ""
    # should_stream = True
    response = VoiceResponse()
    start = Start()
    start.stream(url=f'wss://{request.host}/stream')
    response.append(start)
    response.say(
        "Thank you for calling Madhya Pradesh Police. Please speak about your problem in 20 seconds")
    response.pause(length=10)
    # should_stream = False
    print(f'Incoming call from {request.form["From"]}')
    number = request.form["From"]
    print(number)
    
    '''caller-name
    details = twilio_client.lookups \
                     .v1 \
                     .phone_numbers(number) \
                     .fetch(add_ons=['nomorobo_spamscore']) \
                     .fetch(type=["caller-name"])
                     
    print(details.caller_name)
    print(details.add_ons)'''
    
    #string to integer conversion, excluding +91
    number_parse = number[3:]
    print(number_parse) 
    
    if isValid(number_parse):
        t = lookup(int(number_parse))
        
        if t:
            response.say("Sorry, we are not available at the moment, Thank you.")
            
        else:
            with response.gather(
                num_digits=1, action=url_for('menu'), method="POST"
            ) as g:
                g.say(message="Thanks for calling MP Police. " +
                    "Please press 1 for emergency." +
                    "Press 2 for help." + "Press 3 for inquiry.", loop=1)
                
                
    else:
        response.say("Not a valid number")
        
    return str(response), 200, {'Content-Type': 'text/xml'}



@app.route('/call/menu', methods=['POST'])
def menu():
    global temp_msg, selected_option
    
    selected_option = request.form['Digits']
    option_actions = {'1': _emergency,
                      '2': _help,
                      '3': _inquiry}
    
    prediction = classify(temp_msg)
    print('model prediction:',prediction)
    print(temp_msg)
    add_to_database(selected_option=selected_option, temp_msg=temp_msg, number=number, prediction=prediction)
        
    if selected_option in option_actions:
        if prediction == 'Theft' and selected_option == '2':
            return str(option_actions[selected_option]()), 200, {'Content-Type':'text/xml'}
        if prediction == 'emergency' and selected_option == '1':
            return str(option_actions[selected_option]()), 200, {'Content-Type':'text/xml'}
        if prediction == 'Inquiry' and selected_option == '3':
            return str(option_actions[selected_option]()), 200, {'Content-Type':'text/xml'}
        response = VoiceResponse()
        response.say("Hello from the outside")
        return str(response), 200, {'Content-Type', 'text/xml'}    
    return _redirect_call()



def _emergency():
    response = VoiceResponse()
    response.say("You have called to emergency Department")
    # legit number routing
    response.dial("+912345678901")
    #response.hangup()
    return response


def _help():
    response = VoiceResponse()
    response.say("You have called to help Department")
    #number
    response.dial("+913456789012")
    return response

def _inquiry():
    response = VoiceResponse()
    response.say("You have called to inquiry Department")
    response.dial("+911234567890")
    return response


def _redirect_call():
    response = VoiceResponse()
    response.say("Sorry, wrong input", voice='alice', language='en-GB')
    response.redirect(url_for('call'))

    return twiml(response)

@sock.route('/stream')
def stream(ws):
    global number, temp_msg, should_stream
    response = VoiceResponse()
    """Receive and transcribe audio stream."""
    rec = vosk.KaldiRecognizer(model, 16000)
    while True:
        message = ws.receive()
        packet = json.loads(message)
        if packet['event'] == 'start':
            print('Streaming is starting')
        elif packet['event'] == 'stop':
            print('\nStreaming has stopped')
        elif packet['event'] == 'media':
            audio = base64.b64decode(packet['media']['payload'])
            audio = audioop.ulaw2lin(audio, 2)
            audio = audioop.ratecv(audio, 2, 1, 8000, 16000, None)[0]
            if rec.AcceptWaveform(audio):
                r = json.loads(rec.Result())
                print(CL + r['text'] + ' ', end='', flush=True)
                temp_msg +=  r['text']
            else:
                r = json.loads(rec.PartialResult())
                print(CL + r['partial'] + BS *
                      len(r['partial']), end='', flush=True)
                temp_msg += r['partial']
                # temp_msg += temp_msg[:(len(temp_msg) - len(r['partial']))]
if __name__ == '__main__':
    connect_database()
    from pyngrok import ngrok
    port = 5000
    public_url = ngrok.connect(port, bind_tls=True).public_url
    number = twilio_client.incoming_phone_numbers.list()[0]
    number.update(voice_url=public_url + '/call')
    print(f'Waiting for calls on {number.phone_number}')
    app.run(port=port)