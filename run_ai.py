import os
import neat
import pygame

from Src.Class.bird import Player
from Src.Class.pipe import Tube
from Src.Class.back import background_image
from Src.constant import WINDOW_HEIGHT, WINDOW_WIDTH, FPS
from Src.color import WHITE, RED, BLUE, BLACK


CHECKPOINT_FILE = 'neat-checkpoint1'


# Global variables
max_score = []
int_try = 0
v_delta = 170
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

def call_flap_up(player: Player):
    """Handle user input events.
    
    Args:
        - player (Player): The player object controlled by user input.
    
    Returns:
        bool: True if the game is still running, False if the user quits.
    """
    player.flap_up()

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                pygame.quit()

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

def update_text_screen(score, n_bird):
    """Update and display text on the screen.
    
    Args:
        score (int): Current score of the game.
    """
    try_text = font.render(f'Bird: {n_bird}', True, BLACK)
    screen.blit(try_text, (10, 10)) 

    score_text = font.render(f'Score: {score}', True, BLACK)
    screen.blit(score_text, (10, 35)) 

    if len(max_score) > 0:
        max_score_text = font.render(f'Max Score: {max(max_score)}', True, BLACK)
        screen.blit(max_score_text, (10, 60)) 

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
    max_gravity = 20
    max_jump_strength = -30

    # Aggiornamento velocita di tutti i tubi
    for i in range(len(tube_list)):
        if tube_list[-1].velocity_y > max_y_velocity:
            tube_list[i].velocity_y += 5
    x_velocity = tube_list[-1].velocity_y - 15
    v_delta -= 5

    # Aggiornaemento velocita player
    
    player.jump_strength += 2

    if player.jump_strength > max_jump_strength:
        player.jump_strength = max_jump_strength

    if player.gravity < max_gravity:
        player.gravity = max_gravity
    else:
        player.gravity -= 0.5

    if v_delta < max_v_delta:
        v_delta = max_v_delta

    print("DIFF = G: ", player.gravity, "Y_V: ", tube_list[-1].velocity_y, "V_D: ", v_delta, "J: ", player.jump_strength)

def calculate_distances_and_draw_lines(player, tube_list, score, show = False):
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
    if show: pygame.draw.line(screen, RED, p1, p2, 2)
    distances.append(distance_between_points(p1, p2))

    # Line 2
    p1 = (player.get_rect().midtop[0] + player.size[0] / 2, player.get_rect().midtop[1])
    p2 = (tube_list[score].get_rect_reverse().midbottom[0] - Tube.size[0] / 2, tube_list[score].get_rect_reverse().midbottom[1])
    if show: pygame.draw.line(screen, BLUE, p1, p2, 2)
    distances.append(distance_between_points(p1, p2))

    # Line 3
    p1 = (player.get_rect().midbottom[0] - player.size[0] / 2, player.get_rect().midbottom[1])
    p2 = (tube_list[score].get_rect().midtop[0] + Tube.size[0] / 2, tube_list[score].get_rect().midtop[1])
    if show: pygame.draw.line(screen, RED, p1, p2, 2)
    distances.append(distance_between_points(p1, p2))

    # Line 4
    p1 = (player.get_rect().midtop[0] - player.size[0] / 2, player.get_rect().midtop[1])
    p2 = (tube_list[score].get_rect_reverse().midbottom[0] + Tube.size[0] / 2, tube_list[score].get_rect_reverse().midbottom[1])
    if show: pygame.draw.line(screen, BLUE, p1, p2, 2)
    distances.append(distance_between_points(p1, p2))

    # Line 5
    p1 = (player.get_rect().midbottom[0] - player.size[0] / 2, player.get_rect().midbottom[1])
    p2 = (tube_list[score].get_rect().midtop[0] - Tube.size[0] / 2, tube_list[score].get_rect().midtop[1])
    if show: pygame.draw.line(screen, RED, p1, p2, 2)
    distances.append(distance_between_points(p1, p2))

    # Line 6
    p1 = (player.get_rect().midtop[0] - player.size[0] / 2, player.get_rect().midtop[1])
    p2 = (tube_list[score].get_rect_reverse().midbottom[0] - Tube.size[0] / 2, tube_list[score].get_rect_reverse().midbottom[1])
    if show: pygame.draw.line(screen, BLUE, p1, p2, 2)
    distances.append(distance_between_points(p1, p2))

    # Line 7
    p1 = (player.get_rect().midbottom[0] + player.size[0] / 2, player.get_rect().midbottom[1])
    p2 = (tube_list[score].get_rect().midtop[0] + Tube.size[0] / 2, tube_list[score].get_rect().midtop[1])
    if show: pygame.draw.line(screen, RED, p1, p2, 2)
    distances.append(distance_between_points(p1, p2))

    # Line 8
    p1 = (player.get_rect().midtop[0] + player.size[0] / 2, player.get_rect().midtop[1])
    p2 = (tube_list[score].get_rect_reverse().midbottom[0] + Tube.size[0] / 2, tube_list[score].get_rect_reverse().midbottom[1])
    if show: pygame.draw.line(screen, BLUE, p1, p2, 2)
    distances.append(distance_between_points(p1, p2))

    return distances


