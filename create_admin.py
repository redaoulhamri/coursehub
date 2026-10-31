import getpass
from sqlalchemy.orm import Session
from database.db_manager import SessionLocal, engine, Base
from database.models import Admin

def create_first_admin():
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    print("--- Create Initial Admin ---")
    email = input("Enter admin email: ").strip()
    
    existing_admin = db.query(Admin).filter(Admin.email == email).first()
    if existing_admin:
        print(f"Error: Admin with email '{email}' already exists!")
        db.close()
        return

    password = getpass.getpass("Enter password: ")
    confirm_password = getpass.getpass("Confirm password: ")

    if password != confirm_password:
        print("Error: Passwords do not match!")
        db.close()
        return

    hashed_pwd = Admin.hash_pwd(password)

    new_admin = Admin(
        email=email,
        hashed_password=hashed_pwd
    )

    try:
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        print(f"\n✅ Success! Admin '{email}' created successfully.")
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error creating admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_first_admin()