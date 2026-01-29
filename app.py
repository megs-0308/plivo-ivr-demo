from flask import Flask, Response, request
import plivo
from plivo import xml

app = Flask(__name__)

AUTH_ID = "MANZJJOGRLNZK0ZMZIMM"
AUTH_TOKEN = "NmU2ZmRhMjYtOTE1OS00YWRiLWJlNmEtNTIxYzUy"

PLIVO_NUMBER = "14692463987"
DESTINATION_NUMBER = "917892490729"


@app.route("/")
def home():
    return "Plivo IVR App Running"


@app.route("/call")
def make_call():
    client = plivo.RestClient(AUTH_ID, AUTH_TOKEN)

    client.calls.create(
        from_=PLIVO_NUMBER,
        to_=DESTINATION_NUMBER,
        answer_url="https://redly-nonadverbial-alexis.ngrok-free.dev/ivr",
        answer_method="POST"
    )

    return "Outbound call triggered"


@app.route("/ivr", methods=["GET", "POST"])
def ivr():
    response = xml.ResponseElement()

    get_digits = response.add(
        xml.GetDigitsElement(
            action="https://redly-nonadverbial-alexis.ngrok-free.dev/language",
            method="POST",
            timeout=15,
            num_digits=1,
            retries=1
        )
    )

    get_digits.add(
        xml.SpeakElement(
            "Press 1 for English. Press 2 for Spanish."
        )
    )

    response.add(
        xml.RedirectElement(
            "https://redly-nonadverbial-alexis.ngrok-free.dev/ivr",
            method="POST"
        )
    )

    return Response(response.to_string(), mimetype="text/xml")


@app.route("/language", methods=["POST"])
def language():
    digit = request.form.get("Digits")
    response = xml.ResponseElement()

    if digit in ["1", "2"]:
        get_digits = response.add(
            xml.GetDigitsElement(
                action="https://redly-nonadverbial-alexis.ngrok-free.dev/option",
                method="POST",
                timeout=15,
                num_digits=1,
                retries=1
            )
        )

        get_digits.add(
            xml.SpeakElement(
                "Press 1 to hear a message. Press 2 to talk to an associate."
            )
        )

        response.add(
            xml.RedirectElement(
                "https://redly-nonadverbial-alexis.ngrok-free.dev/language",
                method="POST"
            )
        )

    else:
        response.add(xml.SpeakElement("Invalid language selection."))
        response.add(
            xml.RedirectElement(
                "https://redly-nonadverbial-alexis.ngrok-free.dev/ivr",
                method="POST"
            )
        )

    return Response(response.to_string(), mimetype="text/xml")



@app.route("/option", methods=["POST"])
def option():
    digit = request.form.get("Digits")
    response = xml.ResponseElement()

    if digit == "1":
        response.add(
            xml.PlayElement(
                "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
            )
        )
    elif digit == "2":
        response.add(
            xml.DialElement("14692463990")
        )
    else:
        response.add(xml.SpeakElement("Invalid option."))

    return Response(response.to_string(), mimetype="text/xml")




if __name__ == "__main__":
    app.run(port=5000)
