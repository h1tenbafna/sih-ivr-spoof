import os
import string
import random
import json
import requests


app = Flask(__name__)
@app.route("/collect",methods=["GET","POST"])
def collect():
   resp=VoiceResponse()
   call_sid = request.values.get("Callsid")
   #Startacall recording
   #Send data to specific webhook when recording is completed
   client.calls(call_sid).recordings.create(
       recording_status_callback=q01,
       recording_channels='dual'
       )
   gather=Gather(input="speech",
                 enhanced="true",
                 speechModel="phone_call",
                 speechTimeout="auto",
                 timeout="20",
                 Language="en-GB",
                 action="/gather_collect")
   gather.say("Please leave a brief message.")
   resp.append(gather)
   resp.say("Sorry,we didn't hear anything.")
   resp.redirect("/end_section")
   return str(resp)
@app.route("/gather_collect",methods=["GET","POST"])
def gather_collect():
   resp=VoiceResponse()