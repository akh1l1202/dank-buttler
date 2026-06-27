import os
from dataclasses import dataclass

@dataclass
class Config:
    telegram_token: str
    gemini_key: str
    giphy_key: str

    @classmethod
    def load(cls) -> "Config":
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        gemini_key = os.getenv("GEMINI_API_KEY")
        giphy_key = os.getenv("GIPHY_API_KEY")

        if not telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is missing from your environment (.env file)")
        if not gemini_key:
            raise ValueError("GEMINI_API_KEY is missing from your environment (.env file)")
        if not giphy_key:
            raise ValueError("GIPHY_API_KEY is missing from your environment (.env file)")

        return cls(
            telegram_token=telegram_token,
            gemini_key=gemini_key,
            giphy_key=giphy_key
        )
