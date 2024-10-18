import pygame
import sys
import random
import heapq

# Initialisation de Pygame
pygame.init()

# Obtenir la taille de l'écran
screen_info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = screen_info.current_w, screen_info.current_h

# Taille des cases du labyrinthe
TILE_SIZE = 40  # Vous pouvez ajuster cette valeur si nécessaire

# Dimensions du labyrinthe (nombre de cases ajusté pour s'adapter à l'écran)
GRID_ROWS = SCREEN_HEIGHT // TILE_SIZE
GRID_COLS = SCREEN_WIDTH // TILE_SIZE

# Charger les sprites
map_image = pygame.image.load('map.jpg')
character_image = pygame.image.load('arthur.png')
treasure_image = pygame.image.load('treasure.png')

# Charger l'image des murs
wall_image = pygame.image.load('mur.jpg')
# Redimensionner l'image des murs à la taille d'une case
wall_image = pygame.transform.scale(wall_image, (TILE_SIZE, TILE_SIZE))

# Charger l'image du chemin (herbe)
grass_image = pygame.image.load('grass.png')
# Redimensionner l'image du chemin à la taille d'une case
grass_image = pygame.transform.scale(grass_image, (TILE_SIZE, TILE_SIZE))

# Charger l'image de la pièce
coin_image = pygame.image.load('coin.png')
# Redimensionner l'image de la pièce à la taille d'une case
coin_image = pygame.transform.scale(coin_image, (TILE_SIZE, TILE_SIZE))

# Redimensionner le personnage et le trésor pour qu'ils s'adaptent à la taille des cases
character_image = pygame.transform.scale(character_image, (TILE_SIZE, TILE_SIZE))
treasure_image = pygame.transform.scale(treasure_image, (TILE_SIZE, TILE_SIZE))

# Rectangle du personnage
character_rect = character_image.get_rect()

# Position initiale et cible sur la carte
start_map_pos = (150, 250)
target_map_pos = (250, 500)
character_rect.topleft = start_map_pos

# Liste pour stocker les positions où des points rouges doivent être affichés
path_trail = []

# Liste des positions des pièces
coins_positions = []

# Initialiser le score
score = 0



# Fonction pour afficher un message au centre de l'écran
def display_message():
    # Charger une police de style pixel art
    pixel_font = pygame.font.Font("PressStart2P.ttf", 30)  # Assurez-vous d'avoir la police .ttf dans le répertoire

    # Définir les deux lignes du message
    line1 = "Arthur a trouvé le trésor!"
    line2 = "Il peut maintenant payer sa note à la taverne."

    # Générer le texte pour chaque ligne
    text1 = pixel_font.render(line1, True, (255, 255, 0))  # Texte en jaune pour la première ligne
    text2 = pixel_font.render(line2, True, (255, 255, 0))  # Texte en jaune pour la deuxième ligne

    # Obtenir les rectangles pour centrer les lignes
    text1_rect = text1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))  # Première ligne un peu plus haut
    text2_rect = text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))  # Deuxième ligne en dessous

    # Définir la taille du cadre (marges autour du texte)
    padding_x, padding_y = 50, 75
    rect_width = max(text1_rect.width, text2_rect.width) + padding_x * 2
    rect_height = text1_rect.height + text2_rect.height + padding_y * 2
    rect_x = min(text1_rect.x, text2_rect.x) - padding_x
    rect_y = text1_rect.y - padding_y

    # Dessiner le rectangle avec un fond blanc transparent
    s = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)  # Créer une surface transparente
    s.fill((255, 255, 255, 128))  # Remplir avec du blanc transparent (alpha=128)
    screen.blit(s, (rect_x, rect_y))  # Dessiner le fond transparent

    # Dessiner le cadre
    pygame.draw.rect(screen, (0, 0, 0), (rect_x, rect_y, rect_width, rect_height), 5)  # Cadre noir de 5px

    # Afficher les deux lignes de texte par-dessus
    screen.blit(text1, text1_rect)
    screen.blit(text2, text2_rect)

