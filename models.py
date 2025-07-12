from app import db
from datetime import datetime

class WordPressConnection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_url = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    app_password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<WordPressConnection {self.site_url}>'

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wp_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    featured_image_url = db.Column(db.String(500))
    wp_connection_id = db.Column(db.Integer, db.ForeignKey('word_press_connection.id'), nullable=False)
    last_synced = db.Column(db.DateTime, default=datetime.utcnow)
    
    wp_connection = db.relationship('WordPressConnection', backref=db.backref('posts', lazy=True))
    
    def __repr__(self):
        return f'<BlogPost {self.title}>'

class ProcessedImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    processed_url = db.Column(db.String(500), nullable=False)
    author = db.Column(db.String(255))
    alt_text = db.Column(db.Text)
    file_size = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ProcessedImage {self.original_url}>'
