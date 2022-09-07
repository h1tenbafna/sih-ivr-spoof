# SPOOFex
Problem statement: "System for Identification of system generated, blank & Spoof calls landing at Dial 100 Police control room"
1. It's a app.py file of python backed flask framework, Twilio Client API is called to fetch client details and recieve calls on a US based trial number offered by Twilio. Since the call is recieved only on a public host & 
the flask app runs on a local host 5000, so we leverage ngrok, cross-platform apllication which exposes a local development server to the internet and divert the traffic, i.e incoming calls recieved onto it. 
2. Once the user calls on the given number, initially before the call is connected the number is verified whether it's a legit Indian number or not, we used Regular expression library of python for this and 
then "the spam_lookup" function lookups into the live spam database to check if that number is in spamlist, if found the IVRS disconnects the call rightaway.
3. As soon as the call is connected, Twilio makes a websocket connection to this endpoint, the user is asked by the IVRS to speak about their problem in about 20 seconds. The while loop is used to read each message and decode it to a python dictionary.
4. A python library known as audioop is used to decode the twilio's foreign mu-law formated encoded data to a 16 bit uncompressed format. Finally the audio from twilio's sample rate is converted to of the requirements of vosk speech recognition engine, now the audio data is recieved by the vosk engine for generating transcript. 
5. If the transcript generated has 0 length that means it's a blank call, so that call is disconnected there itself.
6. This transcript is then fed to different models such as Multinomial Naive bayes classifier and after some sentiment analysis the call is classified into different categories such as Spam call, Emergency call, Inquiry related or Complaint. 
7. Simultaneously, the user is asked to enter a single digit input such as 1 for Emergency, 2 for Inquiry and 3 for Complaint. So after mapping both the results i.e user input and model prediction,  a final output is given and the call is routed to the respective department and if found spam, the police can add the number into the spamlist.
8. All the data such as, phone number, transcript, user input, time and model prediction are stored into the live database (PostgreSQL). 
9. So on the front webpage, model prediction, user input, department to which the call is forwaded to and the phone number are displayed with extra features such as instructions for the operator and add to spam button.

# Flowchart
![3](https://user-images.githubusercontent.com/87855947/188958305-472ffee6-c25a-4936-b052-ba9e32316b15.jpg)

# Stack
