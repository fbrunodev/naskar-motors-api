from py_vapid import Vapid

v = Vapid()
v.generate_keys()

print("=== Cole estas variaveis no Render ===")
print(f"VAPID_PUBLIC_KEY={v.public_key.decode()}")
print(f"VAPID_PRIVATE_KEY={v.private_key.decode()}")
