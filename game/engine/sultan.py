import chess

class SultanKhan():

    def __init__(self):
        # enum game_status as defined in chess_displayable.rpy
        self.INCHECK = 1
        self.THREEFOLD = 2
        self.FIFTYMOVES = 3
        self.DRAW = 4
        self.CHECKMATE = 5
        self.STALEMATE = 6

        self.board = None 

    def init_board(self, args):
        fen = args[1]
        self.board = chess.Board(fen=fen)
    def get_piece_at(self, args):
        file_idx, rank_idx = int(args[1]), int(args[2])
        piece = self.board.piece_at(chess.square(file_idx, rank_idx))
        if piece:
            print(piece.symbol())
        else:
            print('None')

    def get_is_capture(self, args):
        move_uci = args[1]
        move = chess.Move.from_uci(move_uci)
        print(self.board.is_capture(move))

    def get_game_status(self):
        if self.board.is_checkmate():
            print(self.CHECKMATE)
            return
        if self.board.is_stalemate():
            print(self.STALEMATE)
            return
        if self.board.can_claim_threefold_repetition():
            print(self.THREEFOLD)
            return
        if self.board.can_claim_fifty_moves():
            print(self.FIFTYMOVES)
            return
        if self.board.is_check():
            print(self.INCHECK)
            return
        print('-1') # no change to game_status
    '''
    AI Logic
    --------------------------------------------------------------------------------
    '''
    
    '''
    --------------------------------------------------------------------------------
    '''
    def get_move(self):
        pass

    def get_legal_moves(self):
        print('#'.join([move.uci() for move in self.board.legal_moves]))

    def push_move(self, args):
        move_uci = args[1]
        move = chess.Move.from_uci(move_uci)
        self.board.push(move)
        print(self.board.turn)

    def pop_move(self):
        # this should not raise an IndexError as the logic has been handled by the caller
        self.board.pop()
        print(self.board.turn)
