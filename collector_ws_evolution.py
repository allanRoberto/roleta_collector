import json, logging, os, datetime, requests, time, websocket

from datetime import UTC 
from helpers.utils.redis_client import r
from pymongo import MongoClient


MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://revesbot:DlBnGmlimRZpIblr@cluster0.c14fnit.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

logging.basicConfig(level=logging.INFO)

# Mongo
client = MongoClient(MONGO_URL)
db = client["roleta_db"]
collection = db["history"]


class Evolution:
    def __init__(self):
        self.url = "https://vaidebet.bet.br/api/user/login"
        self.payloadLogin = {
            "requestBody": {
                "username": "allanrsilva",
                "email": "null",
                "phone": "null",
                "keepLoggedIn": "null",
                "password": "419300@Al",
                "loginType": "1",
            }
        }

        self.headersLogin = {
            "Content-Type": "application/json",
            "Origin": "https://m.vaidebet.bet.br",
            "Referer": "https://m.vaidebet.bet.br/",
        }

        self.urlevo = "https://vaidebet.bet.br/api/user/casinoapi/openGame"

        
        self.desiredArgs = {
            "7nyiaws9tgqrzaz3": "evolution-Football-studio-roulette",
            "7x0b1tgh7agmf6hv": "evolution-immersive-roulette",
            "8clwnwrupuvf0osq": "evolution-ruleta-en-vivo",
            "48z5pjps3ntvqc1b": "evolution-auto-roulette",
            "AmericanTable001": "evolution-american-roulette",
            "01rb77cq1gtenhmo": "evolution-auto-roulette-vip",
            "LightningSpain01": "evolution-ruleta-relampago-en-vivo",
            "LightningTable01": "evolution-lightning-roulette",
            "PorROU0000000001": "evolution-roleta-ao-vivo",
            "PorROULigh000001": "evolution-roleta-relampago",
            "RedDoorRoulette1": "evolution-red-door-roulette",
            "SpeedAutoRo00001": "evolution-speed-auto-roulette",
            "XxxtremeLigh0001": "evolution-xxxtreme-lightning-roulette",
            "f1f4rm9xgh4j3u2z": "evolution-auto-roulette-la-partage",
            "k37tle5hfceqacik": "evolution-auto-lightning-roulette",
            "laiayvwaiczqe2p7": "evolution-ruleta-automatica",
            "lkcbrbdckjxajdol": "evolution-speed-roulette",
            "oqa3v7a2t25ydg5e": "evolution-ruleta-bola-rapida-en-vivo",
            "p675txa7cdt6za26": "evolution-ruleta-en-espanol",
            "vctlz20yfnmp1ylr": "evolution-roulette",
            "wzg6kdkad1oe7m5k": "evolution-vip-roulette",
            "mrpuiwhx5slaurcy": "evolution-hippodrome-grand-casino",
            "DoubleBallRou001": "evolution-double-ball-roulette",
        }

        self.max_reconnect_attempts = 3
        self.reconnect_attempts = 0
        self.evoSessionId = None
        self.results = {}

    def pegar_session(self, attempt=1, max_attempts=3):
        if attempt > max_attempts:
            print(f"Max attempts ({max_attempts}) reached. Stopping.")
            return
        try:
            with requests.Session() as session:
                response = session.post(
                    self.url, json=self.payloadLogin, headers=self.headersLogin
                )

                if response.status_code != 200:
                    raise Exception(
                        "Login falhou com status code: " + str(response.status_code)
                    )

                print("Login bem-sucedido!")
                dados = response.json()
                traderId = dados["data"]["traderId"]
                pgUser = dados["data"]["code"]
                s7oryO9STV = response.headers.get("s7oryO9STV")

                headersEvo = {
                    "Content-Type": "application/json",
                    "Origin": "https://m.vaidebet.bet.br",
                    "Referer": "https://m.vaidebet.bet.br/",
                    "s7oryO9STV": s7oryO9STV,
                    "X-Pgdevice": "d",
                    "X-Pgtradername": str(traderId),
                    "X-Pgusername": pgUser,
                }

                payloadEvo = {
                    "requestBody": {
                        "gameId": "20801",
                        "channel": "web",
                        "vendorId": 130,
                        "redirectUrl": "https://m.vaidebet.bet.br/ptb/games/livecasino/detail/20801",
                    },
                    "identity": None,
                    "device": "d",
                    "languageId": 23,
                }

                print(self.urlevo)
                response2 = session.post(self.urlevo, json=payloadEvo, headers=headersEvo)

                data = response2.json()
                url = data["data"]["gameUrl"]
                response = session.get(url)

                EVOSESSIONID = (
                    response.history[2]
                    .headers["Set-Cookie"]
                    .split("EVOSESSIONID=")[1]
                    .split(";")[0]
                )

                return EVOSESSIONID

        except Exception as e:
            print(f"Attempt {attempt} failed with error: {e}")
            print("Trying again after 5 seconds...")
            time.sleep(5)
            self.pegar_session(attempt + 1, max_attempts)

    def connect_to_wss(self):
        def on_message(ws, message):
            message = json.loads(message)

            if message.get("type") == "lobby.historyUpdated":
                for arg in message.get("args", {}):
                    if arg in self.desiredArgs:

                        game_name = self.desiredArgs[arg]
                        game_results = message["args"][arg]["results"][0][0]['number']


                        if game_results :
                            slug = game_name
                            last_result = game_results
                            result = int(last_result)

                            now = datetime.datetime.now(UTC)

                            collection.insert_one({
                                "roulette_id": slug,
                                "roulette_name" : slug,
                                "value": result,
                                "timestamp": now
                            })

                            # trim para 500
                            count = collection.count_documents({"roulette_id": slug})
                            if count > 500:
                                exced = count - 500
                                antigos = collection.find(
                                    {"roulette_id": slug},
                                    sort=[("timestamp", 1)],
                                    limit=exced
                                )
                                ids = [d["_id"] for d in antigos]
                                collection.delete_many({"_id": {"$in": ids}})

                            r.publish("new_result", json.dumps({"slug": slug, "result": result}))
                            print(f"[{slug}] ✅ Resultado salvo: {result}")
                        else :
                            print(f"No results found for {game_name}")

        def on_error(ws, error):
            print("Error:", error)

        def on_close(ws, close_status_code, close_msg):
            print("### closed ###")
            self.on_ws_close()

        def on_open(ws):
            print("Connection opened")
            message = {
                "id": "jbjrenmu5j",
                "type": "lobby.initLobby",
                "args": {"version": 2},
            }
            ws.send(json.dumps(message))

        self.initiate_connection(on_open, on_message, on_error, on_close)

    def initiate_connection(self, on_open, on_message, on_error, on_close):
        wss_url = f"wss://vaidebetoss.evo-games.com/public/lobby/socket/v2/s3xlf5xgpo4qfdwx?messageFormat=json&device=Desktop&features=opensAt%2CmultipleHero%2CshortThumbnails%2CskipInfosPublished%2Csmc%2CuniRouletteHistory%2CbacHistoryV2%2Cfilters%2CtableDecorations&instance=cjysk7-s3xlf5xgpo4qfdwx-&EVOSESSIONID={self.evoSessionId}&client_version=6.20250520.71644.51887-e2cf87eb3b"

        ws = websocket.WebSocketApp(
            wss_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        ws.run_forever()

    def on_ws_close(self):
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            print(f"Attempt to reconnect ({self.reconnect_attempts})...")
            time.sleep(1)
            self.connect_to_wss()
        else:
            print("Max reconnect attempts reached. Starting over...")
            self.reconnect_attempts = 0
            self.start()

    def start(self):
        self.reconnect_attempts = 0

        evoSessionId = self.pegar_session()
        if evoSessionId:
            self.evoSessionId = evoSessionId
            self.connect_to_wss()

if __name__ == "__main__":
    Evolution().start()