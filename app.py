from crypto import choixCle, clePrivee, clePublique, codageRSA, decodageRSA, estPremier, inverseModulaire, premierAleatoire, premierAleatoireAvecRandom
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret!'
""" socketio = SocketIO(app) """

from flask import session, g
import pymysql.cursors

def get_db():
    if 'db' not in g:
        g.db =  pymysql.connect(
            host="localhost",                 # à modifier
            user="login",                     # à modifier
            password="secret",                # à modifier
            database="BDD_votrelogin",        # à modifier
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        # à activer sur les machines personnelles :
        activate_db_options(db)
    return g.db

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def activate_db_options(db):
    cursor = db.cursor()
    # Vérifier et activer l'option ONLY_FULL_GROUP_BY si nécessaire
    cursor.execute("SHOW VARIABLES LIKE 'sql_mode'")
    result = cursor.fetchone()
    if result:
        modes = result['Value'].split(',')
        if 'ONLY_FULL_GROUP_BY' not in modes:
            print('MYSQL : il manque le mode ONLY_FULL_GROUP_BY')   # mettre en commentaire
            cursor.execute("SET sql_mode=(SELECT CONCAT(@@sql_mode, ',ONLY_FULL_GROUP_BY'))")
            db.commit()
        else:
            print('MYSQL : mode ONLY_FULL_GROUP_BY  ok')   # mettre en commentaire
    # Vérifier et activer l'option lower_case_table_names si nécessaire
    cursor.execute("SHOW VARIABLES LIKE 'lower_case_table_names'")
    result = cursor.fetchone()
    if result:
        if result['Value'] != '0':
            print('MYSQL : valeur de la variable globale lower_case_table_names differente de 0')   # mettre en commentaire
            cursor.execute("SET GLOBAL lower_case_table_names = 0")
            db.commit()
        else :
            print('MYSQL : variable globale lower_case_table_names=0  ok')    # mettre en commentaire
    cursor.close()

    

@app.route('/')
def index():

    p, q, e = choixCle(100, 500)
    n_pub, e_pub = clePublique(p, q, e)
    n_priv, d_priv = clePrivee(p, q, e)

    M = "Hello"
    message_ints = [ord(c) for c in M]
    C = [codageRSA(m, n_pub, e_pub) for m in message_ints]
    M_decoded = ''.join([chr(decodageRSA(c, n_priv, d_priv)) for c in C])

    return render_template('index.html', original_message=M, coded_message=C, decoded_message=M_decoded)

@app.route('/generate_key')
def generate_key():
    p, q, e = choixCle(100, 500)
    n_pub, e_pub = clePublique(p, q, e)
    n_priv, d_priv = clePrivee(p, q, e)
    return {
        'public_key': {'n': n_pub, 'e': e_pub},
        'private_key': {'n': n_priv, 'd': d_priv}
    }
@app.route('/send_public_key', methods=['POST'])
def send_public_key():
    # requete sql pour stocker clé publique avec id user ? maybe
    sql = "INSERT INTO public_keys (id_user, n, e) VALUES (%s, %s, %s)"
    cursor.execute(sql, (user_id, n, e))
    connection.commit()
    cursor.close()
    
    return {'status': 'success'}





# Quand un message arrive
""" @socketio.on('message')
def handle_message(data):
    print(f"Message reçu: {data}")
    # Renvoie à tout le monde (ou à une room)
    send(data, broadcast=True) """

@app.route('/test_crypto')
def test_crypto():
    return "Test Crypto Route"

if __name__ == '__main__':
    app.run(debug=True)
    # socketio.run(app, debug=True)