# Fonction pour générer un labyrinthe avec un chemin garanti
def generate_maze(rows, cols):
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    stack = []
    start = (1, 1)
    maze[start[0]][start[1]] = 0
    stack.append(start)

    while stack:
        current = stack[-1]
        x, y = current
        neighbors = []

        # Directions possibles : gauche, droite, haut, bas
        directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 1 <= nx < rows - 1 and 1 <= ny < cols - 1 and maze[nx][ny] == 1:
                neighbors.append((nx, ny))

        if neighbors:
            next_cell = random.choice(neighbors)
            stack.append(next_cell)
            maze[next_cell[0]][next_cell[1]] = 0

            # Supprimer le mur entre les cellules
            wall_x = (x + next_cell[0]) // 2
            wall_y = (y + next_cell[1]) // 2
            maze[wall_x][wall_y] = 0
        else:
            stack.pop()

    return maze

# Générer un labyrinthe
maze = generate_maze(GRID_ROWS, GRID_COLS)

# Placer le trésor dans une case accessible (non mur)
def place_treasure(maze):
    while True:
        x = random.randint(1, GRID_ROWS - 2)
        y = random.randint(1, GRID_COLS - 2)
        if maze[x][y] == 0:  # Trouver une case qui n'est pas un mur
            return (x, y)

treasure = place_treasure(maze)

# Fonction pour placer des pièces aléatoirement sur des cases accessibles
def place_coins(maze, num_coins):
    positions = []
    while len(positions) < num_coins:
        x = random.randint(1, GRID_ROWS - 2)
        y = random.randint(1, GRID_COLS - 2)
        if maze[x][y] == 0 and (x, y) not in positions and (x, y) != treasure:
            positions.append((x, y))
    return positions

# Générer des pièces
coins_positions = place_coins(maze, 10)  # Placer 10 pièces aléatoirement

# Fonction pour déplacer le personnage sur la carte
def move_character_on_map():
    if character_rect.x < target_map_pos[0]:
        character_rect.x += 2
    elif character_rect.x > target_map_pos[0]:
        character_rect.x -= 2

    if character_rect.y < target_map_pos[1]:
        character_rect.y += 2
    elif character_rect.y > target_map_pos[1]:
        character_rect.y -= 2

    # Retourne True si le personnage a atteint la position cible
    return character_rect.topleft == target_map_pos

# Fonction pour dessiner le labyrinthe avec l'image des murs et du chemin (herbe)
def draw_maze(offset_x, offset_y):
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            cell = maze[row][col]
            x = offset_x + col * TILE_SIZE
            y = offset_y + row * TILE_SIZE
            if cell == 1:
                # Utiliser l'image des murs
                screen.blit(wall_image, (x, y))
            else:
                # Utiliser l'image du chemin (herbe)
                screen.blit(grass_image, (x, y))

# Fonction A* pour trouver le chemin le plus court
def a_star(maze, start, goal):
    rows, cols = len(maze), len(maze[0])
    frontier = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == goal:
            break

        neighbors = [
            (current[0] + 1, current[1]),
            (current[0] - 1, current[1]),
            (current[0], current[1] + 1),
            (current[0], current[1] - 1)
        ]

        for next in neighbors:
            x, y = next
            if 0 <= x < rows and 0 <= y < cols and maze[x][y] == 0:
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + abs(goal[0] - x) + abs(goal[1] - y)
                    heapq.heappush(frontier, (priority, next))
                    came_from[next] = current

    # Reconstruire le chemin
    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from.get(current)
        if current is None:
            return None
    path.append(start)
    path.reverse()
    return path

# Trouver le chemin le plus court entre l'entrée et le trésor
entrance = (1, 1)
path = a_star(maze, entrance, treasure)

# Vérification si un chemin a été trouvé
if path is None:
    print("Aucun chemin n'a été trouvé entre l'entrée et le trésor.")
    pygame.quit()
    sys.exit()

