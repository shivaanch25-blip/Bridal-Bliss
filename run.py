from app import create_app, db
import os

app = create_app()

if __name__ == '__main__':
    # Ensure static upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, port=5000)
