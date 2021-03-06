import os

DEBUG = False
HOST = '0.0.0.0'
PORT = 5000
THREADED = True
MONGODB_DB = os.environ.get("MONGO_DB", "local")
VECTOR_MODELS_DIR = "vector_models/"
SUPERVISED_VECTOR_MODELS_DIR = "supervised_models/"
