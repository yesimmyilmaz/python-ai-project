
import chess
import chess.polyglot
import time
import math
import random


PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}


PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]
GENERIC_PST = [0]*64


def mirror_square_index(index):
    rank = index // 8
    file = index % 8
    return (7 - rank) * 8 + file

def piece_square_value(piece_type, square, color):
    if piece_type == chess.PAWN:
        table = PAWN_TABLE
    else:
        table = GENERIC_PST
    return table[square] if color == chess.WHITE else table[mirror_square_index(square)]


def evaluate_board(board: chess.Board):
    if board.is_checkmate():
        return -999999 if board.turn == chess.WHITE else 999999
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
        return 0

    material = pst = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            sign = 1 if piece.color == chess.WHITE else -1
            material += sign * PIECE_VALUES[piece.piece_type]
            pst += sign * piece_square_value(piece.piece_type, square, piece.color)

    white_moves = black_moves = 0
    if board.turn == chess.WHITE:
        white_moves = len(list(board.legal_moves))
        board.push(chess.Move.null())
        black_moves = len(list(board.legal_moves))
        board.pop()
    else:
        black_moves = len(list(board.legal_moves))
        board.push(chess.Move.null())
        white_moves = len(list(board.legal_moves))
        board.pop()

    mobility = 10 * (white_moves - black_moves)
    return material + pst + mobility


def score_move_for_ordering(board, move):
    score = 0
    if board.is_capture(move):
        captured = board.piece_at(move.to_square)
        if captured:
            score += 1000 * PIECE_VALUES[captured.piece_type]
    if move.promotion:
        score += 100000
    score += random.randint(0, 10)
    return -score


def minimax_root(board, depth, is_maximizing):
    best_move = None
    best_value = -math.inf if is_maximizing else math.inf
    moves = list(board.legal_moves)
    moves.sort(key=lambda m: score_move_for_ordering(board, m))
    for move in moves:
        board.push(move)
        val = minimax(board, depth - 1, -math.inf, math.inf, not is_maximizing)
        board.pop()
        if is_maximizing and val > best_value:
            best_value = val
            best_move = move
        if not is_maximizing and val < best_value:
            best_value = val
            best_move = move
    return best_move, best_value

def minimax(board, depth, alpha, beta, is_maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)
    moves = list(board.legal_moves)
    moves.sort(key=lambda m: score_move_for_ordering(board, m))
    if is_maximizing:
        max_eval = -math.inf
        for move in moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for move in moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval


def human_vs_ai(depth=3):
    board = chess.Board()
    print("Human (White) vs AI (Black). Enter moves in UCI (e.g., e2e4) or 'quit'.")
    while not board.is_game_over():
        print(board)
        if board.turn == chess.WHITE:
            move_uci = input("Your move: ").strip()
            if move_uci == "quit":
                break
            try:
                move = chess.Move.from_uci(move_uci)
                if move in board.legal_moves:
                    board.push(move)
                else:
                    print("Illegal move. Try again.")
            except:
                print("Invalid format. Use UCI like e2e4, g1f3, etc.")
        else:
            print("AI is thinking...")
            t0 = time.time()
            move, val = minimax_root(board, depth, is_maximizing=True)
            t1 = time.time()
            if move is None:
                print("AI found no move.")
                break
            board.push(move)
            print(f"AI move: {move} (eval {val:.1f}) time {t1-t0:.2f}s")
    print(board)
    print("Game over:", board.result(), board.outcome())

def ai_vs_ai(depth1=2, depth2=2, rounds=1):
    results = {"1-0":0, "0-1":0, "1/2-1/2":0}
    for r in range(rounds):
        board = chess.Board()
        while not board.is_game_over():
            if board.turn == chess.WHITE:
                move, val = minimax_root(board, depth1, is_maximizing=True)
                if move is None:
                    break
                board.push(move)
            else:
                move, val = minimax_root(board, depth2, is_maximizing=True)
                if move is None:
                    break
                board.push(move)
        res = board.result()
        results[res] += 1
        print(f"Round {r+1}/{rounds} result: {res}")
    print("Aggregate:", results)
    return results


def ai_move(board, depth=2):
    """Make a move for AI from GUI."""
    if board.is_game_over():
        return None
    move, _ = minimax_root(board, depth, is_maximizing=(board.turn==chess.WHITE))
    if move:
        board.push(move)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Simple Chess AI with minimax + alpha-beta (python-chess).")
    parser.add_argument("--mode", choices=["human", "ai"], default="human")
    parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--depth2", type=int, default=3)
    parser.add_argument("--rounds", type=int, default=1)
    args = parser.parse_args()

    if args.mode == "human":
        human_vs_ai(depth=args.depth)
    else:
        ai_vs_ai(depth1=args.depth, depth2=args.depth2, rounds=args.rounds)
