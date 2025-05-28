import pygame
from Src.Class.bird import Player
from Src.Class.pipe import Tube
from Src.Class.back import background_image
from Src.constant import WINDOW_HEIGHT, WINDOW_WIDTH, FPS
from Src.color import WHITE, RED, BLUE, BLACK


# Global variables
max_score = []
game_quit = True
int_try = 0
v_delta = 200
x_velocity = 0


# Initialize Pygame
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Flippy Bird')
font = pygame.font.Font(None, 36)



def distance_between_points(point1, point2):
    """
    Calculate the Euclidean distance between two points in a 2D Cartesian coordinate system.

    Parameters:
        - point1 (tuple of two floats/integers): The coordinates of the first point as a tuple (x1, y1).
        - point2 (tuple of two floats/integers): The coordinates of the second point as a tuple (x2, y2).

    Returns:
        - float: The Euclidean distance between the two points.
    """
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

def load_screen():
    """
    Load background images onto the screen.
    """
    screen.blit(background_image, (0, 0))
    screen.blit(background_image, (288, 0)) 

def handle_command(player: Player):
    """Handle user input events.
    
    Args:
        - player (Player): The player object controlled by user input.
    
    Returns:
        bool: True if the game is still running, False if the user quits.
    """
    is_alive = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_alive = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.flap_up()
            if event.key == pygame.K_1:
                pygame.quit()
    return is_alive

def get_collidate(player: Player, tube_list: list[Tube], tube_index: int):
    """Check collision between player and tubes.
    
    Args:
        - player (Player): The player object.
        - tube_list (list[Tube]): List of Tube objects.
        - tube_index (int): Index of the current tube in the list.
    
    Returns:
        bool: True if collision occurs, False otherwise.
    """
    player_rect = player.get_rect()
    tube_rect = tube_list[tube_index].get_rect()
    tube_rectreverse = tube_list[tube_index].get_rect_reverse()

    if player_rect.colliderect(tube_rect) or player_rect.colliderect(tube_rectreverse):
        return True
    
    return False

def update(dt, player: Player, tube_list: list[Tube]):
    """Update game entities based on delta time.
    
    Args:
        - dt (float): Time elapsed since the last update.
        - player (Player): The player object.
        - tube_list (list[Tube]): List of Tube objects.
    """
    player.update(dt)

    for tube in tube_list:
        if not tube.offscreen():
            tube.update(dt)

def collidate_player(player: Player, tube_list: list[Tube], tube_index: int):
    """Check if player collides with any tubes.
    
    Args:
        - player (Player): The player object.
        - tube_list (list[Tube]): List of Tube objects.
        - tube_index (int): Index of the current tube in the list.
    
    Returns:
        bool: True if player collides, False otherwise.
    """
    is_alive = True

    if get_collidate(player, tube_list, tube_index-1):
        max_score.append(tube_index)
        is_alive = False

    if tube_index > 2:
        if get_collidate(player, tube_list, tube_index-2):
            max_score.append(tube_index)
            is_alive = False

    return is_alive

def increment_diff(player: Player, tube_list: list[Tube]):
    """
    Adjust the difficulty of the game by modifying the velocity parameters based on player interactions and tube positions.

    Parameters:
        - player (Player): The player object, which typically contains attributes such as score, position, etc.
        - tube_list (list of Tube): A list of Tube objects, where each Tube represents an obstacle in the game.
    """

    global v_delta, x_velocity
    
    # Variabili massime
    max_v_delta = 110
    max_y_velocity = 20
    max_gravity = 8
    max_jump_strength = -24

    # Aggiornamento velocita di tutti i tubi
    for i in range(len(tube_list)):
        if tube_list[-1].velocity_y > max_y_velocity:
            tube_list[i].velocity_y += 5
    x_velocity = tube_list[-1].velocity_y - 15
    v_delta -= 5

    # Aggiornaemento velocita player
    player.gravity -= 0.5
    player.jump_strength += 2

    if player.jump_strength > max_jump_strength:
        player.jump_strength = max_jump_strength

    if player.gravity < max_gravity:
        player.gravity = max_gravity

    if v_delta < max_v_delta:
        v_delta = max_v_delta


    #print("J: ", player.jump_strength,  "G: ", player.gravity, "X_V: ", x_velocity, "V_D: ", v_delta, "Y_V: ", tube_list[-1].velocity_y)

def update_text_screen(score):
    """Update and display text on the screen.
    
    Args:
        score (int): Current score of the game.
    """
    try_text = font.render(f'Try: {int_try}', True, (255, 255, 255))
    screen.blit(try_text, (10, 10)) 

    score_text = font.render(f'Score: {score}', True, (255, 255, 255))
    screen.blit(score_text, (10, 35)) 

    if len(max_score) > 0:
        max_score_text = font.render(f'Max Score: {max(max_score)}', True, (255, 255, 255))
        screen.blit(max_score_text, (10, 60)) 

