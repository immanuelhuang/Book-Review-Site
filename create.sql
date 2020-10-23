CREATE TABLE books (
    isbn VARCHAR PRIMARY KEY,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year INTEGER NOT NULL
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    password VARCHAR NOT NULL
);

CREATE TABLE reviews (
    rating INTEGER NOT NULL,
    review VARCHAR,
    book_isbn VARCHAR REFERENCES books(isbn),
    user_id INTEGER REFERENCES users(id)
);