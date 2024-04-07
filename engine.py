import random

class Ship:
    def __init__(self, size):
        self.row = random.randrange(0,9)
        self.col = random.randrange(0,9)
        self.size = size
        self.orientation = random.choice(["h", "v"])
        self.indexes = self.compute_indexes()

    def compute_indexes(self):
        start_index = self.row * 10 + self.col
        if self.orientation == "h":
            return [start_index + i for i in range(self.size)]
        elif self.orientation == "v":
            return [start_index + i*10 for i in range(self.size)]


class Player:
    def __init__(self):
        self.ships = []
        self.search = ["U" for i in range(100)] # "U" znaci neznama policka
        self.place_ships(sizes = [5,4,3,3,2])
        list_of_lists = [ship.indexes for ship in self.ships]
        self.indexes = [index for sublist in list_of_lists for index in sublist]

    def place_ships(self, sizes):
        for size in sizes:
            placed = False
            while not placed:

                # tvorba nove lodi
                ship = Ship(size)

                # kontrola zda je mozna poloha lodi
                possible = True
                for i in ship.indexes:

                    # indexy musi byt < 100
                    if i >= 100:
                        possible = False
                        break

                    # lod musi zustat v jednom radku/sloupci
                    new_row = i // 10
                    new_col = i % 10
                    if new_row != ship.row and new_col != ship.col:
                        possible = False
                        break

                    # lode se nesmi prekryvat
                    for other_ship in self.ships:
                        if i in other_ship.indexes:
                            possible = False
                            break

                # pokladani lode
                if possible:
                    self.ships.append(ship)
                    placed = True

    def show_ships(self):
        indexes = ["-" if i not in self.indexes else "X" for i in range(100)]
        for row in range(10):
            print(" ".join(indexes[(row-1)*10:row*10]))


class Game:
    def __init__(self, human1, human2):
        self.human1 = human1
        self.human2 = human2
        self.player1 = Player()
        self.player2 = Player()
        self.player1_turn = True
        self.computer_turn = True if not self.human1 else False
        self.over = False
        self.result = None
        self.n_shots = 0

    def make_move(self, i):
        #print(i)
        player = self.player1 if self.player1_turn else self.player2
        opponent = self.player2 if self.player1_turn else self.player1
        hit = False

        # trefa "H" nebo ne "M"
        if i in opponent.indexes:
            player.search[i] = "H"
            hit = True

            # je lod potopena? "S"
            for ship in opponent.ships:
                sunk = True
                for i in ship.indexes:
                    if player.search[i] == "U":
                        sunk = False
                        break
                if sunk:
                    for i in ship.indexes:
                        player.search[i] = "S"

        else:
            player.search[i] = "M"

        # kontrola zda hra skoncila
        game_over = True
        for i in opponent.indexes:
            if player.search[i] == "U":
                game_over = False
        self.over = game_over
        self.result = 1 if self.player1_turn else 2

        # zmena hrace
        if not hit:
            self.player1_turn = not self.player1_turn

            # vymena mezi hracem a pocitacem
            if (self.human1 and not self.human2) or (not self.human1 and self.human2):
                self.computer_turn = not self.computer_turn

        # pocitadlo kroku
        self.n_shots += 1

    def random_ai(self):
        search = self.player1.search if self.player1_turn else self.player2.search
        unknown = [i for i, square in enumerate(search) if square == "U"]
        if len(unknown) > 0:
            random_index = random.choice(unknown)
            self.make_move(random_index)

    def basic_ai(self):

        # setup
        search = self.player1.search if self.player1_turn else self.player2.search
        unknown = [i for i, square in enumerate(search) if square == "U"]
        hits = [i for i, square in enumerate(search) if square == "H"]

        # hledani okolo zasazenych lodi
        unknown_with_neighbouring_hits1 = []
        unknown_with_neighbouring_hits2 = []
        for u in unknown:
            if any(u + offset in hits for offset in (1, -1, -10, 10)):
                unknown_with_neighbouring_hits1.append(u)
            if any(u + offset in hits for offset in (2, -2, -20, 20)):
                unknown_with_neighbouring_hits2.append(u)

        # vyber 2. nejblizsi pole "U" kolem trefeneho "H" pole
        for u in unknown:
            if u in unknown_with_neighbouring_hits1 and u in unknown_with_neighbouring_hits2:
                self.make_move(u)
                return

        # vyber nejblizsi pole "U" kolem trefeneho "H" pole
        if len(unknown_with_neighbouring_hits1) > 0:
            self.make_move(random.choice(unknown_with_neighbouring_hits1))
            return

        # vyber pole podle sachovnice
        checker_board = []
        for u in unknown:
            row = u // 10
            col = u % 10
            if (row + col) % 2 == 0:
                checker_board.append(u)
        if len(checker_board) > 0:
            self.make_move(random.choice(checker_board))
            return

        # random vyber
        self.random_ai()