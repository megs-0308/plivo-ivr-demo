from flask import Flask, Response, request
import plivo
from plivo import xml

app = Flask(__name__)

from dotenv import load_dotenv
import os

load_dotenv()

AUTH_ID = os.getenv("PLIVO_AUTH_ID")
AUTH_TOKEN = os.getenv("PLIVO_AUTH_TOKEN")


PLIVO_NUMBER = "+14692463987"
CALLER_NUMBER = "+917892490729"
AGENT_NUMBER = "+919027710597"


@app.route("/call", methods=["GET"])
def call():
    client = plivo.RestClient(AUTH_ID, AUTH_TOKEN)
    client.calls.create(
        from_=PLIVO_NUMBER,
        to_=CALLER_NUMBER,
        answer_url="https://redly-nonadverbial-alexis.ngrok-free.dev/ivr",
        answer_method="GET"
    )
    return "Call triggered"


# LEVEL 1
@app.route("/ivr", methods=["GET", "POST"])
def ivr():
    r = xml.ResponseElement()

    gd = r.add(xml.GetDigitsElement(
        action="https://redly-nonadverbial-alexis.ngrok-free.dev/language",
        method="POST",
        timeout=15,
        num_digits=1
    ))

    gd.add(xml.SpeakElement(
        "Press 1 for English. Press 2 for Spanish."
    ))

    r.add(xml.RedirectElement(
        "https://redly-nonadverbial-alexis.ngrok-free.dev/ivr",
        method="POST"
    ))

    return Response(r.to_string(), mimetype="text/xml")


# LEVEL 2
@app.route("/language", methods=["POST"])
def language():
    r = xml.ResponseElement()

    gd = r.add(xml.GetDigitsElement(
        action="https://redly-nonadverbial-alexis.ngrok-free.dev/option",
        method="POST",
        timeout=15,
        num_digits=1
    ))

    gd.add(xml.SpeakElement(
        "Press 1 to hear a message. Press 2 to talk to an associate."
    ))

    r.add(xml.RedirectElement(
        "https://redly-nonadverbial-alexis.ngrok-free.dev/language",
        method="POST"
    ))

    return Response(r.to_string(), mimetype="text/xml")


# OPTION
@app.route("/option", methods=["POST"])
def option():
    digit = request.form.get("Digits")
    r = xml.ResponseElement()

    if digit == "1":
        r.add(
            xml.PlayElement(
                "https://raw.githubusercontent.com/megs-0308/plivo-ivr-demo/main/demo_audio.mp3"
            )
        )

    elif digit == "2":
        dial = xml.DialElement(caller_id=PLIVO_NUMBER)
        dial.add(xml.NumberElement("+919027710597"))
        r.add(dial)   # 🔴 ADD DIAL TO RESPONSE ONLY AFTER NUMBER

    else:
        r.add(xml.SpeakElement("Invalid option"))

    return Response(r.to_string(), mimetype="text/xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
