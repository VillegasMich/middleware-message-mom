class Util:
    @staticmethod
    def set_token(token: str):
        """Stores the authentication token"""
        global TOKEN
        TOKEN = token

    @staticmethod
    def get_headers():
        """Returns headers with authentication token"""
        if not TOKEN:
            return {}
        return {"Authorization": f"Bearer {TOKEN}"}
