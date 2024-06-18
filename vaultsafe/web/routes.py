# vaultsafe/web/routes.py
from functools import wraps

from flask import render_template, redirect, url_for, flash, request, session, Blueprint

from vaultsafe.db.models import Vault, Credential, Mnemonic, session as db_session
from vaultsafe.utils.crypto_utils import encrypt, derive_vault_key, generate_fernet_key
from vaultsafe.utils.general_utils import convert_utc_to_local_str
from vaultsafe.config import DATABASE_PATH

bp = Blueprint('main', __name__)

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('You need to login first.', 'error')
            return redirect(url_for('main.login'))
        return func(*args, **kwargs)
    return decorated_function


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not DATABASE_PATH.exists():
            flash('Database not found. Please initialize the app by running: vaultsafe init', 'error')
            return render_template('login.html')
        
        master_passwd = request.form['master_passwd']
        vault = db_session.query(Vault).first()
        if vault.check_password(master_passwd):
            session['logged_in'] = True

            # Generate the vault_key
            vault_key = derive_vault_key(master_key=master_passwd)

            # Save the vault_key to the session
            session['vault_key'] = vault_key

            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid master password!', 'error')
    return render_template('login.html')


@bp.route('/dashboard')
@login_required
def dashboard():
    credentials = db_session.query(Credential).all()
    return render_template('dashboard.html', credentials=credentials, convert_utc_to_local_str=convert_utc_to_local_str)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_credential():
    if request.method == 'POST':
        # Extract form data
        name = request.form.get('name')
        mnemonics = request.form.get('mnemonics').split(', ')
        username = request.form.get('username') if 'username' in request.form else None
        password = request.form.get('password') if 'password' in request.form else None
        recovery_key = request.form.get('recovery_key') if 'recovery_key' in request.form else None
        url = request.form.get('url') if 'url' in request.form else None
        primary_email = request.form.get('primary_email') if 'primary_email' in request.form else None
        secondary_email = request.form.get('secondary_email') if 'secondary_email' in request.form else None
        token = request.form.get('token') if 'token' in request.form else None
        notes = request.form.get('notes') if 'notes' in request.form else None

        # Get the vault_key from the session
        vault_key = session['vault_key']

        # Generate a new key for the credential
        credential_key = generate_fernet_key()

        # Encrypt credentials
        encrypted_username = encrypt(username, credential_key) if username else None
        encrypted_password = encrypt(password, credential_key) if password else None
        encrypted_url = encrypt(url, credential_key) if url else None
        encrypted_recovery_key = encrypt(recovery_key, credential_key) if recovery_key else None
        encrypted_primary_email = encrypt(primary_email, credential_key) if primary_email else None
        encrypted_secondary_email = encrypt(secondary_email, credential_key) if secondary_email else None
        encrypted_token = encrypt(token, credential_key) if token else None
        encrypted_notes = encrypt(notes, credential_key) if notes else None

        encrypted_credential_key = encrypt(credential_key, vault_key)

        # Create the credential object
        credential = Credential(
            name=name,
            url=encrypted_url,
            username=encrypted_username,
            password=encrypted_password,
            encrypted_key=encrypted_credential_key,
            token=encrypted_token,
            recovery_key=encrypted_recovery_key,
            primary_email=encrypted_primary_email,
            secondary_email=encrypted_secondary_email,
            notes=encrypted_notes
        )

        # Add the credential to the database
        db_session.add(credential)
        db_session.commit()

        # Associate mnemonics with the credential
        for mnemonic in mnemonics:
            mnemonic_entry = Mnemonic(name=mnemonic, credential=credential)
            db_session.add(mnemonic_entry)

        db_session.commit()

        flash('Credential added successfully!')
        return redirect(url_for('main.dashboard'))

    return render_template('add_credential.html')

