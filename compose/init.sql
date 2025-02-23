CREATE TABLE users (
    token VARCHAR(255),
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    PRIMARY KEY (email)
);

CREATE TABLE diary (
    id VARCHAR(255) PRIMARY KEY,
    user_email VARCHAR(255) REFERENCES users(email),
    date DATE NOT NULL,
    text TEXT NOT NULL,
    emotion_estandar VARCHAR(255) NOT NULL,
    emotion_idioma VARCHAR(255) NOT NULL
);

CREATE TABLE personal_profile (
    user_email VARCHAR(255) REFERENCES users(email),
    score_neuroticismo DECIMAL NOT NULL,
    score_extroversion DECIMAL NOT NULL,
    score_agreeableness DECIMAL NOT NULL,
    score_conscientiousness DECIMAL NOT NULL,
    score_openness DECIMAL NOT NULL,
    PRIMARY KEY (user_email)
);

CREATE TABLE user_history (
    user_email VARCHAR(255) REFERENCES users(email),
    interaction TEXT NOT NULL,
    id_interaction VARCHAR(255) NOT NULL,
    PRIMARY KEY (id_interaction)
);

INSERT INTO users (token, email, password)
VALUES (
    '',  -- Token vacío inicialmente
    'admin',
    'admin' 
);