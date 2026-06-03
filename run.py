from app import create_app
import os

config_path = os.environ.get('BRIDAL_BLISS_CONFIG', 'config.Config')
app = create_app(config_path)

if __name__ == '__main__':
    # Ensure static upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=app.config.get('DEBUG', False), port=int(os.environ.get('PORT', 5000)))
