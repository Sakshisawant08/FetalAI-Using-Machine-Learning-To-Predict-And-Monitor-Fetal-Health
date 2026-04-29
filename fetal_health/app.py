
from flask import Flask, render_template, request, make_response
import pickle
import numpy as np
import warnings
from datetime import datetime
import io

app = Flask(__name__)

# Suppress sklearn warnings
warnings.filterwarnings("ignore", category=UserWarning)

# ============================================
# LOAD MODEL
# ============================================
try:
    model = pickle.load(open("model.pkl", "rb"))
    print("Model loaded successfully!")
    print(f"Model type: {type(model)}")
except Exception as e:
    print(f"Error loading model: {e}")
    print("Creating dummy predictor for testing...")
    
    class DummyModel:
        def predict(self, features):
            # Simple rule-based prediction based on baseline value
            baseline = features[0][0]  # First feature is baseline_value
            if baseline < 130:
                return np.array([1])  # Normal
            elif baseline < 150:
                return np.array([2])  # Suspect
            else:
                return np.array([3])  # Pathological
    
    model = DummyModel()
    print("Dummy model created!")

# ============================================
# ROUTES
# ============================================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict")
def predict_page():
    return render_template("predict.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Get all 21 form data fields
        baseline_value = float(request.form["baseline_value"])
        accelerations = float(request.form["accelerations"])
        fetal_movement = float(request.form["fetal_movement"])
        uterine_contractions = float(request.form["uterine_contractions"])
        light_decelerations = float(request.form["light_decelerations"])
        severe_decelerations = float(request.form["severe_decelerations"])
        prolonged_decelerations = float(request.form["prolonged_decelerations"])
        abnormal_short_term_variability = float(request.form["abnormal_short_term_variability"])
        mean_short_term_variability = float(request.form["mean_short_term_variability"])
        percentage_long_term_variability = float(request.form["percentage_long_term_variability"])
        mean_long_term_variability = float(request.form["mean_long_term_variability"])
        histogram_width = float(request.form["histogram_width"])
        histogram_min = float(request.form["histogram_min"])
        histogram_max = float(request.form["histogram_max"])
        histogram_number_of_peaks = float(request.form["histogram_number_of_peaks"])
        histogram_number_of_zeroes = float(request.form["histogram_number_of_zeroes"])
        histogram_mode = float(request.form["histogram_mode"])
        histogram_mean = float(request.form["histogram_mean"])
        histogram_median = float(request.form["histogram_median"])
        histogram_variance = float(request.form["histogram_variance"])
        histogram_tendency = float(request.form["histogram_tendency"])
        
        # Create feature array with all 21 features
        features = np.array([[
            baseline_value,
            accelerations,
            fetal_movement,
            uterine_contractions,
            light_decelerations,
            severe_decelerations,
            prolonged_decelerations,
            abnormal_short_term_variability,
            mean_short_term_variability,
            percentage_long_term_variability,
            mean_long_term_variability,
            histogram_width,
            histogram_min,
            histogram_max,
            histogram_number_of_peaks,
            histogram_number_of_zeroes,
            histogram_mode,
            histogram_mean,
            histogram_median,
            histogram_variance,
            histogram_tendency
        ]])
        
        # Make prediction
        prediction = model.predict(features)[0]
        pred_val = int(prediction) if isinstance(prediction, (int, float, np.integer, np.floating)) else prediction
        
        # Map prediction to result
        if pred_val == 1:
            result = {
                "status": "Normal",
                "color": "success",
                "message": "Your baby's health is normal. Continue regular checkups.",
                "icon": "fa-heart-pulse"
            }
        elif pred_val == 2:
            result = {
                "status": "Suspect",
                "color": "warning",
                "message": "Further medical check is recommended. Please consult your doctor.",
                "icon": "fa-triangle-exclamation"
            }
        else:
            result = {
                "status": "Pathological",
                "color": "danger",
                "message": "High risk detected! Immediate medical attention is required.",
                "icon": "fa-heart-crack"
            }
        
        # Create query parameters for download link
        query_params = f"?status={result['status']}&message={result['message']}&baseline_value={baseline_value}&accelerations={accelerations}&fetal_movement={fetal_movement}&uterine_contractions={uterine_contractions}&light_decelerations={light_decelerations}&severe_decelerations={severe_decelerations}&prolonged_decelerations={prolonged_decelerations}&abnormal_short_term_variability={abnormal_short_term_variability}&mean_short_term_variability={mean_short_term_variability}&percentage_long_term_variability={percentage_long_term_variability}&mean_long_term_variability={mean_long_term_variability}&histogram_width={histogram_width}&histogram_min={histogram_min}&histogram_max={histogram_max}&histogram_number_of_peaks={histogram_number_of_peaks}&histogram_number_of_zeroes={histogram_number_of_zeroes}&histogram_mode={histogram_mode}&histogram_mean={histogram_mean}&histogram_median={histogram_median}&histogram_variance={histogram_variance}&histogram_tendency={histogram_tendency}"
        
        return render_template("result.html", result=result, 
                               download_link=f"/download_report{query_params}",
                               data={
                                   "baseline_value": baseline_value,
                                   "accelerations": accelerations,
                                   "fetal_movement": fetal_movement,
                                   "uterine_contractions": uterine_contractions,
                                   "light_decelerations": light_decelerations,
                                   "severe_decelerations": severe_decelerations,
                                   "prolonged_decelerations": prolonged_decelerations,
                                   "abnormal_short_term_variability": abnormal_short_term_variability,
                                   "mean_short_term_variability": mean_short_term_variability,
                                   "percentage_long_term_variability": percentage_long_term_variability,
                                   "mean_long_term_variability": mean_long_term_variability,
                                   "histogram_width": histogram_width,
                                   "histogram_min": histogram_min,
                                   "histogram_max": histogram_max,
                                   "histogram_number_of_peaks": histogram_number_of_peaks,
                                   "histogram_number_of_zeroes": histogram_number_of_zeroes,
                                   "histogram_mode": histogram_mode,
                                   "histogram_mean": histogram_mean,
                                   "histogram_median": histogram_median,
                                   "histogram_variance": histogram_variance,
                                   "histogram_tendency": histogram_tendency
                               })
    
    except Exception as e:
        result = {
            "status": "Error",
            "color": "secondary",
            "message": f"An error occurred: {str(e)}",
            "icon": "fa-circle-exclamation"
        }
        return render_template("result.html", result=result, data=None)


@app.route("/download_report")
def download_report():
    try:
        # Get data from query parameters (stored in session or passed as params)
        import urllib.parse
        
        # Get parameters from URL
        params = request.args
        
        # Create report content
        report_content = f"""
FETAL HEALTH PREDICTION REPORT
================================
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

PREDICTION RESULT:
----------------
Status: {params.get('status', 'Unknown')}
Message: {params.get('message', 'No message available')}

INPUT PARAMETERS (21 Values):
---------------------------
1. Baseline Value (bpm): {params.get('baseline_value', 'N/A')}
2. Accelerations: {params.get('accelerations', 'N/A')}
3. Fetal Movement: {params.get('fetal_movement', 'N/A')}
4. Uterine Contractions: {params.get('uterine_contractions', 'N/A')}
5. Light Decelerations: {params.get('light_decelerations', 'N/A')}
6. Severe Decelerations: {params.get('severe_decelerations', 'N/A')}
7. Prolonged Decelerations: {params.get('prolonged_decelerations', 'N/A')}
8. Abnormal Short Term Variability: {params.get('abnormal_short_term_variability', 'N/A')}
9. Mean Short Term Variability: {params.get('mean_short_term_variability', 'N/A')}
10. Percentage Long Term Variability: {params.get('percentage_long_term_variability', 'N/A')}
11. Mean Long Term Variability: {params.get('mean_long_term_variability', 'N/A')}
12. Histogram Width: {params.get('histogram_width', 'N/A')}
13. Histogram Min: {params.get('histogram_min', 'N/A')}
14. Histogram Max: {params.get('histogram_max', 'N/A')}
15. Histogram Number of Peaks: {params.get('histogram_number_of_peaks', 'N/A')}
16. Histogram Number of Zeroes: {params.get('histogram_number_of_zeroes', 'N/A')}
17. Histogram Mode: {params.get('histogram_mode', 'N/A')}
18. Histogram Mean: {params.get('histogram_mean', 'N/A')}
19. Histogram Median: {params.get('histogram_median', 'N/A')}
20. Histogram Variance: {params.get('histogram_variance', 'N/A')}
21. Histogram Tendency: {params.get('histogram_tendency', 'N/A')}

RECOMMENDATIONS:
---------------
"""
        
        # Add recommendations based on status
        status = params.get('status', '')
        if status == 'Normal':
            report_content += """
• Continue regular prenatal checkups
• Maintain a healthy diet and stay hydrated
• Monitor baby's movements daily
• Get adequate rest and sleep
"""
        elif status == 'Suspect':
            report_content += """
• Schedule a follow-up with your doctor soon
• Increase fetal movement monitoring
• Consider additional diagnostic tests
• Rest and avoid strenuous activities
"""
        elif status == 'Pathological':
            report_content += """
• Seek immediate medical attention
• Contact your healthcare provider right away
• Go to nearest hospital or clinic
• Do not delay - your baby's health is priority
"""
        
        report_content += f"""

MEDICAL DISCLAIMER:
-----------------
This is an AI-powered prediction tool and should not replace professional medical advice.
Always consult with qualified healthcare providers for medical decisions.

Generated by: FetalAI - Fetal Health Prediction System
Website: http://127.0.0.1:5000
"""
        
        # Create response
        response = make_response(report_content)
        response.headers['Content-Type'] = 'text/plain'
        response.headers['Content-Disposition'] = f'attachment; filename=FetalAI_Report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        
        return response
        
    except Exception as e:
        # Error handling
        error_report = f"Error generating report: {str(e)}"
        response = make_response(error_report)
        response.headers['Content-Type'] = 'text/plain'
        response.headers['Content-Disposition'] = 'attachment; filename=error_report.txt'
        return response


# ============================================
# RUN APP
# ============================================
if __name__ == "__main__":
    print("Starting FetalAI Server...")
    print("Open: http://127.0.0.1:5000")
    app.run(debug=True, use_reloader=False)
