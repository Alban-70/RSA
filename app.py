#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Flask, render_template, request, redirect, flash, session, g
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash
import pymysql.cursors
import os
from dotenv import load_dotenv
import ast

from crypto import choixCle, clePrivee, clePublique, codageRSA, decodageRSA

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecret!')

ph = PasswordHasher()


def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(stored_hash: str, password_attempt: str) -> bool:
    try:
        return ph.verify(stored_hash, password_attempt)
    except VerifyMismatchError:
        return False
    except (VerificationError, InvalidHash):
        return False

def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host=os.environ.get("HOST"),
            user=os.environ.get("LOGIN"),
            password=os.environ.get("PASSWORD"),
            database=os.environ.get("DATABASE"),
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
        return render_template('login.html')

    username = session.get('username')
    private_key = session.get('private_key')
    selected_contact = session.get('last_destinataire')
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT username, n, e FROM public_keys ORDER BY username")
    users_with_keys = cursor.fetchall()

    all_messages = []

    if private_key:
        n_priv, d_priv = private_key
        if selected_contact:
            cursor.execute(
                "SELECT encrypted_message, date_envoi, username_src FROM messages WHERE username_dest = %s AND username_src = %s", 
                (username, selected_contact)
            )
        else:
            cursor.execute(
                "SELECT encrypted_message, date_envoi, username_src FROM messages WHERE username_dest = %s", 
                (username,)
            )
        rows = cursor.fetchall()
        
        for row in rows:
            try:
                encrypted_message = ast.literal_eval(row['encrypted_message'])
                decrypted = ''.join([chr(decodageRSA(int(c), n_priv, d_priv)) for c in encrypted_message])
                all_messages.append({
                    'content': decrypted,
                    'date': row.get('date_envoi'),
                    'from': row.get('username_src'),
                    'type': 'received'
                })
            except Exception as e:
                print(f"Erreur déchiffrement: {e}")
                all_messages.append({
                    'content': "[Message non déchiffrable]",
                    'date': row.get('date_envoi'),
                    'from': row.get('username_src'),
                    'type': 'received'
                })

    if selected_contact:
        cursor.execute(
            "SELECT encrypted_message_sender, date_envoi, username_dest FROM messages WHERE username_src = %s AND username_dest = %s",
            (username, selected_contact)
        )
    else:
        cursor.execute(
            "SELECT encrypted_message_sender, date_envoi, username_dest FROM messages WHERE username_src = %s",
            (username,)
        )
    sent_rows = cursor.fetchall()
    
    for row in sent_rows:
        content = '[Message non disponible]'
        if private_key and row.get('encrypted_message_sender'):
            try:
                n_priv, d_priv = private_key
                encrypted_sender = ast.literal_eval(row['encrypted_message_sender'])
                decrypted_sent = ''.join([chr(decodageRSA(int(c), n_priv, d_priv)) for c in encrypted_sender])
                content = decrypted_sent
            except Exception as e:
                print(f"Erreur déchiffrement message envoyé: {e}")
                content = '[Message non déchiffrable]'
        
        all_messages.append({
            'content': content,
            'date': row.get('date_envoi'),
            'to': row.get('username_dest'),
            'type': 'sent'
        })
    all_messages.sort(key=lambda msg: msg.get('date') or '')

    print("All messages sorted:", all_messages)
    

    return render_template(
        'index.html',
        private_key=session.get('private_key'),
        public_key=session.get('public_key'),
        all_messages=all_messages,
        users_with_keys=users_with_keys
    )




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    username = request.form.get('username', '')
    password = request.form.get('password', '')

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        flash('Nom d\'utilisateur déjà pris.')
        return redirect('/register')

    hash_pw = hash_password(password)
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hash_pw))
    db.commit()
    
    p, q, e = choixCle(100, 500)
    n_pub, e_pub = clePublique(p, q, e)
    n_priv, d_priv = clePrivee(p, q, e)
    
    cursor.execute("INSERT INTO public_keys (username, n, e) VALUES (%s, %s, %s)", (username, n_pub, e_pub))
    db.commit()
    
    flash('Inscription réussie. Vos clés ont été générées automatiquement. Veuillez vous connecter.')
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username', '')
    password = request.form.get('password', '')

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()

    if result and verify_password(result['password'], password):
        session['username'] = username
        
        cursor.execute("SELECT n, e FROM public_keys WHERE username = %s", (username,))
        existing_key = cursor.fetchone()
        
        if not existing_key:
            p, q, e = choixCle(100, 500)
            n_pub, e_pub = clePublique(p, q, e)
            n_priv, d_priv = clePrivee(p, q, e)
            
            cursor.execute("INSERT INTO public_keys (username, n, e) VALUES (%s, %s, %s)", (username, n_pub, e_pub))
            db.commit()
            
            session['private_key'] = (n_priv, d_priv)
            session['public_key'] = (n_pub, e_pub)
            flash('Connexion réussie. Vos clés ont été générées automatiquement.')
        else:
            session['public_key'] = (existing_key['n'], existing_key['e'])
            flash('Connexion réussie.')
        
        return redirect('/')
    else:
        flash('Nom d\'utilisateur ou mot de passe incorrect.')
        return redirect('/login')


