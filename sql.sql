DROP TABLE IF EXISTS public_keys;DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS messages;


CREATE TABLE users (
    username VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE public_keys (
    n INT NOT NULL,
    e INT NOT NULL,
    username VARCHAR(255) REFERENCES users(username)
);
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    username_dest VARCHAR(255) REFERENCES users(username),
    username_src VARCHAR(255) REFERENCES users(username),
    encrypted_message TEXT NOT NULL,
    encrypted_message_sender TEXT,
    date_envoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (username, password) VALUES ('default_user', 'default_password');
INSERT INTO public_keys (username, n, e) VALUES ('default_user', 3233, 17);
INSERT INTO messages (username_dest, username_src, encrypted_message) VALUES ('nbouche', 'default_user', '1234567890');
