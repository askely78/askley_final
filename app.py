import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Mémoire temporaire des points par utilisateur
user_points = {}
user_feedback = {}

@app.route("/webhook", methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', '')
    sender = request.values.get('From', '')
    print(f"📥 Message reçu de {sender} : {incoming_msg}")

    response = MessagingResponse()

    # Si l'utilisateur donne une évaluation
    if incoming_msg.strip().isdigit() and 1 <= int(incoming_msg.strip()) <= 5:
        note = int(incoming_msg.strip())
        user_feedback[sender] = note
        user_points[sender] = user_points.get(sender, 0) + note * 10
        reply = f"⭐ Merci pour votre évaluation ({note}/5) ! Vous avez maintenant {user_points[sender]} points Askley."
        response.message(reply)
        print(f"📤 Réponse : {reply}")
        return str(response)

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": "Tu es Askley, un assistant intelligent de conciergerie. Tu aides les utilisateurs à réserver hôtels, restaurants, plats, etc."},
                {"role": "user", "content": incoming_msg}
            ]
        )
        reply = completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Erreur GPT : {e}")
        reply = "❌ Erreur GPT. Veuillez réessayer."

    response.message(reply + "\n\n⭐ Évaluez ce service (1 à 5) pour gagner des points Askley.")
    print(f"📤 Réponse : {reply}")
    return str(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)