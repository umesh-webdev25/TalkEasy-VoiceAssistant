import os
from datetime import timedelta

class Config:
    # MongoDB Configuration
    MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'voiceAssistance')
    MONGODB_SSL_CERT = os.getenv('MONGODB_SSL_CERT', True)
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '60'))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '30'))
    
    # Security Configuration
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPER = True
    PASSWORD_REQUIRE_LOWER = True
    PASSWORD_REQUIRE_DIGIT = True
    PASSWORD_REQUIRE_SPECIAL = True
    
    # Rate Limiting
    LOGIN_RATE_LIMIT = "5/minute"
    API_RATE_LIMIT = "100/minute"
    
    # Session Configuration
    SESSION_TIMEOUT = timedelta(hours=24)
    REQUIRE_EMAIL_VERIFICATION = True
    
    # Email Configuration
    EMAIL_SENDER = os.getenv('EMAIL_SENDER', 'talkeasyofficial100@gmail.com')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    
    @classmethod
    def validate_config(cls):
        required_vars = [
            ('JWT_SECRET_KEY', cls.JWT_SECRET_KEY),
            ('EMAIL_PASSWORD', cls.EMAIL_PASSWORD),
            ('MONGODB_URL', cls.MONGODB_URL)
        ]
        
        missing = [var[0] for var in required_vars if not var[1]]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")