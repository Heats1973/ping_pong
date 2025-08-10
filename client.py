from pygame import *
import socket
import json as js
from threading import Thread

#Pygame settings
Width,height = 800,600

init()
screen = display.set_mode((Width, height))
clock = time.Clock()
display.set_caption("Пінг понг")

#Server 
def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 8080))
            buffer = ""
            game_state = []
            my_id = int(client.recv(24).decode())
            return my_id, game_state, buffer, client
        except:
            pass

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

#Fonts
winner_font = font.Font(None, 72)
main_font = font.Font(None, 36)



#Game
game_over = False
winner = None
you_winner = None

my_id, game_state, buffer, client = connect_to_server()
Thread(target=receive, daemon=True).start()
while True:
    for e in event.get():
        if e.type == QUIT:
            exit
    
    if "countdown" in game_state and game_state["countdown"] > 0:
        screen.fill((0,0,0))
        countdown_text = font.Font(None, 72).render(str(game_state["countdown"], True, (255,255,255)))
        screen.blit(countdown_text, (Width // 2 - 20, height // 2 - 30))
        display.update()
        continue
    
    if "winner" in game_state and game_state["winner"] is not None:
        screen.fill((20,20,20))

        if you_winner is None:
            if game_state["winner"] == my_id:
                you_winner == True
            else:
                you_winner == False
        
        if you_winner:
            text = "You won"
        else:
            text = "You lose"
        
        win_text = winner_font.render(text, True   , (255, 215, 0))
        text_rect = win_text.get_rect(center=(Width // 2, height // 2))
        screen.blit(win_text, text_rect)

        text = winner_font.render("- Restart", True, (255, 215, 0))
        text_rect = win_text.get_rect(center = (Width // 2, height // 2 + 120))
        screen.blit(text,text_rect)

        display.update()
        continue

    if game_state:
        screen.fill((30,30,30))
        draw.rect(screen, (0,255,0), (20, game_state["paddles"][0], 20, 100))
        draw.rect(screen, (0,255,0), (Width - 40, game_state["paddles"][1], 20, 100))
        draw.circle(screen, (0,255,0), (game_state["ball"]["x"], game_state["ball"]["y"], 10))
    