"""
setup_admin.py
──────────────
Run this once after importing database.sql to create a working admin account.

Usage:
    python setup_admin.py
"""

from werkzeug.security import generate_password_hash
import MySQLdb

# ── Change these to match your MySQL credentials ──
HOST     = 'localhost'
USER     = 'root'
PASSWORD = 'mysql'                   # ← your MySQL password
DATABASE = 'cpds_main'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin@123'    # ← desired admin password
ADMIN_EMAIL    = 'admin@cpds.edu'

db  = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWORD, db=DATABASE)
cur = db.cursor()

hashed = generate_password_hash(ADMIN_PASSWORD)
cur.execute("DELETE FROM admin WHERE username=%s", (ADMIN_USERNAME,))
cur.execute(
    "INSERT INTO admin (username, password, email) VALUES (%s, %s, %s)",
    (ADMIN_USERNAME, hashed, ADMIN_EMAIL)
)
db.commit()
cur.close()
db.close()

print(f"✅  Admin created: username='{ADMIN_USERNAME}'  password='{ADMIN_PASSWORD}'")
print("   You can now log in at  http://127.0.0.1:5000/admin/login")
