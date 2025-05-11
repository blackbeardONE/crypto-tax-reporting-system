import sys
from db import SessionLocal, User

def check_admin(username):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"User '{username}' not found.")
    else:
        print(f"User '{username}' is_admin: {user.is_admin}")
    db.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_admin_user.py <username>")
    else:
        check_admin(sys.argv[1])