# Déplacer le personnage le long du chemin et laisser des points rouges
def move_along_path(character_rect, path, offset_x, offset_y):
    if path:
        next_tile = path.pop(0)
        # Ajouter la position actuelle à la liste des points rouges
        path_trail.append((offset_x + next_tile[1] * TILE_SIZE + TILE_SIZE // 2, offset_y + next_tile[0] * TILE_SIZE + TILE_SIZE // 2))
        character_rect.topleft = (offset_x + next_tile[1] * TILE_SIZE, offset_y + next_tile[0] * TILE_SIZE)

# Fonction pour dessiner les points rouges sur le chemin parcouru
def draw_path_trail():
    for point in path_trail:
        pygame.draw.circle(screen, (255, 0, 0), point, 5)  # Dessiner un petit cercle rouge

# Fonction pour dessiner les pièces
def draw_coins(offset_x, offset_y):
    for coin in coins_positions:
        coin_x = offset_x + coin[1] * TILE_SIZE
        coin_y = offset_y + coin[0] * TILE_SIZE
        screen.blit(coin_image, (coin_x, coin_y))

# Fonction pour ramasser les pièces si le personnage passe dessus
def collect_coins(character_rect, offset_x, offset_y):
    global coins_positions, score
    collected = []
    for coin in coins_positions:
        coin_rect = pygame.Rect(offset_x + coin[1] * TILE_SIZE, offset_y + coin[0] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        if character_rect.colliderect(coin_rect):
            collected.append(coin)
            score += 10  # Incrémenter le score pour chaque pièce ramassée
    # Retirer les pièces ramassées
    coins_positions = [coin for coin in coins_positions if coin not in collected]

# Fonction pour afficher le score
def draw_score():
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, (255, 255, 0))
    screen.blit(score_text, (10, 10))

# Vérifier si Arthur a trouvé le trésor
def check_treasure_found(character_rect, offset_x, offset_y):
    treasure_rect = pygame.Rect(offset_x + treasure[1] * TILE_SIZE, offset_y + treasure[0] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    return character_rect.colliderect(treasure_rect)

def main():
    global screen

    # Demander à l'utilisateur de choisir entre fenêtré ou plein écran
    mode = input("Voulez-vous démarrer en mode plein écran ? (o/n) : ")

    if mode.lower() == 'o':
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    pygame.display.set_caption("Carte et Labyrinthe")

    game_state = "map"  # Initialement sur la carte
    character_path = path[:]  # Cloner le chemin pour l'utiliser dans le labyrinthe
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))

        if game_state == "map":
            screen.blit(map_image, (0, 0))
            screen.blit(character_image, character_rect)

            # Déplacer le personnage sur la carte
            if move_character_on_map():
                game_state = "labyrinth"

        elif game_state == "labyrinth":
            labyrinth_width = GRID_COLS * TILE_SIZE
            labyrinth_height = GRID_ROWS * TILE_SIZE
            offset_x = (SCREEN_WIDTH - labyrinth_width) // 2
            offset_y = (SCREEN_HEIGHT - labyrinth_height) // 2

            draw_maze(offset_x, offset_y)
            screen.blit(treasure_image, (offset_x + treasure[1] * TILE_SIZE, offset_y + treasure[0] * TILE_SIZE))
            screen.blit(character_image, character_rect)
            draw_coins(offset_x, offset_y)  # Dessiner les pièces
            collect_coins(character_rect, offset_x, offset_y)  # Ramasser les pièces
            move_along_path(character_rect, character_path, offset_x, offset_y)
            draw_path_trail()  # Dessiner les points rouges laissés sur le chemin
            draw_score()  # Afficher le score

            # Vérifier si Arthur a trouvé le trésor
            if check_treasure_found(character_rect, offset_x, offset_y):
                # Afficher le message et les confettis
                display_message()
                pygame.display.flip()

        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
