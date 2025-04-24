import os
import numpy as np
import joblib
import logging

def predict_material(spectral_data, color_label):
    """
    Predict filament material for one 18-dim spectral sample and a color code.
    This version is fully self-contained and does not rely on external functions.
    """
    
    logger = logging.getLogger("octoprint.plugins.pfvs")
    logger.setLevel(logging.DEBUG)
    logger.debug("Starting material prediction process.")

    COLOR_MAP = {
        'B': 'Blue',
        'G': 'Green',
        'R': 'Red',
        'K': 'Black',
        'W': 'White'
    }

    # Normalize color label
    cl = color_label.strip()
    if len(cl) == 1:
        code = cl.upper()
        if code not in COLOR_MAP:
            raise ValueError(f"Unknown color code: {color_label!r}")
        full = COLOR_MAP[code]
    else:
        full = cl.capitalize()
        if full not in COLOR_MAP.values():
            raise ValueError(f"Unknown color name: {color_label!r}")

    # Validate spectral data shape
    X = np.array(spectral_data, dtype=float).reshape(1, -1)
    logger.debug(f"Raw input shape: {X.shape}")
    if X.shape[1] != 18:
        raise ValueError("Need exactly 18 spectral channel values.")

    # Load model components
    model_dir = os.path.join(os.path.dirname(__file__), 'models_per_color')
    comp = {}
    to_load = [
        ('scaler',    f'{full}_scaler.pkl'),
        ('weights',   f'{full}_feature_weights.pkl'),
        ('scaler_w',  f'{full}_scaler_weighted.pkl'),
        ('pca',       f'{full}_pca_weighted.pkl'),
        ('svm',       f'{full}_svm_model.pkl'),
        ('encoder',   'material_encoder.pkl')
    ]
    for key, fname in to_load:
        path = os.path.join(model_dir, fname)
        logger.debug(f"Loading {key} from {path}")
        comp[key] = joblib.load(path)
        logger.debug(f"  → {key} loaded (type={type(comp[key]).__name__})")

    # Run prediction pipeline
    Xs = comp['scaler'].transform(X)
    logger.debug(f"After scaler.transform: {Xs.shape}, sample[0]={Xs[0,:3]}…")

    Xw = Xs * comp['weights']
    logger.debug(f"After weighting: {Xw.shape}, weighted[0]={Xw[0,:3]}…")

    Xsw = comp['scaler_w'].transform(Xw)
    logger.debug(f"After scaler_weighted.transform: {Xsw.shape}, sample[0]={Xsw[0,:3]}…")

    Xp = comp['pca'].transform(Xsw)
    logger.debug(f"After PCA.transform: {Xp.shape}, components={comp['pca'].n_components_}")

    y_enc = comp['svm'].predict(Xp)
    logger.debug(f"SVM.predict returned encoded label: {y_enc}")

    material = comp['encoder'].inverse_transform(y_enc.astype(int))[0]
    logger.info(f"Color={color_label}, Predicted material={material}")
    
    return material

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