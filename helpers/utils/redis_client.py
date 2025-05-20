# from dotenv import load_dotenv
# import os
# from upstash_redis import Redis

# load_dotenv()

# REDIS_HOST = os.getenv("REDIS_HOST")
# REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")


# redis = Redis(url=REDIS_HOST, token=REDIS_PASSWORD) 

from dotenv import load_dotenv
import redis
import os

load_dotenv()

# Obtenha as variáveis de ambiente (configuradas no Cloud Run)
redis_host = os.getenv('REDISHOST', "localhost")
redis_port = int(os.getenv('REDISPORT', 6379))

print(f"{redis_host} redis host ...")

# Crie uma instância do cliente Redis
try:
    r = redis.StrictRedis(host=redis_host, port=redis_port, db=0)
    r.ping()  # Tenta se conectar ao servidor Redis
    print(f"Conexão com Redis estabelecida em {redis_host}:{redis_port}")
except redis.exceptions.ConnectionError as e:
    print(f"Erro ao conectar ao Redis: {e}")

# from dotenv import load_dotenv
# import os
# import redis as redisConnect

# load_dotenv()


# redis_host = os.environ.get("REDISHOST", "10.45.145.124")
# redis_port = int(os.environ.get("REDISPORT", 6379))
# redis = redisConnect.StrictRedis(host=redis_host, port=redis_port)



