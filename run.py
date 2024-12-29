from app import create_app, db
import pytesseract
from flask_migrate import Migrate

# If necessary, set the tesseract path
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  # Change this path if necessary

app = create_app()
migrate = Migrate(app, db)  # Initialize migration with your app and db

with app.app_context():
    db.create_all()  # Or use flask-migrate for handling schema changes

    print("Database tables created.")

if __name__ == "__main__":
    app.run(port=5003, debug=True)
