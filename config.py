import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bridal-bliss-luxury-secret-key-19283746'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'bridal_bliss.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload folder for user styling photos
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
