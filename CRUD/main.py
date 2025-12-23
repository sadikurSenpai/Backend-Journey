from fastapi import FastAPI, HTTPException
from schemas import TodoItem

app = FastAPI()

# keys are IDs (int), values are the TodoItem objects
fake_db = {}

# A simple counter to generate unique IDs
current_id = 0

@app.get('/')
def home():
    return {'message': 'Welcome to the To-Do API!'}

@app.post('/items', response_model=dict)
def add_item(item: TodoItem):
    global current_id
    current_id += 1
    # Store the item in our fake database
    fake_db[current_id] = item
    return {'id': current_id, 'item': item}

@app.get('/items')
def get_all_items(limit: int = 10, offset: int = 0):
    # Convert dictionary values to a list to return them
    print(fake_db)
    all_items = list(fake_db.values())
    print(all_items)
    # Implement slicing for pagination
    return all_items[offset : offset + limit]

@app.get('/items/{item_id}')
def get_specific_item(item_id: int):
    if item_id in fake_db:
        return fake_db[item_id]
    else:
        raise HTTPException(status_code=404, detail='Item not found!')

@app.put('/items/{item_id}')
def update_item(item_id: int, updated_item: TodoItem):
    if item_id in fake_db:
        fake_db[item_id] = updated_item
        return {'id': item_id, 'item': updated_item}
    else:
        raise HTTPException(status_code=404, detail="Item Not Found")

@app.delete('/items/{item_id}')
def delete_item(item_id: int):
    if item_id in fake_db:
        removed_item = fake_db.pop(item_id)
        return {'message': f"Item '{removed_item.title}' removed!"}
    else:
        raise HTTPException(status_code=404, detail="Item not found!")
