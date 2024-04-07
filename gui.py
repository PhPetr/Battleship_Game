from engine import Game

# nastaveni pygame
import pygame
pygame.init()
pygame.font.init()
pygame.display.set_caption("Battleship game")
myfont = pygame.font.SysFont("fresansttf", 100)
font_size = 32
arial = pygame.font.SysFont("arial", font_size)

# globalni promenne
SQ_SIZE = 45
H_MARGIN = SQ_SIZE * 4
V_MARGIN = SQ_SIZE

WIDTH = SQ_SIZE * 10 * 2 + H_MARGIN
HEIGHT = SQ_SIZE * 10 * 2 + V_MARGIN
INDENT = 10
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))

Human1 = True
Human2 = False

# barvy
Grey = (24, 135, 180)
White = (255, 250, 250)
Metal = (170, 170, 170)
Red = (214, 40, 40)
Blue = (0, 72, 110)
Orange = (247, 127, 0)
Colours = {"U": Grey, "M":Blue, "H":Orange, "S":Red}

# vykreslovani mrizky
def draw_grid(player, left = 0, top = 0, search = False):
    for i in range(100):
        x = left + i % 10 * SQ_SIZE
        y = top + i // 10 * SQ_SIZE
        square = pygame.Rect(x, y, SQ_SIZE, SQ_SIZE)
        pygame.draw.rect(SCREEN, White, square, width=3)
        if search:
            x += SQ_SIZE // 2
            y += SQ_SIZE // 2
            pygame.draw.circle(SCREEN, Colours[player.search[i]], (x,y), radius=SQ_SIZE//4)

# vykreslovani lodi na mrizky
def draw_ships(player, left = 0, top = 0):
    for ship in player.ships:
        x = left + ship.col * SQ_SIZE + INDENT
        y = top + ship.row * SQ_SIZE + INDENT
        if ship.orientation == "h":
            width = ship.size * SQ_SIZE - 2*INDENT
            height = SQ_SIZE - 2*INDENT
        else:
            width = SQ_SIZE - 2*INDENT
            height = ship.size * SQ_SIZE - 2*INDENT
        rectangle = pygame.Rect(x, y, width, height)
        pygame.draw.rect(SCREEN, Metal, rectangle, border_radius=15)

# vykreslovani textu

def render_multi_line(screen, text, x, y, font):
    lines = text.splitlines()
    text_height = font.size(lines[0])[1]
    for i, l in enumerate(lines):
        screen.blit(font.render(l, True, White), (x, y + text_height * i))

def load_score(file):
    try:
        with open(file, 'r') as f:
            data = f.read()
            f.close()
            return data
    except FileNotFoundError:
        data = 0
        return data

def write_score(file, value):
    try:
        with open(file, 'w') as w:
            w.write(str(value))
            w.close()
    except FileNotFoundError:
        f = open(file, 'w')
        f.write(str(1))
        f.close()

def store_result():
    if game.result == 1:
        write_score("P1_wins.txt")
    elif game.result == 2:
        write_score("AI_wins.txt")

game = Game(Human1, Human2)

n_wins1 = 0
n_wins2 = 0

# pygame loop
animating = True
pausing = False
while animating:

    # interakce uzivatelem
    for event in pygame.event.get():

        # zavreni okna
        if event.type == pygame.QUIT:
            animating = False

        # kliknuti mysi
        if event.type == pygame.MOUSEBUTTONDOWN and not game.over:
            x,y = pygame.mouse.get_pos()
            if game.player1_turn and x < SQ_SIZE * 10 and y < SQ_SIZE * 10:
                row = y // SQ_SIZE
                col = x // SQ_SIZE
                index = row * 10 + col
                game.make_move(index)
            elif not game.player1_turn and x > WIDTH - SQ_SIZE * 10 and y > SQ_SIZE * 10 + V_MARGIN:
                row = (y - SQ_SIZE * 10 - V_MARGIN) // SQ_SIZE
                col = (x - SQ_SIZE * 10 - H_MARGIN) // SQ_SIZE
                index = row * 10 + col
                game.make_move(index)

        # pauza
        if event.type == pygame.KEYDOWN:

            # ESC na zavreni
            if event.key == pygame.K_ESCAPE:
                animating = False

            # Mezernik pro pauzovani
            if event.key == pygame.K_SPACE:
                pausing = not pausing

            # restart hry [enter]
            if event.key == pygame.K_RETURN:
                if game.result == 1:
                    write_score("P1_wins.txt", n_wins1)
                elif game.result == 2:
                    write_score("AI_wins.txt", n_wins2)
                game = Game(Human1, Human2)

    # execution
    if not pausing:

        # vykresleni pozadi
        SCREEN.fill(Grey)

        # vykresleni hledaci mrizky
        draw_grid(game.player1, search=True)
        draw_grid(game.player2, search=True, left=(WIDTH - H_MARGIN)//2 + H_MARGIN, top=(HEIGHT - V_MARGIN)//2 + V_MARGIN)

        #vykresleni mrizky s lodmi
        draw_grid(game.player1, top=(HEIGHT - V_MARGIN)//2 + V_MARGIN)

        # vykresleni lodi na mrizky
        draw_ships(game.player1, top=(HEIGHT - V_MARGIN)//2 + V_MARGIN)

        n_wins1 = int(load_score("P1_wins.txt"))
        n_wins2 = int(load_score("AI_wins.txt"))
        line = "← make your guesses with\n" \
               "mouse clicks \n" \
               "\n" \
               "Controls:\n" \
               "ESC = quit \n" \
               "SPACE = pause \n" \
               "ENTER = restart \n" \
               "\n" \
               "wins:\n" \
               f"P1: {n_wins1}\n" \
               f"AI: {n_wins2}\n" \
               "AI guesses ↓\n"
        if not game.over: # vykresleni textu
            render_multi_line(SCREEN, line, (WIDTH - H_MARGIN)//2 + H_MARGIN-SQ_SIZE+40, 0, arial)

        # tah pocitace
        if not game.over and game.computer_turn:
            if game.player1_turn:
                game.basic_ai()
            else:
                game.basic_ai()

        # konec hry
        if game.over:
            draw_grid(game.player2, left=(WIDTH - H_MARGIN) // 2 + H_MARGIN) # vykresleni mrizky pro lode pocitace

            draw_ships(game.player2, left=(WIDTH - H_MARGIN) // 2 + H_MARGIN) # vykresleni lodi pocitace

            if game.result == 1:
                n_wins1 += 1
                text = "Player " + str(game.result) + " wins!"
                wid = WIDTH//2 - 240
            elif game.result == 2:
                n_wins2 += 1
                text = "AI wins!"
                wid = WIDTH//2 - 140

            textbox = myfont.render(text, True, Grey, White)
            SCREEN.blit(textbox, (wid, HEIGHT//2 - 20))

        # aktualizovani obrazovky
        pygame.display.flip()