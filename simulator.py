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
def simulate_game(game, seed=None) -> list[Player]:
    """
    Runs a single simulation of the game without graphics.
    and returns the players leaderboard.
    """
    if seed is not None:
        random.seed(seed)
    canvas = DummyCanvas()
    label = DummyLabel()
    board = DummyBoard(game, canvas, label)
    while board.play():
        pass
    players_sorted = sorted(board.players, key=lambda p: p.gold, reverse=True)
    return players_sorted


def run_simulations(num_games, game):
    """
    Runs num_games game simulations in separate processes and collects statistics on all players.
    After completion, displays in the console how many wins and total gold each bot accumulated.
    """
    # results: player name -> (wins, total_gold)
    results: dict[str, tuple[int, int]] = {}

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(simulate_game, game, seed=i) for i in range(num_games)]
        for future in concurrent.futures.as_completed(futures):
            leaderboard: list[Player] = future.result()
            for idx, player in enumerate(leaderboard):
                wins, total_gold = results.get(player.name, (0, 0))
                if idx == 0:
                    wins += 1
                total_gold += player.gold
                results[player.name] = (wins, total_gold)

    sorted_results = sorted(results.items(), key=lambda item: item[1][0], reverse=True)

    print("Simulation Results:")
    for rank, (bot, (wins, total_gold)) in enumerate(sorted_results, start=1):
        print(f"{rank}. {bot}: {wins} wins, {total_gold} total gold")


def run_games(num_games=10, filename="game.json"):
    """
    Performs timing measurements and starts the game.
    """
    start_time = time.time()
    print(f"Starting {num_games} simulations at {start_time}")
    game = json.loads(Path(filename).read_text())
    run_simulations(num_games, game)
    end_time = time.time()
    print(f"Finished {num_games} simulations at {end_time}")
    print(f"Total time: {(end_time - start_time):.2f} s")

if __name__ == "__main__":
    run_games(NUM_GAMES, GAME_DATA)
