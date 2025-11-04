# chess_gui.py
import pygame
import chess
import sys
from chess_ai import ai_move  # GUI calls the AI wrapper


WIDTH, HEIGHT = 640, 640
SQUARE_SIZE = WIDTH // 8
FPS = 30


LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
SELECT_COLOR = (186, 202, 68)


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess AI (Human vs AI)")
clock = pygame.time.Clock()

# Font for Unicode pieces
font = pygame.font.SysFont("Segoe UI Symbol", 48)

# Unicode piece symbols
PIECE_UNICODE = {
    "P": "♙", "N": "♘", "B": "♗", "R": "♖", "Q": "♕", "K": "♔",
    "p": "♟", "n": "♞", "b": "♝", "r": "♜", "q": "♛", "k": "♚"
}

# --- Draw board ---
def draw_board(screen, board, selected_square=None):
    for row in range(8):
        for col in range(8):
            color = LIGHT if (row + col) % 2 == 0 else DARK
            pygame.draw.rect(screen, color, (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    if selected_square:
        row, col = selected_square
        pygame.draw.rect(screen, SELECT_COLOR, (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    # Draw pieces
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row = 7 - (square // 8)
            col = square % 8
            symbol = PIECE_UNICODE[piece.symbol()]
            text_surface = font.render(symbol, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(col*SQUARE_SIZE + SQUARE_SIZE/2, row*SQUARE_SIZE + SQUARE_SIZE/2))
            screen.blit(text_surface, text_rect)

# --- Main loop ---
def main():
    board = chess.Board()
    selected_square = None
    from_square = None
    running = True

    while running:
        draw_board(screen, board, selected_square)
        pygame.display.flip()
        clock.tick(FPS)

        if board.is_game_over():
            print("Game Over:", board.result())
            pygame.time.wait(2000)
            running = False
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            # Human (White) input
            if board.turn == chess.WHITE and event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                col = pos[0] // SQUARE_SIZE
                row = 7 - (pos[1] // SQUARE_SIZE)
                square = chess.square(col, row)

                if selected_square is None:
                    if board.piece_at(square) and board.piece_at(square).color == chess.WHITE:
                        selected_square = (row, col)
                        from_square = square
                else:
                    to_square = square
                    move = chess.Move(from_square, to_square)
                    if move in board.legal_moves:
                        board.push(move)
                        selected_square = None
                        from_square = None
                    else:
                        selected_square = None
                        from_square = None

        # AI (Black) move
        if board.turn == chess.BLACK and not board.is_game_over():
            pygame.time.wait(300)
            ai_move(board, depth=2)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
