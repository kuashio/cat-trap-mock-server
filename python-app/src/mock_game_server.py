import asyncio
import json
import random
import websockets
import numpy as np

class Game:
    def __init__(self, size):
        self.size = size
        self.hexgrid = np.zeros((size, size), dtype=int)
        self.cat = (size // 2, size // 2)
        self.hexgrid[self.cat] = 6  # Place the cat in the middle
        for _ in range(3):
            while True:
                r, c = random.randint(0, size - 1), random.randint(0, size - 1)
                if self.hexgrid[r, c] == 0 and not (r == size // 2 and c == size // 2):
                    self.hexgrid[r, c] = 1  # Block the tile
                    break

    def move_cat(self):
        free_tiles = np.argwhere(self.hexgrid == 0)
        if free_tiles.size > 0:
            r, c = free_tiles[random.randint(0, len(free_tiles) - 1)]
            self.hexgrid[self.cat] = 0  # Clear the old position
            self.hexgrid[r, c] = 6  # Move the cat to the new position
            self.cat = (r, c)
        return self.hexgrid.tolist()

    def block_tile(self, r, c):
        self.hexgrid[r, c] = 1

    def unblock_tile(self, r, c):
        self.hexgrid[r, c] = 0

    def place_cat(self, r, c):
        self.hexgrid[self.cat] = 0  # Clear previous cat position
        self.hexgrid[r, c] = 6
        self.cat = (r, c)

async def handler(websocket, path):
    game = None
    async for message in websocket:
        print("Received message:", message)  # Debug log
        data = json.loads(message)
        if data['command'] == 'new_game':
            game = Game(data['size'])
            await websocket.send(json.dumps({'command': 'updateGrid', 'data': json.dumps(game.hexgrid.tolist())}))
        elif data['command'] == 'move' and game:
            r, c = data['clicked_tile']
            game.block_tile(r, c)
            updated_grid = game.move_cat()
            await websocket.send(json.dumps({'command': 'updateGrid', 'data': json.dumps(updated_grid)}))
        elif data['command'] == 'edit' and game:
            action = data['action']
            r, c = data['tile']
            if action == 'block':
                game.block_tile(r, c)
            elif action == 'unblock':
                game.unblock_tile(r, c)
            elif action == 'place_cat':
                game.place_cat(r, c)
            await websocket.send(json.dumps({'command': 'updateGrid', 'data': json.dumps(game.hexgrid.tolist())}))
        if game and check_endgame(game):
            await websocket.send(json.dumps({'command': 'endgame', 'reason': check_endgame(game)}))

def check_endgame(game):
    # Example logic for endgame conditions
    if not np.any(game.hexgrid == 0):  # No free tiles
        return 1  # Cat trapped
    # Add timeout logic here if necessary
    return None

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
