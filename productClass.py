class Product:
    def __init__(self, id, name, price, stock, picture):
        self.__id = id
        self.__name = name
        self.__price = price
        self.__stock = stock
        self.__picture = picture



        def is_in_stock(self):
            return self.__stock > 0



        def reduce_stock(self, qty):
            if qty <= self.__stock:
                self.__stock -= qty
            else:
                print("Not enough in stock")



        def increase_stock(self, qty):
            if qty > 0:
                self.__stock += qty