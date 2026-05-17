from asyncio import gather
from decimal import Decimal
from fastapi import HTTPException
from http import HTTPStatus
from redis.asyncio import Redis
from app.integrations.shipping_integration import ShippingIntegration
from app.integrations.catalog_integration import CatalogIntegration
from app.services.cart_service import CartService
from app.schemas.shipping import CartShippingResponse, ShippingOption



class ShippingService:
    @staticmethod
    async def calculate_cart_shipping(redis: Redis, user_id: str, destination_zip: str):
        # 1. Pega os itens do carrinho
        cart_data = await CartService.get_items(redis, user_id)

        if not cart_data['items']:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Carrinho vazio.")

        # 2. Busca dimensões no Catalog
        products_ids = [item["product_variant_id"] for item in cart_data["items"]]
        catalog_data = await CatalogIntegration.fetch_all_prices(products_ids)

        # 3. Agrupa os produtos por Loja e monta o formato que o Melhor Envio exige
        stores_payloads = {}
        for item in cart_data["items"]:
            variant_id = item["product_variant_id"]
            catalog_info = catalog_data.get(variant_id)
            
            if not catalog_info:
                continue

            if item["store_id"] not in stores_payloads:
                stores_payloads[item["store_id"]] = []
            
            # Adiciona o item com dimensões da Variante
            stores_payloads[item["store_id"]].append({
                "id": variant_id,
                "width": catalog_info.get('width', 10),
                "height": catalog_info.get('height', 10),
                "length": catalog_info.get('length', 10),
                "weight": catalog_info.get('weight', 0.5),
                "insurance_value": catalog_info.get('unit_price', 0),
                "quantity": item["quantity"]
            })

        # 4. Dispara as requisições simultâneas para o Melhor Envio 
        tasks = []
        stores_ids_list = list(stores_payloads.keys())
        
        for store_id in stores_ids_list:
            # Busca o CEP da loja no microsserviço Catalog
            store_zip = await CatalogIntegration.get_store_zip(store_id) 
            
            payload_produtos = stores_payloads[store_id]
            
            # Prepara a "tarefa" assíncrona, mas não executa ainda
            tasks.append(
                ShippingIntegration.calculate_store_freight(store_zip, destination_zip, payload_produtos)
            )
        
        # Executa todas as requisições às lojas AO MESMO TEMPO
        results = await gather(*tasks)
        
        # 5. Processa os resultados para criar o frete "Integral"
        # Variáveis de Totais...
        total_cheapest_price = Decimal("0.00")
        max_cheapest_time = 0
        breakdown_cheapest = {}

        total_fastest_price = Decimal("0.00")
        max_fastest_time = 0
        breakdown_fastest = {}
        
        # 1. Nova Flag para avisar o front-end
        requires_pickup = False 

        for store_id, options in zip(stores_ids_list, results):
            if not options:
                raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=f"Erro ao cotar frete para a loja {store_id}")

            valid_options = [opt for opt in options if "error" not in opt]

            # 2. O Plano B (Fallback) entra aqui!
            if not valid_options:
                requires_pickup = True
                
                # Valores padrão de segurança caso os Correios não entreguem na porta
                default_price = 25.00
                default_time = 15 
                
                cheapest_store_opt = {"price": default_price, "delivery_time": default_time}
                fastest_store_opt = {"price": default_price, "delivery_time": default_time}
            else:
                cheapest_store_opt = min(valid_options, key=lambda x: float(x.get("price", 0)))
                fastest_store_opt = min(valid_options, key=lambda x: int(x.get("delivery_time", 99)))

            # Soma nos totais
            price_cheap = Decimal(str(cheapest_store_opt.get("price")))
            price_fast = Decimal(str(fastest_store_opt.get("price")))

            total_cheapest_price += price_cheap
            total_fastest_price += price_fast

            max_cheapest_time = max(max_cheapest_time, int(cheapest_store_opt.get("delivery_time", 0)))
            max_fastest_time = max(max_fastest_time, int(fastest_store_opt.get("delivery_time", 0)))

            breakdown_cheapest[store_id] = price_cheap
            breakdown_fastest[store_id] = price_fast

        # 3. Alterando o nome do frete para orientar a usuária no Carrinho
        if requires_pickup:
            name_economy = "Econômico (Retirada obrigatória em Agência dos Correios)"
            name_express = "Expresso (Retirada obrigatória em Agência dos Correios)"
        else:
            name_economy = "Econômico"
            name_express = "Expresso"

        # 4. Retorna o Schema montadinho com os nomes atualizados
        return CartShippingResponse(
            cheapest=ShippingOption(
                name=name_economy,
                total_price=total_cheapest_price,
                max_delivery_time=max_cheapest_time,
                stores_breakdown=breakdown_cheapest
            ),
            fastest=ShippingOption(
                name=name_express,
                total_price=total_fastest_price,
                max_delivery_time=max_fastest_time,
                stores_breakdown=breakdown_fastest
            )
        )