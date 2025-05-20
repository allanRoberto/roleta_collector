import asyncio
import json
import os
import websockets
from websockets.exceptions import ConnectionClosedError
from helpers.utils.redis_client import r
import time

id_to_slug = {
    "210": "pragmatic-auto-mega-roulette",
    "204": "pragmatic-mega-roulette",
    "292": "pragmatic-immersive-roulette-deluxe",
    "213": "pragmatic-korean-roulette",
    "225": "pragmatic-auto-roulette",
    "201": "pragmatic-roulette-2",
    "266": "pragmatic-vip-auto-roulette",
    "226": "pragmatic-speed-auto-roulette",
    "230": "pragmatic-roulete-3",
    "203": "pragmatic-speed-roulette-1",
    "227": "pragmatic-roulette-1",
    "545": "pragmatic-vip-roulette",
    "211a1": "pragmatic-lucky-6-roulette",
    "208": "pragmatic-turkish-mega-roulette",
    "287": "pragmatic-mega-roulette-brazilian",
    "298": "pragmatic-italian-mega-roulette",
    "224": "pragmatic-turkish-roulette",
    "240": "pragmatic-powerup-roulette",
    "205": "pragmatic-speed-roulette-2",
    "233": "pragmatic-romanian-roulette",
    "234": "pragmatic-roulette-italian",
    "237": "pragmatic-brazilian-roulette",
    "222": "pragmatic-german-roulette",
    "221": "pragmatic-russian-roulette",  
    "223": "pragmatic-roulette-italia-tricolore",
    "262": "pragmatic-vietnamese-roulette",
    "206": "pragmatic-roulette-macao"
}

async def subscribe(ws):
    subscribe_message = {
        "type": "subscribe",
        "isDeltaEnabled": True,
        "casinoId": "ppcar00000005644",
        "key": list(id_to_slug.keys()),
        "currency": "BRL"
    }
    await ws.send(json.dumps(subscribe_message))

async def handle_message(message: str):
    try:
        data = json.loads(message)
        table_id = data.get("tableId")

        if table_id not in id_to_slug or "last20Results" not in data:
            return

        slug = id_to_slug[table_id]
        last_result = data["last20Results"][0]
        result = int(last_result["result"])
        game_id = last_result.get("gameId")

        if not game_id:
            print(f"[{slug}] ⚠️ gameId ausente")
            return

        dedup_key = f"game:{slug}:{game_id}"
        if not r.exists(dedup_key):
            
            r.set(dedup_key, 1, ex=300)
            r.lpush(f"history:{slug}", result)
            r.ltrim(f"history:{slug}", 0, 199)
            r.publish("new_result", json.dumps({"slug": slug, "result": result}))
            print(f"[{slug}] ✅ Resultado salvo: {result} (gameId: {game_id})")
        else:
            print(f"[{slug}] ⏩ Resultado já registrado: {result}")
    except Exception as e:
        print(Exception, e)
        print("Erro ao processar:", e)

async def run_pragmatic():
    print("🚀 Iniciando conexão com WebSocket da Pragmatic...")

    ws_url = "wss://dga.pragmaticplaylive.net/ws"
    headers = {
        "Origin": "https://client.pragmaticplaylive.net",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
    }

    while True:
        try:
            print("🔌 Conectando ao WebSocket...")
            async with websockets.connect(ws_url, additional_headers=headers) as ws:
                print("✅ Conectado! Enviando inscrição...")
                await subscribe(ws)
                print("📡 Inscrição enviada. Aguardando mensagens...")
                async for message in ws:
                    await handle_message(message)
        except (ConnectionClosedError, OSError) as e:
            print(f"🔌 Conexão perdida: {e}, tentando reconectar em 2s…")
            await asyncio.sleep(0.5 )

 