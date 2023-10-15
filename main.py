from game_logic.board import Board, Coord
from game_logic.game import Game
from game_logic.player import Player


def main():
    board = Board(10, 10)
    players = [Player(10, 0), Player(10, 1)]
    game = Game(board=board, players=players)
    game.build_warrior(players[0], Coord(0, 0, game.board))
    game.end_turn(players[0])
    game.build_warrior(players[1], Coord(9, 9, game.board))

    print(game)


if __name__ == "__main__":
    main()
