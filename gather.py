import websockets
import asyncio
import json
from pending_class import PendingClassUpdate
from time import monotonic
import csv


pending = PendingClassUpdate()

def handle_message(msg: dict, pending: PendingClassUpdate):
    pending.last_update = monotonic()
    obj = msg.get("b", {}).get("o", {})
    cmd = obj.get("cmd")

    match cmd:
        case "updateClass":
            pending.class_update = obj

        case "aura+p":
            pending.aura_p = obj

        case "sAct":
            pending.s_act = obj

        case "seia":
            pending.seia = obj
    
    if pending.ready():
        process_class(pending)
        pending.__init__()  # reset state
        
def csv_to_json():
    with open("scrolls.csv", "r") as f:
        reader = csv.reader(f)
        name_ids = list(reader)
        new_dict = {}
        for name, id in name_ids:
            new_dict[id] = name
        return new_dict

def process_class(pending: PendingClassUpdate):
    with open("classes.json") as f:
        data = json.load(f)
    if pending.seia is not None:
        scrolls = csv_to_json()
        with open("scrolls.json") as f:
            data = json.load(f)
            name = scrolls.get(str(pending.seia['o']['id']), str(pending.seia['o']['id']))
            
            prev_data = data.get(name, {})
            pending.seia.update({"name": name})
            prev_data.update(pending.seia)
            
            data[name] = prev_data
            with open("scrolls.json", "w") as f:
                json.dump(data, f, indent=4)
            
    if pending.class_update is not None:
        prev_data = data.get(pending.class_update["sClassName"], {})
    
        prev_data.update(pending.class_update)
        prev_data.update(pending.aura_p)
        prev_data.update(pending.s_act)
        
        data[pending.class_update["sClassName"]] = prev_data
        
        with open("classes.json", "w") as f:
            json.dump(data, f, indent=4)

async def hello():
    async with websockets.connect("ws://localhost:8765") as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            handle_message(data, pending)


if __name__ == "__main__":
    asyncio.run(hello())