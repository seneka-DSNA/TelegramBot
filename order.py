class Order:
    def __init__(self):
        self.products: dict[int, int] = {}
        self.address: str | None = None
        self.message: str = ""
        self.delivery_time: str | None = None

    def add_product(self, product_id: int):
        self.products[product_id] = self.products.get(product_id, 0) + 1
    def remove_product(self, product_id: int):
        if product_id not in self.products:
            return
        if self.products[product_id] <= 1:
            del self.products[product_id]
        else:
            self.products[product_id] -= 1
    def has_products(self) -> bool:
        return bool(self.products)

    def set_address(self, address: str):
        if not address:
            raise ValueError("Address cannot be empty")
        self.address = address

    def set_message(self, message: str):
        self.message = message or ""

    def set_delivery_time(self, delivery_time: str):
        if not delivery_time:
            raise ValueError("Delivery time cannot be empty")
        self.delivery_time = delivery_time

    def is_complete(self) -> bool:
        return bool(self.products and self.address and self.delivery_time)

