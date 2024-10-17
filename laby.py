import pygame
import sys
import random
import heapq

# Initialisation de Pygame
pygame.init()

# Dimensions de l'écran
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

# Taille des cases du labyrinthe
TILE_SIZE = 40

# Dimensions du labyrinthe
GRID_ROWS = 15
GRID_COLS = 20

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

def main():
    global screen
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
            move_along_path(character_rect, character_path, offset_x, offset_y)
            draw_path_trail()  # Dessiner les points rouges laissés sur le chemin

        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