@bp.route('/update/<uuid>', methods=['GET', 'POST'])
@login_required
def update_credential(uuid):
    credential = db_session.query(Credential).filter_by(uuid=uuid).first()

    vault_key = session['vault_key']

    if request.method == 'POST':
        # Extract form data
        name = request.form.get('name')
        mnemonics = request.form.get('mnemonics').split(', ')

        username = request.form.get('username') if 'username' in request.form and request.form.get('username') != Credential.NONE_STR else None
        password = request.form.get('password') if 'password' in request.form and request.form.get('password') != Credential.NONE_STR else None
        recovery_key = request.form.get('rkey') if 'rkey' in request.form and request.form.get('rkey') != Credential.NONE_STR else None
        url = request.form.get('url') if 'url' in request.form  and request.form.get('url') != Credential.NONE_STR else None
        primary_email = request.form.get('pemail') if 'pemail' in request.form and request.form.get('pemail') != Credential.NONE_STR else None
        secondary_email = request.form.get('semail') if 'semail' in request.form and request.form.get('semail') != Credential.NONE_STR else None
        token = request.form.get('token') if 'token' in request.form and request.form.get('token') != Credential.NONE_STR else None
        notes = request.form.get('notes') if 'notes' in request.form and request.form.get('notes') != Credential.NONE_STR else None

        # Get Credential key
        credential_key = credential.get_decrypted_key(vault_key)

        # Update credential attributes
        credential.name = name
        credential.url = encrypt(url, credential_key) if url else None
        credential.username = encrypt(username, credential_key) if username else None
        credential.password = encrypt(password, credential_key) if password else None
        credential.recovery_key = encrypt(recovery_key, credential_key) if recovery_key else None
        credential.primary_email = encrypt(primary_email, credential_key) if primary_email else None
        credential.secondary_email = encrypt(secondary_email, credential_key) if secondary_email else None
        credential.token = encrypt(token, credential_key) if token else None
        credential.notes = encrypt(notes, credential_key) if notes else None

        new_mnemonics = []
        # Query all mnemonics whose credential_id is not equal to the current credential's id
        existing_mnemonics = db_session.query(Mnemonic.name).filter(
            Mnemonic.name.in_(mnemonics), Mnemonic.credential_id != credential.id
        ).all()
        existing_mnemonic_names = {mnemonic.name for mnemonic in existing_mnemonics}


        for mnemonic in set(mnemonics):
            if mnemonic in existing_mnemonic_names:
                print(f"Note: The mnemonic '{mnemonic}' already exists and cannot be reused for a new credential. Skipped!")
            else:
                new_mnemonics.append(mnemonic)

        # Delete existing mnemonics
        for mn in credential.mnemonics:
            db_session.delete(mn)
        
        db_session.commit()

        # Add new mnemonics
        for mnemonic in set(new_mnemonics):
            mnemonic_entry = Mnemonic(name=mnemonic, credential=credential)
            db_session.add(mnemonic_entry)

        db_session.commit()

        flash('Credential updated successfully!')
        return redirect(url_for('main.dashboard'))

    return render_template('update_credential.html', credential=credential.json(vault_key))


@bp.route('/get/<uuid>', methods=['GET'])
@login_required
def get_credential(uuid):
    credential = db_session.query(Credential).filter_by(uuid=uuid).first()
    if not credential:
        flash('Credential not found.', 'error')
        return redirect(url_for('main.dashboard'))
    
    vault_key = session['vault_key']
    
    return render_template('get_credential.html', credential=credential.json(vault_key), none_str=Credential.NONE_STR)

@bp.route('/get', methods=['GET', 'POST'])
@login_required
def get():
    credential = None
    vault_key = session['vault_key']

    if request.method == 'POST':
        mnemonic = request.form.get('mnemonic')
        print(mnemonic)
        if mnemonic:
            mnemonic_entry = db_session.query(Mnemonic).filter_by(name=mnemonic).first()
            if not mnemonic_entry:
                flash(f"Mnemonic not found with the name '{mnemonic}'.", 'error')
            else:
                # Get the credential associated with the mnemonic
                credential = mnemonic_entry.credential
        else:
            flash("Please enter a mnemonic onto the search bar!", 'error')

    credential_json = credential.json(vault_key) if credential else None
    
    return render_template('get.html', credential=credential_json, none_str=Credential.NONE_STR)


@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_credential(id):
    credential = db_session.query(Credential).get(id)
    
    if not credential:
        flash('Credential not found.', 'error')
        return redirect(url_for('main.dashboard'))
    
    db_session.delete(credential)
    db_session.commit()
    
    flash(f'Credential "{credential.name}" deleted successfully!', 'success')
    return redirect(url_for('main.dashboard'))


@bp.route('/logout')
@login_required
def logout():
    # Implement logout logic
    session['logged_in'] = False
    return redirect(url_for('main.index'))