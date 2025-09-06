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
    from app.models.crackme import CrackmeModel
    
    # Get latest crackmes for homepage
    latest_crackmes = CrackmeModel.get_visible_crackmes(limit=10)
    total_crackmes = CrackmeModel.count_crackmes()
    
    return render_template('index.html', 
                          crackmes=latest_crackmes,
                          total_crackmes=total_crackmes)


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
    from app.models.crackme import CrackmeModel
    from app.models.solution import SolutionModel
    from app.models.comment import CommentModel
    
    user = UserModel.get_by_name(username)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('main.index'))
    
    # Update user stats
    user.nb_crackmes = CrackmeModel.count_by_user(username)
    user.nb_solutions = SolutionModel.count_by_user(username)
    user.nb_comments = CommentModel.count_by_user(username)
    
    # Get user's recent activity
    user_crackmes = CrackmeModel.get_by_author(username, limit=5)
    user_solutions = SolutionModel.get_by_author(username, limit=5)
    user_comments = CommentModel.get_by_author(username, limit=5)
    
    return render_template('user/profile.html', 
                          user=user,
                          crackmes=user_crackmes,
                          solutions=user_solutions,
                          comments=user_comments)


# Crackme routes
@crackme_bp.route('/crackme/<hex_id>')
def crackme_detail(hex_id):
    """Crackme detail page - equivalent to controller.CrackMeGET"""
    from app.models.crackme import CrackmeModel
    from app.models.solution import SolutionModel
    from app.models.comment import CommentModel
    
    crackme = CrackmeModel.get_by_hex_id(hex_id)
    if not crackme or not crackme.visible:
        flash('Crackme not found', 'error')
        return redirect(url_for('main.index'))
    
    # Get solutions and comments
    solutions = SolutionModel.get_by_crackme(hex_id)
    comments = CommentModel.get_by_crackme(hex_id)
    
    return render_template('crackme/detail.html', 
                          crackme=crackme, 
                          solutions=solutions, 
                          comments=comments)


@crackme_bp.route('/upload/crackme', methods=['GET'])
@login_required
def upload_crackme():
    """Upload crackme page - equivalent to controller.UploadCrackMeGET"""
    return render_template('crackme/upload.html')


@crackme_bp.route('/upload/crackme', methods=['POST'])
@login_required
def upload_crackme_post():
    """Upload crackme form submission - equivalent to controller.UploadCrackMePOST"""
    from app.models.crackme import Crackme
    from werkzeug.utils import secure_filename
    import os
    
    name = request.form.get('name', '').strip()
    info = request.form.get('info', '').strip()
    lang = request.form.get('lang', '').strip()
    arch = request.form.get('arch', '').strip()
    platform = request.form.get('platform', '').strip()
    
    # Validate input
    if not all([name, info, lang, arch, platform]):
        flash('All fields are required', 'error')
        return render_template('crackme/upload.html')
    
    # Handle file upload
    if 'file' not in request.files:
        flash('File is required', 'error')
        return render_template('crackme/upload.html')
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return render_template('crackme/upload.html')
    
    if file:
        try:
            # Create crackme
            crackme = Crackme(
                name=name,
                info=info,
                lang=lang,
                arch=arch,
                platform=platform,
                author=session['username']
            )
            crackme.save()
            
            # Save file temporarily for moderation
            filename = secure_filename(file.filename)
            temp_filename = f"{session['username']}+++{crackme.hex_id}+++{filename}"
            temp_path = os.path.join('tmp', 'crackme', temp_filename)
            
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            file.save(temp_path)
            
            flash('Crackme uploaded successfully! It will be reviewed before being published.', 'success')
            return redirect(url_for('main.index'))
            
        except Exception as e:
            flash(f'Error uploading crackme: {str(e)}', 'error')
            return render_template('crackme/upload.html')


