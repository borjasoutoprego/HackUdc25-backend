CREATE TABLE users (
    token VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    PRIMARY KEY (email)
);

CREATE TABLE diary (
    user_email VARCHAR(255) REFERENCES users(email),
    date DATE NOT NULL,
    text TEXT NOT NULL,
    emotion VARCHAR(255) NOT NULL,
    PRIMARY KEY (user_email, date)
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


INSERT INTO users (token, email, password)
VALUES (
    '',  -- Token vacío inicialmente
    'admin',
    'admin' 
);