CREATE TABLE IF NOT EXISTS users(
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS comics(
    id SERIAL PRIMARY KEY,
    issue INTEGER NOT NULL,
    name TEXT NOT NULL,
    publisher TEXT,
    writer TEXT NOT NULL,
    release_date DATE,
    aquired_date DATE,
    cover TEXT,
    comic_shop TEXT,
    price DECIMAL,
    user_id INTEGER NOT NULL REFERENCES users(id),
    UNIQUE(issue, name, publisher, writer, release_date, aquired_date, cover, comic_shop, price, user_id)
);