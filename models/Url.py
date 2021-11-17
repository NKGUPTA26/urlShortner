from datetime import datetime
from database import db

class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500),nullable = False)
    short_url = db.Column(db.String(500), nullable=True)
    total_clicks = db.Column(db.Integer, nullable=True, default=0)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.now())
    clicks = db.relationship("Clicks",backref = 'url',lazy=True)
    
    def __repr__(self):
        return f"{self.original_url},{self.short_url},{self.clicks},{self.datetime}"

class Clicks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url_click_at_time = db.Column(db.Integer, nullable=True, default=0)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    url_id = db.Column(db.Integer, db.ForeignKey('url.id'), nullable=False)
    
    def __repr__(self):
        return f"{self.url_click_at_time},{self.url_id}"