@app.route('/disconnect')
def disconnect():
    session.clear()
    return redirect('/')


@app.route('/select_contact', methods=['POST'])
def select_contact():
    """Route pour sélectionner un contact et afficher uniquement sa conversation"""
    contact = request.form.get('contact', '')
    if contact:
        session['last_destinataire'] = contact
    else:
        session.pop('last_destinataire', None)
    return redirect('/')


@app.route('/generate_key')
def generate_key():
    username = session.get('username')
    if not username:
        flash("Connectez-vous d'abord.")
        return redirect('/login')

    p, q, e = choixCle(100, 500)
    n_pub, e_pub = clePublique(p, q, e)
    n_priv, d_priv = clePrivee(p, q, e)

    session['private_key'] = (n_priv, d_priv)
    session['public_key'] = (n_pub, e_pub)

    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM public_keys WHERE username = %s", (username,))
    cursor.execute("INSERT INTO public_keys (username, n, e) VALUES (%s, %s, %s)", (username, n_pub, e_pub))
    db.commit()

    flash("Clés générées avec succès !")
    return redirect('/')


@app.route('/crypter_message', methods=['POST'])
def crypter_message():
    destinataire = request.form.get('destinataire', '')
    message = request.form.get('message', '')

    if not destinataire or not message:
        flash("Destinataire et message requis.")
        return redirect('/')

    session['last_destinataire'] = destinataire

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT n, e FROM public_keys WHERE username = %s", (destinataire,))
    key = cursor.fetchone()
    if not key:
        flash(f"Clé publique de {destinataire} non trouvée.")
        return redirect('/')

    public_key_dest = (key['n'], key['e'])
    encrypted_for_dest = str([codageRSA(ord(c), public_key_dest[0], public_key_dest[1]) for c in message])

    encrypted_for_sender = None
    username_src = session.get('username')
    sender_public_key = session.get('public_key')
    
    if sender_public_key:
        encrypted_for_sender = str([codageRSA(ord(c), sender_public_key[0], sender_public_key[1]) for c in message])
    
    cursor.execute(
        "INSERT INTO messages (username_src, username_dest, encrypted_message, encrypted_message_sender) VALUES (%s, %s, %s, %s)", 
        (username_src, destinataire, encrypted_for_dest, encrypted_for_sender)
    )
    db.commit()

    flash("Message envoyé !")
    return redirect('/')


import ast
from flask import jsonify

@app.route('/decrypter_messages')
def decrypter_messages():
    username = session.get('username')
    private_key = session.get('private_key')

    if not username:
        return jsonify({"error": "Utilisateur non connecté"}), 403
    
    if not private_key:
        return jsonify({"error": "Clé privée manquante - veuillez vous reconnecter"}), 403

    n_priv, d_priv = private_key
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT encrypted_message FROM messages WHERE username_dest = %s", (username,))
    rows = cursor.fetchall()

    decrypted_messages = []
    for row in rows:
        try:
            encrypted_message = ast.literal_eval(row['encrypted_message'])
            decrypted = ''.join([chr(decodageRSA(int(c), n_priv, d_priv)) for c in encrypted_message])
            decrypted_messages.append(decrypted)
        except Exception as e:
            decrypted_messages.append(f"[Erreur: {str(e)}]")

    return jsonify({"status": "success", "count": len(decrypted_messages), "messages": decrypted_messages})

if __name__ == '__main__':
    app.run(debug=True)
