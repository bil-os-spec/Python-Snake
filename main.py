import pygame
import sys
import random
import os
import math
import json
from pygame import gfxdraw
from pygame.locals import *
from enum import Enum
from collections import deque
from typing import List, Tuple, Dict, Optional

# Initialization
pygame.init()
pygame.mixer.init()

# Constants
class GameState(Enum):
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    SETTINGS = 4
    SHOP = 5
    STATS = 6

class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

# Color system with 100+ colors
COLORS = {
    # Basic colors
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "YELLOW": (255, 255, 0),
    "PURPLE": (128, 0, 128),
    "ORANGE": (255, 165, 0),
    "CYAN": (0, 255, 255),
    "GRAY": (128, 128, 128),
    
    # Extended color palette
    "DARK_RED": (139, 0, 0),
    "LIGHT_RED": (255, 102, 102),
    "DARK_GREEN": (0, 100, 0),
    "LIGHT_GREEN": (144, 238, 144),
    "DARK_BLUE": (0, 0, 139),
    "LIGHT_BLUE": (173, 216, 230),
    "GOLD": (255, 215, 0),
    "SILVER": (192, 192, 192),
    "PINK": (255, 192, 203),
    "HOT_PINK": (255, 105, 180),
    "DEEP_PINK": (255, 20, 147),
    "LAVENDER": (230, 230, 250),
    "INDIGO": (75, 0, 130),
    "TEAL": (0, 128, 128),
    "TURQUOISE": (64, 224, 208),
    "AQUAMARINE": (127, 255, 212),
    "MINT": (189, 252, 201),
    "OLIVE": (128, 128, 0),
    "LIME": (0, 255, 0),
    "MAROON": (128, 0, 0),
    "NAVY": (0, 0, 128),
    "CORAL": (255, 127, 80),
    "SALMON": (250, 128, 114),
    "BEIGE": (245, 245, 220),
    "IVORY": (255, 255, 240),
    "TAN": (210, 180, 140),
    "CHOCOLATE": (210, 105, 30),
    "CRIMSON": (220, 20, 60),
    "KHAKI": (240, 230, 140),
    "MAGENTA": (255, 0, 255),
    "OLD_LAVENDER": (121, 104, 120),
    "PASTEL_PURPLE": (207, 159, 255),
    "PERIWINKLE": (204, 204, 255),
    "PLUM": (221, 160, 221),
    "VIOLET": (238, 130, 238),
    "DARK_ORCHID": (153, 50, 204),
    "DARK_VIOLET": (148, 0, 211),
    "BLUE_VIOLET": (138, 43, 226),
    "MEDIUM_ORCHID": (186, 85, 211),
    "MEDIUM_PURPLE": (147, 112, 219),
    "PALE_VIOLET": (219, 112, 147),
    "THISTLE": (216, 191, 216),
    "ORCHID": (218, 112, 214),
    "FUCHSIA": (255, 0, 255),
    "DEEP_PURPLE": (102, 0, 153),
    "AMETHYST": (153, 102, 204),
    "LILAC": (200, 162, 200),
    "LAVENDER_BLUSH": (255, 240, 245),
    "GHOST_WHITE": (248, 248, 255),
    "ALICE_BLUE": (240, 248, 255),
    "AZURE": (240, 255, 255),
    "BABY_BLUE": (137, 207, 240),
    "LIGHT_CYAN": (224, 255, 255),
    "PALE_TURQUOISE": (175, 238, 238),
    "AQUA": (0, 255, 255),
    "DARK_CYAN": (0, 139, 139),
    "CADET_BLUE": (95, 158, 160),
    "POWDER_BLUE": (176, 224, 230),
    "SKY_BLUE": (135, 206, 235),
    "LIGHT_SKY_BLUE": (135, 206, 250),
    "STEEL_BLUE": (70, 130, 180),
    "DODGER_BLUE": (30, 144, 255),
    "CORNFLOWER_BLUE": (100, 149, 237),
    "ROYAL_BLUE": (65, 105, 225),
    "MEDIUM_BLUE": (0, 0, 205),
    "MIDNIGHT_BLUE": (25, 25, 112),
    "DARK_SLATE_BLUE": (72, 61, 139),
    "SLATE_BLUE": (106, 90, 205),
    "MEDIUM_SLATE_BLUE": (123, 104, 238),
    # Add more colors as needed...
}

# Game settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BLOCK_SIZE = 24
BASE_SPEED = 15
MAX_SPEED = 60
MIN_SPEED = 5
GRID_WIDTH = SCREEN_WIDTH // BLOCK_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)
pygame.display.set_caption("Ultimate Snake Game 2024")
clock = pygame.time.Clock()

# Load fonts
try:
    title_font = pygame.font.Font("assets/fonts/RetroGaming.ttf", 72)
    font_large = pygame.font.Font("assets/fonts/RetroGaming.ttf", 48)
    font_medium = pygame.font.Font("assets/fonts/RetroGaming.ttf", 36)
    font_small = pygame.font.Font("assets/fonts/RetroGaming.ttf", 24)
    font_tiny = pygame.font.Font("assets/fonts/RetroGaming.ttf", 18)
except:
    # Fallback to system fonts if custom fonts not found
    title_font = pygame.font.SysFont("arial", 72, bold=True)
    font_large = pygame.font.SysFont("arial", 48)
    font_medium = pygame.font.SysFont("arial", 36)
    font_small = pygame.font.SysFont("arial", 24)
    font_tiny = pygame.font.SysFont("arial", 18)

# Particle system
class Particle:
    def __init__(self, x, y, color, velocity, lifetime, size, gravity=0):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.gravity = gravity
        self.alpha = 255
        
    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.velocity[1] += self.gravity
        self.lifetime -= 1
        self.alpha = int(255 * (self.lifetime / self.max_lifetime))
        
    def draw(self, surface):
        if self.lifetime > 0:
            alpha_color = (*self.color[:3], self.alpha) if len(self.color) == 4 else (*self.color, self.alpha)
            pygame.gfxdraw.filled_circle(surface, int(self.x), int(self.y), int(self.size), alpha_color)

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def add_particle(self, particle):
        self.particles.append(particle)
        
    def add_explosion(self, x, y, color, count=20):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 3)
            velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            lifetime = random.randint(30, 90)
            size = random.randint(2, 5)
            self.particles.append(Particle(x, y, color, velocity, lifetime, size, 0.1))
            
    def update(self):
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update()
            
    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)

# Sound system
class SoundSystem:
    def __init__(self):
        self.sounds = {}
        self.music_tracks = {}
        self.muted = False
        self.volume = 0.5
        self.current_music = None
        
    def load_sound(self, name, path):
        try:
            self.sounds[name] = pygame.mixer.Sound(path)
            self.sounds[name].set_volume(self.volume)
        except:
            print(f"Failed to load sound: {path}")
            
    def load_music(self, name, path):
        self.music_tracks[name] = path
        
    def play_sound(self, name, loops=0):
        if not self.muted and name in self.sounds:
            self.sounds[name].play(loops)
            
    def play_music(self, name, loops=-1):
        if not self.muted and name in self.music_tracks:
            pygame.mixer.music.load(self.music_tracks[name])
            pygame.mixer.music.set_volume(self.volume * 0.7)  # Music slightly quieter
            pygame.mixer.music.play(loops)
            self.current_music = name
            
    def stop_music(self):
        pygame.mixer.music.stop()
        self.current_music = None
        
    def toggle_mute(self):
        self.muted = not self.muted
        pygame.mixer.music.set_volume(0 if self.muted else self.volume * 0.7)
        for sound in self.sounds.values():
            sound.set_volume(0 if self.muted else self.volume)
            
    def set_volume(self, volume):
        self.volume = max(0, min(1, volume))
        if not self.muted:
            pygame.mixer.music.set_volume(self.volume * 0.7)
            for sound in self.sounds.values():
                sound.set_volume(self.volume)

