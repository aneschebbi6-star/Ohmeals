"""
OHMEALS - Entry Point
Run this file to start the Flask application.
"""
from app import create_app

app = create_app('development')

if __name__ == '__main__':
    app.run(debug=True)
