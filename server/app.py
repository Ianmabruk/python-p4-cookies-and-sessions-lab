#!/usr/bin/env python3

from flask import Flask, jsonify, session
from flask_migrate import Migrate
from models import db, Article, User  # Ensure your models.py defines these correctly

# ------------------------
# Flask App Setup
# ------------------------
app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'  # Used for session hashing

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.sort_keys = False  # Fix deprecated JSON_SORT_KEYS

# Initialize DB and migrations
db.init_app(app)
migrate = Migrate(app, db)

# Automatically create tables if they don't exist
with app.app_context():
    db.create_all()

# ------------------------
# Routes
# ------------------------

@app.route('/clear')
def clear_session():
    """Reset the user's session page_views to 0."""
    session['page_views'] = 0
    return {'message': 'Session cleared successfully.'}, 200

@app.route('/articles')
def index_articles():
    """Return all articles in the database."""
    articles = Article.query.all()
    return jsonify([a.to_dict() for a in articles]), 200

@app.route('/articles/<int:id>')
def show_article(id):
    """Return a single article and track page views for the paywall feature."""
    
    # Initialize page_views if this is the first request
    session['page_views'] = session.get('page_views', 0)
    
    # Increment page_views
    session['page_views'] += 1

    # Check if user exceeded max allowed page views
    if session['page_views'] > 3:
        return jsonify({'message': 'Maximum pageview limit reached'}), 401

    # Fetch the article safely
    article = db.session.get(Article, id)
    if not article:
        return jsonify({'message': f'Article with id {id} not found'}), 404

    return jsonify(article.to_dict()), 200

@app.route('/users')
def index_users():
    """Return all users."""
    users = User.query.all()
    return jsonify([u.to_dict() for u in users]), 200

@app.route('/users/<int:id>')
def show_user(id):
    """Return a single user."""
    user = db.session.get(User, id)
    if not user:
        return jsonify({'message': f'User with id {id} not found'}), 404
    return jsonify(user.to_dict()), 200

# ------------------------
# Main
# ------------------------
if __name__ == '__main__':
    app.run(port=5555, debug=True)
