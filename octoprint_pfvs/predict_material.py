import os
import numpy as np
import joblib
import logging

def predict_material(spectral_data, color_label):
    """
    Predicts the filament material given spectral data and a color label.
    
    Parameters:
        spectral_data (list or np.array): An array of 18 spectral channel values.
        color_label (str): A single-character string representing the filament color ('R', 'B', 'G', etc.).
    
    Returns:
        str: Predicted filament material.
    """
    logger = logging.getLogger("octoprint.plugins.pfvs")
    logger.setLevel(logging.DEBUG)
    logger.debug("Starting material prediction process.")
    
    # Define paths
    model_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load the trained model and preprocessing tools
    try:
        scaler = joblib.load(model_dir + '/scaler.pkl')
        pca = joblib.load(model_dir + '/pca.pkl')
        model = joblib.load(model_dir + '/svm_model.pkl')
        material_encoder = joblib.load(model_dir + '/material_encoder.pkl')
        color_encoder = joblib.load(model_dir + '/color_encoder.pkl')
        logger.debug("Models and preprocessing tools loaded successfully.")
    except Exception as e:
        logger.error(f"Error loading models or preprocessing tools: {e}")
        raise
    
    # Ensure spectral data is a NumPy array
    spectral_data = np.array(spectral_data)
    logger.debug(f"Spectral data type: {spectral_data.dtype}, shape: {spectral_data.shape}")
    
    # Validate input dimensions
    if spectral_data.shape[0] != 18:
        logger.error("Spectral data must contain exactly 18 channel values.")
        raise ValueError("Spectral data must contain exactly 18 channel values.")
    
    # Encode the color
    try:
        encoded_color = color_encoder.transform([color_label])[0]
        logger.debug(f"Encoded color: {encoded_color}")
    except Exception as e:
        logger.error(f"Error encoding color: {e}")
        raise
    
    # Combine spectral data with encoded color
    combined_sample = np.append(spectral_data, encoded_color).reshape(1, -1)
    logger.debug(f"Combined sample shape: {combined_sample.shape}, dtype: {combined_sample.dtype}")
    
    # Scale the combined data
    try:
        scaled_sample = scaler.transform(combined_sample)
        logger.debug(f"Scaled sample dtype after scaling: {scaled_sample.dtype}")
    except Exception as e:
        logger.error(f"Error scaling data: {e}")
        raise
    
    # Apply PCA
    try:
        pca_sample = pca.transform(scaled_sample) # Ensure pca_sample is float32
        logger.debug(f"PCA transformed sample dtype: {pca_sample.dtype}")
    except Exception as e:
        logger.error(f"Error applying PCA: {e}")
        raise
    
    # Predict material type
    try:
        logger.debug("Before Predicted")
        predicted_material_encoded = model.predict(pca_sample)
        predicted_material_encoded = predicted_material_encoded.astype(np.int32)

        logger.debug("After Predicted")
        logger.debug(f"Predicted Material Encoded DType: {predicted_material_encoded.dtype}")
        predicted_material = material_encoder.inverse_transform(predicted_material_encoded)[0]
        logger.debug(f"Predicted Material DType: {predicted_material.dtype}")
        logger.debug(f"Predicted Material: {predicted_material}")
    except Exception as e:
        logger.error(f"Error predicting material: {e}")
        raise
    
    return predicted_material