# Initialize sound system
sound_system = SoundSystem()
try:
    sound_system.load_sound("eat", "assets/sounds/eat.wav")
    sound_system.load_sound("crash", "assets/sounds/crash.wav")
    sound_system.load_sound("powerup", "assets/sounds/powerup.wav")
    sound_system.load_sound("click", "assets/sounds/click.wav")
    sound_system.load_music("background", "assets/music/background.mp3")
    sound_system.load_music("menu", "assets/music/menu.mp3")
except:
    print("Sound files not found, continuing without sound")

# Snake class with enhanced features
class Snake:
    def __init__(self):
        self.reset()
        self.skin_index = 0
        self.skins = [
            {"body": COLORS["PURPLE"], "head": COLORS["DEEP_PURPLE"]},
            {"body": COLORS["CYAN"], "head": COLORS["DARK_CYAN"]},
            {"body": COLORS["ORANGE"], "head": COLORS["DARK_ORCHID"]},
            {"body": COLORS["GREEN"], "head": COLORS["DARK_GREEN"]},
            {"body": COLORS["GOLD"], "head": COLORS["YELLOW"]},
            {"body": COLORS["PINK"], "head": COLORS["HOT_PINK"]},
            {"body": COLORS["BLUE_VIOLET"], "head": COLORS["INDIGO"]},
            {"body": COLORS["TEAL"], "head": COLORS["TURQUOISE"]},
        ]
        self.eye_color = COLORS["WHITE"]
        self.pupil_color = COLORS["BLACK"]
        self.tongue_out = False
        self.tongue_timer = 0
        self.tail_history = deque(maxlen=10)  # For smoother tail movement
        self.glow_effect = False
        self.glow_timer = 0
        self.glow_colors = [COLORS["RED"], COLORS["ORANGE"], COLORS["YELLOW"], COLORS["GREEN"], 
                          COLORS["BLUE"], COLORS["INDIGO"], COLORS["VIOLET"]]
        
    def reset(self):
        self.body = [[SCREEN_WIDTH//2, SCREEN_HEIGHT//2]]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.length = 1
        self.speed = BASE_SPEED
        self.invincible = False
        self.shield = False
        self.powerups = {}
        self.score_multiplier = 1.0
        self.combo = 0
        self.combo_timer = 0
        self.last_move_time = 0
        self.growth_pending = 0
        self.tail_history.clear()
        self.trail_particles = []
        
    def move(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time < 1000 // self.speed:
            return
            
        self.last_move_time = current_time
        self.direction = self.next_direction
        
        # Add current position to tail history before moving
        self.tail_history.appendleft(self.body[0].copy())
        
        head = self.body[0].copy()
        
        if self.direction == Direction.RIGHT:
            head[0] += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            head[0] -= BLOCK_SIZE
        elif self.direction == Direction.UP:
            head[1] -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            head[1] += BLOCK_SIZE
            
        self.body.insert(0, head)
        
        # Handle pending growth
        if self.growth_pending > 0:
            self.growth_pending -= 1
        else:
            if len(self.body) > self.length:
                # Add trail particle when tail moves
                if len(self.body) > 1:
                    tail = self.body[-1]
                    self.trail_particles.append({
                        'pos': tail.copy(),
                        'timer': 15,
                        'color': self.skins[self.skin_index]["body"],
                        'size': BLOCK_SIZE // 2
                    })
                self.body.pop()
                
        # Update tongue animation
        self.tongue_timer = (self.tongue_timer + 1) % 60
        self.tongue_out = self.tongue_timer < 10
        
        # Update glow effect
        if self.glow_effect:
            self.glow_timer = (self.glow_timer + 1) % len(self.glow_colors)
            
        # Update trail particles
        for p in self.trail_particles:
            p['timer'] -= 1
            p['size'] = max(0, p['size'] - 0.5)
        self.trail_particles = [p for p in self.trail_particles if p['timer'] > 0]
        
    def change_direction(self, new_direction):
        # Prevent 180-degree turns
        if (new_direction == Direction.UP and self.direction != Direction.DOWN) or \
           (new_direction == Direction.DOWN and self.direction != Direction.UP) or \
           (new_direction == Direction.LEFT and self.direction != Direction.RIGHT) or \
           (new_direction == Direction.RIGHT and self.direction != Direction.LEFT):
            self.next_direction = new_direction
            
    def grow(self, amount=1):
        self.growth_pending += amount
        self.length += amount
        self.speed = min(self.speed + 0.2, MAX_SPEED)
        
    def shrink(self, amount=1):
        self.length = max(1, self.length - amount)
        self.speed = max(self.speed - 1, MIN_SPEED)
        
    def draw(self, surface):
        # Draw trail particles
        for p in self.trail_particles:
            alpha = int(255 * (p['timer'] / 15))
            color = (*p['color'][:3], alpha) if len(p['color']) == 4 else (*p['color'], alpha)
            pygame.gfxdraw.filled_circle(
                surface, 
                p['pos'][0] + BLOCK_SIZE // 2, 
                p['pos'][1] + BLOCK_SIZE // 2, 
                int(p['size']), 
                color
            )
        
        # Draw body
        skin = self.skins[self.skin_index]
        for index, block in enumerate(self.body):
            # Calculate interpolated position for smoother movement
            if index < len(self.tail_history):
                ratio = index / len(self.body)
                interp_x = block[0] * ratio + self.tail_history[index][0] * (1 - ratio)
                interp_y = block[1] * ratio + self.tail_history[index][1] * (1 - ratio)
                draw_pos = [interp_x, interp_y]
            else:
                draw_pos = block
                
            # Draw body segment
            if index == 0:  # Head
                self.draw_head(surface, draw_pos, skin["head"])
            else:  # Body
                self.draw_body_segment(surface, draw_pos, skin["body"], index)
                
    def draw_body_segment(self, surface, pos, color, index):
        # Glow effect for special segments
        if self.glow_effect and index % 5 == 0:
            glow_color = self.glow_colors[self.glow_timer]
            pygame.gfxdraw.filled_circle(
                surface, 
                pos[0] + BLOCK_SIZE // 2, 
                pos[1] + BLOCK_SIZE // 2, 
                BLOCK_SIZE // 2 + 2, 
                (*glow_color, 100)
            )
            
        # Main body segment
        pygame.draw.rect(
            surface, 
            color, 
            (pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE),
            border_radius=4
        )
        
        # Add some details to the body segments
        inner_size = BLOCK_SIZE - 4
        inner_color = (
            min(color[0] + 30, 255),
            min(color[1] + 30, 255),
            min(color[2] + 30, 255)
        )
        pygame.draw.rect(
            surface, 
            inner_color, 
            (pos[0] + 2, pos[1] + 2, inner_size, inner_size),
            border_radius=2
        )
        
    def draw_head(self, surface, pos, color):
        # Draw head with eyes and tongue
        pygame.draw.rect(
            surface, 
            color, 
            (pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE),
            border_radius=6
        )
        
        # Draw eyes based on direction
        eye_size = BLOCK_SIZE // 4
        pupil_size = eye_size // 2
        
        if self.direction == Direction.RIGHT:
            # Eyes on the right side
            left_eye_pos = (pos[0] + BLOCK_SIZE - eye_size - 4, pos[1] + 6)
            right_eye_pos = (pos[0] + BLOCK_SIZE - eye_size - 4, pos[1] + BLOCK_SIZE - 6 - eye_size)
        elif self.direction == Direction.LEFT:
            # Eyes on the left side
            left_eye_pos = (pos[0] + 4, pos[1] + 6)
            right_eye_pos = (pos[0] + 4, pos[1] + BLOCK_SIZE - 6 - eye_size)
        elif self.direction == Direction.UP:
            # Eyes on the top
            left_eye_pos = (pos[0] + 6, pos[1] + 4)
            right_eye_pos = (pos[0] + BLOCK_SIZE - 6 - eye_size, pos[1] + 4)
        else:  # DOWN
            # Eyes on the bottom
            left_eye_pos = (pos[0] + 6, pos[1] + BLOCK_SIZE - eye_size - 4)
            right_eye_pos = (pos[0] + BLOCK_SIZE - 6 - eye_size, pos[1] + BLOCK_SIZE - eye_size - 4)
            
        # Draw eyes
        pygame.draw.rect(surface, self.eye_color, (*left_eye_pos, eye_size, eye_size), border_radius=eye_size//2)
        pygame.draw.rect(surface, self.eye_color, (*right_eye_pos, eye_size, eye_size), border_radius=eye_size//2)
        
        # Draw pupils
        pygame.draw.rect(surface, self.pupil_color, 
                        (left_eye_pos[0] + (eye_size - pupil_size)//2, 
                         left_eye_pos[1] + (eye_size - pupil_size)//2, 
                         pupil_size, pupil_size), border_radius=pupil_size//2)
        pygame.draw.rect(surface, self.pupil_color, 
                        (right_eye_pos[0] + (eye_size - pupil_size)//2, 
                         right_eye_pos[1] + (eye_size - pupil_size)//2, 
                         pupil_size, pupil_size), border_radius=pupil_size//2)
        
        # Draw tongue when eating
        if self.tongue_out:
            tongue_length = BLOCK_SIZE // 2
            tongue_width = BLOCK_SIZE // 6
            tongue_base = (pos[0] + BLOCK_SIZE // 2, pos[1] + BLOCK_SIZE // 2)
            
            if self.direction == Direction.RIGHT:
                tongue_points = [
                    tongue_base,
                    (tongue_base[0] + tongue_length, tongue_base[1] - tongue_width),
                    (tongue_base[0] + tongue_length, tongue_base[1] + tongue_width)
                ]
            elif self.direction == Direction.LEFT:
                tongue_points = [
                    tongue_base,
                    (tongue_base[0] - tongue_length, tongue_base[1] - tongue_width),
                    (tongue_base[0] - tongue_length, tongue_base[1] + tongue_width)
                ]
            elif self.direction == Direction.UP:
                tongue_points = [
                    tongue_base,
                    (tongue_base[0] - tongue_width, tongue_base[1] - tongue_length),
                    (tongue_base[0] + tongue_width, tongue_base[1] - tongue_length)
                ]
            else:  # DOWN
                tongue_points = [
                    tongue_base,
                    (tongue_base[0] - tongue_width, tongue_base[1] + tongue_length),
                    (tongue_base[0] + tongue_width, tongue_base[1] + tongue_length)
                ]
                
            pygame.draw.polygon(surface, COLORS["HOT_PINK"], tongue_points)

# Food system with multiple types
class Food:
    def __init__(self):
        self.types = {
            "normal": {"color": COLORS["GREEN"], "value": 1, "rarity": 60},
            "speed": {"color": COLORS["CYAN"], "value": 2, "rarity": 15, "effect": "speed_boost"},
            "slow": {"color": COLORS["BLUE"], "value": -1, "rarity": 10, "effect": "slow"},
            "bonus": {"color": COLORS["ORANGE"], "value": 3, "rarity": 10},
            "golden": {"color": COLORS["GOLD"], "value": 5, "rarity": 3, "effect": "score_boost"},
            "rainbow": {"color": COLORS["RED"], "value": 7, "rarity": 2, "effect": "rainbow"},
            "poison": {"color": COLORS["DARK_GREEN"], "value": -2, "rarity": 5, "effect": "shrink"},
            "invincible": {"color": COLORS["WHITE"], "value": 0, "rarity": 5, "effect": "invincible"},
            "shield": {"color": COLORS["SILVER"], "value": 0, "rarity": 5, "effect": "shield"},
            "glow": {"color": COLORS["MAGENTA"], "value": 2, "rarity": 5, "effect": "glow"}
        }
        self.spawn_timer = 0
        self.current_color_index = 0
        self.rainbow_colors = [COLORS["RED"], COLORS["ORANGE"], COLORS["YELLOW"], 
                              COLORS["GREEN"], COLORS["BLUE"], COLORS["INDIGO"], COLORS["VIOLET"]]
        self.respawn()
        
    def respawn(self):
        total_rarity = sum(food["rarity"] for food in self.types.values())
        r = random.uniform(0, total_rarity)
        upto = 0
        
        for name, props in self.types.items():
            if upto + props["rarity"] >= r:
                self.type = name
                self.color = props["color"]
                self.value = props["value"]
                self.effect = props.get("effect")
                break
            upto += props["rarity"]
            
        self.pos = [
            random.randrange(BLOCK_SIZE, SCREEN_WIDTH - BLOCK_SIZE, BLOCK_SIZE),
            random.randrange(BLOCK_SIZE, SCREEN_HEIGHT - BLOCK_SIZE, BLOCK_SIZE)
        ]
        self.spawn_time = pygame.time.get_ticks()
        self.spawn_animation = True
        self.animation_timer = 0
        
    def update(self):
        # Rainbow food color animation
        if self.type == "rainbow":
            self.current_color_index = (self.current_color_index + 1) % len(self.rainbow_colors)
            self.color = self.rainbow_colors[self.current_color_index]
            
        # Spawn animation
        if self.spawn_animation:
            self.animation_timer += 1
            if self.animation_timer > 30:
                self.spawn_animation = False
                
        # Food expiration (only some types expire)
        if self.type in ["bonus", "golden", "rainbow"]:
            if pygame.time.get_ticks() - self.spawn_time > 10000:  # 10 seconds
                self.respawn()
                
    def draw(self, surface):
        size = BLOCK_SIZE
        
        if self.spawn_animation:
            # Growing animation when food spawns
            size = int(BLOCK_SIZE * (self.animation_timer / 30))
            
        x, y = self.pos[0] + (BLOCK_SIZE - size) // 2, self.pos[1] + (BLOCK_SIZE - size) // 2
        
        # Special drawing for different food types
        if self.type == "golden":
            # Golden food has a shine effect
            pygame.draw.rect(surface, self.color, (x, y, size, size), border_radius=size//2)
            
            # Draw shine lines
            shine_color = COLORS["YELLOW"]
            center_x, center_y = x + size//2, y + size//2
            pygame.draw.line(
                surface, shine_color, 
                (center_x - size//4, center_y - size//4),
                (center_x + size//4, center_y + size//4), 
                2
            )
            pygame.draw.line(
                surface, shine_color, 
                (center_x + size//4, center_y - size//4),
                (center_x - size//4, center_y + size//4), 
                2
            )
        elif self.type == "rainbow":
            # Rainbow food has a swirling effect
            pygame.draw.rect(surface, self.color, (x, y, size, size), border_radius=size//2)
            
            # Draw rainbow rings
            for i in range(3):
                ring_color = self.rainbow_colors[(self.current_color_index + i*2) % len(self.rainbow_colors)]
                ring_size = size - i*4 - 2
                pygame.draw.rect(
                    surface, ring_color, 
                    (x + i*2 + 1, y + i*2 + 1, ring_size, ring_size), 
                    border_radius=ring_size//2, 
                    width=2
                )
        else:
            # Regular food drawing
            pygame.draw.rect(surface, self.color, (x, y, size, size), border_radius=size//2)
            
            # Add some details for special foods
            if self.type in ["speed", "slow", "invincible", "shield", "glow"]:
                symbol_size = size // 2
                symbol_x, symbol_y = x + (size - symbol_size) // 2, y + (size - symbol_size) // 2
                
                if self.type == "speed":
                    pygame.draw.polygon(
                        surface, COLORS["WHITE"], 
                        [(symbol_x, symbol_y), 
                         (symbol_x + symbol_size, symbol_y + symbol_size//2),
                         (symbol_x, symbol_y + symbol_size)]
                    )
                elif self.type == "slow":
                    pygame.draw.rect(
                        surface, COLORS["WHITE"], 
                        (symbol_x, symbol_y, symbol_size, symbol_size), 
                        border_radius=2
                    )
                elif self.type == "invincible":
                    pygame.draw.circle(
                        surface, COLORS["WHITE"], 
                        (symbol_x + symbol_size//2, symbol_y + symbol_size//2), 
                        symbol_size//2
                    )
                elif self.type == "shield":
                    pygame.draw.polygon(
                        surface, COLORS["WHITE"], 
                        [(symbol_x + symbol_size//2, symbol_y),
                         (symbol_x, symbol_y + symbol_size),
                         (symbol_x + symbol_size, symbol_y + symbol_size)]
                    )
                elif self.type == "glow":
                    pygame.draw.line(
                        surface, COLORS["WHITE"], 
                        (symbol_x, symbol_y + symbol_size//2),
                        (symbol_x + symbol_size, symbol_y + symbol_size//2), 
                        2
                    )
                    pygame.draw.line(
                        surface, COLORS["WHITE"], 
                        (symbol_x + symbol_size//2, symbol_y),
                        (symbol_x + symbol_size//2, symbol_y + symbol_size), 
                        2
                    )

# Obstacle system with different types
class Obstacle:
    def __init__(self):
        self.positions = []
        self.moving = True
        self.directions = {}
        self.types = {}  # Store type for each obstacle
        self.generate()
        
    def generate(self):
        self.positions = []
        self.directions = {}
        self.types = {}
        
        # Generate different types of obstacles
        for _ in range(15):
            pos = [
                random.randrange(0, SCREEN_WIDTH - BLOCK_SIZE, BLOCK_SIZE),
                random.randrange(0, SCREEN_HEIGHT - BLOCK_SIZE, BLOCK_SIZE)
            ]
            self.positions.append(pos)
            
            # Assign random direction for moving obstacles
            self.directions[tuple(pos)] = random.choice(list(Direction))
            
            # Assign random type
            obstacle_type = random.choice(["normal", "bouncy", "spiky", "ghost"])
            self.types[tuple(pos)] = obstacle_type
            
    def move(self):
        if self.moving:
            for index, pos in enumerate(self.positions):
                direction = self.directions[tuple(pos)]
                new_pos = pos.copy()
                
                if direction == Direction.UP:
                    new_pos[1] -= BLOCK_SIZE
                elif direction == Direction.DOWN:
                    new_pos[1] += BLOCK_SIZE
                elif direction == Direction.LEFT:
                    new_pos[0] -= BLOCK_SIZE
                elif direction == Direction.RIGHT:
                    new_pos[0] += BLOCK_SIZE
                    
                # Check boundaries and bounce if needed
                if new_pos[0] < 0 or new_pos[0] >= SCREEN_WIDTH:
                    if self.types[tuple(pos)] == "bouncy":
                        self.directions[tuple(pos)] = Direction.LEFT if direction == Direction.RIGHT else Direction.RIGHT
                    else:
                        new_pos[0] = (new_pos[0] + SCREEN_WIDTH) % SCREEN_WIDTH
                elif new_pos[1] < 0 or new_pos[1] >= SCREEN_HEIGHT:
                    if self.types[tuple(pos)] == "bouncy":
                        self.directions[tuple(pos)] = Direction.UP if direction == Direction.DOWN else Direction.DOWN
                    else:
                        new_pos[1] = (new_pos[1] + SCREEN_HEIGHT) % SCREEN_HEIGHT
                
                self.positions[index] = new_pos
                old_key = tuple(pos)
                new_key = tuple(new_pos)
                if old_key in self.directions:
                    self.directions[new_key] = self.directions.pop(old_key)
                if old_key in self.types:
                    self.types[new_key] = self.types.pop(old_key)
                    
    def draw(self, surface):
        for pos in self.positions:
            obstacle_type = self.types[tuple(pos)]
            
            if obstacle_type == "normal":
                color = COLORS["RED"]
                pygame.draw.rect(surface, color, (pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))
            elif obstacle_type == "bouncy":
                color = COLORS["ORANGE"]
                pygame.draw.rect(surface, color, (pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE), border_radius=4)
                # Draw bounce lines
                pygame.draw.line(
                    surface, COLORS["YELLOW"], 
                    (pos[0] + 2, pos[1] + 2),
                    (pos[0] + BLOCK_SIZE - 2, pos[1] + BLOCK_SIZE - 2), 
                    2
                )
                pygame.draw.line(
                    surface, COLORS["YELLOW"], 
                    (pos[0] + BLOCK_SIZE - 2, pos[1] + 2),
                    (pos[0] + 2, pos[1] + BLOCK_SIZE - 2), 
                    2
                )
            elif obstacle_type == "spiky":
                color = COLORS["DARK_RED"]
                pygame.draw.rect(surface, color, (pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))
                # Draw spikes
                center_x, center_y = pos[0] + BLOCK_SIZE//2, pos[1] + BLOCK_SIZE//2
                for angle in range(0, 360, 45):
                    rad = math.radians(angle)
                    end_x = center_x + math.cos(rad) * BLOCK_SIZE//2
                    end_y = center_y + math.sin(rad) * BLOCK_SIZE//2
                    pygame.draw.line(
                        surface, COLORS["YELLOW"], 
                        (center_x, center_y),
                        (end_x, end_y), 
                        2
                    )
            elif obstacle_type == "ghost":
                # Semi-transparent ghost obstacle
                ghost_color = (*COLORS["GRAY"], 150)
                pygame.draw.rect(
                    surface, ghost_color, 
                    (pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE), 
                    border_radius=BLOCK_SIZE//4
                )
                # Draw ghost eyes
                eye_color = (*COLORS["WHITE"], 200)
                pygame.draw.circle(
                    surface, eye_color, 
                    (pos[0] + BLOCK_SIZE//3, pos[1] + BLOCK_SIZE//3), 
                    BLOCK_SIZE//6
                )
                pygame.draw.circle(
                    surface, eye_color, 
                    (pos[0] + BLOCK_SIZE*2//3, pos[1] + BLOCK_SIZE//3), 
                    BLOCK_SIZE//6
                )
                # Draw pupils
                pygame.draw.circle(
                    surface, (*COLORS["BLACK"], 200), 
                    (pos[0] + BLOCK_SIZE//3, pos[1] + BLOCK_SIZE//3), 
                    BLOCK_SIZE//10
                )
                pygame.draw.circle(
                    surface, (*COLORS["BLACK"], 200), 
                    (pos[0] + BLOCK_SIZE*2//3, pos[1] + BLOCK_SIZE//3), 
                    BLOCK_SIZE//10
                )

# Power-up system
class PowerUp:
    def __init__(self):
        self.active = False
        self.type = None
        self.end_time = 0
        self.particle_system = ParticleSystem()
        
    def activate(self, power_type, duration):
        self.active = True
        self.type = power_type
        self.end_time = pygame.time.get_ticks() + duration
        self.particle_system.add_explosion(
            random.randint(0, SCREEN_WIDTH),
            random.randint(0, SCREEN_HEIGHT),
            COLORS["YELLOW"],
            50
        )
        
    def update(self):
        current_time = pygame.time.get_ticks()
        if self.active and current_time >= self.end_time:
            self.active = False
            self.type = None
            self.particle_system.add_explosion(
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                COLORS["PURPLE"],
                50
            )
            
        self.particle_system.update()
        
    def draw(self, surface):
        if self.active:
            # Draw timer bar at top of screen
            remaining = max(0, self.end_time - pygame.time.get_ticks())
            percentage = remaining / 5000  # Assuming 5s duration
            
            bar_width = SCREEN_WIDTH * percentage
            color = COLORS["GREEN"] if percentage > 0.5 else COLORS["YELLOW"] if percentage > 0.25 else COLORS["RED"]
            
            pygame.draw.rect(surface, color, (0, 0, bar_width, 5))
            
            # Draw power-up icon
            icon_size = 30
            margin = 10
            icon_rect = pygame.Rect(SCREEN_WIDTH - icon_size - margin, margin, icon_size, icon_size)
            
            if self.type == "invincible":
                pygame.draw.circle(surface, COLORS["WHITE"], icon_rect.center, icon_size//2)
                pygame.draw.circle(surface, COLORS["RED"], icon_rect.center, icon_size//2 - 3)
            elif self.type == "shield":
                pygame.draw.polygon(
                    surface, COLORS["SILVER"], 
                    [(icon_rect.left, icon_rect.bottom),
                     (icon_rect.centerx, icon_rect.top),
                     (icon_rect.right, icon_rect.bottom)]
                )
            elif self.type == "score_boost":
                pygame.draw.rect(surface, COLORS["GOLD"], icon_rect)
                text = font_tiny.render("x2", True, COLORS["BLACK"])
                surface.blit(text, (icon_rect.centerx - text.get_width()//2, 
                                   icon_rect.centery - text.get_height()//2))
                
        self.particle_system.draw(surface)

# Button class for UI
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=COLORS["WHITE"], font=font_medium):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font
        self.is_hovered = False
        self.clicked = False
        self.border_radius = 10
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, COLORS["WHITE"], self.rect, 2, border_radius=self.border_radius)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def update(self, mouse_pos, mouse_click):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.clicked = self.is_hovered and mouse_click
        return self.clicked
        
    def set_text(self, new_text):
        self.text = new_text

# Main game class
class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.obstacle = Obstacle()
        self.powerup = PowerUp()
        self.particle_system = ParticleSystem()
        self.state = GameState.MENU
        self.score = 0
        self.high_score = self.load_highscore()
        self.level = 1
        self.lives = 3
        self.combo = 0
        self.combo_timer = 0
        self.difficulty = "NORMAL"  # EASY, NORMAL, HARD
        self.backgrounds = [
            COLORS["BLACK"], 
            (30, 30, 30), 
            (50, 50, 100),
            (20, 40, 20),
            (40, 20, 40),
            (20, 20, 40),
            (40, 40, 20)
        ]
        self.current_bg = 0
        self.grid_visible = False
        self.settings = {
            "sound_volume": 0.7,
            "music_volume": 0.5,
            "show_fps": True,
            "snake_skin": 0,
            "difficulty": "NORMAL"
        }
        self.load_settings()
        self.fps_counter = 0
        self.fps_timer = 0
        self.fps = 0
        self.clock = pygame.time.Clock()
        self.menu_buttons = [
            Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100, 300, 60, "Start Game", 
                  COLORS["PURPLE"], COLORS["DEEP_PURPLE"]),
            Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 20, 300, 60, "Settings", 
                  COLORS["BLUE"], COLORS["DARK_BLUE"]),
            Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 60, 300, 60, "Quit", 
                  COLORS["RED"], COLORS["DARK_RED"])
        ]
        self.pause_buttons = [
            Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 60, 300, 60, "Resume", 
                  COLORS["GREEN"], COLORS["DARK_GREEN"]),
            Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 20, 300, 60, "Main Menu", 
                  COLORS["BLUE"], COLORS["DARK_BLUE"]),
            Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 100, 300, 60, "Quit", 
                  COLORS["RED"], COLORS["DARK_RED"])
        ]
        self.settings_buttons = [
            Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT - 100, 300, 60, "Back", 
                  COLORS["PURPLE"], COLORS["DEEP_PURPLE"])
        ]
        self.game_over_buttons = [
            Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 40, 300, 60, "Play Again", 
                  COLORS["GREEN"], COLORS["DARK_GREEN"]),
            Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 120, 300, 60, "Main Menu", 
                  COLORS["BLUE"], COLORS["DARK_BLUE"])
        ]
        
        # Initialize sound system with settings
        sound_system.set_volume(self.settings["sound_volume"])
        pygame.mixer.music.set_volume(self.settings["music_volume"])
        
        # Start menu music
        sound_system.play_music("menu")
        
    def load_highscore(self):
        try:
            with open("highscore.dat", "r") as f:
                return int(f.read())
        except:
            return 0
            
    def save_highscore(self):
        with open("highscore.dat", "w") as f:
            f.write(str(max(self.score, self.high_score)))
            
    def load_settings(self):
        try:
            with open("settings.json", "r") as f:
                self.settings = json.load(f)
                self.current_bg = self.settings.get("background", 0)
                self.difficulty = self.settings.get("difficulty", "NORMAL")
                self.snake.skin_index = self.settings.get("snake_skin", 0)
        except:
            self.save_settings()
            
    def save_settings(self):
        self.settings["background"] = self.current_bg
        self.settings["snake_skin"] = self.snake.skin_index
        self.settings["difficulty"] = self.difficulty
        with open("settings.json", "w") as f:
            json.dump(self.settings, f)
            
    def reset(self):
        self.snake.reset()
        self.food.respawn()
        self.obstacle.generate()
        self.score = 0
        self.level = 1
        self.lives = 3
        self.combo = 0
        self.combo_timer = 0
        
        # Adjust difficulty
        if self.difficulty == "EASY":
            self.snake.speed = BASE_SPEED - 5
            self.obstacle.moving = False
        elif self.difficulty == "NORMAL":
            self.snake.speed = BASE_SPEED
            self.obstacle.moving = True
        elif self.difficulty == "HARD":
            self.snake.speed = BASE_SPEED + 5
            self.obstacle.moving = True
            self.obstacle.generate()  # More obstacles in hard mode
            
    def check_collision(self):
        head = self.snake.body[0]
        
        # Wall collision
        if head[0] < 0 or head[0] >= SCREEN_WIDTH or head[1] < 0 or head[1] >= SCREEN_HEIGHT:
            if not self.snake.invincible:
                return True
            else:
                # Wrap around if invincible
                self.snake.body[0] = [
                    (head[0] + SCREEN_WIDTH) % SCREEN_WIDTH,
                    (head[1] + SCREEN_HEIGHT) % SCREEN_HEIGHT
                ]
                
        # Self collision
        for block in self.snake.body[1:]:
            if head == block and not self.snake.shield:
                return True
                
        # Obstacle collision
        for obs in self.obstacle.positions:
            if head == obs:
                if self.snake.invincible:
                    # Destroy obstacle if invincible
                    if obs in self.obstacle.positions:
                        self.obstacle.positions.remove(obs)
                        self.particle_system.add_explosion(obs[0], obs[1], COLORS["RED"], 20)
                        sound_system.play_sound("powerup")
                elif not self.snake.shield:
                    return True
                else:
                    # Use up shield
                    self.snake.shield = False
                    sound_system.play_sound("powerup")
                    break
                    
        return False
        
    def check_food_collision(self):
        if self.snake.body[0] == self.food.pos:
            # Apply food effect
            if self.food.effect == "speed_boost":
                self.snake.speed = min(self.snake.speed + 3, MAX_SPEED)
                sound_system.play_sound("powerup")
            elif self.food.effect == "slow":
                self.snake.speed = max(self.snake.speed - 3, MIN_SPEED)
            elif self.food.effect == "score_boost":
                self.score += self.food.value * 2  # Double points
                sound_system.play_sound("powerup")
            elif self.food.effect == "rainbow":
                self.snake.grow(3)
                self.score += self.food.value
                sound_system.play_sound("powerup")
            elif self.food.effect == "shrink":
                self.snake.shrink(2)
            elif self.food.effect == "invincible":
                self.snake.invincible = True
                self.snake.powerups["invincible"] = pygame.time.get_ticks() + 10000  # 10 seconds
                sound_system.play_sound("powerup")
            elif self.food.effect == "shield":
                self.snake.shield = True
                self.snake.powerups["shield"] = pygame.time.get_ticks() + 8000  # 8 seconds
                sound_system.play_sound("powerup")
            elif self.food.effect == "glow":
                self.snake.glow_effect = True
                self.snake.powerups["glow"] = pygame.time.get_ticks() + 7000  # 7 seconds
                sound_system.play_sound("powerup")
            else:
                self.score += self.food.value
                
            # Normal food collection
            if not self.food.effect or self.food.effect not in ["shrink"]:
                self.snake.grow()
                sound_system.play_sound("eat")
                
                # Combo system
                self.combo += 1
                self.combo_timer = 180  # 3 seconds at 60 FPS
                if self.combo >= 5:
                    bonus = self.combo // 5
                    self.score += bonus
                    self.particle_system.add_explosion(
                        self.food.pos[0], self.food.pos[1], 
                        COLORS["GOLD"], 10 + bonus * 2
                    )
            else:
                self.combo = 0
                
            self.food.respawn()
            
            # Level progression
            if self.score >= self.level * 10:
                self.level += 1
                self.obstacle.generate()
                sound_system.play_sound("powerup")
                
    def update_combo(self):
        if self.combo_timer > 0:
            self.combo_timer -= 1
        elif self.combo > 0:
            self.combo = 0
            
    def draw_combo(self, surface):
        if self.combo > 1:
            combo_text = font_small.render(f"COMBO x{self.combo}!", True, COLORS["GOLD"])
            text_shadow = font_small.render(f"COMBO x{self.combo}!", True, COLORS["BLACK"])
            
            # Position above snake head
            head_pos = self.snake.body[0]
            text_x = head_pos[0] + BLOCK_SIZE//2 - combo_text.get_width()//2
            text_y = head_pos[1] - 40
            
            # Draw with shadow for better visibility
            surface.blit(text_shadow, (text_x + 2, text_y + 2))
            surface.blit(combo_text, (text_x, text_y))
            
            # Draw combo timer bar
            bar_width = 60 * (self.combo_timer / 180)
            pygame.draw.rect(surface, COLORS["GOLD"], (text_x + combo_text.get_width()//2 - 30, text_y + 30, bar_width, 5)))
            
    def draw_grid(self, surface):
        if self.grid_visible:
            for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
                pygame.draw.line(surface, (*COLORS["GRAY"], 30), (x, 0), (x, SCREEN_HEIGHT))
            for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
                pygame.draw.line(surface, (*COLORS["GRAY"], 30), (0, y), (SCREEN_WIDTH, y))
                
    def draw_hud(self, surface):
        # Score and level
        score_text = font_small.render(f"Score: {self.score}", True, COLORS["WHITE"])
        high_score_text = font_small.render(f"High Score: {self.high_score}", True, COLORS["YELLOW"])
        level_text = font_small.render(f"Level: {self.level}", True, COLORS["CYAN"])
        
        surface.blit(score_text, (10, 10))
        surface.blit(high_score_text, (10, 40))
        surface.blit(level_text, (10, 70))
        
        # Lives
        for i in range(self.lives):
            pygame.draw.rect(
                surface, COLORS["RED"], 
                (SCREEN_WIDTH - 40 - i * 30, 10, 25, 25), 
                border_radius=5
            )
            
        # FPS counter
        if self.settings["show_fps"]:
            fps_text = font_tiny.render(f"FPS: {self.fps}", True, COLORS["WHITE"])
            surface.blit(fps_text, (SCREEN_WIDTH - fps_text.get_width() - 10, SCREEN_HEIGHT - 30))
            
    def draw_pause_overlay(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        pause_text = font_large.render("PAUSED", True, COLORS["WHITE"])
        surface.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//3))
        
    def draw_game_over(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        game_over_text = font_large.render("GAME OVER", True, COLORS["RED"])
        score_text = font_medium.render(f"Final Score: {self.score}", True, COLORS["WHITE"])
        high_score_text = font_medium.render(f"High Score: {max(self.score, self.high_score)}", True, COLORS["YELLOW"])
        
        surface.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//4))
        surface.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        surface.blit(high_score_text, (SCREEN_WIDTH//2 - high_score_text.get_width()//2, SCREEN_HEIGHT//2))
        
    def draw_menu(self, surface):
        # Animated background
        for i in range(20):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(2, 5)
            alpha = random.randint(50, 150)
            pygame.draw.circle(
                surface, (*COLORS["PURPLE"], alpha), 
                (x, y), size
            )
        
        title_text = title_font.render("ULTIMATE SNAKE", True, COLORS["PURPLE"])
        shadow_text = title_font.render("ULTIMATE SNAKE", True, COLORS["BLACK"])
        
        # Draw with shadow for better visibility
        surface.blit(shadow_text, (SCREEN_WIDTH//2 - title_text.get_width()//2 + 3, 100 + 3))
        surface.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 100))
        
        version_text = font_tiny.render("Version 2.0", True, COLORS["WHITE"])
        surface.blit(version_text, (SCREEN_WIDTH - version_text.get_width() - 10, SCREEN_HEIGHT - 20))
        
        # Draw menu buttons
        for button in self.menu_buttons:
            button.draw(surface)
            
    def draw_settings(self, surface):
        surface.fill(self.backgrounds[self.current_bg])
        
        title_text = font_large.render("SETTINGS", True, COLORS["WHITE"])
        surface.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 50))
        
        # Draw settings options
        y_offset = 150
        option_spacing = 60
        
        # Sound Volume
        sound_text = font_medium.render("Sound Volume:", True, COLORS["WHITE"])
        surface.blit(sound_text, (SCREEN_WIDTH//2 - 200, y_offset))
        
        # Volume slider
        pygame.draw.rect(
            surface, COLORS["GRAY"], 
            (SCREEN_WIDTH//2 + 50, y_offset, 200, 30)
        )
        pygame.draw.rect(
            surface, COLORS["GREEN"], 
            (SCREEN_WIDTH//2 + 50, y_offset, int(200 * self.settings["sound_volume"]), 30)
        )
        
        # Music Volume
        music_text = font_medium.render("Music Volume:", True, COLORS["WHITE"])
        surface.blit(music_text, (SCREEN_WIDTH//2 - 200, y_offset + option_spacing))
        
        pygame.draw.rect(
            surface, COLORS["GRAY"], 
            (SCREEN_WIDTH//2 + 50, y_offset + option_spacing, 200, 30)
        )
        pygame.draw.rect(
            surface, COLORS["BLUE"], 
            (SCREEN_WIDTH//2 + 50, y_offset + option_spacing, int(200 * self.settings["music_volume"]), 30)
        )
        
        # Show FPS
        fps_text = font_medium.render("Show FPS Counter:", True, COLORS["WHITE"])
        surface.blit(fps_text, (SCREEN_WIDTH//2 - 200, y_offset + option_spacing * 2))
        
        fps_toggle_color = COLORS["GREEN"] if self.settings["show_fps"] else COLORS["RED"]
        pygame.draw.rect(
            surface, fps_toggle_color, 
            (SCREEN_WIDTH//2 + 50, y_offset + option_spacing * 2, 60, 30), 
            border_radius=5
        )
        fps_toggle_text = font_small.render("ON" if self.settings["show_fps"] else "OFF", True, COLORS["WHITE"])
        surface.blit(fps_toggle_text, (SCREEN_WIDTH//2 + 80 - fps_toggle_text.get_width()//2, 
                                     y_offset + option_spacing * 2 + 15 - fps_toggle_text.get_height()//2))
        
        # Background Selection
        bg_text = font_medium.render("Background:", True, COLORS["WHITE"])
        surface.blit(bg_text, (SCREEN_WIDTH//2 - 200, y_offset + option_spacing * 3))
        
        pygame.draw.rect(
            surface, self.backgrounds[self.current_bg], 
            (SCREEN_WIDTH//2 + 50, y_offset + option_spacing * 3, 60, 30)
        )
        bg_button_text = font_small.render("Change", True, COLORS["WHITE"])
        surface.blit(bg_button_text, (SCREEN_WIDTH//2 + 80 - bg_button_text.get_width()//2, 
                                    y_offset + option_spacing * 3 + 15 - bg_button_text.get_height()//2))
        
        # Snake Skin
        skin_text = font_medium.render("Snake Skin:", True, COLORS["WHITE"])
        surface.blit(skin_text, (SCREEN_WIDTH//2 - 200, y_offset + option_spacing * 4))
        
        pygame.draw.rect(
            surface, self.snake.skins[self.snake.skin_index]["body"], 
            (SCREEN_WIDTH//2 + 50, y_offset + option_spacing * 4, 60, 30)
        )
        skin_button_text = font_small.render("Change", True, COLORS["WHITE"])
        surface.blit(skin_button_text, (SCREEN_WIDTH//2 + 80 - skin_button_text.get_width()//2, 
                                      y_offset + option_spacing * 4 + 15 - skin_button_text.get_height()//2))
        
        # Difficulty
        difficulty_text = font_medium.render("Difficulty:", True, COLORS["WHITE"])
        surface.blit(difficulty_text, (SCREEN_WIDTH//2 - 200, y_offset + option_spacing * 5))
        
        difficulty_color = {
            "EASY": COLORS["GREEN"],
            "NORMAL": COLORS["YELLOW"],
            "HARD": COLORS["RED"]
        }[self.difficulty]
        
        pygame.draw.rect(
            surface, difficulty_color, 
            (SCREEN_WIDTH//2 + 50, y_offset + option_spacing * 5, 100, 30), 
            border_radius=5
        )
        difficulty_button_text = font_small.render(self.difficulty, True, COLORS["WHITE"])
        surface.blit(difficulty_button_text, (SCREEN_WIDTH//2 + 100 - difficulty_button_text.get_width()//2, 
                                             y_offset + option_spacing * 5 + 15 - difficulty_button_text.get_height()//2))
        
        # Draw back button
        for button in self.settings_buttons:
            button.draw(surface)
            
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        
        for event in pygame.event.get():
            if event.type == QUIT:
                self.save_highscore()
                self.save_settings()
                pygame.quit()
                sys.exit()
                
            if event.type == KEYDOWN:
                if self.state == GameState.PLAYING:
                    if event.key == K_ESCAPE or event.key == K_p:
                        self.state = GameState.PAUSED
                        sound_system.play_sound("click")
                    elif event.key == K_RIGHT or event.key == K_d:
                        self.snake.change_direction(Direction.RIGHT)
                    elif event.key == K_LEFT or event.key == K_a:
                        self.snake.change_direction(Direction.LEFT)
                    elif event.key == K_UP or event.key == K_w:
                        self.snake.change_direction(Direction.UP)
                    elif event.key == K_DOWN or event.key == K_s:
                        self.snake.change_direction(Direction.DOWN)
                    elif event.key == K_b:
                        self.current_bg = (self.current_bg + 1) % len(self.backgrounds)
                        sound_system.play_sound("click")
                    elif event.key == K_g:
                        self.grid_visible = not self.grid_visible
                        sound_system.play_sound("click")
                    elif event.key == K_SPACE:
                        self.snake.skin_index = (self.snake.skin_index + 1) % len(self.snake.skins)
                        sound_system.play_sound("click")
                        
                elif self.state == GameState.PAUSED:
                    if event.key == K_ESCAPE or event.key == K_p:
                        self.state = GameState.PLAYING
                        sound_system.play_sound("click")
                        
                elif self.state == GameState.MENU:
                    if event.key == K_RETURN:
                        self.state = GameState.PLAYING
                        self.reset()
                        sound_system.play_music("background")
                        sound_system.play_sound("click")
                        
                elif self.state == GameState.GAME_OVER:
                    if event.key == K_r:
                        self.state = GameState.PLAYING
                        self.reset()
                        sound_system.play_music("background")
                        sound_system.play_sound("click")
                    elif event.key == K_m:
                        self.state = GameState.MENU
                        sound_system.play_music("menu")
                        sound_system.play_sound("click")
                        
        # Handle button clicks
        if self.state == GameState.MENU:
            if self.menu_buttons[0].update(mouse_pos, mouse_click):  # Start Game
                self.state = GameState.PLAYING
                self.reset()
                sound_system.play_music("background")
                sound_system.play_sound("click")
            elif self.menu_buttons[1].update(mouse_pos, mouse_click):  # Settings
                self.state = GameState.SETTINGS
                sound_system.play_sound("click")
            elif self.menu_buttons[2].update(mouse_pos, mouse_click):  # Quit
                self.save_highscore()
                self.save_settings()
                pygame.quit()
                sys.exit()
                
        elif self.state == GameState.PAUSED:
            if self.pause_buttons[0].update(mouse_pos, mouse_click):  # Resume
                self.state = GameState.PLAYING
                sound_system.play_sound("click")
            elif self.pause_buttons[1].update(mouse_pos, mouse_click):  # Main Menu
                self.state = GameState.MENU
                sound_system.play_music("menu")
                sound_system.play_sound("click")
            elif self.pause_buttons[2].update(mouse_pos, mouse_click):  # Quit
                self.save_highscore()
                self.save_settings()
                pygame.quit()
                sys.exit()
                
        elif self.state == GameState.SETTINGS:
            if self.settings_buttons[0].update(mouse_pos, mouse_click):  # Back
                self.state = GameState.MENU
                self.save_settings()
                sound_system.play_sound("click")
                
            # Handle settings changes
            if mouse_click:
                # Sound volume slider
                if SCREEN_HEIGHT//2 + 50 <= mouse_pos[0] <= SCREEN_HEIGHT//2 + 250 and 150 <= mouse_pos[1] <= 180:
                    volume = (mouse_pos[0] - (SCREEN_HEIGHT//2 + 50)) / 200
                    self.settings["sound_volume"] = max(0, min(1, volume))
                    sound_system.set_volume(self.settings["sound_volume"])
                    sound_system.play_sound("click")
                    
                # Music volume slider
                if SCREEN_HEIGHT//2 + 50 <= mouse_pos[0] <= SCREEN_HEIGHT//2 + 250 and 210 <= mouse_pos[1] <= 240:
                    volume = (mouse_pos[0] - (SCREEN_HEIGHT//2 + 50)) / 200
                    self.settings["music_volume"] = max(0, min(1, volume))
                    pygame.mixer.music.set_volume(self.settings["music_volume"])
                    sound_system.play_sound("click")
                    
                # FPS toggle
                if SCREEN_HEIGHT//2 + 50 <= mouse_pos[0] <= SCREEN_HEIGHT//2 + 110 and 270 <= mouse_pos[1] <= 300:
                    self.settings["show_fps"] = not self.settings["show_fps"]
                    sound_system.play_sound("click")
                    
                # Background change
                if SCREEN_HEIGHT//2 + 50 <= mouse_pos[0] <= SCREEN_HEIGHT//2 + 110 and 330 <= mouse_pos[1] <= 360:
                    self.current_bg = (self.current_bg + 1) % len(self.backgrounds)
                    sound_system.play_sound("click")
                    
                # Snake skin change
                if SCREEN_HEIGHT//2 + 50 <= mouse_pos[0] <= SCREEN_HEIGHT//2 + 110 and 390 <= mouse_pos[1] <= 420:
                    self.snake.skin_index = (self.snake.skin_index + 1) % len(self.snake.skins)
                    sound_system.play_sound("click")
                    
                # Difficulty change
                if SCREEN_HEIGHT//2 + 50 <= mouse_pos[0] <= SCREEN_HEIGHT//2 + 150 and 450 <= mouse_pos[1] <= 480:
                    difficulties = ["EASY", "NORMAL", "HARD"]
                    current_index = difficulties.index(self.difficulty)
                    self.difficulty = difficulties[(current_index + 1) % len(difficulties)]
                    sound_system.play_sound("click")
                    
        elif self.state == GameState.GAME_OVER:
            if self.game_over_buttons[0].update(mouse_pos, mouse_click):  # Play Again
                self.state = GameState.PLAYING
                self.reset()
                sound_system.play_music("background")
                sound_system.play_sound("click")
            elif self.game_over_buttons[1].update(mouse_pos, mouse_click):  # Main Menu
                self.state = GameState.MENU
                sound_system.play_music("menu")
                sound_system.play_sound("click")
                
    def update(self):
        # Calculate FPS
        self.fps_counter += 1
        if pygame.time.get_ticks() - self.fps_timer >= 1000:
            self.fps = self.fps_counter
            self.fps_counter = 0
            self.fps_timer = pygame.time.get_ticks()
            
        if self.state == GameState.PLAYING:
            self.snake.move()
            self.food.update()
            self.obstacle.move()
            self.powerup.update()
            self.particle_system.update()
            self.update_combo()
            
            # Check for collisions
            if self.check_collision():
                sound_system.play_sound("crash")
                self.lives -= 1
                if self.lives <= 0:
                    self.state = GameState.GAME_OVER
                    self.save_highscore()
                    sound_system.stop_music()
                else:
                    # Reset snake but keep score
                    self.snake.reset()
                    
            self.check_food_collision()
            
    def draw(self):
        screen.fill(self.backgrounds[self.current_bg])
        
        if self.state == GameState.MENU:
            self.draw_menu(screen)
        elif self.state == GameState.PLAYING:
            self.draw_grid(screen)
            self.food.draw(screen)
            self.obstacle.draw(screen)
            self.snake.draw(screen)
            self.powerup.draw(screen)
            self.particle_system.draw(screen)
            self.draw_hud(screen)
            self.draw_combo(screen)
        elif self.state == GameState.PAUSED:
            self.draw_grid(screen)
            self.food.draw(screen)
            self.obstacle.draw(screen)
            self.snake.draw(screen)
            self.powerup.draw(screen)
            self.particle_system.draw(screen)
            self.draw_hud(screen)
            self.draw_pause_overlay(screen)
            
            # Draw pause menu buttons
            for button in self.pause_buttons:
                button.draw(screen)
        elif self.state == GameState.GAME_OVER:
            self.draw_grid(screen)
            self.food.draw(screen)
            self.obstacle.draw(screen)
            self.snake.draw(screen)
            self.powerup.draw(screen)
            self.particle_system.draw(screen)
            self.draw_hud(screen)
            self.draw_game_over(screen)
            
            # Draw game over buttons
            for button in self.game_over_buttons:
                button.draw(screen)
        elif self.state == GameState.SETTINGS:
            self.draw_settings(screen)
            
        pygame.display.flip()
        
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()