def calculate_distances_and_draw_lines(player, tube_list, score):
    """
    Calculate distances between specified points of the player and the tubes, and draw lines on the screen.

    Parameters:
        - player (Player): The player object.
        - tube_list (list of Tube): A list of Tube objects.
        - score (int): The current score, used to index the tube_list.

    Returns:
        - list of float: A list of distances calculated between specified points of the player and tubes.
    """
    
    distances = []

    # Line 1
    p1 = (player.get_rect().midbottom[0] + player.size[0] / 2, player.get_rect().midbottom[1])
    p2 = (tube_list[score].get_rect().midtop[0] - Tube.size[0] / 2, tube_list[score].get_rect().midtop[1])
    pygame.draw.line(screen, RED, p1, p2, 2)
    distances.append(distance_between_points(p1, p2))

    # Line 2
    p1 = (player.get_rect().midtop[0] + player.size[0] / 2, player.get_rect().midtop[1])
    p2 = (tube_list[score].get_rect_reverse().midbottom[0] - Tube.size[0] / 2, tube_list[score].get_rect_reverse().midbottom[1])
    pygame.draw.line(screen, BLUE, p1, p2, 2)
    distances.append(distance_between_points(p1, p2))

    # Line 3
    p1 = (player.get_rect().midbottom[0] - player.size[0] / 2, player.get_rect().midbottom[1])
    p2 = (tube_list[score].get_rect().midtop[0] + Tube.size[0] / 2, tube_list[score].get_rect().midtop[1])
    pygame.draw.line(screen, RED, p1, p2, 2)
    distances.append(distance_between_points(p1, p2))

    # Line 4
    p1 = (player.get_rect().midtop[0] - player.size[0] / 2, player.get_rect().midtop[1])
    p2 = (tube_list[score].get_rect_reverse().midbottom[0] + Tube.size[0] / 2, tube_list[score].get_rect_reverse().midbottom[1])
    pygame.draw.line(screen, BLUE, p1, p2, 2)
    distances.append(distance_between_points(p1, p2))

    # Line 5
    p1 = (player.get_rect().midbottom[0] - player.size[0] / 2, player.get_rect().midbottom[1])
    p2 = (tube_list[score].get_rect().midtop[0] - Tube.size[0] / 2, tube_list[score].get_rect().midtop[1])
    pygame.draw.line(screen, RED, p1, p2, 2)
    distances.append(distance_between_points(p1, p2))

    # Line 6
    p1 = (player.get_rect().midtop[0] - player.size[0] / 2, player.get_rect().midtop[1])
    p2 = (tube_list[score].get_rect_reverse().midbottom[0] - Tube.size[0] / 2, tube_list[score].get_rect_reverse().midbottom[1])
    pygame.draw.line(screen, BLUE, p1, p2, 2)
    distances.append(distance_between_points(p1, p2))

    # Line 7
    p1 = (player.get_rect().midbottom[0] + player.size[0] / 2, player.get_rect().midbottom[1])
    p2 = (tube_list[score].get_rect().midtop[0] + Tube.size[0] / 2, tube_list[score].get_rect().midtop[1])
    pygame.draw.line(screen, RED, p1, p2, 2)
    distances.append(distance_between_points(p1, p2))

    # Line 8
    p1 = (player.get_rect().midtop[0] + player.size[0] / 2, player.get_rect().midtop[1])
    p2 = (tube_list[score].get_rect_reverse().midbottom[0] + Tube.size[0] / 2, tube_list[score].get_rect_reverse().midbottom[1])
    pygame.draw.line(screen, BLUE, p1, p2, 2)
    distances.append(distance_between_points(p1, p2))

    return distances


def run():
    global game_quit, v_delta, x_velocity

    score = 0
    tube_index = 0
    tube_list = [Tube(v_delta, x_velocity)]
    player = Player()
    is_alive = True

    while is_alive:
        dt = clock.tick(FPS) / 100
        is_alive = handle_command(player)

        load_screen()

        # Aggiornamento player e tubi
        update(dt, player, tube_list)

        # Aumenta lo score 
        if player.position[0] > tube_list[score].position[0] + Tube.size[0] : 
            score += 1

            if score%4 == 1:
                increment_diff(player, tube_list)

        # Crea nuovi tubie
        if tube_list[-1].position[0] < 400:
            tube_list.append(Tube(v_delta, x_velocity))
            tube_index += 1

        # Disegna il tuboe e player sullo schermo
        player.draw(screen)
        for tube in tube_list:
            if not tube.offscreen():
                tube.draw(screen)

        # Get 8 size distance
        distanze = calculate_distances_and_draw_lines(player, tube_list, score)

        # Collisione player e tubo
        is_alive = collidate_player(player, tube_list, tube_index)

        update_text_screen(score)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    while game_quit:
        int_try += 1
        v_delta = 200
        x_velocity = 0
        run()
