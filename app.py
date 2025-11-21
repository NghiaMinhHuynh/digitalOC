from flask import Flask, jsonify
from flask_cors import CORS
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server
import matplotlib.pyplot as plt

from pbp_situation_model import train_pbp_model, predict_play
from run_model import train_run_models, predict_run_metrics


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/suggestPlay/<situation>", methods=['GET'])
def suggest_play(situation):
    ''' Endpoint from the React frontend to get play suggestion based on the incoming situation '''

    # Convert the attributes from the URL string to a list of appropriate types
    '''
        The string is as follows:

        "down [0], ydstogo [1], yardline_100 [2], goal_to_go [3], quarter_seconds_remaining [4], half_seconds_remaining [5], 
        game_seconds_remaining [6], score_differential [7], posteam_timeouts_remaining [8], defteam_timeouts_remaining [9], 
        posteam [10], defteam [11]"
    '''
    situation = situation.split(',')
    situation = [int(situation[0]), int(situation[1]), int(situation[2]), int(situation[3]), int(situation[4]),
                 int(situation[5]), int(situation[6]), int(situation[7]), int(situation[8]), int(situation[9]),
                 situation[10], situation[11]]

    # Predict whether the play type for the given situation should be a run or pass
    prediction, confidence = predict_play(situation, trained_model=train_pbp_model()[0], feature_columns=train_pbp_model()[1])



    # Depending on the prediction, feed it into the run or pass model
    if prediction == 'run':
        run_prediction = predict_run_metrics(situation, trained_models=train_run_models())
        run_gap = run_prediction['run_gap']
        run_location = run_prediction['run_location']
        offense_formation = run_prediction['offense_formation']
        personnel_off = run_prediction['personnel_off']

        print(f"Suggested Run Play Metrics")
        print(f"Run Gap: {run_gap}")
        print(f"Run Location: {run_location}")
        print(f"Offense Formation: {offense_formation}")
        print(f"Personnel Offense: {personnel_off}")



    if prediction == 'pass':
        # For pass plays, we would ideally call a function to predict pass metrics
        # Since that function is not defined, we will just print a placeholder
        print("Pass Prediction: [Placeholder for pass metrics prediction]")


    # IMPORTANT: Placeholder return statement, visualization will be added later
    return f"Suggested play: {prediction} with confidence {confidence}"


    # Generate your matplotlib visualization here
    # Example: Replace this with your actual plotting code
    # fig, ax = plt.subplots()
    # ... your plotting code ...
    
    # Convert plot to base64 image
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()  # Important: close the plot to free memory
    
    # Return JSON with prediction data and image
    return jsonify({
        'prediction': prediction,
        'confidence': float(confidence),
        'visualization': f'data:image/png;base64,{img_base64}',
        'run_gap': run_gap if prediction == 'run' else None,
        'run_location': run_location if prediction == 'run' else None,
        'offense_formation': offense_formation if prediction == 'run' else None,
        'personnel_off': personnel_off if prediction == 'run' else None
    })


if __name__ == "__main__":
    app.run()