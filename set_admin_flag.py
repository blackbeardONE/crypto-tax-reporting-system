from db import SessionLocal, User

def set_admin(username):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"User '{username}' not found.")
    else:
        user.is_admin = True
        db.commit()
        print(f"User '{username}' is_admin flag set to True.")
    db.close()

if __name__ == "__main__":
    set_admin("admin")
