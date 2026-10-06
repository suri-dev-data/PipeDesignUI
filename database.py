import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            code TEXT,
            email TEXT,
            site TEXT,
            photo_url TEXT
        )
    ''')

    # Create materials table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            density REAL,
            thermal_conductivity REAL,
            structural_strength REAL,
            color_hex TEXT
        )
    ''')

    # Create pipes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
    ''')

    # Create layers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS layers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pipe_id INTEGER,
            name TEXT,
            material TEXT,
            thickness INTEGER,
            color_hex TEXT,
            dasharray TEXT,
            opacity REAL,
            is_dashed BOOLEAN,
            FOREIGN KEY(pipe_id) REFERENCES pipes(id)
        )
    ''')

    # Insert default user if not exists
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO users (name, code, email, site, photo_url)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            "John Doe",
            "ENG-042",
            "john.doe@suriteca.com",
            "Terminal 042 - North Sea",
            "https://lh3.googleusercontent.com/aida-public/AB6AXuAjNys49LiJyqwXpRuHbq-y_og3paF2fPKBXjtSy85WTePefxy9wgetaLkVm6NYL86F1uCu2GON6SPHLqLdzRYcCWWwgi8TY_cMCZkn38v8XircngPzFFGE7Sf15M9JVEG9Qydv5dTX1hS09DUKGanW_e04tTa1KIzugC66eNcPLOn5qQ_ENNqTDZvp8fYyiYBEQtUfGKzty7kzHDZZEV-jRgcJkdjj1usfISUUuEF7-qzm8bhEnaK6Sg56SViQh71kwaTx50nWrmk"
        ))

    # Insert default materials if not exists
    cursor.execute('SELECT COUNT(*) FROM materials')
    if cursor.fetchone()[0] == 0:
        materials = [
            ("PTFE Polymer", "Coating", 2200, 0.25, 30.0, "#607A6D"),
            ("X65 Carbon Steel", "Metal", 7850, 45.0, 450.0, "#7D9B88"),
            ("Polyurethane Foam", "Insulation", 40, 0.03, 2.0, "#8CB8B6"),
            ("High-Density PE", "Jacket", 950, 0.45, 25.0, "#A3BCA9"),
            ("Concrete Weight", "Weight", 2400, 1.4, 40.0, "#BCE3C5"),
            ("Epoxy Resin", "Coating", 1150, 0.3, 60.0, "#CDE0D4")
        ]
        cursor.executemany('''
            INSERT INTO materials (name, category, density, thermal_conductivity, structural_strength, color_hex)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', materials)

    # Insert default pipe and layers if not exists
    cursor.execute('SELECT COUNT(*) FROM pipes')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO pipes (name) VALUES (?)', ("Default Pipe",))
        pipe_id = cursor.lastrowid
        
        layers = [
            (pipe_id, "Inner Coating", "PTFE Polymer", 5, "#607A6D", "", 0.8, False),
            (pipe_id, "Steel Wall", "X65 Carbon Steel", 30, "#7D9B88", "", 0.8, False),
            (pipe_id, "Thermal Insulation", "Polyurethane Foam", 50, "#8CB8B6", "4 8", 0.2, True),
            (pipe_id, "Outer Jacket", "High-Density PE", 15, "#A3BCA9", "", 0.8, False)
        ]
        cursor.executemany('''
            INSERT INTO layers (pipe_id, name, material, thickness, color_hex, dasharray, opacity, is_dashed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', layers)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
