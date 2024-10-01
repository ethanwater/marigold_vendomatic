from flask import Flask, jsonify, request

app = Flask(__name__)
DEFAULT_QUANTITY = 5
class Beverage:
    def __init__(self, name):
        self.name = name
        self.quantity = DEFAULT_QUANTITY

class VendoMatic:
    def __init__(self):
        self.beverages = {
            'Pop': Beverage('Pop'),
            'Coffee': Beverage('Coffee'),
            'Water': Beverage('Water')
        }
        self.quarter_count = 0
        self.cost = 2

    def add_quartr(self, amt):
        if not isinstance(amt, int) or amt <= 0:
            raise ValueError(f"invalid coin amount")
        self.quarter_count+= amt

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
        raise ValueError(f"beverage doesn't exist!")

    def vend(self, beverage):
        beverage = self.beverages.get(beverage)

        if beverage is None:
            return None, {'error': str(beverage.name + 'does not exist!')}, 400 
        if beverage.quantity <= 0:
            return None, {'error': str(beverage.name + 'is out of stock')}, 404 
        if self.quarter_count < self.cost:
            return None, {'error': 'insufficient quarters, you have: ' + self.quarter_count + '; need atleast 2'}, 403  

        change = self.quarter_count - self.cost
        beverage.quantity -= 1
        self.quarter_count = 0

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
            vendomatic.add_quartr(data.get('coin'))  
            response = jsonify({"message": "added a quarter to the vendomatic"})
            response.headers['X-Coins'] = str(vendomatic.quarter_count)
            return response, 204  
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

@app.route('/', methods=['DELETE'])
def return_change():
    change = vendomatic.quarter_count
    response = jsonify({"change": change})
    response.headers['X-Coins'] = str(vendomatic.quarter_count)
    vendomatic.quarter_count = 0
    return response, 204

@app.route('/inventory', methods=['GET'])
def get_inventory():
    try:
        return jsonify(vendomatic.get_inventory()), 200  
    except ValueError as err:
        return jsonify({"error": "cannot get inventory" + str(err)}), 400

@app.route('/inventory/<string:beverage>', methods=['GET'])
def get_beverage_quantity(beverage):
    quantity = vendomatic.get_beverage_quantity(beverage)
    if quantity is None:
        beverages = ", ".join([beverage.name for beverage in vendomatic.beverages.values()])
        return jsonify({"error": "beverage does not exist. beverages available are: " + beverages}), 404
    return jsonify(quantity), 200  

@app.route('/inventory/<string:beverage>', methods=['PUT'])
def vend_beverage(beverage):
    beverage, data, status = vendomatic.vend(beverage)

    if status == 404 or status == 403:
        response = jsonify(data)  
        response.headers['X-Coins'] = str(vendomatic.quarter_count)
        return response, status  

    response = jsonify({'quantity': data['quantity']})

    vendomatic.quarter_count = 0
    response.headers['X-Coins'] = str(vendomatic.quarter_count)
    response.headers['X-Inventory-Remaining'] = str(data['inventory_remain'])
    return response, status

vendomatic = VendoMatic()
if __name__ == '__main__':
    app.run(port=8080)
