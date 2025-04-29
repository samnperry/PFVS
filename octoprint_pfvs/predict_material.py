import os
import numpy as np
import joblib
import logging

# Standalone material-prediction function using saved pipeline in ./models_per_color
def predict_material(spectral_array, color_label):
    """
    Predicts filament material from a spectral scan and color label.

    Assumes the current working directory contains a 'models_per_color' folder with:
      - material_encoder.pkl
      - <Color>_scaler.pkl
      - <Color>_feature_weights.pkl
      - <Color>_scaler_weighted.pkl
      - <Color>_pca_weighted.pkl
      - <Color>_svm_model.pkl

    Args:
        spectral_array (array-like): 1D array of raw spectral values.
        color_label (str): filament color (e.g. 'black', 'white').

    Returns:
        str: material prediction (e.g., 'PLA', 'PET', 'ASA').
    """
    
    logger = logging.getLogger("octoprint.plugins.pfvs")
    logger.setLevel(logging.DEBUG)
    logger.debug("Starting material prediction process.")
    
    # Ensure numpy array and correct shape
    X = np.array(spectral_array, dtype=float)
    if X.ndim == 1:
        X = X.reshape(1, -1)

    # Base model directory
    model_dir = os.path.dirname(os.path.abspath(__file__)) + "/models_per_color"

    # Load global material encoder
    encoder_path = os.path.join(model_dir, 'material_encoder.pkl')
    logger.debug(f'{encoder_path}')
    material_encoder = joblib.load(encoder_path)
    logger.error("Material encoded")

    # Normalize color label and build file prefix
    clr = color_label.strip().capitalize()
    prefix = ""
    
    if (clr == 'R'):
        prefix = "Red"
    elif (clr == 'B'):
        prefix = "Blue"
    elif (clr == 'G'):
        prefix = "Green"
    elif (clr == 'K'):
        prefix = "Black"
    elif (clr == 'W'):
        prefix = "White"
    
    prefix = model_dir + "/" + prefix    

    # Load pipeline components
    scaler           = joblib.load(f'{prefix}_scaler.pkl')
    feature_weights  = joblib.load(f'{prefix}_feature_weights.pkl')
    scaler_weighted  = joblib.load(f'{prefix}_scaler_weighted.pkl')
    pca              = joblib.load(f'{prefix}_pca_weighted.pkl')
    svm_model        = joblib.load(f'{prefix}_svm_model.pkl')
    logger.error("All models loaded in")

    # Pipeline: scale, weight, scale, PCA, SVM
    X_scaled     = scaler.transform(X)
    X_weighted   = X_scaled * feature_weights
    X_wt_scaled  = scaler_weighted.transform(X_weighted)
    X_pca        = pca.transform(X_wt_scaled)
    y_pred       = svm_model.predict(X_pca)

    # Return decoded label
    logger.error(material_encoder.inverse_transform(y_pred)[0])
    return material_encoder.inverse_transform(y_pred)[0]


# def predict_material(spectral_data, color_label):
#     """
#     Predicts the filament material given spectral data and a color label.
    
#     Parameters:
#         spectral_data (list or np.array): An array of 18 spectral channel values.
#         color_label (str): A single-character string representing the filament color ('R', 'B', 'G', etc.).
    
#     Returns:
#         str: Predicted filament material.
#     """
#     logger = logging.getLogger("octoprint.plugins.pfvs")
#     logger.setLevel(logging.DEBUG)
#     logger.debug("Starting material prediction process.")
    
#     # Define paths
#     model_dir = os.path.dirname(os.path.abspath(__file__))
    
#     # Load the trained model and preprocessing tools
#     try:
#         scaler = joblib.load(model_dir + '/scaler.pkl')
#         pca = joblib.load(model_dir + '/pca.pkl')
#         model = joblib.load(model_dir + '/svm_model.pkl')
#         material_encoder = joblib.load(model_dir + '/material_encoder.pkl')
#         color_encoder = joblib.load(model_dir + '/color_encoder.pkl')
#     except Exception as e:
#         logger.error(f"Error loading models or preprocessing tools: {e}")
#         raise
    
#     # Ensure spectral data is a NumPy array
#     spectral_data = np.array(spectral_data)
    
#     # Validate input dimensions
#     if spectral_data.shape[0] != 18:
#         raise ValueError("Spectral data must contain exactly 18 channel values.")
    
#     # Encode the color
#     try:
#         encoded_color = color_encoder.transform([color_label])[0]
#     except Exception as e:
#         logger.error(f"Error encoding color: {e}")
#         raise
    
#     # Combine spectral data with encoded color
#     combined_sample = np.append(spectral_data, encoded_color).reshape(1, -1)
    
#     # Scale the combined data
#     try:
#         scaled_sample = scaler.transform(combined_sample)
#     except Exception as e:
#         logger.error(f"Error scaling data: {e}")
#         raise
    
#     # Apply PCA
#     try:
#         pca_sample = pca.transform(scaled_sample) # Ensure pca_sample is float32
#     except Exception as e:
#         logger.error(f"Error applying PCA: {e}")
#         raise
    
#     # Predict material type
#     try:
#         predicted_material_encoded = model.predict(pca_sample)
#         predicted_material_encoded = predicted_material_encoded.astype(np.int32)
#         predicted_material = material_encoder.inverse_transform(predicted_material_encoded)[0]
#     except Exception as e:
#         logger.error(f"Error predicting material: {e}")
#         raise
    
#     return predicted_material