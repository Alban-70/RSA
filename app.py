from crypto import choixCle, clePrivee, clePublique, codageRSA, decodageRSA
from flask import Flask, render_template, request, session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret!'

@app.route('/')
def index():
    return render_template(
        'index.html',
        private_key=session.get('private_key'),
        public_key=session.get('public_key'),
        encrypted_message=session.get('encrypted_message'),
        decrypted_message=session.get('decrypted_message')
    )

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

    #db = get_db()
    #cursor = db.cursor()
    #cursor.execute("INSERT INTO public_keys (username, n, e) VALUES (%s, %s, %S)"


    return render_template(
        'index.html',
        private_key=session['private_key'],
        public_key=session['public_key']
    )

@app.route('/crypter_message', methods=['POST'])
def crypter_message():
    public_key = session.get('public_key')
    if not public_key:
        return "Vous devez générer une clé publique d'abord.", 400

    n_pub, e_pub = public_key
    M = request.form.get('message', '')

    if not M:
        return "Message vide.", 400

    message_ints = [ord(c) for c in M]
    C = [codageRSA(m, n_pub, e_pub) for m in message_ints]

    session['encrypted_message'] = C
    session.pop('decrypted_message', None)

    return render_template(
        'index.html',
        private_key=session.get('private_key'),
        public_key=public_key,
        encrypted_message=C
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

if __name__ == '__main__':
    app.run(debug=True)
