from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    profile: str = "profiles/worker_main"
    headless: bool = False
    url: str = "https://example.com"
    width: int = 1460
    height: int = 920
    trace: bool = True
    trace_path: str = "traces/trace.zip"
    video_dir: str | None = None
    class Config: env_prefix = "GUI_"
