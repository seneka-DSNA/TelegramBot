from enum import Enum


class OrderState(Enum):
    SELECT_PRODUCT = "select_product"
    ADDRESS = "address"
    MESSAGE = "message"
    TIME = "time" 
    CONFIRM = "confirm"

