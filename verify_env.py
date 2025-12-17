import os
from app import create_app, db
from app.models import User

try:
    print("Creating app...")
    app = create_app()
    print("App created.")
    
    with app.app_context():
        print("Checking database...")
        db.create_all()
        print("Database tables created/verified.")
        
        user_count = User.query.count()
        print(f"User count: {user_count}")
        
        print("Environment verification successful.")
except Exception as e:
    print(f"Environment verification FAILED: {e}")
