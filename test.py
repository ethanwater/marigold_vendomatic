import http.client
import json

def test(task, func):
    try:
        func()
        print(f"✅ {task} passed!")
    except AssertionError as e:
        print(f"❌ {task} failed: {e}")


def test_add_quarter():
    conn = http.client.HTTPConnection("localhost", 8080)
    headers = {'Content-Type': 'application/json'}
    payload = json.dumps({"coin": 1})
    
    conn.request("PUT", "/", payload, headers)
    response = conn.getresponse()
    
    assert response.status == 204, f"Expected 204, but got {response.status} instead"
    assert response.getheader('X-Coins') == '1', f"Expected 1 coin, but got {response.getheader('X-Coins')} coins instead"

def test_get_inventory():
    conn = http.client.HTTPConnection("localhost", 8080)
    conn.request("GET", "/inventory")
    response = conn.getresponse()
    
    json.loads(response.read().decode())
    assert response.status == 200, f"Expected 200, but got {response.status} instead"

def test_get_beverage_inventory():
    conn = http.client.HTTPConnection("localhost", 8080)
    conn.request("GET", "/inventory/Pop")

    response = conn.getresponse()
    inventory = json.loads(response.read().decode())

    assert response.status == 200, f"Expected 200, but got {response.status} instead"
    assert inventory == 4, f"Expected 4 inventory remaining, but got {inventory} instead" 

def test_purchase_beverage():
    conn = http.client.HTTPConnection("localhost", 8080)
    headers = {'Content-Type': 'application/json'}

    for _ in range(2):  
        conn.request("PUT", "/", json.dumps({"coin": 1}), headers)
        response = conn.getresponse()
        response.read() 
        assert response.status == 204, f"Expected 204, but got {response.status} instead"

    conn.request("PUT", "/inventory/Pop", headers=headers)
    response = conn.getresponse()
    _ = json.loads(response.read().decode())

    assert response.status == 200, f"Expected 200, got {response.status}"
    assert response.getheader('X-Coins') == '0', f"Expected 0 x-coins, but got {response.getheader('X-Coins')} coins instead"
    assert response.getheader('X-Inventory-Remaining') == '4', f"Expected 4 inventory remaining, but got {response.getheader('X-Inventory-Remaining')} instead"

    conn.close()  

def test_return_change():
    headers = {'Content-Type': 'application/json'}
    conn = http.client.HTTPConnection("localhost", 8080)
    conn.request("PUT", "/", json.dumps({"coin": 1}), headers)
    response = conn.getresponse()

    conn.request("DELETE", "/")
    response = conn.getresponse()
    
    assert response.status == 204, f"Expected 204, but got {response.status} instead"
    assert response.getheader('X-Coins') == '1', f"Expected 0 x-coins, but got {response.getheader('X-Coins')} coins instead"

if __name__ == "__main__":
    print("Running vend-o-tests...\n")
    test("Add quarter", test_add_quarter)
    test("Purchase beverage", test_purchase_beverage)
    test("Get inventory", test_get_inventory)
    test("Get beverage inventory", test_get_beverage_inventory)
    test("Return change", test_return_change)
