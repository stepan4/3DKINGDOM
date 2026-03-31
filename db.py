import sqlite3

conn = sqlite3.connect("users.db", check_same_thread=False)
conn.row_factory = sqlite3.Row 
cur = conn.cursor()

# ТАБЛИЦА ДЛЯ ПОЛЬЗОВАТЕЛЕЙ
cur.execute(''' CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100),
            email VARCHAR(200),
            password VARCHAR(250))''')

# ТАБЛИЦА ДЛЯ МОДЕЛЕЙ
cur.execute(''' CREATE TABLE IF NOT EXISTS models(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(255),
            category VARCHAR(100),
            description TEXT,
            file_path VARCHAR(255),
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id))''')


# ФУНКЦИЯ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ
def create_user(user):
    name = user.get("name")
    email = user.get("email")
    password = user.get("password")
    cur.execute(''' INSERT INTO users(name, email, password)
                VALUES
                (?, ?, ?)''', [name, email, password])
    conn.commit()
    return cur.lastrowid

def get_user_by_id(user_id):
    cur.execute("SELECT * FROM users WHERE id = ?", [user_id])
    return cur.fetchone()

def get_user_by_email(email):
    cur.execute("SELECT * FROM users WHERE email = ?", [email])
    return cur.fetchone()

def delete_user(user_id):
    cur.execute("DELETE FROM users WHERE id = ?", [user_id])
    conn.commit()


# ФУНКЦИИ ДЛЯ МОДЕЛЕЙ
def create_model(title, category, description, file_path, user_id):
    cur.execute('''INSERT INTO models (title, category, description, file_path, user_id) 
                   VALUES (?, ?, ?, ?, ?)''', (title, category, description, file_path, user_id))
    conn.commit()

def get_all_models():
    cur.execute("SELECT * FROM models ORDER BY id DESC")
    return cur.fetchall()

def get_model_by_id(model_id):
    cur.execute("SELECT * FROM models WHERE id = ?", [model_id])
    return cur.fetchone()

def get_models_by_category(category):
    cur.execute("SELECT * FROM models WHERE category = ? ORDER BY id DESC", [category])
    return cur.fetchall()