import os
from dataclasses import dataclass

@dataclass
class Config:
    telegram_token: str
    gemini_key: str
    tenor_key: str
    giphy_key: str | None = None
    serp_key: str | None = None

    @classmethod
    def load(cls) -> "Config":
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        gemini_key = os.getenv("GEMINI_API_KEY")
        tenor_key = os.getenv("TENOR_API_KEY")

        # Let's be helpful and raise descriptive errors
        if not telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is missing from your environment (.env file)")
        if not gemini_key:
            raise ValueError("GEMINI_API_KEY is missing from your environment (.env file)")
        if not tenor_key:
            raise ValueError("TENOR_API_KEY is missing from your environment (.env file)")

        return cls(
            telegram_token=telegram_token,
            gemini_key=gemini_key,
            tenor_key=tenor_key,
            giphy_key=os.getenv("GIPHY_API_KEY"),
            serp_key=os.getenv("SERP_API_KEY")
        )
