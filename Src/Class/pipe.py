import os
import pygame
import random

# Variable
from ..constant import WINDOW_HEIGHT, WINDOW_WIDTH
tube_image = pygame.image.load(os.path.join('.', 'Src', 'flappy', 'pipe', 'pipe.png'))
tube_image_reverse = pygame.image.load(os.path.join('.', 'Src', 'flappy', 'pipe', 'pipe2.png'))
pipe_width, pipe_height = tube_image.get_size()

class Tube:
    """
    Represents a tube object in the Flappy Bird game.
    """
    size = [pipe_width, pipe_height]

    def __init__(self, v_delta, x_velocity=0):
        """
        Initializes a new Tube object with a random vertical position.

        Args:
            - v_delta (int): Initial vertical position of the tube.
            - x_velocity (int, optional): Horizontal velocity of the tube (default is 0).
        """
        self.x_velocity = x_velocity
        self.delta = random.randint(-180, 180)  # Random vertical variation

        # Calculate heights of the tube and its reversed counterpart
        self.h_tube = v_delta + self.delta
        self.h_tube_rotate = v_delta - self.delta

        # Initialize positions of the tube and its reversed counterpart
        self.position = [WINDOW_WIDTH, WINDOW_HEIGHT - pipe_height + self.h_tube]
        self.position_rotate = [WINDOW_WIDTH, 0 - self.h_tube_rotate]

        # Set vertical velocity based on horizontal velocity
        self.velocity_y = 15 + self.x_velocity

    def get_rect(self):
        """
        Returns a pygame.Rect object for the normal tube.

        Returns:
        - pygame.Rect: Rect object representing the bounding box of the normal tube.
        """
        return pygame.Rect(self.position, (pipe_width, pipe_height))

    def get_rect_reverse(self):
        """
        Returns a pygame.Rect object for the reversed tube.

        Returns:
            - pygame.Rect: Rect object representing the bounding box of the reversed tube.
        """
        return pygame.Rect(self.position_rotate, (pipe_width, pipe_height))

    def draw(self, screen):
        """
        Draws the tube and the reversed tube on the screen.

        Args:
            - screen (pygame.Surface): Surface onto which to draw.
        """
        screen.blit(tube_image, self.position)  # Draw normal tube
        screen.blit(tube_image_reverse, self.position_rotate)  # Draw reversed tube

    def update(self, dt):
        """
        Updates the position of the tube based on elapsed time.

        Args:
        - dt (float): Time elapsed since the last update.
        """
        self.position[0] -= self.velocity_y * dt
        self.position_rotate[0] -= self.velocity_y * dt

    def offscreen(self):
        """
        Checks if the tube is completely offscreen.

        Returns:
            - bool: True if the tube is offscreen, False otherwise.
        """
        return self.position[0] + pipe_width < 0
