import audioop
import base64
import json
from tabnanny import check
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
from spam_lookup import lookup
from number_validity import isValid
from Numbers_Routing import getRandomEmergency, getRandomHelp, getRandomInquiry
app = Flask(__name__)
sock = Sock(app)
twilio_account_sid = "ACb570e0d0321934733824f7c7f8c88c5c"
twilio_auth_token = "9f20b219969c3ad2b6ce0da45db9dac9"
twilio_client = Client(twilio_account_sid, twilio_auth_token)
model = vosk.Model('model')

database = ""
cursor = ""


prediction = "asdfasdfasdf"
def connect_database():
    global database, cursor
    import psycopg2
    db_url = "postgresql://srikanth:5zx_u0fv14b4BLPnCs4_8A@free-tier12.aws-ap-south-1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&options=--cluster%3Ddread-macaw-1079"
    database = psycopg2.connect(db_url) 
    cursor = database.cursor()    

def check_spam(number):
    global database, cursor
    query = f'SELECT mobile_number from spam_list where mobile_number = \'{number}\''
    cursor.execute(query)
    database.commit()
    return len(cursor.fetchall()) == 1

def add_to_spam_list(number):
    global databse, cursor
    try:
        query = f'insert into spam_list (mobile_number) values (\'{number}\')'
        cursor.execute(query)
        database.commit()
    except:
        print("Number already in spam list")

def add_to_database(temp_msg, selected_option, number, prediction):
    message1 = temp_msg
    message2 = ""
    for i in range(len(message1)):
        if message1[i] == "\'":
            message2 += " "
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

@app.route('/', methods=['GET'])
def home():
    global selected_option, number, temp_msg
    return render_template("ivrs.html")

@app.route('/get-call-details', methods=['GET'])
def get_details():
    global temp_msg, selected_option, number
    return jsonify(
        message= str(temp_msg),
        mob_number= str(number)[3:],
        selected_option= str(selected_option),
        prediction=str(prediction)
    )

@app.route('/add-to-spam-list', methods=['PUT'])
def spam_call():
    req = request.get_json()
    add_to_spam_list(number=req['number'])
    return "added to spam list"

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
    number = request.form["From"]
    number_parse = number[3:]
    if isValid(number_parse):
        if check_spam(number[3:]):
            response.say('Call Blocked.')
            return str(response), 200, {'Content-Type': 'text/xml'}
    else:
        response.say("Not a valid number")
    response.say(
        "Thank you for calling Madhya Pradesh Police. Please speak about your problem in 20 seconds")
    response.pause(length=10)
    # should_stream = False
    print(f'Incoming call from {request.form["From"]}')
    print(number)
    
    #string to integer conversion, excluding +91
    print(number_parse) #7083022822
    print(isValid(number_parse))
    with response.gather(
        num_digits=1, action=url_for('menu'), method="POST"
    ) as g:
        g.say(message="Thanks for calling MP Police. " +
            "Please press 1 for emergency." +
            "Press 2 for help." + "Press 3 for inquiry.", loop=1)
    return str(response), 200, {'Content-Type': 'text/xml'}



@app.route('/call/menu', methods=['POST'])
def menu():
    global temp_msg, selected_option, prediction


    
    selected_option = request.form['Digits']
    option_actions = {'1': _emergency,
                      '2': _help,
                      '3': _inquiry}
    
    print(temp_msg)
    temp_msg = temp_msg.strip()
    print(len(temp_msg))
    if len(temp_msg) == 0:
        response = VoiceResponse()
        response.say("Blank call detected") 
        prediction = "Blank Call"
        add_to_database(selected_option="NA", number=number, prediction="Blank Call", temp_msg="NA")
        return str(response), 200, {'Content-Type': 'text/xml'}
    
    prediction = classify(temp_msg)
    print('model prediction:',prediction)
    add_to_database(selected_option=selected_option, temp_msg=temp_msg, number=number, prediction=prediction)
    
    response = VoiceResponse()
    if selected_option in option_actions:
        if prediction == 'Theft' and selected_option == '2':
            return str(option_actions[selected_option]()), 200, {'Content-Type':'text/xml'}
        if prediction == 'emergency' and selected_option == '1':
            return str(option_actions[selected_option]()), 200, {'Content-Type':'text/xml'}
        if prediction == 'Inquiry' and selected_option == '3':
            return str(option_actions[selected_option]()), 200, {'Content-Type':'text/xml'}
        response.say("Hello from the outside")
    _redirect_call(response)
    return str(response), 200, {'Content-Type':'text/xml'}



def _emergency():
    response = VoiceResponse()
    response.say("You have called to emergency Department")
    # legit number routing
    response.dial(getRandomEmergency())
    #response.hangup()
    return response


def _help():
    response = VoiceResponse()
    response.say("You have called to help Department")
    #number
    response.dial(getRandomHelp())
    return response

def _inquiry():
    response = VoiceResponse()
    response.say("You have called to inquiry Department")
    response.dial(getRandomInquiry())
    return response


def _redirect_call(response):
    response = VoiceResponse()
    response.say("Sorry, wrong input", voice='alice', language='en-GB')
    response.redirect(url_for('call'))

@sock.route('/stream')
def stream(ws):
    global number, temp_msg, should_stream, selected_option, prediction
    response = VoiceResponse()
    """Receive and transcribe audio stream."""
    rec = vosk.KaldiRecognizer(model, 16000)
    while True:
        message = ws.receive()
        packet = json.loads(message)
        if packet['event'] == 'start':
            print('Streaming is starting')
        elif packet['event'] == 'stop':
            number = ""
            temp_msg = ""
            selected_option = ""
            prediction = ""
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
                temp_msg = temp_msg[0:(len(temp_msg) - len(r['partial']))]
if __name__ == '__main__':
    connect_database()
    from pyngrok import ngrok
    port = 5000
    public_url = ngrok.connect(port, bind_tls=True).public_url
    twilio_number = twilio_client.incoming_phone_numbers.list()[0]
    twilio_number.update(voice_url=public_url + '/call')
    print(f'Waiting for calls on {twilio_number.phone_number}')
    app.run(port=port)