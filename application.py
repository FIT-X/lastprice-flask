import json
from flask import Flask, request, redirect, Response, json
import requests
import io
import time
import datetime
import sys
import os
import json
import subprocess
# from google.cloud import storage
from twilio.twiml.voice_response import Gather, Record, VoiceResponse, Say
from twilio.twiml.messaging_response import MessagingResponse
##from google.cloud import speech
##from google.cloud.speech import enums
##from google.cloud.speech import types
##from google.cloud import translate
##from twilio.twiml.voice_response import VoiceResponse

from flask_cors import CORS



hardcoremode = sys.argv[1]

##usage python haggleServer.py <hardcoremode>
##hardcoremode = 0|1

if hardcoremode == '1':
    import Pricing_Response2 as pr
else:
    import Pricing_Response as pr

app = Flask(__name__)
CORS(app)

callState = 0
origPrice = 0
currPrice = 0
targetPrice = 0
nextBestPrice = 0
nextBestHotel = ''
customerName = ''
finalflag = 0

##targetDate = '03-08-2019'

def processSpeech(text):
    url = "https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/045addc1-1ff3-4544-9dfa-0ff75676c333"

    querystring = {"verbose":"true","timezoneOffset":"-360","subscription-key":"1369b2092ac840408d4fd2a8f76d8f3d","q":text}

    payload = ""
    headers = {}

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)

    return response.text

@app.route("/dummy", methods=['GET', 'POST'])
def dummy():

    ##res = request.json

    js = "<html> <body>OK THIS WoRKS</body></html>"

    resp = Response(js, status=200, mimetype='text/html')
    ##resp.headers['Link'] = 'http://google.com'

    return resp

@app.route("/setup", methods=['GET', 'POST'])
def setupcall():


    ##res = request.json

    global currPrice 
    global targetPrice
    global nextBestPrice 
    global nextBestHotel 
    global customerName
    global origPrice
    global callState

    currPrice = float(request.args['currprice'])
    targetPrice = float(request.args['targetprice'])
    nextBestPrice = float(request.args['nextbestprice'])
    nextBestHotel = request.args['nextbesthotel']
    customerName = request.args['customername']
    origPrice = float(request.args['currprice'])
    callState = 0

    print (currPrice)
    print(targetPrice)
    print (nextBestPrice)
    print (nextBestHotel)
    print (customerName)
    

    js = "<html> <body>OK THIS WoRKS</body></html>"

    resp = Response(js, status=200, mimetype='text/html')
    ##resp.headers['Link'] = 'http://google.com'

    return resp


@app.route("/status", methods=['GET', 'POST'])
def getstatus():


    ##res = request.json

    global currPrice 
    global targetPrice
    global nextBestPrice 
    global nextBestHotel 
    global customerName
    global origPrice
    global callState
    
    status = {}

    if callState == 1:
        status["calling"] = True
    else:
        status["calling"] = False

    print (currPrice)
    print(targetPrice)
    print (nextBestPrice)
    print (nextBestHotel)
    print (customerName)

    statusjson = json.dumps(str(status))

    print(statusjson)

    js = "<html> <body>OK THIS WoRKS</body></html>"

    resp = Response(statusjson, status=200, mimetype='application/json')
    ##resp.headers['Link'] = 'http://google.com'

    return resp



@app.route("/dummyJson", methods=['GET', 'POST'])
def dummyJson():

##    res = request.get_json()
##    print (res)

    resraw = request.get_data()
    print (resraw)

    args = request.args
    form = request.form
    values = request.values

##    print (args)
##    print (form)
##    print (values)

    sres = request.form.to_dict()

    speechResult = sres['SpeechResult']
    print ('transcribed speech is ' +speechResult)

    js = "<html> <body>OK THIS WoRKS with JSON</body></html>"

    ##message = speechResult

    response = VoiceResponse()
    ##response.say(message, voice='alice')
    ##response.play('https://api.twilio.com/cowbell.mp3', loop=1)
    ##response.play(soundurl, loop=1)
    gather = Gather(input='speech dtmf', action = 'https://haggler.azurewebsites.net/dummyJson', timeout=3, num_digits=1)
    message = speechResult + ' Please press 1 to exit or say ok to agree.'
    gather.say(message, voice = 'Polly.Kimberly')
    response.append(gather)
    print(response)

    response = str(response)

    ##resp = Response(js, status=200, mimetype='text/html')
    resp = Response(response, status=200, mimetype='text/xml')
    ##resp.headers['Link'] = 'http://google.com'

    return resp

@app.route("/endCallExit", methods=['GET', 'POST'])
def endcallexit():
    ##do call ending stuff here

    js = "<html> <body>OK THIS WoRKS with JSON</body></html>"

    resp = Response(js, status=200, mimetype='text/html')

    return resp


@app.route("/propagate", methods=['GET', 'POST'])
def propagate():

##    res = request.get_json()
##    print (res)

    ##callState = callState + 1

    global finalflag

    global callState
    global currPrice
    global origPrice
    global customerName

    resraw = request.get_data()
    print (resraw)

    args = request.args
    form = request.form
    values = request.values

