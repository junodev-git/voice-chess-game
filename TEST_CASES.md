| Test # | Test Title | Test Type | Preconditions | Test Steps | Expected Result | Resources Needed |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Validate square mapping from mouse position | Unit Test | GUI initialized; valid screen size | Call get_square_from_pos((75,75)) | Should return correct square (e.g., b2) | board_renderer.py, unittest |
| 2 | Legal move push validation | Unit Test | Standard board setup | Push e2 to e4 using python-chess API | White pawn moves to e4 | python-chess, unittest |
| 3 | Illegal move rejection | Unit Test | Standard board setup | Try pushing e1 to e5 (invalid) | Move rejected; not in legal_moves | python-chess, unittest |
| 4 | Chess piece image loading | Unit Test | images_svg folder with files | Load SVG, convert to PNG | Image object created for each piece | pygame, cairosvg, unittest |
| 5 | Board rendering validation | Integration Test | Main game loop active; pygame screen initialized | Start game and observe board | Board displays correctly with pieces and colors | main.py, board_renderer.py |
| 6 | Piece selection and highlight logic | Functionality Test | Active chessboard | Click on a piece; verify highlights | Correct squares highlighted and circles shown | main.py, pygame |
| 7 | Checkmate detection | Functionality Test | Board set in checkmate scenario | Push final move; call is_game_over() | Returns True and displays "Game Over" | python-chess, main.py |
| 8 | Test performance on game start | Performance Test | Cold start | Measure time to initialize and draw frame | Start time under 2 seconds | main.py, time module |
| 9 | Voice command parsing for basic move | Unit Test | Voice module initialized | Simulate voice: "Move pawn to e4" | Parsed output generates "e2e4" | command_parser.py, speechrecognition, unittest.mock |
| 10 | Invalid voice command handling | Unit Test | Voice module active; game initialized | Simulate invalid voice: "Fly king to moon" | Error handled gracefully, no crash | command_parser.py, speechrecognition, unittest.mock |
| 11 | Voice command for special move (castling) | Unit Test | Board ready for castling | Simulate voice: "Castle kingside" | Castling move (e1g1) generated and executed | command_parser.py, python-chess, unittest.mock |
