
# VendoMatic API
The VendoMatic API simulates a vending machine that handles beverages and transactions. It tracks the inventory of three beverages: Pop, Coffee, and Water.

### My Approach
To stay true to the Marigold codebase, I created this API in Python and used Flask (this is the only dependency in the application). In terms of design, I used the Singleton design pattern since it is optimal for shared routing states and simply looks pretty. It was vital from the start to ensure that the inventory management system was scalable, resilient, and dynamic- so I designed the API from an "inventory-first" approach. I've also implemented unit tests to follow best-practices. If desired, both app.py and test.py can be implemented within an actions workflow, however that would be overkill for this demonstration. 

**to comment? or not to comment?** 

You will also notice that there are no comments in my code- this is because I was once taught that comments does not equal clear/good code- instead, the style and orchestration of it does. I have written the code so that it is readable and friendly to other developers. Of course in production comments become quite necessary in large codebases with different developers programming styles and technqiues. I personally enjoy putting in comments but for the sake of and 'cleanliness' I chose to not include them here.

### Features
- Dynamic Inventory Management
- Unit Testing

### Capabilities:
- Add a coin (US quarter) to the vendomatic
- Get the available inventory of beverages
- Purchase and dispense a beverage
- Return change

## Installation

### Prerequisites
- Python 3.x installed
- Flask installed (pip3 install flask) 


### Steps to Run:
1. Clone the repository or copy the script in desired directory
```
git clone https://github.com/ethanwater/marigold_vendomatic.git
```
2. Install dependencies (we only use Flask here)
```
pip3 install flask
```
or...
```
pip3 install -r requirements.txt
```
2. Run the Flask application:
```
python3 app.py
```
The app will be available on http://localhost:8080/.

## How to Use
You can run the following commands in your terminal to interact with the API. *Be sure that the app is running.*

### Add a Coin [PUT]
Adds a single quarter to the vending machine. The total number of inserted quarters is returned in the response header (X-Coins).
Changing the coin amount from 1 will produce an error.
```
curl -X PUT http://localhost:8080/ -H "Content-Type: application/json" -d '{"coin": 1}' -i
```
**Success**
* Status Code: 204 No Content
* X-Coins: Number of coins returned


**Failure**
- Status Code: 400 Bad Request - Invalid number of coins in body

### Return Change [DELETE]
Returns all quarters inserted into the vending machine and resets the coin count.
```
curl -X DELETE http://localhost:8080/ -i
```
**Success**
* Status Code: 204 No Content
* X-Coins: Number of coins returned
  
**Failure**
- Status Code: 400 Bad Request - No coins to be returned


### Get Inventory[GET /inventory]
Fetches the current inventory for all available beverages.

**note**: *when implementing the API, i noticed that simply returning an array of integers to reprsent the inventory was too vague. I went with the more friendly and verbose approach of displaying the beverage name alongside it's quantity.*
```
curl -X GET http://localhost:8080/inventory -i
```
**Success**
* Status Code: 200 OK
* Body: Quantity of all beverages
  
**Failure**
- Status Code: 500 Internal Server Error


### Get Inventory for Specific Beverage [GET /inventory/{beverage_id}]
Fetches the quantity available for a specific beverage (ids: Pop, Coffee, or Water).
```
curl -X GET http://localhost:8080/inventory/Pop -i
```
**Success**
* Status Code: 200 OK
* Body: Quantity of the specified beverage
  
**Failure**
- Status Code: 500 Internal Server Error

### Purchase a Beverage (PUT /inventory/{beverage_id})
Attempts to purchase a specified beverage (Pop, Coffee, or Water). The API requires two quarters (inserted via the PUT / endpoint) to dispense a beverage.

```
curl -X PUT http://localhost:8080/inventory/Pop -i
```
**Success**:
- X-Coins: Remaining change.
- X-Inventory-Remaining: Quantity left of the purchased beverage.
- Status Code: 200 OK

**Failure**
- Status Code: 403 Forbidden - Insufficient quarters
- Status Code: 404 Not Found - Invalid beverage_id
- X-Coins: Number of coins to be accepted. || Number of coins (0/1)




## Testing
**note:** *be sure to run the tests on a fresh start of the flask app in another terminal window, otherwise- it will fail*.
To run the unit tests, simply run:
```
python3 test.py
```


**MIT License**
