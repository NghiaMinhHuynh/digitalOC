from flask import Flask, jsonify, send_file
from flask_cors import CORS
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for Flask
import matplotlib.pyplot as plt

from pbp_situation_model import predict_play
from run_model import predict_run_metrics, predict_run_metric_candidates
from pass_model import predict_pass_metrics, predict_pass_metric_candidates
from routeDrawer.playDraw import visualize_play

import joblib
from pathlib import Path

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


# Load the PBP, run and pass models when the application starts
model_dir = Path("models")
model_dir.mkdir(exist_ok=True)
pbp_model = joblib.load(model_dir / "pbp_situation_model.joblib")
run_models = joblib.load(model_dir / "run_models.joblib")
pass_models = joblib.load(model_dir / "pass_models.joblib")

import json
with open(model_dir / "pbp_situation_model_meta.json", 'r') as f:
    metadata = json.load(f)
pbp_feature_columns = metadata["feature_columns"]

def clean_personnel_for_visual(personnel_off):
    if not personnel_off:
        return personnel_off
    return ', '.join([
        part for part in personnel_off.split(', ')
        if any(pos in part for pos in ['RB', 'WR', 'TE'])
    ])


def dedupe_plays(plays):
    seen = set()
    unique = []

    for play in plays:
        key = tuple(sorted(play.items()))
        if key not in seen:
            seen.add(key)
            unique.append(play)

    return unique


def build_run_play_candidates(situation, run_models, play_type_confidence, top_k_each=3):
    candidates = predict_run_metric_candidates(situation, run_models, top_k=top_k_each)

    required = ["run_gap", "run_location", "offense_formation", "personnel_off"]
    if not all(metric in candidates for metric in required):
        return []

    plays = []
    for gap in candidates["run_gap"]:
        for loc in candidates["run_location"]:
            for formation in candidates["offense_formation"]:
                for personnel in candidates["personnel_off"]:
                    score = (
                        play_type_confidence
                        * gap["prob"]
                        * loc["prob"]
                        * formation["prob"]
                        * personnel["prob"]
                    )

                    plays.append({
                        "play_type": "run",
                        "score": float(score),
                        "run_gap": gap["label"],
                        "run_location": loc["label"],
                        "offense_formation": formation["label"],
                        "personnel_off": personnel["label"],
                    })

    plays.sort(key=lambda x: x["score"], reverse=True)
    return dedupe_plays(plays)


def build_pass_play_candidates(situation, pass_models, play_type_confidence, top_k_each=2):
    candidates = predict_pass_metric_candidates(situation, pass_models, top_k=top_k_each)

    required = [
        "pass_length", "pass_location", "offense_formation",
        "offense_personnel", "route", "receiver_position"
    ]
    if not all(metric in candidates for metric in required):
        return []

    plays = []
    for pass_length in candidates["pass_length"]:
        for pass_location in candidates["pass_location"]:
            for formation in candidates["offense_formation"]:
                for personnel in candidates["offense_personnel"]:
                    for route in candidates["route"]:
                        for receiver in candidates["receiver_position"]:
                            score = (
                                play_type_confidence
                                * pass_length["prob"]
                                * pass_location["prob"]
                                * formation["prob"]
                                * personnel["prob"]
                                * route["prob"]
                                * receiver["prob"]
                            )

                            plays.append({
                                "play_type": "pass",
                                "score": float(score),
                                "pass_length": pass_length["label"],
                                "pass_location": pass_location["label"],
                                "offense_formation": formation["label"],
                                "offense_personnel": personnel["label"],
                                "route": route["label"],
                                "receiver_position": receiver["label"],
                            })

    plays.sort(key=lambda x: x["score"], reverse=True)
    return dedupe_plays(plays)

@app.route("/suggestPlay/<situation>", methods=['GET'])
def suggest_play(situation):
    """
    Return top 3 play suggestions as JSON.
    """
    situation = situation.split(',')
    situation = [
        int(situation[0]), int(situation[1]), int(situation[2]), int(situation[3]),
        int(situation[4]), int(situation[5]), int(situation[6]), int(situation[7]),
        int(situation[8]), int(situation[9]), situation[10], situation[11]
    ]

    score_diff = abs(situation[7])
    if score_diff > 16:
        print("NOTICE: Game state is non-competitive. Suggestion may be biased by clock-management.")

    yardline = situation[2]
    is_midfield_aggression = 1 if 35 <= yardline <= 45 else 0
    is_deep_redzone = 1 if yardline <= 10 else 0

    situation.append(is_midfield_aggression)
    situation.append(is_deep_redzone)

    prediction_int, confidence = predict_play(
    situation,
    trained_model=pbp_model,
    feature_columns=pbp_feature_columns
)

    prediction_int = int(prediction_int)

    if len(confidence.shape) == 2:
        run_conf = float(confidence[0][0])
        pass_conf = float(confidence[0][1])
    else:
        run_conf = float(confidence[0])
        pass_conf = float(confidence[1])

    run_candidates = build_run_play_candidates(
        situation=situation,
        run_models=run_models,
        play_type_confidence=run_conf,
        top_k_each=3
    )

    pass_candidates = build_pass_play_candidates(
        situation=situation,
        pass_models=pass_models,
        play_type_confidence=pass_conf,
        top_k_each=2
    )

    all_candidates = run_candidates + pass_candidates
    all_candidates.sort(key=lambda x: x["score"], reverse=True)

    top_3 = all_candidates[:3]

    return jsonify({
        "plays": top_3
    })


@app.route("/playVisualization", methods=['GET'])
def get_play_visualization():
    return send_file('play_visualization.png', mimetype='image/png')


if __name__ == "__main__":
    app.run()
