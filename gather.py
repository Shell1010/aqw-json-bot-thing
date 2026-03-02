import websockets
import asyncio
import json
from pending_class import PendingClassUpdate
from time import monotonic

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

        case _:
            pass
        
    print(pending.ready(), "here")
    
    if pending.ready():
        process_class(pending)
        pending.__init__()  # reset state

def process_class(pending: PendingClassUpdate):
    with open("classes.json") as f:
        data = json.load(f)
        
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