@crackme_bp.route('/lasts/<int:page>')
def latest_crackmes(page=1):
    """Latest crackmes page - equivalent to controller.LastCrackMesGET"""
    from app.models.crackme import CrackmeModel
    
    per_page = 20
    skip = (page - 1) * per_page
    
    crackmes = CrackmeModel.get_visible_crackmes(limit=per_page, skip=skip)
    total_count = CrackmeModel.count_crackmes()
    
    has_next = (skip + per_page) < total_count
    has_prev = page > 1
    
    return render_template('crackme/latest.html', 
                          crackmes=crackmes,
                          page=page,
                          has_next=has_next,
                          has_prev=has_prev)


# Solution routes  
@crackme_bp.route('/upload/solution/<crackme_hex_id>', methods=['GET'])
@login_required
def upload_solution(crackme_hex_id):
    """Upload solution page - equivalent to controller.UploadSolutionGET"""
    from app.models.crackme import CrackmeModel
    
    crackme = CrackmeModel.get_by_hex_id(crackme_hex_id)
    if not crackme or not crackme.visible:
        flash('Crackme not found', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('solution/upload.html', crackme=crackme)


@crackme_bp.route('/upload/solution/<crackme_hex_id>', methods=['POST'])
@login_required
def upload_solution_post(crackme_hex_id):
    """Upload solution form submission - equivalent to controller.UploadSolutionPOST"""
    from app.models.crackme import CrackmeModel
    from app.models.solution import Solution
    from werkzeug.utils import secure_filename
    import os
    
    crackme = CrackmeModel.get_by_hex_id(crackme_hex_id)
    if not crackme or not crackme.visible:
        flash('Crackme not found', 'error')
        return redirect(url_for('main.index'))
    
    info = request.form.get('info', '').strip()
    
    # Validate input
    if not info:
        flash('Solution description is required', 'error')
        return render_template('solution/upload.html', crackme=crackme)
    
    # Handle file upload
    if 'file' not in request.files:
        flash('File is required', 'error')
        return render_template('solution/upload.html', crackme=crackme)
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return render_template('solution/upload.html', crackme=crackme)
    
    if file:
        try:
            # Create solution
            solution = Solution(
                info=info,
                author=session['username'],
                crackme_id=crackme.object_id
            )
            solution.save()
            
            # Save file temporarily for moderation
            filename = secure_filename(file.filename)
            temp_filename = f"{session['username']}+++{solution.hex_id}+++{filename}"
            temp_path = os.path.join('tmp', 'solution', temp_filename)
            
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            file.save(temp_path)
            
            flash('Solution uploaded successfully! It will be reviewed before being published.', 'success')
            return redirect(url_for('crackme.crackme_detail', hex_id=crackme_hex_id))
            
        except Exception as e:
            flash(f'Error uploading solution: {str(e)}', 'error')
            return render_template('solution/upload.html', crackme=crackme)


# Comment route
@crackme_bp.route('/comment/<hex_id>', methods=['POST'])
@login_required
def leave_comment(hex_id):
    """Leave comment - equivalent to controller.LeaveCommentPOST"""
    from app.models.comment import CommentModel
    
    content = request.form.get('content', '').strip()
    
    if not content:
        flash('Comment cannot be empty', 'error')
        return redirect(url_for('crackme.crackme_detail', hex_id=hex_id))
    
    try:
        CommentModel.create_comment(hex_id, session['username'], content)
        flash('Comment added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding comment: {str(e)}', 'error')
    
    return redirect(url_for('crackme.crackme_detail', hex_id=hex_id))


# Search route
@main_bp.route('/search', methods=['GET', 'POST'])
def search():
    """Search page - equivalent to controller.SearchGET/SearchPOST"""
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if query:
            return redirect(url_for('main.search', q=query))
    
    query = request.args.get('q', '').strip()
    crackmes = []
    
    if query:
        from app.models.crackme import CrackmeModel
        crackmes = CrackmeModel.search_crackmes(query)
    
    return render_template('search.html', query=query, crackmes=crackmes)


# Error handlers
@main_bp.errorhandler(404)
def not_found(error):
    """404 error handler - equivalent to controller.Error404"""
    return render_template('errors/404.html'), 404


@main_bp.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return render_template('errors/500.html'), 500