import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app.models import db, User, UserPreference, Wishlist, BudgetPlan, Notification
from app.utils.ai_engine import format_budget_plan
from app.utils.audit import log_event
from app.utils.auth_helpers import bride_required

auth_bp = Blueprint('auth', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'bride')

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))

        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Initialize wishlist for brides
        if role == 'bride':
            wishlist = Wishlist(user_id=new_user.id)
            db.session.add(wishlist)
            # Create a default budget plan
            budget = BudgetPlan(
                user_id=new_user.id,
                total_budget=150000.0,
                dress_budget=60000.0,
                jewelry_budget=45000.0,
                makeup_budget=22500.0,
                accessories_budget=11250.0,
                emergency_budget=11250.0
            )
            db.session.add(budget)
            db.session.commit()

        log_event(new_user.id, 'create', 'user', new_user.id, f'New user registered with role={role}')
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            log_event(user.id, 'login', 'user', user.id, f'User logged in: {user.username}')
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            if user.role == 'admin':
                return redirect(next_page or url_for('admin.dashboard'))
            elif user.role == 'salon_owner':
                return redirect(next_page or url_for('owner.dashboard'))
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    log_event(current_user.id, 'logout', 'user', current_user.id, f'User logged out: {current_user.username}')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/notifications')
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=notifications)


@auth_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first_or_404()
    notification.is_read = True
    db.session.commit()
    return redirect(url_for('auth.notifications'))


@auth_bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    flash('All notifications marked as read.', 'success')
    return redirect(url_for('auth.notifications'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@bride_required
def profile():
        
    pref = UserPreference.query.filter_by(user_id=current_user.id).first()
    budget_plan = BudgetPlan.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        skin_tone = request.form.get('skin_tone')
        face_shape = request.form.get('face_shape')
        hair_length = request.form.get('hair_length')
        wedding_theme = request.form.get('wedding_theme')
        pref_colors = request.form.get('preferred_colors')
        jewelry_style = request.form.get('jewelry_style')
        budget_val = request.form.get('budget', 150000.0)

        try:
            budget_val = float(budget_val)
        except ValueError:
            budget_val = 150000.0

        # Handle image upload
        image_path = pref.face_image_path if pref else None
        if 'face_image' in request.files:
            file = request.files['face_image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"user_{current_user.id}_{file.filename}")
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(full_path)
                image_path = f"/static/uploads/{filename}"

        if not pref:
            pref = UserPreference(
                user_id=current_user.id,
                skin_tone=skin_tone,
                face_shape=face_shape,
                hair_length=hair_length,
                wedding_theme=wedding_theme,
                preferred_colors=pref_colors,
                jewelry_style=jewelry_style,
                budget=budget_val,
                face_image_path=image_path
            )
            db.session.add(pref)
        else:
            pref.skin_tone = skin_tone
            pref.face_shape = face_shape
            pref.hair_length = hair_length
            pref.wedding_theme = wedding_theme
            pref.preferred_colors = pref_colors
            pref.jewelry_style = jewelry_style
            pref.budget = budget_val
            pref.face_image_path = image_path

        # Update budget plan
        alloc = format_budget_plan(budget_val)
        if not budget_plan:
            budget_plan = BudgetPlan(
                user_id=current_user.id,
                total_budget=budget_val,
                dress_budget=alloc['dress'],
                jewelry_budget=alloc['jewelry'],
                makeup_budget=alloc['makeup'],
                accessories_budget=alloc['accessories'],
                emergency_budget=alloc['emergency']
            )
            db.session.add(budget_plan)
        else:
            budget_plan.total_budget = budget_val
            budget_plan.dress_budget = alloc['dress']
            budget_plan.jewelry_budget = alloc['jewelry']
            budget_plan.makeup_budget = alloc['makeup']
            budget_plan.accessories_budget = alloc['accessories']
            budget_plan.emergency_budget = alloc['emergency']

        db.session.commit()
        flash('Preferences and Styling Profile updated!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html', pref=pref, budget=budget_plan)
