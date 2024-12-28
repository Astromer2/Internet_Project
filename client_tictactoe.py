import socket

HOST = '127.0.0.1'  # Replace with the server's IP if needed
PORT = 5000  # Replace with the server's port if needed


def connect_to_server(host, port):
    """
    Establishes a connection to the server and allows continuous communication.
    """
    # Step 1: Create a socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Step 2: Connect to the server
    client_socket.connect((host, port))
    print(f"[CONNECTED] Successfully connected to {host}:{port}")

    try:
        # game_running = False   Flag to indicate if the game is active

        while True:
            # Step 1: Take input from the user
            message = input(
                "write 'start' to begin the game, 'quit' to disconnect, or any other message to communicate:\n")
            client_socket.send(message.encode('utf-8'))

            # Step 2: Handle 'quit' command
            if message.lower() == 'quit':
                print("[DISCONNECT] Closing connection.")
                break

            # Step 3: Receive server response
            response = client_socket.recv(1024).decode('utf-8')
            print(f"[SERVER RESPONSE] {response}")

            # Step 4: Handle 'start' command
            if message.lower() == 'start':
                print("[GAME START] Starting the game...")
                # game_running = True
                play_game(client_socket)  # Enter the game loop
                # game_running = False   Exit the game loop
                print("[GAME END] You can continue communicating or quit.")

    except ConnectionResetError:
        print("[ERROR] Server disconnected unexpectedly.")
    finally:
        client_socket.close()


def send_move(client_socket, move):
    """
    Sends the player's move to the server.
    """
    try:
        client_socket.send(move.encode('utf-8'))
        print(f"[SENT] Move sent to server: {move}")
    except BrokenPipeError:
        print("[ERROR] Unable to send move. Connection to the server is broken.")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred while sending move: {e}")


def receive_game_update(client_socket):
    """
    Receives updates from the server.
    """
    try:
        update = client_socket.recv(1024).decode('utf-8')
        if not update:
            print("[ERROR] Lost connection to the server.")
            return None
        return update
    except ConnectionResetError:
        print("[ERROR] Connection to the server was reset.")
        return None


def play_game(client_socket):
    """
    Handles the main game loop when the game is active.
    """
    print("[INFO] Entering the game loop...")
    while True:
        # Step 1: Receive the current game state from the server
        update = receive_game_update(client_socket)
        if update is None:
            print("[INFO] Closing the game due to server connection loss.")
            break

        # Step 2: Process the server's update
        try:
            game_data = eval(update)  # Convert the response string to a Python dictionary
            game_state = game_data["board"]
            status = game_data["status"]
            winner = game_data.get("winner")
            next_turn = game_data["next_turn"]

            # Step 3: Display the updated game board
            display_board(game_state)

            # Step 4: Check game status
            if status == "win":
                print(f"[GAME OVER] {winner} wins!")
                break
            elif status == "draw":
                print("[GAME OVER] It's a draw!")
                break

            # Step 5: Handle the player's turn
            if next_turn == "X":  # Adjust this logic to match the client's player marker
                move = input("Enter your move (row, column or 'end' to stop the game: ")
                if move.lower() == "end":
                    print("[GAME END] Exiting the game loop...")
                    break
                send_move(client_socket, move)
            else:
                print("[WAIT] Waiting for the opponent's move...")

        except Exception as e:
            print(f"[ERROR] Failed to process game state: {e}")
            break


def display_board(game_state):
    """
    Displays the current game board in a text-based format.

    Args:
        game_state (list of list): A 3x3 matrix representing the Tic-Tac-Toe board.
                                   Each cell can contain 'X', 'O', or '' (empty string).
    """
    print("\nCurrent Board:")
    for row in game_state:
        print(" | ".join(cell if cell else " " for cell in row))
        print("-" * 9)


# Direct execution block
if __name__ == "__main__":
    connect_to_server(HOST, PORT)