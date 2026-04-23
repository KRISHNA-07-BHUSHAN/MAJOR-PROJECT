# models package
# sentinalCloud-backend/app/models/__init__.py

"""
The models package handles loading machine learning models and running predictions.
"""
from .deep_model import predict_ensemble

# This makes the predict_ensemble function directly available when importing the models package.
__all__ = ["predict_ensemble"]