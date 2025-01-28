from db.db_handler import DatabaseHandler

class UserService:
    @staticmethod
    def get_user(user_id: int):
        db = DatabaseHandler()
        user = db.get_user(user_id)
        db.close()
        return user