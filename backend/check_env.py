from app.config import settings
print("GEMINI_API_KEY:", repr(settings.GEMINI_API_KEY[:10]) if settings.GEMINI_API_KEY else "EMPTY")
