import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.TCKN = os.getenv('TCKN')
        self.PASSWORD = os.getenv('PASSWORD')
        self.API_KEY = os.getenv('OPENAI_API_KEY')
        self.LOGIN_URL = 'https://online.spor.istanbul/uyegiris'
        self.DASHBOARD_URL = 'https://online.spor.istanbul/uyespor'
        
        if not self.TCKN or not self.PASSWORD or not self.API_KEY:
            raise ValueError("Missing TCKN, PASSWORD, or API_KEY in environment.")
