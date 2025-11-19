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
    username VARCHAR(255) REFERENCES users(username),
    encrypted_message TEXT NOT NULL
);

INSERT INTO users (username, password) VALUES ('default_user', 'default_password');
INSERT INTO public_keys (username, n, e) VALUES ('default_user', 3233, 17);
INSERT INTO messages (username, encrypted_message) VALUES ('default_user', '[187, 220, 187, 220, 187, 220, 187, 220, 187, 220]');
