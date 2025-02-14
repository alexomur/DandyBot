import main
from main import Board, Player
import random
import time
import json
from pathlib import Path
import concurrent.futures

NUM_GAMES = 10          # Number of games running simultaneously. Uses multitasking (be careful using powerful AIs)
GAME_DATA = "game.json" # Location of the file with information about players and levels


# Classes easy to calculate
class DummyBoard(Board):
    def __init__(self, game, canvas, label):
        main.PliTk = DummyPliTk
        super().__init__(game, canvas, label)

class DummyCanvas:
    def config(self, **kwargs):
        pass
    def pack(self, **kwargs):
        pass
    def create_image(self, x, y, **kwargs):
        return 0
    def delete(self, item):
        pass
    def itemconfigure(self, item, **kwargs):
        pass

class DummyLabel:
    def __init__(self):
        self.text = ""
    def __setitem__(self, key, value):
        self.text = value

class DummyPliTk:
    def __init__(self, canvas, x, y, cols, rows, tileset, scale):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.cols = cols
        self.rows = rows
    def resize(self, cols, rows):
        self.cols = cols
        self.rows = rows
    def set_tile(self, x, y, index):
        pass


# Simulation funcs
def simulate_game(game, seed=None) -> Player:
    """
    Runs a single simulation of the game without graphics
    and returns the name of the winning bot.
    """
    if seed is not None:
        random.seed(seed)
    canvas = DummyCanvas()
    label = DummyLabel()
    board = DummyBoard(game, canvas, label)
    while board.play():
        pass
    players_sorted = sorted(board.players, key=lambda p: p.gold, reverse=True)
    winner = players_sorted[0]
    return winner


def run_simulations(num_games, game):
    """
    Runs num_games game simulations in separate processes and collects statistics on wins.
    After completion, displays in the console how many times each bot won.
    """
    results: dict[str, (int, int)] = {} # player name : (wins, gold)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(simulate_game, game, seed=i) for i in range(num_games)]
        for future in concurrent.futures.as_completed(futures):
            winner = future.result()
            results[winner.name] = tuple(a + b for a, b in zip(results.get(winner.name, (0, 0)), (1, winner.gold)))

    print("Simulation Results:")
    for bot, wins in results.items():
        print(f"{bot}: {wins[0]} wins, {wins[1]} total gold")


def run_games(num_games=10, filename="game.json"):
    """
    Performs timing measurements and starts the game
    """
    start_time = time.time()
    print(f"Starting {num_games} simulations at {start_time}")
    game = json.loads(Path(filename).read_text())
    run_simulations(num_games, game)
    end_time = time.time()
    print(f"Finished {num_games} simulations at {end_time}")
    print(f"Total time: {(end_time - start_time)} s")

if __name__ == "__main__":
    run_games(NUM_GAMES, GAME_DATA)
