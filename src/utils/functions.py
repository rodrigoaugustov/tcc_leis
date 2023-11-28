from src.services.crud import Session


def already_exists(url, table):
    session = Session()
    if session.query(table).filter(table.url == url).first():
        session.close()
        return True
    else:
        session.close()
        return False