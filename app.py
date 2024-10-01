from flask import Flask, jsonify, request
import logging

#TODO: maybe implement case handling (upper to lower etc)

app = Flask(__name__)
MAX_BEVERAGE_QUANTITY = 5

class Beverage:
    def __init__(self, name):
        self.name = name
        self.quantity = MAX_BEVERAGE_QUANTITY

class VendoMatic:
    def __init__(self):
        self.beverages = {
            'Pop': Beverage('Pop'),
            'Coffee': Beverage('Coffee'),
            'Water': Beverage('Water')
        }
        self.coin_count = 0
        self.cost = 2

    def add_coin(self, amt):
        if not isinstance(amt, int) or amt <= 0:
            raise ValueError(f"invalid coin amount")
        self.coin_count+= amt
        logging.debug(self.coin_count)

    def get_inventory(self):
        inventory = []
        for beverage in self.beverages.values():
            item = {
                "name": beverage.name,
                "quantity": beverage.quantity
            }
            inventory.append(item)
        return inventory

    def get_beverage_quantity(self, beverage):
        target = self.beverages.get(beverage)
        if target is not None:
            return target.quantity
        logging.error(beverage + " does not exist, perhaps due to a typo from the user")
        raise ValueError(f"beverage doesn't exist!")

    def vend(self, beverage):
        beverage = self.beverages.get(beverage)

        if beverage is None:
            return None, {'error': str(beverage.name + ' does not exist.')}, 400 
        if beverage.quantity <= 0:
            return None, {'error': str(beverage.name + ' is out of stock.')}, 404 
        if self.coin_count < self.cost:
            logging.warning(self.coin_count)
            return None, {'error': 'Insufficient coins. You have: ' + self.coin_count + ' coins, but you need atleast 2.'}, 403  

        change = self.coin_count - self.cost
        logging.debug(change)
        beverage.quantity -= 1
        logging.debug(beverage.quantity)
        self.coin_count = 0

        return beverage.name, {
            'quantity': 1,
            'change': change,
            'inventory_remain': beverage.quantity
        }, 200  

@app.route('/', methods=['PUT'])
def add_coin():
    try:
        data = request.get_json()
        if data.get('coin') == 1:
            vendomatic.add_coin(data.get('coin'))  
            response = jsonify({"message": "Added 1 coin to the vendomatic."})
            response.headers['X-Coins'] = str(vendomatic.coin_count)
            return response, 204  
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

@app.route('/', methods=['DELETE'])
def return_change():
    try:
        change = vendomatic.coin_count
        if change == 0:
            return jsonify({"error": "No change to be returned."}), 400
        response = jsonify({"change": change})
        response.headers['X-Coins'] = str(vendomatic.coin_count)
        vendomatic.coin_count = 0
        return response, 204
    except AttributeError as err:
        return jsonify({"error": "Attribute error: " + str(err)}), 500
    except ValueError as err:
        return jsonify({"error": "Invalid operation: " + str(err)}), 400

@app.route('/inventory', methods=['GET'])
def get_inventory():
    try:
        return jsonify(vendomatic.get_inventory()), 200  
    except ValueError:
        return jsonify({"error": "Unable to fetch the inventory."}), 400

@app.route('/inventory/<string:beverage>', methods=['GET'])
def get_beverage_quantity(beverage):
    try:
        quantity = vendomatic.get_beverage_quantity(beverage)
        return jsonify(quantity), 200  
    except:
        beverages = ", ".join([beverage.name for beverage in vendomatic.beverages.values()])
        return jsonify({"error": "The input beverage does not exist. Beverages available are: " + beverages + "."}), 404
    

@app.route('/inventory/<string:beverage>', methods=['PUT'])
def vend_beverage(beverage):
    beverage, data, status = vendomatic.vend(beverage)

    if status == 404 or status == 403:
        response = jsonify(data)  
        response.headers['X-Coins'] = str(vendomatic.coin_count)
        return response, status  

    vendomatic.coin_count = 0

    response = jsonify({'quantity': data['quantity']})
    response.headers['X-Coins'] = str(vendomatic.coin_count)
    response.headers['X-Inventory-Remaining'] = str(data['inventory_remain'])
    return response, status

vendomatic = VendoMatic()
if __name__ == '__main__':
    app.run(port=8080)
