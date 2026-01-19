from order_state import OrderState
from order import Order


class OrderService:
    def __init__(self, order: Order):
        self.order = order

    def next_state(self, current_state: OrderState) -> OrderState:
        transitions = {
            OrderState.SELECT_PRODUCT: OrderState.ADDRESS,
            OrderState.ADDRESS: OrderState.MESSAGE,
            OrderState.MESSAGE: OrderState.CONFIRM
        }
        return transitions[current_state]

    def can_continue_from_products(self) -> bool:
        return len(self.order.products) > 0

    def is_ready_to_confirm(self) -> bool:
        return self.order.is_complete()
    def confirm_order(self, order: Order) -> int:
        return self.order_repo.insert(order)
