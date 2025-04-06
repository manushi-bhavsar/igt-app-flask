from flask import Flask, render_template, request, jsonify, session
from capstone import IowaGamblingTask, Deck
from collections import defaultdict

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management

app.static_folder = "static"
app.template_folder = "templates"

# --- Helpers ---
def serialize_game(game):
    return {
        "bank": game.bank,
        "deck_choices": dict(game.deck_choices),
        "decks": {k: vars(v) for k, v in game.decks.items()},
    }

def deserialize_game(data):
    game = IowaGamblingTask()
    game.bank = data.get("bank", 2000)
    game.deck_choices = defaultdict(int, data.get("deck_choices", {}))
    game.decks = {k: Deck(**v) for k, v in data["decks"].items()}
    return game

# --- Routes ---
@app.route("/reset")
def reset():
    session.clear()
    return "Session cleared. Refresh the page to start a new game."

@app.route("/button")
def button_page():
    return render_template("button.html")

@app.route("/")
def index():
    session.clear()  # Always reset the game at the start
    session["game"] = serialize_game(IowaGamblingTask())
    return render_template("index.html")

@app.route("/deck_option")
def deck_option():
    if "game" in session:
        game = deserialize_game(session["game"])
        round_number = sum(game.deck_choices.values())
        return render_template("deck_option.html", bank=game.bank, round=round_number)
    return render_template("deck_option.html", bank="--", round="--")

@app.route("/choose_deck", methods=["POST"])
def choose_deck():
    data = request.get_json()
    deck_choice = data.get("deck", "").upper()

    if "game" not in session:
        return jsonify({"error": "Game session not found. Please refresh the page."}), 400

    game = deserialize_game(session["game"])

    if deck_choice not in game.decks:
        return jsonify({"error": "Invalid deck choice."}), 400

    # Play the deck
    net_gain = game.decks[deck_choice].play()
    gain = game.decks[deck_choice].last_gain
    penalty = game.decks[deck_choice].last_penalty

    game.bank += net_gain
    game.deck_choices[deck_choice] += 1
    round_number = sum(game.deck_choices.values())

    # Save game
    session["game"] = serialize_game(game)

    # Store latest result
    session["last_result"] = {
        "gain": gain,
        "penalty": penalty,
        "net_gain": net_gain,
        "round": round_number,
        "bank": game.bank
    }

    # If round 100, store final data
    if round_number >= 100:
        session["final_score"] = {
            "bank": game.bank,
            "round": round_number,
            "deck_choices": dict(game.deck_choices)
        }
        return jsonify({"redirect": "/final"})

    return jsonify({
        "redirect": "/gain_loss",
        "bank": game.bank,
        "round": round_number
    })

@app.route("/gain_loss")
def gain_loss():
    result = session.get("last_result", {
        "gain": 0,
        "penalty": 0,
        "net_gain": 0,
        "round": 0,
        "bank": 2000
    })
    return render_template("gain_loss.html", result=result)

@app.route("/final")
def final():
    game_data = session.get("game")
    if game_data:
        game = deserialize_game(game_data)
        deck_choices = dict(game.deck_choices)
    else:
        deck_choices = {}

    final_data = session.get("final_score", {})
    return render_template("final.html", result=final_data, deck_choices=deck_choices)

if __name__ == "__main__":
    app.run(debug=True)