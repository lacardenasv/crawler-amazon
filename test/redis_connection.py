import redis
redis_host = "127.0.0.1"
redis_port = 6379
redis_db = 0


def test_connection():
    redis_connection = redis.Redis(
        host=redis_host,
        port=redis_port,
        db=redis_db
    )
    redis_connection.ping()
    print('connected to redis {}'.format(redis_host))


if __name__ == '__main__':
    test_connection()