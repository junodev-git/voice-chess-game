import pygame
import chess
import sys
import os
import speech_recognition as sr
import keyboard
import threading
from tkinter import Tk, filedialog
import cairosvg
from io import BytesIO

# boardSize
WIDTH, HEIGHT = 600, 600
BOARD_SIZE = 8
SQUARE_SIZE = WIDTH // BOARD_SIZE

# boardColor
WHITE_COLOR = (238, 238, 210)
BLACK_COLOR = (118, 150, 86)
HIGHLIGHT_COLOR = (246, 246, 130)
LEGAL_MOVE_COLOR = (186, 202, 68, 150)

# upLoad Chess Piece Images
PIECE_IMAGES = {}
DEFAULT_IMAGE_DIR = "images_svg"  # Default folder for SVG images
EXPECTED_FILES = {
    'P': 'wP.svg', 'N': 'wN.svg', 'B': 'wB.svg', 'R': 'wR.svg', 'Q': 'wQ.svg', 'K': 'wK.svg',
    'p': 'bP.svg', 'n': 'bN.svg', 'b': 'bB.svg', 'r': 'bR.svg', 'q': 'bQ.svg', 'k': 'bK.svg'
}

def load_piece_images(screen, image_dir=DEFAULT_IMAGE_DIR):
    """Loads chess piece images (SVG) from the specified directory. Prompts for upload if missing."""
    global PIECE_IMAGES
    PIECE_IMAGES = {}
    os.makedirs(image_dir, exist_ok=True)  # Ensures the directory exists

    target_size = (int(SQUARE_SIZE * 0.8), int(SQUARE_SIZE * 0.8))

    for piece_symbol, filename in EXPECTED_FILES.items():
        filepath = os.path.join(image_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'rb') as f:
                    svg_data = f.read()
                png_data = cairosvg.svg2png(bytestring=svg_data, output_width=target_size[0], output_height=target_size[1])
                img = pygame.image.load(BytesIO(png_data)).convert_alpha()
                PIECE_IMAGES[piece_symbol] = img
            except FileNotFoundError:
                print(f"Error: SVG file not found at {filepath}")
                PIECE_IMAGES[piece_symbol] = None
            except cairosvg.SVGParseError as e:
                print(f"Error parsing SVG file {filepath}: {e}")
                PIECE_IMAGES[piece_symbol] = None
            except pygame.error as e:
                print(f"Error loading rendered PNG for {filepath}: {e}")
                PIECE_IMAGES[piece_symbol] = None
        else:
            print(f"SVG file not found: {filepath}")
            print(f"Please upload an SVG image for the {piece_symbol} ({filename})")
            uploaded_path = upload_piece_image(piece_symbol, screen, initial_dir=image_dir, default_name=filename, filetypes=[("SVG files", "*.svg"), ("All files", "*.*")])
            if uploaded_path:
                try:
                    with open(uploaded_path, 'rb') as f:
                        svg_data = f.read()
                    png_data = cairosvg.svg2png(bytestring=svg_data, output_width=target_size[0], output_height=target_size[1])
                    img = pygame.image.load(BytesIO(png_data)).convert_alpha()
                    PIECE_IMAGES[piece_symbol] = img
                    # Optionally save the uploaded SVG with the expected filename
                    try:
                        import shutil
                        shutil.copyfile(uploaded_path, filepath)
                        print(f"Uploaded SVG saved as: {filepath}")
                    except Exception as e:
                        print(f"Error saving uploaded SVG: {e}")
                except FileNotFoundError:
                    print(f"Error: Uploaded SVG file not found.")
                    PIECE_IMAGES[piece_symbol] = None
                except cairosvg.SVGParseError as e:
                    print(f"Error parsing uploaded SVG file: {e}")
                    PIECE_IMAGES[piece_symbol] = None
                except pygame.error as e:
                    print(f"Error loading rendered PNG for uploaded SVG: {e}")
                    PIECE_IMAGES[piece_symbol] = None
                else:
                    print(f"No SVG image uploaded for {piece_symbol}.")
                    PIECE_IMAGES[piece_symbol] = None

def upload_piece_image(piece_symbol, screen, initial_dir=None, default_name=None, filetypes=None):
    """Opens a file dialog to upload an image for a specific piece."""
    root = Tk()
    root.withdraw()  # Hide the main tkinter window
    if filetypes is None:
        filetypes=[("All files", "*.*")]
    file_path = filedialog.askopenfilename(
        title=f"Upload image for {piece_symbol}",
        filetypes=filetypes,
        initialdir=initial_dir,
        defaultextension=".svg" if "*.svg" in [ft[1] for ft in filetypes] else "",
        initialfile=default_name
    )
    return file_path

