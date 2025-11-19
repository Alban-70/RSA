from crypto import choixCle, clePrivee, clePublique, codageRSA, decodageRSA
from flask import Flask, render_template, request, session
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret!'

#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Flask, request, render_template, redirect, flash

app = Flask(__name__)
app.secret_key = 'une cle(token) : grain de sel(any random string)'

from flask import session, g
import pymysql.cursors

import os                                 # à ajouter
from dotenv import load_dotenv            # à ajouter
load_dotenv()                             # à ajouter

ph = PasswordHasher()

def hash_password(password: str) -> str:
    # renvoie le hash encodé (inclut le salt et les paramètres)
    return ph.hash(password)

def verify_password(stored_hash: str, password_attempt: str) -> bool:
    try:
        return ph.verify(stored_hash, password_attempt)
    except VerifyMismatchError:
        return False
    except (VerificationError, InvalidHash):
        # hash corrompu ou autre erreur
        return False
    


def get_db():
    if 'db' not in g:
        g.db =  pymysql.connect(
            host=os.environ.get("HOST"),                # à modifier
            user=os.environ.get("LOGIN"),               # à modifier
            password=os.environ.get("PASSWORD"),        # à modifier
            database=os.environ.get("DATABASE"),        # à modifier
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)  
    if db is not None:
        db.close()


@app.route('/')
def index():

    if 'username' not in session:
        return render_template(
            'login.html',
        )


    return render_template(
        'index.html',
        received_messages=session.get('received_messages', [])
    )

@app.route('/disconnect', methods=['GET'])
def disconnect():
    
    session.pop('username', None)
    session.pop('received_messages', None)
    session.pop('private_key', None)
    session.pop('public_key', None)
    session.pop('encrypted_message', None)
    session.pop('decrypted_message', None)
    return redirect('/')

@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        flash('Nom d\'utilisateur déjà pris.')
        return redirect('/register')

    hash_password_str = hash_password(password)
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hash_password_str))
    db.commit()

    flash('Inscription réussie. Veuillez vous connecter.')
    return redirect('/generate_key?username-local=' + username)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()
    if result and verify_password(result['password'], password):
        session['username'] = username
        flash('Connexion réussie.')
        return render_template('index.html')
    else:
        flash('Nom d\'utilisateur ou mot de passe incorrect.')
        return redirect('/')
    
    


@app.route('/generate_key')
def generate_key():
    p, q, e = choixCle(100, 500)
    n_pub, e_pub = clePublique(p, q, e)
    n_priv, d_priv = clePrivee(p, q, e)

    session['private_key'] = (n_priv, d_priv)
    session['public_key'] = (n_pub, e_pub)

    session.pop('encrypted_message', None)
    session.pop('decrypted_message', None)

    username = request.args.get('username-local', 'default_user')

    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO public_keys (username, n, e) VALUES (%s, %s, %s)", (username, n_pub, e_pub))
    db.commit()

    return render_template(
        'index.html',
        private_key=session['private_key'],
        public_key=session['public_key']
    )

@app.route('/crypter_message', methods=['POST'])
def crypter_message():

    db = get_db()
    cursor = db.cursor()
    username_input = request.form.get('username-input', 'default_user')
    cursor.execute("SELECT n, e FROM public_keys WHERE username = %s", (username_input ,))
    result = cursor.fetchone()
    if not result:
        return "Clé publique non trouvée pour l'utilisateur spécifié.", 400
    public_key = (result['n'], result['e'])

    message = request.form.get('message', '')
    crypted_message = str([codageRSA(ord(c), public_key[0], public_key[1]) for c in message])

    cursor.execute("INSERT INTO messages (username, encrypted_message) VALUES (%s, %s)", (username_input, crypted_message))
    db.commit()

    return render_template(
        'index.html',
        private_key=session.get('private_key'),
        public_key=public_key,
        encrypted_message=crypted_message
    )

@app.route('/decrypter_message', methods=['POST'])
def decrypter_message():
    private_key = session.get('private_key')
    if not private_key:
        return "Vous devez générer une clé privée d'abord.", 400

    n_priv, d_priv = private_key

    C = session.get('encrypted_message')
    if not C:
        return "Aucun message à déchiffrer.", 400

    try:
        M_decoded = ''.join([chr(decodageRSA(c, n_priv, d_priv)) for c in C])
    except ValueError:
        M_decoded = '-'.join(str(decodageRSA(c, n_priv, d_priv)) for c in C)

    session['decrypted_message'] = M_decoded

    return render_template(
        'index.html',
        private_key=private_key,
        public_key=session.get('public_key'),
        encrypted_message=C,
        decrypted_message=M_decoded
    )

@app.route('/show_message', methods=['GET'])
def show_messages():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT encrypted_message FROM messages WHERE username = %s", (session.get('username'),))
    received_messages = [row['encrypted_message'] for row in cursor.fetchall()]
    session['received_messages'] = received_messages
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
