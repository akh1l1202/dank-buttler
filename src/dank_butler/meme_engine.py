import httpx
import base64
import json
import logging
import asyncio
from typing import Optional
from dank_butler.config import Config

logger = logging.getLogger(__name__)

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


class MemeEngine:
    def __init__(self, config: Config):
        self.config = config

    async def _gemini(self, prompt: str, image_bytes: bytes = None) -> str:
        parts = []
        if image_bytes:
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(image_bytes).decode()
                }
            })
        parts.append({"text": prompt})

        payload = {"contents": [{"parts": parts}]}

        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                GEMINI_URL,
                params={"key": self.config.gemini_key},
                json=payload
            )
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()

    async def _description_to_query(self, description: str) -> str:
        prompt = (
            f"Convert this meme description into a short, precise Google/Giphy search query (max 6 words). "
            f"Return ONLY the search query, nothing else.\n\nDescription: {description}"
        )
        return await self._gemini(prompt)

    async def _verify_meme(self, image_url: str, description: str) -> tuple[bool, str]:
        """Download image and ask Gemini if it matches the description."""
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(image_url)
                if resp.status_code != 200:
                    return False, ""
                image_bytes = resp.content

            prompt = (
                f"The user is looking for this meme: '{description}'\n\n"
                f"Does this image match what they're describing? "
                f"Reply with JSON only: {{\"match\": true/false, \"confidence\": 0-100, \"explanation\": \"brief explanation of the meme\"}}"
            )
            result = await self._gemini(prompt, image_bytes)
            result = result.replace("```json", "").replace("```", "").strip()
            data = json.loads(result)
            if data.get("match") and data.get("confidence", 0) >= 60:
                return True, data.get("explanation", "")
            return False, ""
        except Exception as e:
            logger.warning(f"Verify failed for {image_url}: {e}")
            return False, ""

    # ── Source 1: Giphy ──────────────────────────────────────────────────────

    async def _search_giphy(self, query: str, description: str) -> Optional[dict]:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://api.giphy.com/v1/gifs/search",
                    params={"q": query, "api_key": self.config.giphy_key, "limit": 5}
                )
                resp.raise_for_status()
                results = resp.json().get("data", [])

            for item in results:
                gif_url = item["images"]["original"]["url"]
                matched, explanation = await self._verify_meme(gif_url, description)
                if matched:
                    return {
                        "url": gif_url,
                        "title": item.get("title", query),
                        "type": "gif",
                        "source": "via Giphy",
                        "explanation": explanation
                    }
        except Exception as e:
            logger.warning(f"Giphy search failed: {e}")
        return None

    # ── Source 2: DuckDuckGo Image Search ────────────────────────────────────

    @staticmethod
    def _ddg_search_sync(query: str) -> list[dict]:
        from ddgs import DDGS
        try:
            with DDGS() as ddgs:
                # Add 'meme' keyword to the search query to ensure relevant results
                return list(ddgs.images(f"{query} meme", max_results=5))
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed: {e}")
            return []

    async def _search_duckduckgo(self, query: str, description: str) -> Optional[dict]:
        try:
            loop = asyncio.get_running_loop()
            # Run the synchronous DuckDuckGo search in a threadpool executor to keep the bot responsive
            results = await loop.run_in_executor(None, self._ddg_search_sync, query)

            for item in results:
                img_url = item.get("image")
                if not img_url:
                    continue
                matched, explanation = await self._verify_meme(img_url, description)
                if matched:
                    return {
                        "url": img_url,
                        "title": item.get("title", query),
                        "type": "image",
                        "source": "via DuckDuckGo Images",
                        "explanation": explanation
                    }
        except Exception as e:
            logger.warning(f"DuckDuckGo Image search failed: {e}")
        return None

    # ── Public methods ────────────────────────────────────────────────────────

    async def find_meme(self, description: str) -> Optional[dict]:
        """Main entry: description → search query → fallback chain → verified result."""
        query = await self._description_to_query(description)
        logger.info(f"Search query: '{query}' for description: '{description}'")

        # Fallback chain: Giphy → DuckDuckGo Images
        result = await self._search_giphy(query, description)
        if result:
            return result

        result = await self._search_duckduckgo(query, description)
        if result:
            return result

        # Last resort: return best Giphy result unverified with a link
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://api.giphy.com/v1/gifs/search",
                    params={"q": query, "api_key": self.config.giphy_key, "limit": 1}
                )
                items = resp.json().get("data", [])
                if items:
                    gif_url = items[0]["images"]["original"]["url"]
                    return {
                        "url": gif_url,
                        "title": items[0].get("title", query),
                        "type": "gif",
                        "source": "best guess via Giphy",
                        "explanation": "⚠️ Couldn't verify this 100% — best match I found."
                    }
        except Exception:
            pass

        return None

    async def explain_meme(self, image_bytes: bytes) -> str:
        """Explain a meme image sent by the user."""
        prompt = (
            "You are a meme expert. Explain this meme:\n"
            "1. What is this meme called / what's its origin?\n"
            "2. What does it mean / when do people use it?\n"
            "3. What makes it funny?\n\n"
            "Keep it concise and fun. Use markdown formatting."
        )
        try:
            return await self._gemini(prompt, image_bytes)
        except Exception as e:
            logger.error(f"Explain failed: {e}")
            return "😅 Couldn't analyze that image. Make sure it's a clear meme!"
