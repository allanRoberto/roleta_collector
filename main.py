import asyncio
import os
from aiohttp import web
from collector_ws_pragmatic import run_pragmatic
# from collector_ws_evolution import run_evolution (futuramente)

async def dummy_http_server():
    async def handler(request):
        return web.Response(text="🟢 Coletor rodando")
    app = web.Application()
    app.router.add_get("/", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8080)))
    await site.start()

async def main():
    print("init ...")
    await asyncio.gather(
        run_pragmatic(),
        # run_evolution(),  # adicione aqui os próximos
        dummy_http_server()
    )

if __name__ == "__main__":
    asyncio.run(main())
