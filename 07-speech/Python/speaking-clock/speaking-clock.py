from dotenv import load_dotenv
from datetime import datetime
import os
import requests, json

# Import namespaces
import azure.cognitiveservices.speech as speech_sdk


def main():
    try:
        global speech_config

        # Get Configuration Settings
        load_dotenv()
        cog_key = os.getenv('COG_SERVICE_KEY')
        cog_region = os.getenv('COG_SERVICE_REGION')

        # Configure speech service
        speech_config = speech_sdk.SpeechConfig(cog_key, cog_region)
        print('Ready to use speech service in:', speech_config.region)
        # Get user input (until they say "stop")
        command = ''
        while command.lower() != 'stop.':
            command = TranscribeCommand()
            if command.lower() == 'what time is it?':
                TellTime()

    except Exception as ex:
        print(ex)


def TranscribeCommand():
    command = 'stop.'

    # Configure speech recognition
    audio_config = speech_sdk.AudioConfig(use_default_microphone=True)
    source_language_config = speech_sdk.languageconfig.SourceLanguageConfig("es-ES")
    speech_recognizer = speech_sdk.SpeechRecognizer(speech_config=speech_config,
                                                    audio_config=audio_config,
                                                    source_language_config=source_language_config)

    # Process speech input
    print('Say "stop" to end...')
    speech = speech_recognizer.recognize_once_async().get()
    if speech.reason == speech_sdk.ResultReason.RecognizedSpeech:
        command = speech.text
        print(command)
        print(Translate(command))
    else:
        print(speech.reason)
        if speech.reason == speech_sdk.ResultReason.Canceled:
            cancellation = speech.cancellation_details
            print(cancellation.reason)
            print(cancellation.error_details)

    # Return the command
    return Translate(command)


def TellTime():
    now = datetime.now()
    response_text = 'The time is {}:{:02d}'.format(now.hour, now.minute)

    # Configure speech synthesis
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config)

    # Synthesize spoken output
    responseSsml = " \
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'> \
            <voice name='en-GB-Susan'> \
                {} \
                <break strength='weak'/> \
                Say stop to end! \
            </voice> \
        </speak>".format(response_text)
    speak = speech_synthesizer.speak_ssml_async(responseSsml).get()
    if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print(speak.reason)
    # Print the response
    print(response_text)


def Translate(text):
    translation = ''
    translator_endpoint = 'https://api.cognitive.microsofttranslator.com'

    # Use the Translator translate function
    path = '/translate'
    url = translator_endpoint + path

    # Build the request
    params = {
        'api-version': '3.0',
        'from': 'es',
        'to': ['en']
    }
    cog_key = os.getenv('COG_SERVICE_KEY')
    cog_region = os.getenv('COG_SERVICE_REGION')
    headers = {
        'Ocp-Apim-Subscription-Key': cog_key,
        'Ocp-Apim-Subscription-Region': cog_region,
        'Content-type': 'application/json'
    }

    body = [{
        'text': text
    }]

    # Send the request and get response
    request = requests.post(url, params=params, headers=headers, json=body)
    response = request.json()

    # Parse JSON array and get translation
    translation = response[0]["translations"][0]["text"]
    # Return the translation
    return translation


if __name__ == "__main__":
    main()
