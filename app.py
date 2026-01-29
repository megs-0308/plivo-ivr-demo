from flask import Flask, Response, request
import plivo
from plivo import xml

app = Flask(__name__)

AUTH_ID = "MANZJJOGRLNZK0ZMZIMM"
AUTH_TOKEN = "NmU2ZmRhMjYtOTE1OS00YWRiLWJlNmEtNTIxYzUy"

PLIVO_NUMBER = "14692463987"
DESTINATION_NUMBER = "917892490729"


@app.route("/call")
def make_call():
    client = plivo.RestClient(AUTH_ID, AUTH_TOKEN)

    client.calls.create(
        from_=PLIVO_NUMBER,
        to_=DESTINATION_NUMBER,
        answer_url="https://redly-nonadverbial-alexis.ngrok-free.dev/ivr",
        answer_method="GET"
    )
    return "Call triggered"


# ---------- LEVEL 1 ----------
@app.route("/ivr", methods=["GET", "POST"])
def ivr():
    r = xml.ResponseElement()

    gd = r.add(
        xml.GetDigitsElement(
            action="https://redly-nonadverbial-alexis.ngrok-free.dev/language",
            method="POST",
            timeout=10,
            num_digits=1,
            bargein="true"
        )
    )

    gd.add(xml.SpeakElement(
        "Press 1 for English. Press 2 for Spanish."
    ))

    return Response(r.to_string(), mimetype="text/xml")


# ---------- LEVEL 2 ----------
@app.route("/language", methods=["POST"])
def language():
    digit = request.form.get("Digits")
    r = xml.ResponseElement()

    if digit in ["1", "2"]:
        gd = r.add(
            xml.GetDigitsElement(
                action="https://redly-nonadverbial-alexis.ngrok-free.dev/option",
                method="POST",
                timeout=10,
                num_digits=1,
                bargein="true"
            )
        )

        gd.add(xml.SpeakElement(
            "Press 1 to hear a message. Press 2 to talk to an associate."
        ))
    else:
        r.add(xml.SpeakElement("Invalid input. Goodbye."))

    return Response(r.to_string(), mimetype="text/xml")


# ---------- OPTION ----------
@app.route("/option", methods=["POST"])
def option():
    digit = request.form.get("Digits")
    r = xml.ResponseElement()

    if digit == "1":
        r.add(xml.PlayElement(
            "https://raw.githubusercontent.com/megs-0308/plivo-ivr-demo/main/demo_audio.mp3"
        ))
    elif digit == "2":
        r.add(xml.DialElement("917892753709"))
    else:
        r.add(xml.SpeakElement("Invalid option."))

    return Response(r.to_string(), mimetype="text/xml")


if __name__ == "__main__":
    app.run(port=5000)
