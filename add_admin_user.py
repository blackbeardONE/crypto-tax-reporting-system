import sys
from db import SessionLocal, User

def add_admin_user(username):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"User '{username}' not found.")
        db.close()
        return
    user.is_admin = True
    db.commit()
    db.close()
    print(f"User '{username}' has been granted admin privileges.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python add_admin_user.py <username>")
    else:
        add_admin_user(sys.argv[1])