# helperFunctions
def get_square_from_pos(pos):
    x, y = pos
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        col = x // SQUARE_SIZE
        row = y // SQUARE_SIZE
        return chess.square(col, 7 - row)
    return None

def get_piece_color(piece_symbol):
    return chess.WHITE if piece_symbol.isupper() else chess.BLACK

# drawBoard
def draw_board(screen):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = WHITE_COLOR if (row + col) % 2 == 0 else BLACK_COLOR
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            # Add location numbers
            font = pygame.font.Font(None, 20)
            rank = 8 - row
            file = chr(ord('a') + col)
            text = font.render(f"{file}{rank}", True, (50, 50, 50)) # Dark grey color
            text_rect = text.get_rect(topleft=(col * SQUARE_SIZE + 5, row * SQUARE_SIZE + 5))
            screen.blit(text, text_rect)

def draw_pieces(screen, board):
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            symbol = piece.symbol()
            if symbol in PIECE_IMAGES and PIECE_IMAGES[symbol]:
                img = PIECE_IMAGES[symbol]
                row, col = 7 - chess.square_rank(square), chess.square_file(square)
                img_rect = img.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2,
                                                row * SQUARE_SIZE + SQUARE_SIZE // 2))
                screen.blit(img, img_rect)
            elif symbol in PIECE_IMAGES and PIECE_IMAGES[symbol] is None:
                pygame.draw.circle(screen, (255, 0, 0), (col * SQUARE_SIZE + SQUARE_SIZE // 2,
                                                       7 - chess.square_rank(square) * SQUARE_SIZE + SQUARE_SIZE // 2), 10)
            else:
                print(f"Warning: Image mapping not found for piece symbol '{symbol}'")

def draw_highlights(screen, selected_square, legal_moves):
    if selected_square is not None:
        row, col = 7 - chess.square_rank(selected_square), chess.square_file(selected_square)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR,
                         (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 5)

        for move in legal_moves:
            dest_row, dest_col = 7 - chess.square_rank(move.to_square), chess.square_file(move.to_square)
            center_x = dest_col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = dest_row * SQUARE_SIZE + SQUARE_SIZE // 2
            surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(surface, LEGAL_MOVE_COLOR, (SQUARE_SIZE // 2, SQUARE_SIZE // 2), SQUARE_SIZE // 4)
            screen.blit(surface, (dest_col * SQUARE_SIZE, dest_row * SQUARE_SIZE))


# Function to capture voice input from the user
def listen_for_move(board):
    color = "White" if board.turn == chess.WHITE else "Black"
    print(f"{color}, your move. Please speak...")

    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)

        # Added voice timeout
        # Must finish before shutdown
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            return None

    try:
        command = r.recognize_google(audio)
        return command.lower()
    except sr.UnknownValueError:
        if listening:
            print("Could not understand the audio.")
    except sr.RequestError:
        if listening:
            print("Speech recognition service is unavailable.")
    return None

# Parses a spoken command into a valid chess move
def parse_voice_move(command, board):
    piece_names = {
        "pawn": chess.PAWN, "knight": chess.KNIGHT, "bishop": chess.BISHOP,
        "rook": chess.ROOK, "queen": chess.QUEEN, "king": chess.KING
    }

    try:
        for name, p_type in piece_names.items():
            if name in command:
                to_square = command.split("to")[-1].strip().replace(" ", "")
                to_sq = chess.parse_square(to_square)
                for move in board.legal_moves:
                    piece = board.piece_at(move.from_square)
                    if piece and piece.piece_type == p_type and move.to_square == to_sq:
                        return move
    except Exception as e:
        print("Error parsing move:", e)
    return None

# Continuously listens for voice input while listening is enabled
def listen_loop(board):
    global listening
    while listening and not board.is_game_over():
        command = listen_for_move(board)
        if not listening or board.is_game_over():
            break
        if command:
            move = parse_voice_move(command, board)
            if move and move in board.legal_moves:
                board.push(move)
            else:
                print("⚠️ Invalid or illegal move.")


# Global variables used to control voice listening state and threading
listening = False
listening_thread = None

# Main Gameplay
def main():

    # Added threading for voice toggle and listening
    global listening, listening_thread

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("chessSpeak +")
    clock = pygame.time.Clock()

    # Load initial piece images (SVG), prompt for upload if missing
    load_piece_images(screen)

    board = chess.Board()
    selected_square = None
    legal_moves_for_selected = []
    running = True

    upload_button_rect = pygame.Rect(10, HEIGHT - 50, 180, 40) # Adjusted button width
    upload_font = pygame.font.Font(None, 24)


    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                global listening
                listening = False

            # Toggles voice functionality
            if keyboard.is_pressed('space'):
                listening = not listening
                print("Listening ON" if listening else "Listening OFF")

                if listening:
                    if not listening_thread or not listening_thread.is_alive():
                        listening_thread = threading.Thread(target=listen_loop, args=(board,))
                        listening_thread.start()
                else:

                    pass

                while keyboard.is_pressed('space'):  # prevent multiple toggles on hold
                    pass

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked_square = get_square_from_pos(pos)

                if upload_button_rect.collidepoint(pos):
                    upload_prompt = "Enter piece symbol to re-upload (e.g., P, n, Q):"
                    piece_to_upload = input(upload_prompt).strip()
                    if piece_to_upload in EXPECTED_FILES:
                        filepath = os.path.join(DEFAULT_IMAGE_DIR, EXPECTED_FILES[piece_to_upload])
                        uploaded_path = upload_piece_image(piece_to_upload, screen, initial_dir=DEFAULT_IMAGE_DIR, default_name=EXPECTED_FILES[piece_to_upload], filetypes=[("SVG files", "*.svg"), ("All files", "*.*")])
                        if uploaded_path:
                            try:
                                with open(uploaded_path, 'rb') as f:
                                    svg_data = f.read()
                                png_data = cairosvg.svg2png(bytestring=svg_data, output_width=(int(SQUARE_SIZE * 0.8)), output_height=(int(SQUARE_SIZE * 0.8)))
                                img = pygame.image.load(BytesIO(png_data)).convert_alpha()
                                PIECE_IMAGES[piece_to_upload] = img
                                try:
                                    import shutil
                                    shutil.copyfile(uploaded_path, filepath)
                                    print(f"Uploaded SVG saved as: {filepath}")
                                except Exception as e:
                                    print(f"Error saving uploaded SVG: {e}")
                            except (FileNotFoundError, cairosvg.SVGParseError, pygame.error) as e:
                                print(f"Error processing uploaded SVG: {e}")
                                PIECE_IMAGES[piece_to_upload] = None
                    else:
                        print(f"Invalid piece symbol: {piece_to_upload}")
                    continue

                # HOW TO MOVE PIECES (remains mostly the same)
                if clicked_square is not None:
                    if selected_square is None:
                        piece = board.piece_at(clicked_square)
                        if piece and get_piece_color(piece.symbol()) == board.turn:
                            selected_square = clicked_square
                            legal_moves_for_selected = [m for m in board.legal_moves if m.from_square == selected_square]
                        else:
                            selected_square = None
                            legal_moves_for_selected = []
                    else:
                        move = chess.Move(from_square=selected_square, to_square=clicked_square)
                        piece = board.piece_at(selected_square)
                        if piece and piece.piece_type == chess.PAWN and (chess.square_rank(clicked_square) == 0 or chess.square_rank(clicked_square) == 7):
                            move.promotion = chess.QUEEN
                        if move in board.legal_moves:
                            board.push(move)
                            selected_square = None
                            legal_moves_for_selected = []
                        elif clicked_square == selected_square:
                            selected_square = None
                            legal_moves_for_selected = []
                        else:
                            new_piece = board.piece_at(clicked_square)
                            if new_piece and get_piece_color(new_piece.symbol()) == board.turn:
                                selected_square = clicked_square
                                legal_moves_for_selected = [m for m in board.legal_moves if m.from_square == selected_square]
                            else:
                                selected_square = None
                                legal_moves_for_selected = []

        # boardDraw
        draw_board(screen)
        draw_highlights(screen, selected_square, legal_moves_for_selected)
        draw_pieces(screen, board)

        # Should probably delete this section of code
        # uploadbutton
        #pygame.draw.rect(screen, (200, 200, 200), upload_button_rect)
        #upload_text = upload_font.render("Upload SVG Image", True, (0, 0, 0))
        #text_rect = upload_text.get_rect(center=upload_button_rect.center)
        #screen.blit(upload_text, text_rect)

        pygame.display.flip()

        # checkMate
        if board.is_game_over():
            print("\n" + "=" * 10 + " GAME OVER " + "=" * 10)
            print(f"Result: {board.result()}")

            listening = False
            if listening_thread and listening_thread.is_alive():
                listening_thread.join(timeout=1)

            pygame.time.wait(2000)
            running = False

        clock.tick(30)

    # Stops background audio from running during shutdown
    if listening_thread and listening_thread.is_alive():
        listening_thread.join()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
