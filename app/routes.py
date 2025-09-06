"""
Flask routes and blueprints
Python equivalent of app/route/route.go
"""

from flask import Blueprint, request, session, redirect, url_for, flash, render_template, jsonify
from functools import wraps
from app.models.user import UserModel

# Create blueprints
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
crackme_bp = Blueprint('crackme', __name__)
user_bp = Blueprint('user', __name__)


# Middleware equivalent decorators
def login_required(f):
    """Decorator that requires user to be logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def anonymous_required(f):
    """Decorator that requires user to NOT be logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


# Main routes
@main_bp.route('/')
def index():
    """Home page - equivalent to controller.IndexGET"""
    return render_template('index.html')


@main_bp.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files - equivalent to controller.Static"""
    from flask import send_from_directory
    return send_from_directory('static', filename)


# Authentication routes
@auth_bp.route('/login', methods=['GET'])
@anonymous_required
def login():
    """Login page - equivalent to controller.LoginGET"""
    return render_template('auth/login.html')


@auth_bp.route('/login', methods=['POST'])
@anonymous_required
def login_post():
    """Login form submission - equivalent to controller.LoginPOST"""
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    
    if not username or not password:
        flash('Username and password are required', 'error')
        return render_template('auth/login.html')
    
    # Authenticate user
    user = UserModel.authenticate(username, password)
    
    if user:
        # Set session
        session['user_id'] = user.hex_id
        session['username'] = user.name
        session.permanent = True
        
        flash(f'Welcome back, {user.name}!', 'success')
        
        # Redirect to intended page or home
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('main.index'))
    else:
        flash('Invalid username or password', 'error')
        return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """Logout - equivalent to controller.LogoutGET"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/register', methods=['GET'])
@anonymous_required
def register():
    """Register page - equivalent to controller.RegisterGET"""
    return render_template('auth/register.html')


@auth_bp.route('/register', methods=['POST'])
@anonymous_required
def register_post():
    """Register form submission - equivalent to controller.RegisterPOST"""
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    # Validate input
    if not all([username, email, password, confirm_password]):
        flash('All fields are required', 'error')
        return render_template('auth/register.html')
    
    if password != confirm_password:
        flash('Passwords do not match', 'error')
        return render_template('auth/register.html')
    
    try:
        # Create user
        user = UserModel.create_user(username, email, password)
        
        # Auto-login after registration
        session['user_id'] = user.hex_id
        session['username'] = user.name
        session.permanent = True
        
        flash(f'Welcome to crackmes.one, {user.name}!', 'success')
        return redirect(url_for('main.index'))
        
    except Exception as e:
        flash(str(e), 'error')
        return render_template('auth/register.html')


# User routes
@user_bp.route('/user/<username>')
def user_profile(username):
    """User profile page - equivalent to controller.UserGET"""
    user = UserModel.get_by_name(username)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('user/profile.html', user=user)


# Crackme routes (stubs for now)
@crackme_bp.route('/crackme/<hex_id>')
def crackme_detail(hex_id):
    """Crackme detail page - equivalent to controller.CrackMeGET"""
    return render_template('crackme/detail.html', hex_id=hex_id)


@crackme_bp.route('/upload/crackme', methods=['GET'])
@login_required
def upload_crackme():
    """Upload crackme page - equivalent to controller.UploadCrackMeGET"""
    return render_template('crackme/upload.html')


@crackme_bp.route('/upload/crackme', methods=['POST'])
@login_required
def upload_crackme_post():
    """Upload crackme form submission - equivalent to controller.UploadCrackMePOST"""
    # TODO: Implement file upload logic
    flash('Crackme upload not yet implemented', 'info')
    return redirect(url_for('crackme.upload_crackme'))


# Error handlers
@main_bp.errorhandler(404)
def not_found(error):
    """404 error handler - equivalent to controller.Error404"""
    return render_template('errors/404.html'), 404


@main_bp.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return render_template('errors/500.html'), 500