# Import the required module for text
# to speech conversion
# gTTS (Google Text-to-Speech)

import os
from gtts import gTTS
import wavio
import speech_recognition as sr
from correlation import correlate
import AzureBlob

import time
import eng_to_ipa as p

# This module is imported so that we can
# play the converted audio
from playsound import playsound
import sounddevice
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

import pyttsx3


def init_engine():
    engine = pyttsx3.init()
    return engine


def change_voice(engine, mytext, language, slow, gender='VoiceGenderFemale'):
    if slow == "true":
        engine.setProperty("rate", 100)
    else:
        engine.setProperty("rate", 145)

    for voice in engine.getProperty('voices'):

        if language in voice.languages and gender == voice.gender:
            engine.setProperty('voice', voice.id)
            engine.say(mytext)
            engine.runAndWait()
            time.sleep(2.1)
            engine.endLoop()
            engine.stop()
            return True


app = Flask(__name__)
CORS(app, support_credentials=True)


@app.route('/')
def launch():
    return "API Running"


@app.route('/downloadBlob/', methods=['GET'])
def downloadBlobDatawithUI():
    myid = str(request.args.get('employeeId'))
    srcfilename = myid + "_recording.wav"
    if os.path.exists(srcfilename):
        os.remove(srcfilename)
    config = AzureBlob.load_config()
    AzureBlob.get_blob_audio(srcfilename, config["azure_storage_connectionstring"], config["container_name"])
    return "Succesfully Downloaded"


@app.route('/removefile/', methods=['GET'])
def removefilefromDiskbyUid():
    myid = str(request.args.get('employeeId'))
    srcfilename = myid + "_recording.wav"
    os.remove(srcfilename)
    return "Succesfully Removed"


@app.route('/practice/', methods=['GET'])
def practiceUserPreference():
    myid = str(request.args.get('employeeId'))
    fps = 44100
    duration = 3
    myobj = gTTS(text="Please start pronunciation after the beep", lang="en", slow=False)
    myobj.save("command_practice.mp3")
    playsound("command_practice.mp3")
    playsound("beep.mp3")
    destfilename = myid + "_user_recording.wav"
    recording = sounddevice.rec(int(duration * fps), samplerate=fps, channels=1)
    # Saving the array in a text file
    # numpy.savetxt("file1.txt", recording)
    sounddevice.wait()
    # write(filename, fps, recording)
    wavio.write(destfilename, recording, fps, sampwidth=2)
    playsound("thankyou.mp3")
    srcfilename = myid + "_recording.wav";

    matched = correlate(srcfilename, destfilename)
    if matched > 65:
        matchingStatus = "High"
    elif matched > 60:
        matchingStatus = "Medium"
    else:
        matchingStatus = "Low"
    # os.remove(srcfilename)
    os.remove(destfilename)
    return str(matched)


@app.route('/test/', methods=['GET'])
def getName():
    playsound("command.mp3")

    return "Name pronunce done!"


@app.route('/standard/', methods=['GET'])
def getTextSpeechConverter():
    mytext = str(request.args.get('username'))
    myid = str(request.args.get('employeeId'))
    language = str(request.args.get('language'))
    voice = str(request.args.get('voice'))
    slow = str(request.args.get('slow'))
    fileName = myid + "_speechrecognition.mp3"
    engine = init_engine()
    isPresent = change_voice(engine, mytext, language, slow, voice)

    if not isPresent:
        if language == "en_GB":
            tld = 'co.uk'
        elif language == "en_IN":
            ltd = 'co.in'
        elif language == "en_US":
            ltd = 'com'
        if slow == "false":
            myobj = gTTS(text=mytext, lang='en', tld=tld, slow=False)
        else:
            myobj = gTTS(text=mytext, lang='en', tld=tld, slow=True)

        myobj.save(fileName)

        # play the audio file
        playsound(fileName)

    txt = p.convert(mytext)
    # os.remove(fileName)
    return txt


@app.route('/usersSignLang/', methods=['GET'])
@cross_origin(supports_credentials=True)
def getusersSignLangSpeech():
    myid = str(request.args.get('employeeId'))
    filename = myid + "_recording.wav"
    # config = AzureBlob.load_config()
    # AzureBlob.get_blob_audio(filename, config["azure_storage_connectionstring"], config["container_name"])

    # play the audio file
    playsound(filename)
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        # listen for the data (load audio to memory)
        audio_data = r.record(source)
        # recognize (convert from speech to text)
        text = r.recognize_google(audio_data)
    # os.remove(filename)
    return text


@app.route('/users/', methods=['GET'])
@cross_origin(supports_credentials=True)
def getusersSpeech():
    myid = str(request.args.get('employeeId'))
    filename = myid + "_recording.wav"
    # config = AzureBlob.load_config()
    # AzureBlob.get_blob_audio(filename, config["azure_storage_connectionstring"], config["container_name"])

    # play the audio file
    playsound(filename)
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        # listen for the data (load audio to memory)
        audio_data = r.record(source)
        # recognize (convert from speech to text)
        text = r.recognize_google(audio_data)

    txt = p.convert(text)
    # os.remove(filename)
    return txt


@app.route('/recording/', methods=['GET'])
def getRecordSpeechConverter():
    myid = str(request.args.get('employeeId'))

    fps = 44100
    duration = 3
    # myobj = gTTS(text="Please record your name with new pronunciation after the beep", lang="en", slow=False)
    # myobj.save("command.mp3")
    playsound("command.mp3")
    playsound("beep.mp3")

    filename = myid + "_recording.wav"
    recording = sounddevice.rec(int(duration * fps), samplerate=fps, channels=1)
    # Saving the array in a text file
    # numpy.savetxt("file1.txt", recording)
    sounddevice.wait()
    # write(filename, fps, recording)
    wavio.write(filename, recording, fps, sampwidth=2)
    playsound("thankyou.mp3")
    config = AzureBlob.load_config()
    AzureBlob.upload_file(filename, config["azure_storage_connectionstring"], config["container_name"])
    # os.remove(filename)

    return "Name pronunce done!"


if __name__ == '__main__':
    app.run(debug=True)
