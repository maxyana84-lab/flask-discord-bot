import os
import requests
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

# 1. SQLite database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Webhook URL is read from the environment, never commit it to Git
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")


# Table model in the database
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# We create a database
with app.app_context():
    db.create_all()


# Function for sending to Discord
def send_to_discord(text):
    if not DISCORD_WEBHOOK_URL:
        print("DISCORD_WEBHOOK_URL is not set")
        return False
    data = {
        "content": text,
        "username": "Flask Bot"
    }
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data, timeout=10)
        return response.status_code == 204
    except Exception as e:
        print(f"Mistake Discord: {e}")
        return False



# Endpoint 1 and 2: Storage and sending
@app.route('/')
def home():
    return "<h1>Flask Server is running!</h1><p>Use /history to view messages.</p>"

@app.route('/submit', methods=['POST', 'GET'])
def handle_message():

    # Getting data from a JSON request
    request_data = request.get_json(force=True)
    user_text = request_data.get('text') if request_data else None

    if not user_text:
        return jsonify({"error": "No text provided"}), 400

    # Save to the database
    new_msg = Message(content=user_text)
    db.session.add(new_msg)
    db.session.commit()

    # Send to Discord
    if send_to_discord(user_text):
        return jsonify({"status": "Success! Saved to DB and sent to Discord"}), 200
    else:
        return jsonify({"status": "Saved to DB, but Discord failed"}), 500


# Endpoint 3: History of the last 30 minutes
@app.route('/history', methods=['POST', 'GET'])
def get_history():
    half_hour_ago = datetime.now(timezone.utc) - timedelta(minutes=30)
    messages = Message.query.filter(Message.timestamp >= half_hour_ago.replace(tzinfo=None)).all()

    output = []
    for msg in messages:
        output.append({
            "id": msg.id,
            "content": msg.content,
            "time": msg.timestamp.strftime("%H:%M:%S")
        })
    return jsonify(output), 200


if __name__ == '__main__':
    # Starting the Flask server
    app.run(
        debug=os.environ.get("FLASK_DEBUG") == "1",
        port=int(os.environ.get("PORT", "5001")),
    )
