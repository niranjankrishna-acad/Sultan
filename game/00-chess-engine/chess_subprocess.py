import sys
import subprocess
from ..engine.sultan import SultanKHan
import_dir = sys.argv[1]
sys.path.append(import_dir)

# https://python-chess.readthedocs.io/en/v0.23.10/
import chess

def main():
    
    chess_engine = SultanKhan()

    while True:
        line = raw_input()
        # some split token corresponding to that in chess_displayable.rpy
        args = line.split('#')
        if not args:
            continue   

        if args[0] == 'fen':
            chess_engine.init_board(args)
        elif args[0] == 'stockfish_move':
            chess_engine.get_move()
        elif args[0] == 'game_status':
            chess_engine.get_game_status()
        elif args[0] == 'piece_at':
            chess_engine.get_piece_at(args)
        elif args[0] == 'is_capture':
            chess_engine.get_is_capture(args)
        elif args[0] == 'legal_moves':
            chess_engine.get_legal_moves()
        elif args[0] == 'push_move':
            chess_engine.push_move(args)
        elif args[0] == 'pop_move':
            chess_engine.pop_move()

        sys.stdout.flush()



if __name__ == '__main__':
    main()