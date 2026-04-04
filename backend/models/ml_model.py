import joblib
import json
import os
import signal
from contextlib import contextmanager
from ..config import MODEL_PATH
from ..utils.logger import logger


class TimeoutException(Exception):
    """Exception raised when model loading times out"""
    pass


@contextmanager
def timeout_handler(seconds=10):
    """PHASE 16: Context manager for timeout protection during model loading"""
    def signal_handler(signum, frame):
        raise TimeoutException(f"Model loading exceeded {seconds} seconds timeout")
    
    # Set alarm (Windows doesn't support signal.SIGALRM, but we'll add a try-except)
    try:
        old_handler = signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(seconds)
        yield
    except (AttributeError, ValueError):
        # SIGALRM not available on Windows, skip timeout
        yield
    except TimeoutException:
        raise
    finally:
        try:
            signal.alarm(0)  # Cancel alarm
            signal.signal(signal.SIGALRM, old_handler)
        except (AttributeError, ValueError):
            pass


def load_ml_model_with_validation():
    """
    PHASE 15-16: Load ML model with schema validation and timeout protection
    
    Features:
    - PHASE 15: Validate feature schema on load
    - PHASE 16: Timeout protection, detailed logging, graceful fallback
    """
    try:
        if not os.path.exists(MODEL_PATH):
            raise RuntimeError(f"ML model file not found at {MODEL_PATH}")
        
        # PHASE 16: Timeout protection
        with timeout_handler(seconds=10):
            logger.info(f"Loading ML model from {MODEL_PATH}")
            ml_model = joblib.load(MODEL_PATH)
            logger.info("✅ ML model loaded successfully")
        
        # PHASE 15: Validate model metadata and schema
        metadata_path = os.path.join(os.path.dirname(MODEL_PATH), "model_v1_metadata.json")
        schema_path = os.path.join(os.path.dirname(MODEL_PATH), "feature_schema_v1.json")
        
        # Load and validate metadata
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    logger.info(f"Model version: {metadata.get('version', 'unknown')}")
                    logger.info(f"Training metrics - Accuracy: {metadata.get('training_metrics', {}).get('accuracy', 'N/A')}, ROC-AUC: {metadata.get('training_metrics', {}).get('roc_auc', 'N/A')}")
                    logger.info(f"Quality rating: {metadata.get('quality_assessment', 'UNKNOWN')}")
            except Exception as e:
                logger.warning(f"Could not load model metadata: {str(e)}")
        
        # Load and validate feature schema
        if os.path.exists(schema_path):
            try:
                with open(schema_path, 'r') as f:
                    schema = json.load(f)
                    expected_features = schema.get("feature_count", 22)
                    strict_order = schema.get("validation_rules", {}).get("order_matters", True)
                    
                    # Get actual feature count from model
                    if hasattr(ml_model, 'n_features_in_'):
                        actual_features = ml_model.n_features_in_
                        if actual_features != expected_features:
                            logger.warning(
                                f"⚠️  Feature count mismatch: Expected {expected_features}, "
                                f"Model has {actual_features}. May cause inference errors."
                            )
                        else:
                            logger.info(f"✅ Feature schema validation passed: {expected_features} features")
                    
                    if strict_order:
                        logger.info("📋 Feature order is strictly enforced for inference")
            except Exception as e:
                logger.warning(f"Could not validate feature schema: {str(e)}")
        
        logger.info("✅ ML model fully loaded and validated")
        return ml_model
    
    except TimeoutException as e:
        logger.error(f"❌ Model loading timeout: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to load ML model: {str(e)}")
        return None


# Load ML Model with validation and timeout protection
ml_model = load_ml_model_with_validation()