import redis
import pickle

r = redis.Redis(
    host='trusting-irreplaceable-veil-38484.db.redis.io',
    port=11492,
    decode_responses=False,
    username="default",
    password="syEzHgqn14f62L8JBWzPwS2z21fU4xxa"
)

def save_obj_by_login(base, login, obj):
    serialized = pickle.dumps(obj)
    r.hset(f"{base}:1", login, serialized)
    r.hexpire(f"{base}:1",  600, login)

def get_obj_by_login(base, login):
    obj = r.hget(f"{base}:1", login)
    try:
        return pickle.loads(obj)
    except TypeError:
        return None

def del_obj_by_login(base, login):
    r.hdel(f"{base}::1", login)

if __name__ == '__main__':
    save_obj_by_login('test', 'default', type(123))
    print(get_obj_by_login('test', 'default'))