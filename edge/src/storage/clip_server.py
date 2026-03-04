import logging
from aiohttp import web
from pathlib import Path

logger = logging.getLogger(__name__)

class ClipServer:
    def __init__(self, config, clip_manager):
        self.config = config
        self.clip_manager = clip_manager
        self.app = web.Application()
        self.app.router.add_get("/edge/clips/{event_id}", self.get_clip)
        self.app.router.add_get("/edge/health", self.get_health)

    async def get_clip(self, request: web.Request) -> web.Response:
        event_id = request.match_info["event_id"]
        clip_path = self.clip_manager.get_clip_path(event_id)
        if not clip_path:
            return web.Response(status=404, text="Clip not found")
        return web.FileResponse(clip_path)

    async def get_health(self, request: web.Request) -> web.Response:
        return web.json_response({"status": "ok"})

    async def start(self, port: int = 8080):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        logger.info("Clip server started on port %d", port)
