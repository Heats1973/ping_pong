from pygame import *
import socket
import json as js
from threading import Thread

# Pygame settings
Width, Height = 800, 600

init()
screen = display.set_mode((Width, Height))
clock = time.Clock()
display.set_caption("Пінг понг")

# Fonts
winner_font = font.Font(None, 72)
main_font = font.Font(None, 36)

# Game variables
game_over = False
winner = None
you_winner = None
game_state = {}
buffer = ""
client = None

# Server connection
def connect_to_server():
    global client
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 9090))
            my_id = int(client.recv(24).decode().strip())
            return my_id
        except:
            pass

# Receiving data
def receive():
    global buffer, game_state, game_over
    while not game_over:
        try:
            data = client.recv(1024).decode()
            buffer += data
            while "\n" in buffer:
                packet, buffer = buffer.split("\n", 1)
                if packet.strip():
                    game_state = js.loads(packet)
        except:
            game_state["winner"] = -1
            break

# Connect and start receiving
my_id = connect_to_server()
Thread(target=receive, daemon=True).start()

# Main game loop
while True:
    for e in event.get():
        if e.type == QUIT:
            game_over = True
            client.close()
            quit()

    screen.fill((0, 0, 0))

    # Countdown display
    if game_state.get("countdown", 0) > 0:
        countdown_text = winner_font.render(str(game_state["countdown"]), True, (255, 255, 255))
        screen.blit(countdown_text, (Width // 2 - 20, Height // 2 - 30))
        display.update()
        clock.tick(60)
        continue

    # Winner display
    if game_state.get("winner") is not None:
        if you_winner is None:
            you_winner = game_state["winner"] == my_id

        screen.fill((20, 20, 20))
        text = "You won" if you_winner else "You lose"
        win_text = winner_font.render(text, True, (255, 215, 0))
        text_rect = win_text.get_rect(center=(Width // 2, Height // 2))
        screen.blit(win_text, text_rect)

        restart_text = winner_font.render("- Restart", True, (255, 215, 0))
        restart_rect = restart_text.get_rect(center=(Width // 2, Height // 2 + 120))
        screen.blit(restart_text, restart_rect)

        display.update()
        clock.tick(60)
        continue

    # Game display
    if game_state:
        screen.fill((30, 30, 30))
        draw.rect(screen, (0, 255, 0), (20, game_state["paddles"].get("0", 250), 20, 100))
        draw.rect(screen, (0, 255, 0), (Width - 40, game_state["paddles"].get("1", 250), 20, 100))
        draw.circle(screen, (0, 255, 0), (game_state["ball"]["x"], game_state["ball"]["y"]), 10)

        score_text = main_font.render(f"{game_state['scores'][0]} : {game_state['scores'][1]}", True, (255, 255, 255))
        screen.blit(score_text, (Width // 2 - 25, 20))

    else:
        waiting_text = main_font.render("Очікування гравців...", True, (255, 255, 255))
        screen.blit(waiting_text, (Width // 2 - 100, 20))

    display.update()
    clock.tick(60)

    # Controls
    keys = key.get_pressed()
    if keys[K_w]:
        client.send(b"UP")
    elif keys[K_s]:
        client.send(b"DOWN")
