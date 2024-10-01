from flask import Flask, jsonify, request
import logging

logging.basicConfig(level=logging.INFO)
MAX_BEVERAGE_QUANTITY = 5

app = Flask(__name__)

class Beverage:
    def __init__(self, name):
        self.name = name
        self.quantity = MAX_BEVERAGE_QUANTITY

class VendoMatic:
    def __init__(self):
        self.coin_count = 0
        self.beverage_cost = 2
        self.beverages = {
            'pop': Beverage('pop'),
            'coffee': Beverage('coffee'),
            'water': Beverage('water')
        }

    def add_coin(self):
        self.coin_count+= 1
        logging.info(f"self.coin_count: {self.coin_count}")

    def reset_coins(self):
        self.coin_count = 0
    
    def if_exists(self, beverage_name):
        return beverage_name in self.beverages 

    def get_inventory(self):
        return [{"name": b.name, "quantity": b.quantity} for b in self.beverages.values()]

    def get_beverage_quantity(self, beverage):
        if not self.if_exists(beverage):
            raise ValueError(f"beverage doesn't exist!")
        target = self.beverages.get(beverage)
        return target.quantity
        
    def vend(self, beverage_name):
        if not self.if_exists(beverage_name):
            logging.warning(f"vend::failed > invalid:NULL'")
            return None, {'error': 'beverage does not exist.'}, 400 

        beverage = self.beverages[beverage_name]
        if beverage.quantity <= 0:
            logging.warning(f"vend::failed {beverage.name} > invalid:out of stock.")
            return None, {'error': f'{beverage.name} is out of stock.'}, 404 
        if self.coin_count < self.beverage_cost:
            logging.warning(f"vend::failed > insufficient coins! current coins: {self.coin_count}")
            return None, {'error': f'Insufficient coins. You have: {self.coin_count} coins, but you need atleast 2.'}, 403  

        change = self.coin_count - self.beverage_cost
        beverage.quantity -= 1
        logging.debug(f"vend::success [change: {change}] [beverage.quantity: {beverage.quantity}]")

        return beverage.name, {
            'quantity': 1,
            'change': change,
            'inventory_remain': beverage.quantity
        }, 200  
    

@app.route('/', methods=['PUT'])
def add_coin():
    data = request.get_json()
    try:
        if data.get('coin') == 1:
            vendomatic.add_coin()  
            resp = jsonify({"message": "cha-ching! added 1 coin"})
            resp.headers['X-Coins'] = str(vendomatic.coin_count)
            return resp, 204  
        else:
            return jsonify({"error": "Invalid number of coins in the request body, must be 1"}), 400
    except:
        return jsonify({"error": "Missing 'coin' key in the request body."}), 400

@app.route('/', methods=['DELETE'])
def return_change():
    change = vendomatic.coin_count
    if change == 0:
        return jsonify({"error": "No coins to be returned."}), 400
    resp = jsonify({"change": change})
    resp.headers['X-Coins'] = str(vendomatic.coin_count)
    vendomatic.reset_coins()
    return resp, 204

@app.route('/inventory', methods=['GET'])
def get_inventory():
    return jsonify(vendomatic.get_inventory()), 200  

@app.route('/inventory/<string:beverage>', methods=['GET'])
def get_beverage_quantity(beverage):
    beverage = str(beverage).lower()
    if vendomatic.if_exists(beverage):
        quantity = vendomatic.get_beverage_quantity(beverage)
        return jsonify(quantity), 200  
    else:
        beverages = ", ".join([beverage.name for beverage in vendomatic.beverages.values()])
        return jsonify({"error": f"The input beverage does not exist. Available beverages are: {beverages}"}), 404

@app.route('/inventory/<string:beverage>', methods=['PUT'])
def purchase_beverage(beverage):
    beverage = str(beverage).lower()
    _, data, status = vendomatic.vend(beverage)

    if status != 200:
        resp = jsonify(data)  
        resp.headers['X-Coins'] = str(data['change']) 
        return resp, status
    else:
        resp = jsonify({'quantity': data['quantity']})
        resp.headers['X-Coins'] = str(data['change'])
        resp.headers['X-Inventory-Remaining'] = str(data['inventory_remain'])
        vendomatic.reset_coins()
        return resp, status


if __name__ == '__main__':
    vendomatic = VendoMatic()
    print("🚀 launching vend-o-matic!")
    app.run(port=8080)
