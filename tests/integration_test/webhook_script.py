import hmac
import hashlib
import time
from app.core.config import settings

# Coloque aqui a sua chave secreta real e o ID da ordem real gerada pelo MP
SECRET = settings.WEBHOOK_SECRET
ORDER_ID = "ORDTST01KRVP8NG16SP1P2HCYEQ5785X" # Pode colocar maiúsculo mesmo

# O script faz o trabalho sujo
data_id_lower = ORDER_ID.lower()
x_request_id = "teste-manual-insomnia"
ts = str(int(time.time() * 1000))

manifest = f"id:{data_id_lower};request-id:{x_request_id};ts:{ts};"
hmac_obj = hmac.new(SECRET.encode(), msg=manifest.encode(), digestmod=hashlib.sha256)
hash_hex = hmac_obj.hexdigest()

print("\n--- COPIE E COLE NO INSOMNIA ---")
print(f"URL: http://localhost:8000/api/v1/orders/webhook/mercadopago?data.id={ORDER_ID}&type=order")
print(f"HEADER x-request-id: {x_request_id}")
print(f"HEADER x-signature: ts={ts},v1={hash_hex}")
print(f"BODY JSON:\n{{\n  \"action\": \"order.updated\",\n  \"data\": {{\"id\": \"{ORDER_ID}\"}}\n}}")