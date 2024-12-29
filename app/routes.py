import os
from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import RegistrationForm, LoginForm, UploadForm
from app.models import User, UploadedFile
from app.utils import extract_text_from_file, summarize_text
from flask import Blueprint
from app import db, login_manager
import logging
from datetime import datetime
from functools import wraps

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

# Constants
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def rate_limit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.endpoint == "main.login":
            ip = request.remote_addr
            # Implementation of rate limiting logic here
            # This is a placeholder - you'd want to use Redis or similar for production
            pass
        return func(*args, **kwargs)
    return wrapper

@main_bp.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.profile'))

    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=hashed_password,
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.commit()
            logger.info(f"New user registered: {user.username}")
            flash('Your account has been created! Please log in.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'danger')
    
    return render_template('register.html', form=form)

@main_bp.route('/')
def home():
    welcome_message = f"Welcome{' back, ' + current_user.username if current_user.is_authenticated else ''}!"
    return render_template('home.html', message=welcome_message)

def process_file(filepath):
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError("Upload file not found")

        file_size = os.path.getsize(filepath)
        if file_size > MAX_FILE_SIZE:
            raise ValueError("File size exceeds maximum limit")

        extracted_text = extract_text_from_file(filepath)
        if not extracted_text:
            raise ValueError("No text could be extracted from the file")

        summarized_text = summarize_text(extracted_text)
        filename = os.path.basename(filepath)
        
        uploaded_file = UploadedFile(
            filename=filename,
            extracted_text=extracted_text,
            summarized_text=summarized_text,
            user_id=current_user.id,
            upload_date=datetime.utcnow(),
            file_size=file_size
        )

        db.session.add(uploaded_file)
        db.session.commit()
        logger.info(f"File processed successfully: {filename}")
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing file {filepath}: {str(e)}")
        raise

@main_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()

    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                
                # Ensure upload directory exists
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                
                file.save(upload_path)
                process_file(upload_path)
                
                flash(f'File "{filename}" uploaded and processed successfully!', 'success')
                return redirect(url_for('main.profile'))
            except Exception as e:
                logger.error(f"Upload error: {str(e)}")
                flash(f'Error processing file: {str(e)}', 'danger')
        else:
            flash('Invalid file type. Allowed types are: ' + ', '.join(ALLOWED_EXTENSIONS), 'danger')

    return render_template('upload.html', form=form)

@main_bp.route('/profile')
@login_required
def profile():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    uploaded_files = UploadedFile.query.filter_by(user_id=current_user.id)\
        .order_by(UploadedFile.uploaded_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('profile.html', 
                         files=uploaded_files, 
                         username=current_user.username)
@main_bp.route('/login', methods=['GET', 'POST'])
@rate_limit
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.upload'))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                logger.info(f"User logged in: {user.username}")
                flash(f'Welcome back, {user.username}!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page if next_page else url_for('main.profile'))
            else:
                logger.warning(f"Failed login attempt for username: {form.username.data}")
                flash('Login unsuccessful. Please check your username and password.', 'danger')
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('An error occurred during login. Please try again.', 'danger')

    return render_template('login.html', form=form)

@main_bp.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    logger.info(f"User logged out: {username}")
    flash('You have been logged out. See you soon!', 'info')
    return redirect(url_for('main.login'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Error handlers
@main_bp.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@main_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500