def eval_genomes(genomes, config):

    global int_try, v_delta, x_velocity

    # Init start variable
    int_try += 1
    v_delta = 160
    x_velocity = 0

    # Variabile for main function
    score = 0       
    tube_index = 0
    tube_list = [Tube(v_delta, x_velocity)]

    nets = []
    ge = []
    birds = []

    # Create a list of birds
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Player())
        ge.append(genome)

    while len(birds) > 0:
        dt = clock.tick(FPS) / 100
        
        # call_flap_up
        load_screen()

        # Aggiornamento player e tubi
        for i, bird in enumerate(birds):
            bird.update(dt)

        for tube in tube_list:
            if not tube.offscreen():
                tube.update(dt)

        # Crea nuovi tubie
        if tube_list[-1].position[0] < 400:
            tube_list.append(Tube(v_delta, x_velocity))
            tube_index += 1

        for i, bird in enumerate(birds):
            ge[i].fitness += 0.1
            
            # Get 8 size distance
            if i == 0:
                distanze = calculate_distances_and_draw_lines(bird, tube_list, score, True)
            else:
                distanze = calculate_distances_and_draw_lines(bird, tube_list, score)

            # Input for function activation
            input_data = input_data = [
                bird.position[0], bird.position[1], bird.jump_strength, 
                bird.gravity, bird.velocity_y,
                distanze[0] * 1.3, distanze[1] * 1.3 , distanze[2] * 1.3 , distanze[3] * 1.3, distanze[4] * 1.3, distanze[5] * 1.3, distanze[6] * 1.3, distanze[7] * 1.3
                #tube_list[score].position[0], tube_list[score].position[1] - 1, tube_list[score].velocity_y,
                #tube_list[score].position_rotate[0], tube_list[score].position_rotate[1] + 1, tube_list[score].velocity_y,
                #x_velocity
            ]

            output = nets[i].activate(input_data)

            if output[0] > 0.995:
                call_flap_up(bird)

        # Disegna il tuboe e player sullo schermo
        for bird in birds:
            bird.draw(screen)

        for tube in tube_list:
            if not tube.offscreen():
                tube.draw(screen)

        for i, bird in enumerate(birds):

            # Get of alive
            is_alive = collidate_player(bird, tube_list, tube_index)
            
            if is_alive:
                if bird.position[0] > tube_list[score].position[0] + Tube.size[0]:

                    # Passaggio del tubo
                    ge[i].fitness += 1
                    score += 1

                    if score%4 == 1:
                        increment_diff(bird, tube_list)
                        
            else:
                ge[i].fitness -= 3
                nets.pop(i)
                ge.pop(i)
                birds.pop(i)

        # Update screen
        update_text_screen(score, len(birds))
        pygame.display.flip()
        clock.tick(FPS)


def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    # Check if the checkpoint file exists
    if os.path.exists(f'{CHECKPOINT_FILE}'):
        print(f"Resuming from {CHECKPOINT_FILE}")
        p = neat.Checkpointer.restore_checkpoint(f'{CHECKPOINT_FILE}')

    else:
        print("CHECKPOINT FILE DONT EXIST")
        p = neat.Population(config)

    # Add reporters to show progress in the terminal
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Add a custom checkpointer that always saves to the same file
    checkpointer = neat.Checkpointer(generation_interval=5, filename_prefix=CHECKPOINT_FILE)
    p.add_reporter(checkpointer)

    # Run for up to 50 generations
    winner = p.run(eval_genomes, 999)

    # Show final stats
    print('\nBest genome:\n{!s}'.format(winner))

    # Save the final state
    checkpointer.save_checkpoint(config, p.population, p.species, 0)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)