##    print (args)
##    print (form)
##    print (values)

    sres = request.form.to_dict()

    js = "<html> <body>OK THIS WoRKS with JSON</body></html>"

    sres = request.form.to_dict()

    if 'SpeechResult' in sres:
        speechResult = sres['SpeechResult']
        print ('transcribed speech is ' +speechResult)

        ptextjson = processSpeech(speechResult)

        print (nextBestHotel)
        print (nextBestPrice)

        if finalflag == 0:
            message, cp, callState = pr.negotiate2( ptextjson, customerName,  currPrice, origPrice)
        else:
            message, callState = pr.final_attempt( ptextjson, customerName)

        if callState == -1:
            response = VoiceResponse()
            response.say(message, voice = 'Polly.Kimberly')
            ##response.play('https://api.twilio.com/cowbell.mp3', loop=1)
            ##response.play(soundurl, loop=1)

            print(response)
            response = str(response)

            resp = Response(response, status=200, mimetype='text/xml')

        else:

            if callState == 2:
                response = VoiceResponse()
                response.say(message, voice = 'Polly.Kimberly')
                ##response.play('https://api.twilio.com/cowbell.mp3', loop=1)
                ##response.play(soundurl, loop=1)

                print(response)
                response = str(response)

                resp = Response(response, status=200, mimetype='text/xml')
            else :
                finalflag = 1

                ##message = speechResult

                response = VoiceResponse()
                ##response.say(message, voice='alice')
                ##response.play('https://api.twilio.com/cowbell.mp3', loop=1)
                ##response.play(soundurl, loop=1)
                gather = Gather(input='speech dtmf', action = 'https://haggler.azurewebsites.net/propagate', timeout=3, num_digits=1)
                ##message = speechResult + ' Please press 1 to exit or say ok, I agree to agree to the proposed price.'
                gather.say(message, voice = 'Polly.Kimberly')
                response.append(gather)
                print(response)

                response = str(response)

                ##resp = Response(js, status=200, mimetype='text/html')
                resp = Response(response, status=200, mimetype='text/xml')
                ##resp.headers['Link'] = 'http://google.com'

        return resp
    else:
        if 'Digits' in sres:

            print (sres['Digits'])

            message = 'We are sorry we could not reach a deal. thank you for your time, goodbye.'
            response = VoiceResponse()
            response.say(message, voice = 'Polly.Kimberly')
            ##response.play('https://api.twilio.com/cowbell.mp3', loop=1)
            ##response.play(soundurl, loop=1)

            print(response)

            response = str(response)

            resp = Response(response, status=200, mimetype='text/xml')
            
        else:
            resp = Response(js, status=200, mimetype='text/html')

    return resp

@app.route("/initialCall", methods=['GET', 'POST'])
def initialCall():

    global currPrice
    global origPrice
    global callState
    
##    res = request.get_json()
##    print (res)

    callState = 1

    resraw = request.get_data()
    print (resraw)

    args = request.args
    form = request.form
    values = request.values

##    print (args)
##    print (form)
##    print (values)

    sres = request.form.to_dict()

    js = "<html> <body>OK THIS WoRKS with JSON</body></html>"

    sres = request.form.to_dict()

    if 'SpeechResult' in sres:
        speechResult = sres['SpeechResult']
        print ('transcribed speech is ' +speechResult)

        print (nextBestHotel)
        print (nextBestPrice)

        ptextjson = processSpeech(speechResult)

        message, op, cp, callState = pr.negotiate1(ptextjson, nextBestHotel, str(nextBestPrice))

        currPrice = float(cp)
        origPrice = float(op)

        if callState == -1:
            response = VoiceResponse()
            response.say(message, voice = 'Polly.Kimberly')
            ##response.play('https://api.twilio.com/cowbell.mp3', loop=1)
            ##response.play(soundurl, loop=1)

            print(response)
            response = str(response)

            resp = Response(response, status=200, mimetype='text/xml')

        else:
            ##message = speechResult
            response = VoiceResponse()
            ##response.say(message, voice='alice')
            ##response.play('https://api.twilio.com/cowbell.mp3', loop=1)
            ##response.play(soundurl, loop=1)
            gather = Gather(input='speech dtmf', action = 'https://haggler.azurewebsites.net/propagate', timeout=3, num_digits=1)
            ##message = speechResult + ' Please press 1 to exit or say ok, I agree to agree to the proposed price.'
            gather.say(message, voice = 'Polly.Kimberly')
            response.append(gather)
            print(response)

            response = str(response)

            ##resp = Response(js, status=200, mimetype='text/html')
            resp = Response(response, status=200, mimetype='text/xml')
            ##resp.headers['Link'] = 'http://google.com'

    else:
        if 'Digits' in sres:

            print (sres['Digits'])

            message = 'We are sorry we could not reach a deal. thank you for your time, goodbye.'
            response = VoiceResponse()
            response.say(message, voice = 'Polly.Kimberly')

            print(response)
            response = str(response)

            resp = Response(response, status=200, mimetype='text/xml')

            
        else:
            resp = Response(js, status=200, mimetype='text/html')

    return resp



if __name__ == "__main__":
    app.run(debug=True,  port = os.getenv('PORT', 8001))
    ##app.run(debug=True, host = '192.168.133.177', port = 8001)

