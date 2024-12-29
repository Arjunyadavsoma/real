from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.orm import validates
import re

class User(db.Model, UserMixin):
    __tablename__ = 'users'  # Convention: use plural for table names
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)  # Increased length for hash
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationship with uploaded files
    files = db.relationship(
        'UploadedFile',
        backref=db.backref('owner', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    @validates('email')
    def validate_email(self, key, email):
        if not email:
            raise ValueError('Email is required')
        
        # Basic email validation pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError('Invalid email format')
        
        if User.query.filter(User.email == email, User.id != self.id).first():
            raise ValueError('Email already registered')
        
        return email.lower()  # Store emails in lowercase

    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError('Username is required')
        
        if len(username) < 3:
            raise ValueError('Username must be at least 3 characters long')
        
        if User.query.filter(User.username == username, User.id != self.id).first():
            raise ValueError('Username already taken')
        
        return username

    def set_password(self, password):
        """Set hashed password."""
        if not password or len(password) < 8:
            raise ValueError('Password must be at least 8 characters long')
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()

    def get_recent_files(self, limit=5):
        """Get user's most recent uploaded files."""
        return self.files.order_by(UploadedFile.uploaded_at.desc()).limit(limit).all()

    def __repr__(self):
        return f"<User {self.username}>"


class UploadedFile(db.Model):
    __tablename__ = 'uploaded_files'  # Convention: use plural for table names
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)  # Increased length for long filenames
    original_filename = db.Column(db.String(255), nullable=False)  # Store original filename
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    mime_type = db.Column(db.String(127), nullable=False)
    extracted_text = db.Column(db.Text, nullable=False)
    summarized_text = db.Column(db.Text, nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime)
    processing_status = db.Column(db.String(20), nullable=False, default='pending')  # pending, processing, completed, failed
    
    # Foreign key relationship
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    @validates('file_size')
    def validate_file_size(self, key, file_size):
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            raise ValueError(f'File size exceeds maximum allowed size of {max_size/1024/1024}MB')
        return file_size

    def update_last_accessed(self):
        """Update last accessed timestamp."""
        self.last_accessed = datetime.utcnow()
        db.session.commit()

    def get_file_size_display(self):
        """Return human-readable file size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024:
                return f"{self.file_size:.1f}{unit}"
            self.file_size /= 1024
        return f"{self.file_size:.1f}TB"

    def __repr__(self):
        return f"<UploadedFile {self.filename} (User: {self.user_id})>"