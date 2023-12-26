from database import SessionFactory


def get_database():
    with SessionFactory() as session:
        return session
