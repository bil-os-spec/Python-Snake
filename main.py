import pygame
import sys
import random
import os
import math
import json
import time
from enum import Enum, auto
from collections import deque, defaultdict
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass
from pygame import gfxdraw
from pygame.locals import *

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
BLOCK_SIZE = 24
FPS = 60
BASE_SPEED = 15
MAX_SPEED = 60
MIN_SPEED = 5
GRID_WIDTH = SCREEN_WIDTH // BLOCK_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE

class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    SETTINGS = auto()
    SHOP = auto()
    STATS = auto()
    MODE_SELECT = auto()
    TUTORIAL = auto()
    LEVEL_COMPLETE = auto()

class GameMode(Enum):
    CLASSIC = auto()
    TIME_ATTACK = auto()
    SURVIVAL = auto()
    MULTIPLAYER = auto()
    CAMPAIGN = auto()

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    
    @staticmethod
    def opposite(dir1, dir2) -> bool:
        return (dir1.value[0] + dir2.value[0] == 0) and (dir1.value[1] + dir2.value[1] == 0)

# Enhanced color system with 150+ colors
COLORS = {
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "YELLOW": (255, 255, 0),
    "PURPLE": (128, 0, 128),
    "CYAN": (0, 255, 255),
    "ORANGE": (255, 165, 0),
    "PINK": (255, 192, 203),
    "GRAY": (128, 128, 128),
    "DARK_GREEN": (0, 100, 0),
    "DARK_RED": (139, 0, 0),
    "DARK_BLUE": (0, 0, 139),
    "LIGHT_BLUE": (173, 216, 230),
    "LIGHT_GREEN": (144, 238, 144),
    "LIGHT_RED": (255, 182, 193),
    "GOLD": (255, 215, 0),
    "SILVER": (192, 192, 192),
    "BRONZE": (205, 127, 50),
    "HOT_PINK": (255, 105, 180),
    "DEEP_PURPLE": (102, 51, 153),
    "DARK_CYAN": (0, 139, 139),
    "INDIGO": (75, 0, 130),
    "VIOLET": (238, 130, 238),
    "TEAL": (0, 128, 128),
    "OLIVE": (128, 128, 0),
    "MAROON": (128, 0, 0),
    "NAVY": (0, 0, 128),
    "AQUA": (0, 255, 255),
    "LIME": (0, 255, 0),
    "FUCHSIA": (255, 0, 255),
    "DARK_ORANGE": (255, 140, 0),
    "SPRING_GREEN": (0, 255, 127),
    "TURQUOISE": (64, 224, 208),
    "CRIMSON": (220, 20, 60),
    "CORAL": (255, 127, 80),
    "SALMON": (250, 128, 114),
    "KHAKI": (240, 230, 140),
    "LAVENDER": (230, 230, 250),
    "THISTLE": (216, 191, 216),
    "PLUM": (221, 160, 221),
    "ORCHID": (218, 112, 214),
    "TOMATO": (255, 99, 71),
    "PEACH_PUFF": (255, 218, 185),
    "SANDY_BROWN": (244, 164, 96),
    "CHOCOLATE": (210, 105, 30),
    "FIREBRICK": (178, 34, 34),
    "DARK_SLATE_GRAY": (47, 79, 79),
    "SEA_GREEN": (46, 139, 87),
    "MEDIUM_AQUAMARINE": (102, 205, 170),
    "CADET_BLUE": (95, 158, 160),
    "STEEL_BLUE": (70, 130, 180),
    "POWDER_BLUE": (176, 224, 230),
    "CORNFLOWER_BLUE": (100, 149, 237),
    "ROYAL_BLUE": (65, 105, 225),
    "MEDIUM_SLATE_BLUE": (123, 104, 238),
    "DARK_VIOLET": (148, 0, 211),
    "DARK_MAGENTA": (139, 0, 139),
    "DEEP_PINK": (255, 20, 147),
    "PALE_VIOLET_RED": (219, 112, 147),
    "MEDIUM_VIOLET_RED": (199, 21, 133),
    "DARK_SALMON": (233, 150, 122),
    "PERU": (205, 133, 63),
    "DARK_GOLDENROD": (184, 134, 11),
    "GOLDENROD": (218, 165, 32),
    "PALE_GOLDENROD": (238, 232, 170),
    "DARK_KHAKI": (189, 183, 107),
    "DARK_OLIVE_GREEN": (85, 107, 47),
    "FOREST_GREEN": (34, 139, 34),
    "LIME_GREEN": (50, 205, 50),
    "PALE_GREEN": (152, 251, 152),
    "MEDIUM_SPRING_GREEN": (0, 250, 154),
    "MEDIUM_SEA_GREEN": (60, 179, 113),
    "LIGHT_SEA_GREEN": (32, 178, 170),
    "DARK_TURQUOISE": (0, 206, 209),
    "MEDIUM_TURQUOISE": (72, 209, 204),
    "PALE_TURQUOISE": (175, 238, 238),
    "LIGHT_CYAN": (224, 255, 255),
    "AZURE": (240, 255, 255),
    "ALICE_BLUE": (240, 248, 255),
    "GHOST_WHITE": (248, 248, 255),
    "WHITE_SMOKE": (245, 245, 245),
    "SEASHELL": (255, 245, 238),
    "BEIGE": (245, 245, 220),
    "OLD_LACE": (253, 245, 230),
    "FLORAL_WHITE": (255, 250, 240),
    "IVORY": (255, 255, 240),
    "ANTIQUE_WHITE": (250, 235, 215),
    "LINEN": (250, 240, 230),
    "LAVENDER_BLUSH": (255, 240, 245),
    "MISTY_ROSE": (255, 228, 225),
    "GAINSBORO": (220, 220, 220),
    "LIGHT_GRAY": (211, 211, 211),
    "DARK_GRAY": (169, 169, 169),
    "DIM_GRAY": (105, 105, 105),
    "SLATE_GRAY": (112, 128, 144),
    "LIGHT_SLATE_GRAY": (119, 136, 153),
    "DARK_SLATE_GRAY": (47, 79, 79),
    "BLACK_OLIVE": (59, 60, 54),
    "JET": (52, 52, 52),
    "ONYX": (53, 56, 57),
    "CHARCOAL": (54, 69, 79),
    "DARK_JUNGLE_GREEN": (26, 36, 33),
    "EERIE_BLACK": (27, 27, 27),
    "RAISIN_BLACK": (36, 33, 36),
    "SMOKY_BLACK": (16, 12, 8),
    "BLACK_BEAN": (61, 12, 2),
    "BLACK_LEATHER_JACKET": (37, 53, 41),
    "BLACK_OLIVE": (59, 60, 54),
    "PHTHALO_GREEN": (18, 53, 36),
    "RICH_BLACK": (0, 17, 26),
    "BLUEBERRY": (79, 134, 247),
    "BUBBLEGUM": (255, 193, 204),
    "CANDY_APPLE_RED": (255, 8, 0),
    "COTTON_CANDY": (255, 188, 217),
    "ELECTRIC_LIME": (204, 255, 0),
    "FRENCH_VIOLET": (136, 6, 206),
    "GRAPE": (111, 45, 168),
    "JAZZBERRY_JAM": (165, 11, 94),
    "LEMON": (255, 247, 0),
    "MACARONI_AND_CHEESE": (255, 189, 136),
    "MANGO": (255, 195, 11),
    "NEON_CARROT": (255, 163, 67),
    "PINK_SHERBET": (247, 143, 167),
    "PUMPKIN": (255, 117, 24),
    "RADICAL_RED": (255, 53, 94),
    "RAZZMATAZZ": (227, 11, 92),
    "ROBIN_EGG_BLUE": (0, 204, 204),
    "SHOCKING_PINK": (252, 15, 192),
    "SUNGLOW": (255, 204, 51),
    "UNMELLOW_YELLOW": (255, 255, 102),
    "WILD_BLUE_YONDER": (162, 173, 208),
    "WILD_STRAWBERRY": (255, 67, 164),
    "WISTERIA": (201, 160, 220),
    "YELLOW_ORANGE": (255, 174, 66),
    "YELLOW_GREEN": (154, 205, 50),
    "ZAFFRE": (0, 20, 168),
    "ZINNWALDITE_BROWN": (44, 22, 8),
    "ZYTHUM": (237, 224, 177),
}

@dataclass
class Particle:
    pos: List[float]
    velocity: List[float]
    color: Tuple[int, int, int]
    lifetime: int
    size: float
    gravity: float = 0
    max_lifetime: int = 0
    alpha: int = 255
    shrink: bool = True
    fade: bool = True
    
    def __post_init__(self):
        self.max_lifetime = self.lifetime
        self.original_size = self.size
        
    def update(self):
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.velocity[1] += self.gravity
        self.lifetime -= 1
        
        if self.fade:
            self.alpha = int(255 * (self.lifetime / self.max_lifetime))
        if self.shrink:
            self.size = self.original_size * (self.lifetime / self.max_lifetime)
        
    def draw(self, surface):
        if self.lifetime > 0:
            alpha_color = (*self.color[:3], self.alpha) if len(self.color) == 4 else (*self.color, self.alpha)
            pygame.gfxdraw.filled_circle(surface, int(self.pos[0]), int(self.pos[1]), int(self.size), alpha_color)

class ParticleSystem:
    def __init__(self):
        self.particles: List[Particle] = []
        
    def add_particle(self, particle: Particle):
        self.particles.append(particle)
        
    def add_explosion(self, x: float, y: float, color: Tuple[int, int, int], count: int = 20, 
                     min_speed: float = 0.5, max_speed: float = 3, size_range: Tuple[int, int] = (2, 5),
                     lifetime_range: Tuple[int, int] = (30, 90), gravity: float = 0.1):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(min_speed, max_speed)
            velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            lifetime = random.randint(*lifetime_range)
            size = random.randint(*size_range)
            self.particles.append(Particle([x, y], velocity, color, lifetime, size, gravity))
            
    def add_firework(self, x: float, y: float, primary_color: Tuple[int, int, int], 
                    secondary_color: Tuple[int, int, int], count: int = 100):
        # Initial explosion
        self.add_explosion(x, y, primary_color, count//2, 2, 5, (3, 6), (40, 80), 0.05)
        
        # Secondary particles
        for _ in range(count//2):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.2, 1.5)
            velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            lifetime = random.randint(60, 120)
            size = random.randint(1, 3)
            self.particles.append(
                Particle([x, y], velocity, secondary_color, lifetime, size, 0.05, 
                shrink=False, fade=True)
            )
            
    def add_trail(self, x: float, y: float, color: Tuple[int, int, int], count: int = 5, 
                 size: int = 3, lifetime: int = 20):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.1, 0.5)
            velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            self.particles.append(
                Particle([x, y], velocity, color, lifetime, size, 0.02, 
                shrink=True, fade=True)
            )
            
    def update(self):
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update()
            
    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)

class SoundSystem:
    def __init__(self):
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_tracks: Dict[str, str] = {}
        self.muted: bool = False
        self.volume: float = 0.5
        self.current_music: Optional[str] = None
        self.sound_volume: float = 0.7
        self.music_volume: float = 0.5
        
    def load_sound(self, name: str, path: str) -> None:
        try:
            self.sounds[name] = pygame.mixer.Sound(path)
            self.sounds[name].set_volume(self.sound_volume)
        except Exception as e:
            print(f"Failed to load sound {path}: {e}")
            
    def load_music(self, name: str, path: str) -> None:
        self.music_tracks[name] = path
        
    def play_sound(self, name: str, loops: int = 0, volume: Optional[float] = None) -> None:
        if not self.muted and name in self.sounds:
            if volume is not None:
                self.sounds[name].set_volume(min(1.0, max(0.0, volume)) * self.sound_volume)
            self.sounds[name].play(loops)
            
    def play_music(self, name: str, loops: int = -1, fade_ms: int = 0) -> None:
        if not self.muted and name in self.music_tracks:
            pygame.mixer.music.load(self.music_tracks[name])
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops, fade_ms=fade_ms)
            self.current_music = name
            
    def stop_music(self, fade_ms: int = 0) -> None:
        pygame.mixer.music.fadeout(fade_ms)
        self.current_music = None
        
    def toggle_mute(self) -> None:
        self.muted = not self.muted
        pygame.mixer.music.set_volume(0 if self.muted else self.music_volume)
        for sound in self.sounds.values():
            sound.set_volume(0 if self.muted else self.sound_volume)
            
    def set_sound_volume(self, volume: float) -> None:
        self.sound_volume = max(0, min(1, volume))
        if not self.muted:
            for sound in self.sounds.values():
                sound.set_volume(self.sound_volume)
                
    def set_music_volume(self, volume: float) -> None:
        self.music_volume = max(0, min(1, volume))
        if not self.muted:
            pygame.mixer.music.set_volume(self.music_volume)

@dataclass
class SnakeSkin:
    name: str
    body: Tuple[int, int, int]
    head: Tuple[int, int, int]
    eye: Tuple[int, int, int] = COLORS["WHITE"]
    pupil: Tuple[int, int, int] = COLORS["BLACK"]
    unlocked: bool = False
    price: int = 0
    special_effect: Optional[str] = None

class Snake:
    def __init__(self, player_num: int = 1):
        self.reset()
        self.player_num = player_num
        self.skin_index = 0
        self.skins = [
            SnakeSkin("Classic", COLORS["GREEN"], COLORS["DARK_GREEN"], unlocked=True),
            SnakeSkin("Purple Haze", COLORS["PURPLE"], COLORS["DEEP_PURPLE"], unlocked=False, price=100),
            SnakeSkin("Cyan Storm", COLORS["CYAN"], COLORS["DARK_CYAN"], unlocked=False, price=150),
            SnakeSkin("Golden", COLORS["GOLD"], COLORS["DARK_ORANGE"], unlocked=False, price=250, special_effect="glow"),
            SnakeSkin("Rainbow", COLORS["RED"], COLORS["VIOLET"], unlocked=False, price=500, special_effect="rainbow"),
            SnakeSkin("Neon Pink", COLORS["HOT_PINK"], COLORS["DEEP_PINK"], unlocked=False, price=200),
            SnakeSkin("Electric Blue", COLORS["LIGHT_BLUE"], COLORS["ROYAL_BLUE"], unlocked=False, price=200),
            SnakeSkin("Fire", COLORS["RED"], COLORS["DARK_ORANGE"], unlocked=False, price=300, special_effect="fire"),
            SnakeSkin("Ice", COLORS["LIGHT_BLUE"], COLORS["DARK_TURQUOISE"], unlocked=False, price=300, special_effect="ice"),
        ]
        self.tongue_out = False
        self.tongue_timer = 0
        self.tail_history = deque(maxlen=20)
        self.glow_effect = False
        self.glow_timer = 0
        self.glow_colors = [COLORS["RED"], COLORS["ORANGE"], COLORS["YELLOW"], 
                          COLORS["GREEN"], COLORS["BLUE"], COLORS["INDIGO"], COLORS["VIOLET"]]
        self.trail_particles = []
        self.rainbow_timer = 0
        self.fire_timer = 0
        self.ice_timer = 0
        
    def reset(self) -> None:
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
        self.trail_particles.clear()
        
    def move(self) -> None:
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time < 1000 // self.speed:
            return
            
        self.last_move_time = current_time
        self.direction = self.next_direction
        
        # Add current head position to tail history for smooth movement
        self.tail_history.appendleft(self.body[0].copy())
        
        head = self.body[0].copy()
        dx, dy = self.direction.value
        head[0] += dx * BLOCK_SIZE
        head[1] += dy * BLOCK_SIZE
            
        self.body.insert(0, head)
        
        if self.growth_pending > 0:
            self.growth_pending -= 1
        else:
            if len(self.body) > self.length:
                if len(self.body) > 1:
                    tail = self.body[-1]
                    # Add trail particles when moving
                    self.trail_particles.append({
                        'pos': tail.copy(),
                        'timer': 15,
                        'color': self.skins[self.skin_index].body,
                        'size': BLOCK_SIZE // 2
                    })
                self.body.pop()
                
        # Tongue animation
        self.tongue_timer = (self.tongue_timer + 1) % 60
        self.tongue_out = self.tongue_timer < 10
        
        # Special effects timers
        if self.glow_effect:
            self.glow_timer = (self.glow_timer + 1) % len(self.glow_colors)
            
        if self.skins[self.skin_index].special_effect == "rainbow":
            self.rainbow_timer = (self.rainbow_timer + 1) % 360
            
        if self.skins[self.skin_index].special_effect == "fire":
            self.fire_timer = (self.fire_timer + 1) % 10
            if self.fire_timer == 0:
                self._add_fire_particles()
                
        if self.skins[self.skin_index].special_effect == "ice":
            self.ice_timer = (self.ice_timer + 1) % 15
            if self.ice_timer == 0:
                self._add_ice_particles()
        
        # Update trail particles
        for p in self.trail_particles:
            p['timer'] -= 1
            p['size'] = max(0, p['size'] - 0.5)
        self.trail_particles = [p for p in self.trail_particles if p['timer'] > 0]
        
    def _add_fire_particles(self):
        for segment in self.body[:5]:  # Add fire to head and first few segments
            for _ in range(2):
                angle = random.uniform(math.pi, math.pi * 2)  # Fire goes up
                speed = random.uniform(0.5, 1.5)
                velocity = [math.cos(angle) * speed * 0.5, math.sin(angle) * speed]
                lifetime = random.randint(20, 40)
                size = random.randint(2, 4)
                color = random.choice([
                    COLORS["RED"],
                    COLORS["DARK_ORANGE"],
                    COLORS["ORANGE"],
                    COLORS["YELLOW"]
                ])
                self.trail_particles.append({
                    'pos': [segment[0] + random.randint(0, BLOCK_SIZE), 
                           segment[1] + random.randint(0, BLOCK_SIZE)],
                    'timer': lifetime,
                    'color': color,
                    'size': size
                })
                
    def _add_ice_particles(self):
        for segment in self.body[:10]:  # Add ice particles to first 10 segments
            if random.random() < 0.3:  # 30% chance to add a particle
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(0.1, 0.3)
                velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                lifetime = random.randint(30, 60)
                size = random.randint(1, 3)
                color = random.choice([
                    COLORS["LIGHT_BLUE"],
                    COLORS["CYAN"],
                    COLORS["POWDER_BLUE"],
                    COLORS["WHITE"]
                ])
                self.trail_particles.append({
                    'pos': [segment[0] + random.randint(0, BLOCK_SIZE), 
                           segment[1] + random.randint(0, BLOCK_SIZE)],
                    'timer': lifetime,
                    'color': color,
                    'size': size
                })
    
    def change_direction(self, new_direction: Direction) -> None:
        if not Direction.opposite(self.direction, new_direction):
            self.next_direction = new_direction
            
    def grow(self, amount: int = 1) -> None:
        self.growth_pending += amount
        self.length += amount
        self.speed = min(self.speed + 0.2, MAX_SPEED)
        
    def shrink(self, amount: int = 1) -> None:
        self.length = max(1, self.length - amount)
        self.speed = max(self.speed - 1, MIN_SPEED)
        
    def draw(self, surface) -> None:
        skin = self.skins[self.skin_index]
        
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
        
        # Draw snake body with smooth movement interpolation
        for index, block in enumerate(self.body):
            if index < len(self.tail_history):
                ratio = index / len(self.body)
                interp_x = block[0] * ratio + self.tail_history[index][0] * (1 - ratio)
                interp_y = block[1] * ratio + self.tail_history[index][1] * (1 - ratio)
                draw_pos = [interp_x, interp_y]
            else:
                draw_pos = block
                
            if index == 0:
                self._draw_head(surface, draw_pos, skin)
            else:
                self._draw_body_segment(surface, draw_pos, skin, index)
                
    def _draw_body_segment(self, surface, pos, skin, index):
        # Special effects
        if skin.special_effect == "glow" or self.glow_effect:
            glow_color = self.glow_colors[self.glow_timer]
            pygame.gfxdraw.filled_circle(
                surface, 
                pos[0] + BLOCK_SIZE // 2, 
                pos[1] + BLOCK_SIZE // 2, 
                BLOCK_SIZE // 2 + 2, 
                (*glow_color, 100)
            )
            
        if skin.special_effect == "rainbow":
            hue = (self.rainbow_timer + index * 10) % 360
            rainbow_color = pygame.Color(0, 0, 0)
            rainbow_color.hsva = (hue, 100, 100, 100)
            body_color = rainbow_color[:3]
        else:
            body_color = skin.body
            
        # Draw main body segment
        pygame.draw.rect(surface, body_color, (pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE), border_radius=4)
        
        # Draw inner highlight
        inner_size = BLOCK_SIZE - 4
        inner_color = (
            min(body_color[0] + 30, 255),
            min(body_color[1] + 30, 255),
            min(body_color[2] + 30, 255)
        )
        pygame.draw.rect(
            surface, inner_color, 
            (pos[0] + 2, pos[1] + 2, inner_size, inner_size),
            border_radius=2
        )
        
        # Draw shield effect if active
        if self.shield:
            shield_size = BLOCK_SIZE + 4
            shield_alpha = 100 + int(155 * (math.sin(pygame.time.get_ticks() / 200) + 1) / 2)
            shield_surface = pygame.Surface((shield_size, shield_size), pygame.SRCALPHA)
            pygame.draw.rect(
                shield_surface, (*COLORS["LIGHT_BLUE"], shield_alpha),
                (0, 0, shield_size, shield_size), border_radius=6
            )
            surface.blit(shield_surface, (pos[0] - 2, pos[1] - 2))
            
    def _draw_head(self, surface, pos, skin):
        # Special head color for rainbow effect
        if skin.special_effect == "rainbow":
            hue = self.rainbow_timer % 360
            rainbow_color = pygame.Color(0, 0, 0)
            rainbow_color.hsva = (hue, 100, 100, 100)
            head_color = rainbow_color[:3]
        else:
            head_color = skin.head
            
        # Draw head
        pygame.draw.rect(
            surface, head_color, 
            (pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE),
            border_radius=6
        )
        
        # Draw eyes
        eye_size = BLOCK_SIZE // 4
        pupil_size = eye_size // 2
        
        dx, dy = self.direction.value
        if dx > 0:  # Right
            left_eye_pos = (pos[0] + BLOCK_SIZE - eye_size - 4, pos[1] + 6)
            right_eye_pos = (pos[0] + BLOCK_SIZE - eye_size - 4, pos[1] + BLOCK_SIZE - 6 - eye_size)
        elif dx < 0:  # Left
            left_eye_pos = (pos[0] + 4, pos[1] + 6)
            right_eye_pos = (pos[0] + 4, pos[1] + BLOCK_SIZE - 6 - eye_size)
        elif dy < 0:  # Up
            left_eye_pos = (pos[0] + 6, pos[1] + 4)
            right_eye_pos = (pos[0] + BLOCK_SIZE - 6 - eye_size, pos[1] + 4)
        else:  # Down
            left_eye_pos = (pos[0] + 6, pos[1] + BLOCK_SIZE - eye_size - 4)
            right_eye_pos = (pos[0] + BLOCK_SIZE - 6 - eye_size, pos[1] + BLOCK_SIZE - eye_size - 4)
            
        pygame.draw.rect(surface, skin.eye, (*left_eye_pos, eye_size, eye_size), border_radius=eye_size//2)
        pygame.draw.rect(surface, skin.eye, (*right_eye_pos, eye_size, eye_size), border_radius=eye_size//2)
        
        pygame.draw.rect(surface, skin.pupil, 
                        (left_eye_pos[0] + (eye_size - pupil_size)//2, 
                         left_eye_pos[1] + (eye_size - pupil_size)//2, 
                         pupil_size, pupil_size), border_radius=pupil_size//2)
        pygame.draw.rect(surface, skin.pupil, 
                        (right_eye_pos[0] + (eye_size - pupil_size)//2, 
                         right_eye_pos[1] + (eye_size - pupil_size)//2, 
                         pupil_size, pupil_size), border_radius=pupil_size//2)
        
        # Draw tongue if out
        if self.tongue_out:
            tongue_length = BLOCK_SIZE // 2
            tongue_width = BLOCK_SIZE // 6
            tongue_base = (pos[0] + BLOCK_SIZE // 2, pos[1] + BLOCK_SIZE // 2)
            
            if self.direction == Direction.RIGHT:
                points = [
                    tongue_base,
                    (tongue_base[0] + tongue_length, tongue_base[1] - tongue_width),
                    (tongue_base[0] + tongue_length, tongue_base[1] + tongue_width)
                ]
            elif self.direction == Direction.LEFT:
                points = [
                    tongue_base,
                    (tongue_base[0] - tongue_length, tongue_base[1] - tongue_width),
                    (tongue_base[0] - tongue_length, tongue_base[1] + tongue_width)
                ]
            elif self.direction == Direction.UP:
                points = [
                    tongue_base,
                    (tongue_base[0] - tongue_width, tongue_base[1] - tongue_length),
                    (tongue_base[0] + tongue_width, tongue_base[1] - tongue_length)
                ]
            else:  # DOWN
                points = [
                    tongue_base,
                    (tongue_base[0] - tongue_width, tongue_base[1] + tongue_length),
                    (tongue_base[0] + tongue_width, tongue_base[1] + tongue_length)
                ]
                
            pygame.draw.polygon(surface, COLORS["HOT_PINK"], points)

@dataclass
class FoodType:
    name: str
    color: Tuple[int, int, int]
    value: int
    rarity: int
    effect: Optional[str] = None
    expires: bool = False
    duration: int = 0
    special_visual: Optional[str] = None
    sound: Optional[str] = None

class FoodSystem:
    def __init__(self, count: int = 1):
        self.food_items: List[Dict[str, Any]] = []
        self.types = [
            FoodType("normal", COLORS["GREEN"], 1, 60),
            FoodType("speed", COLORS["CYAN"], 2, 15, "speed_boost", False, 0, "symbol", "powerup"),
            FoodType("slow", COLORS["BLUE"], 2, 10, "slow_down", False, 0, "symbol", "powerup"),
            FoodType("invincible", COLORS["GOLD"], 3, 8, "invincible", True, 15000, "glow", "powerup"),
            FoodType("shield", COLORS["LIGHT_BLUE"], 3, 8, "shield", True, 10000, "ring", "powerup"),
            FoodType("glow", COLORS["PURPLE"], 3, 5, "glow", True, 20000, "pulse", "powerup"),
            FoodType("golden", COLORS["GOLD"], 5, 5, None, False, 0, "star", "coin"),
            FoodType("rainbow", COLORS["RED"], 10, 2, "score_multiplier", True, 10000, "rainbow", "special"),
            FoodType("poison", COLORS["DARK_GREEN"], -1, 12, "shrink", False, 0, "skull", "negative"),
            FoodType("combo", COLORS["ORANGE"], 0, 8, "combo_boost", False, 0, "combo", "powerup"),
            FoodType("bomb", COLORS["DARK_RED"], -2, 5, "bomb", False, 0, "bomb", "negative"),
        ]
        self.rainbow_colors = [COLORS["RED"], COLORS["ORANGE"], COLORS["YELLOW"], 
                             COLORS["GREEN"], COLORS["BLUE"], COLORS["INDIGO"], COLORS["VIOLET"]]
        for _ in range(count):
            self.food_items.append(self._create_food())
            
    def _create_food(self) -> Dict[str, Any]:
        total_rarity = sum(food.rarity for food in self.types)
        r = random.uniform(0, total_rarity)
        upto = 0
        
        for food_type in self.types:
            if upto + food_type.rarity >= r:
                food = {
                    "type": food_type.name,
                    "color": food_type.color,
                    "value": food_type.value,
                    "effect": food_type.effect,
                    "pos": [
                        random.randrange(BLOCK_SIZE, SCREEN_WIDTH - BLOCK_SIZE, BLOCK_SIZE),
                        random.randrange(BLOCK_SIZE, SCREEN_HEIGHT - BLOCK_SIZE, BLOCK_SIZE)
                    ],
                    "spawn_time": pygame.time.get_ticks(),
                    "spawn_animation": True,
                    "animation_timer": 0,
                    "expires": food_type.expires,
                    "duration": food_type.duration,
                    "special_visual": food_type.special_visual,
                    "sound": food_type.sound,
                    "rotation": 0,
                    "pulse_timer": 0,
                    "pulse_direction": 1
                }
                
                if food_type.name == "rainbow":
                    food["current_color_index"] = 0
                    
                return food
            upto += food_type.rarity
        return self._create_food()  # Fallback
        
    def respawn(self, index: int = 0) -> None:
        if index < len(self.food_items):
            self.food_items[index] = self._create_food()
            
    def update(self) -> None:
        for food in self.food_items:
            # Rainbow color cycling
            if food["type"] == "rainbow":
                food["current_color_index"] = (food.get("current_color_index", 0) + 1) % len(self.rainbow_colors)
                food["color"] = self.rainbow_colors[food["current_color_index"]]
                
            # Spawn animation
            if food["spawn_animation"]:
                food["animation_timer"] += 1
                if food["animation_timer"] > 30:
                    food["spawn_animation"] = False
                    
            # Expiration timer
            if food.get("expires", False):
                if pygame.time.get_ticks() - food["spawn_time"] > food.get("duration", 10000):
                    self.respawn(self.food_items.index(food))
                    
            # Rotation for special foods
            if food.get("special_visual") in ["star", "combo", "bomb"]:
                food["rotation"] = (food.get("rotation", 0) + 1) % 360
                
            # Pulse animation
            if food.get("special_visual") == "pulse":
                food["pulse_timer"] += food["pulse_direction"] * 0.1
                if food["pulse_timer"] > 1 or food["pulse_timer"] < 0:
                    food["pulse_direction"] *= -1
                    
    def draw(self, surface) -> None:
        for food in self.food_items:
            size = BLOCK_SIZE
            
            if food["spawn_animation"]:
                size = int(BLOCK_SIZE * (food["animation_timer"] / 30))
                
            x, y = food["pos"][0] + (BLOCK_SIZE - size) // 2, food["pos"][1] + (BLOCK_SIZE - size) // 2
            
            # Draw different food types with special visuals
            if food["type"] == "golden":
                self._draw_golden_food(surface, x, y, size, food)
            elif food["type"] == "rainbow":
                self._draw_rainbow_food(surface, x, y, size, food)
            elif food.get("special_visual") == "symbol":
                self._draw_symbol_food(surface, x, y, size, food)
            elif food.get("special_visual") == "glow":
                self._draw_glow_food(surface, x, y, size, food)
            elif food.get("special_visual") == "ring":
                self._draw_ring_food(surface, x, y, size, food)
            elif food.get("special_visual") == "pulse":
                self._draw_pulse_food(surface, x, y, size, food)
            elif food.get("special_visual") == "star":
                self._draw_star_food(surface, x, y, size, food)
            elif food.get("special_visual") == "combo":
                self._draw_combo_food(surface, x, y, size, food)
            elif food.get("special_visual") == "bomb":
                self._draw_bomb_food(surface, x, y, size, food)
            elif food.get("special_visual") == "skull":
                self._draw_skull_food(surface, x, y, size, food)
            else:
                pygame.draw.rect(surface, food["color"], (x, y, size, size), border_radius=size//2)
                
    def _draw_golden_food(self, surface, x, y, size, food):
        pygame.draw.rect(surface, food["color"], (x, y, size, size), border_radius=size//2)
        center_x, center_y = x + size//2, y + size//2
        
        # Draw star shape
        star_points = []
        for i in range(5):
            angle = math.radians(food.get("rotation", 0) + i * 72 - 90)
            outer_x = center_x + math.cos(angle) * size//3
            outer_y = center_y + math.sin(angle) * size//3
            star_points.append((outer_x, outer_y))
            
            inner_angle = angle + math.radians(36)
            inner_x = center_x + math.cos(inner_angle) * size//6
            inner_y = center_y + math.sin(inner_angle) * size//6
            star_points.append((inner_x, inner_y))
            
        pygame.draw.polygon(surface, COLORS["YELLOW"], star_points)
        
    def _draw_rainbow_food(self, surface, x, y, size, food):
        pygame.draw.rect(surface, food["color"], (x, y, size, size), border_radius=size//2)
        for i in range(3):
            ring_color = self.rainbow_colors[(food.get("current_color_index", 0) + i*2) % len(self.rainbow_colors)]
            ring_size = size - i*4 - 2
            pygame.draw.rect(
                surface, ring_color, 
                (x + i*2 + 1, y + i*2 + 1, ring_size, ring_size), 
                border_radius=ring_size//2, 
                width=2
            )
            
    def _draw_symbol_food(self, surface, x, y, size, food):
        pygame.draw.rect(surface, food["color"], (x, y, size, size), border_radius=size//2)
        symbol_size = size // 2
        symbol_x, symbol_y = x + (size - symbol_size) // 2, y + (size - symbol_size) // 2
        
        if food["type"] == "speed":
            pygame.draw.polygon(
                surface, COLORS["WHITE"], 
                [(symbol_x, symbol_y), 
                 (symbol_x + symbol_size, symbol_y + symbol_size//2),
                 (symbol_x, symbol_y + symbol_size)]
            )
        elif food["type"] == "slow":
            pygame.draw.line(
                surface, COLORS["WHITE"],
                (symbol_x, symbol_y + symbol_size//2),
                (symbol_x + symbol_size, symbol_y + symbol_size//2),
                3
            )
        elif food["type"] == "combo":
            font = pygame.font.SysFont("Arial", symbol_size, bold=True)
            text = font.render("C", True, COLORS["WHITE"])
            surface.blit(text, (symbol_x, symbol_y))
            
    def _draw_glow_food(self, surface, x, y, size, food):
        glow_size = int(size * 1.5)
        glow_x, glow_y = x - (glow_size - size)//2, y - (glow_size - size)//2
        glow_alpha = 100 + int(155 * (math.sin(pygame.time.get_ticks() / 200) + 1) / 2)
        glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        pygame.draw.rect(
            glow_surface, (*food["color"], glow_alpha),
            (0, 0, glow_size, glow_size), border_radius=glow_size//2
        )
        surface.blit(glow_surface, (glow_x, glow_y))
        pygame.draw.rect(surface, food["color"], (x, y, size, size), border_radius=size//2)
        
    def _draw_ring_food(self, surface, x, y, size, food):
        pygame.draw.rect(surface, food["color"], (x, y, size, size), border_radius=size//2)
        ring_size = size - 4
        pygame.draw.rect(
            surface, COLORS["WHITE"], 
            (x + 2, y + 2, ring_size, ring_size), 
            border_radius=ring_size//2, 
            width=2
        )
        
    def _draw_pulse_food(self, surface, x, y, size, food):
        pulse_size = int(size * (0.8 + food["pulse_timer"] * 0.2))
        pulse_x, pulse_y = x + (size - pulse_size)//2, y + (size - pulse_size)//2
        pygame.draw.rect(surface, food["color"], (pulse_x, pulse_y, pulse_size, pulse_size), border_radius=pulse_size//2)
        
    def _draw_star_food(self, surface, x, y, size, food):
        pygame.draw.rect(surface, food["color"], (x, y, size, size), border_radius=size//2)
        center_x, center_y = x + size//2, y + size//2
        
        # Draw rotating star
        star_points = []
        for i in range(5):
            angle = math.radians(food["rotation"] + i * 72 - 90)
            outer_x = center_x + math.cos(angle) * size//3
            outer_y = center_y + math.sin(angle) * size//3
            star_points.append((outer_x, outer_y))
            
            inner_angle = angle + math.radians(36)
            inner_x = center_x + math.cos(inner_angle) * size//6
            inner_y = center_y + math.sin(inner_angle) * size//6
            star_points.append((inner_x, inner_y))
            
        pygame.draw.polygon(surface, COLORS["WHITE"], star_points)
        
    def _draw_combo_food(self, surface, x, y, size, food):
        pygame.draw.rect(surface, food["color"], (x, y, size, size), border_radius=size//2)
        center_x, center_y = x + size//2, y + size//2
        
        # Draw combo symbol (C with +)
        font = pygame.font.SysFont("Arial", size//2, bold=True)
        text_c = font.render("C", True, COLORS["WHITE"])
        text_plus = font.render("+", True, COLORS["WHITE"])
        
        surface.blit(text_c, (center_x - size//3, center_y - size//4))
        surface.blit(text_plus, (center_x, center_y - size//4))
        
    def _draw_bomb_food(self, surface, x, y, size, food):
        pygame.draw.rect(surface, food["color"], (x, y, size, size), border_radius=size//2)
        center_x, center_y = x + size//2, y + size//2
        
        # Draw bomb symbol
        pygame.draw.circle(surface, COLORS["BLACK"], (center_x, center_y - size//8), size//4)
        pygame.draw.line(
            surface, COLORS["BLACK"],
            (center_x, center_y - size//8 - size//4),
            (center_x, center_y - size//8 - size//3),
            2
        )
        
    def _draw_skull_food(self, surface, x, y, size, food):
        pygame.draw.rect(surface, food["color"], (x, y, size, size), border_radius=size//2)
        center_x, center_y = x + size//2, y + size//2
        
        # Draw skull symbol
        pygame.draw.circle(surface, COLORS["WHITE"], (center_x - size//6, center_y - size//6), size//6)
        pygame.draw.circle(surface, COLORS["WHITE"], (center_x + size//6, center_y - size//6), size//6)
        pygame.draw.rect(
            surface, COLORS["WHITE"],
            (center_x - size//4, center_y, size//2, size//3)
        )
        pygame.draw.circle(surface, COLORS["BLACK"], (center_x - size//6, center_y - size//6), size//12)
        pygame.draw.circle(surface, COLORS["BLACK"], (center_x + size//6, center_y - size//6), size//12)
        pygame.draw.line(
            surface, COLORS["BLACK"],
            (center_x - size//4, center_y + size//8),
            (center_x + size//4, center_y + size//8),
            2
        )

class Obstacle:
    def __init__(self):
        self.blocks = []
        self.moving = False
        self.direction = Direction.RIGHT
        self.move_timer = 0
        self.move_delay = 500  # ms
        self.generate()
        
    def generate(self, count=10):
        self.blocks = []
        for _ in range(count):
            x = random.randrange(0, SCREEN_WIDTH, BLOCK_SIZE)
            y = random.randrange(0, SCREEN_HEIGHT, BLOCK_SIZE)
            # Make sure obstacle doesn't spawn on snake or food
            if (x != SCREEN_WIDTH//2 and y != SCREEN_HEIGHT//2 and 
                abs(x - SCREEN_WIDTH//2) > BLOCK_SIZE*3 and 
                abs(y - SCREEN_HEIGHT//2) > BLOCK_SIZE*3):
                self.blocks.append([x, y])
                
    def move(self):
        if not self.moving:
            return
            
        current_time = pygame.time.get_ticks()
        if current_time - self.move_timer < self.move_delay:
            return
            
        self.move_timer = current_time
        
        dx, dy = self.direction.value
        for block in self.blocks:
            block[0] += dx * BLOCK_SIZE
            block[1] += dy * BLOCK_SIZE
            
            # Wrap around screen edges
            if block[0] >= SCREEN_WIDTH:
                block[0] = 0
            elif block[0] < 0:
                block[0] = SCREEN_WIDTH - BLOCK_SIZE
                
            if block[1] >= SCREEN_HEIGHT:
                block[1] = 0
            elif block[1] < 0:
                block[1] = SCREEN_HEIGHT - BLOCK_SIZE
                
        # Randomly change direction occasionally
        if random.random() < 0.05:
            self.direction = random.choice(list(Direction))
            
    def draw(self, surface):
        for block in self.blocks:
            pygame.draw.rect(surface, COLORS["GRAY"], (block[0], block[1], BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(surface, COLORS["DARK_GRAY"], (block[0]+2, block[1]+2, BLOCK_SIZE-4, BLOCK_SIZE-4))

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 color: Tuple[int, int, int], hover_color: Tuple[int, int, int], 
                 text_color: Tuple[int, int, int] = COLORS["WHITE"], font=None,
                 border_radius: int = 10, outline: bool = True, 
                 outline_color: Tuple[int, int, int] = COLORS["WHITE"],
                 outline_hover_color: Tuple[int, int, int] = COLORS["YELLOW"],
                 sound: Optional[str] = "click"):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font or font_medium
        self.is_hovered = False
        self.clicked = False
        self.border_radius = border_radius
        self.outline = outline
        self.outline_color = outline_color
        self.outline_hover_color = outline_hover_color
        self.sound = sound
        self.pulse_timer = 0
        self.pulse_speed = 0.05
        
    def draw(self, surface) -> None:
        color = self.hover_color if self.is_hovered else self.color
        outline_color = self.outline_hover_color if self.is_hovered else self.outline_color
        
        # Draw pulsing effect if hovered
        if self.is_hovered:
            self.pulse_timer += self.pulse_speed
            pulse_alpha = int(100 * (math.sin(self.pulse_timer) + 1) / 2)
            pulse_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(
                pulse_surface, (*outline_color[:3], pulse_alpha),
                (0, 0, self.rect.width, self.rect.height),
                border_radius=self.border_radius
            )
            surface.blit(pulse_surface, (self.rect.x, self.rect.y))
        
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        
        if self.outline:
            pygame.draw.rect(
                surface, outline_color, self.rect, 
                2, border_radius=self.border_radius
            )
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def update(self, mouse_pos: Tuple[int, int], mouse_click: bool) -> bool:
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        clicked = self.is_hovered and mouse_click
        
        if clicked and not self.clicked and self.sound:
            pygame.mixer.Sound(f"assets/sounds/{self.sound}.wav").play()
            
        self.clicked = clicked
        return self.clicked
        
    def set_text(self, new_text: str) -> None:
        self.text = new_text

class Slider:
    def __init__(self, x: int, y: int, width: int, height: int, 
                 min_value: float, max_value: float, initial_value: float,
                 color: Tuple[int, int, int] = COLORS["GRAY"],
                 active_color: Tuple[int, int, int] = COLORS["BLUE"],
                 handle_color: Tuple[int, int, int] = COLORS["WHITE"]):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.color = color
        self.active_color = active_color
        self.handle_color = handle_color
        self.handle_radius = height * 1.5
        self.dragging = False
        self.changed = False
        
    def draw(self, surface):
        # Draw track
        pygame.draw.rect(
            surface, self.color,
            (self.rect.x, self.rect.y + self.rect.height//2 - 2, 
             self.rect.width, 4),
            border_radius=2
        )
        
        # Draw active portion
        active_width = int((self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width)
        pygame.draw.rect(
            surface, self.active_color,
            (self.rect.x, self.rect.y + self.rect.height//2 - 2, 
             active_width, 4),
            border_radius=2
        )
        
        # Draw handle
        handle_x = self.rect.x + active_width
        pygame.draw.circle(
            surface, self.handle_color,
            (handle_x, self.rect.y + self.rect.height//2),
            self.handle_radius
        )
        pygame.draw.circle(
            surface, COLORS["BLACK"],
            (handle_x, self.rect.y + self.rect.height//2),
            self.handle_radius, 2
        )
        
    def update(self, mouse_pos, mouse_click):
        mouse_x, mouse_y = mouse_pos
        handle_x = self.rect.x + int((self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width)
        handle_rect = pygame.Rect(
            handle_x - self.handle_radius, 
            self.rect.y + self.rect.height//2 - self.handle_radius,
            self.handle_radius * 2, 
            self.handle_radius * 2
        )
        
        self.changed = False
        
        if mouse_click:
            if handle_rect.collidepoint(mouse_pos):
                self.dragging = True
            elif self.rect.collidepoint(mouse_pos):
                # Clicked on the track - jump to that position
                self.value = self.min_value + (mouse_x - self.rect.x) / self.rect.width * (self.max_value - self.min_value)
                self.value = max(self.min_value, min(self.max_value, self.value))
                self.changed = True
                return True
                
        if not pygame.mouse.get_pressed()[0]:
            self.dragging = False
            
        if self.dragging:
            self.value = self.min_value + (mouse_x - self.rect.x) / self.rect.width * (self.max_value - self.min_value)
            self.value = max(self.min_value, min(self.max_value, self.value))
            self.changed = True
            return True
            
        return False

class Game:
    def __init__(self):
        self._initialize_pygame()
        self._load_assets()
        self._setup_game_objects()
        self._setup_ui()
        self._load_save_data()
        
    def _initialize_pygame(self):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)
        pygame.display.set_caption("Ultimate Snake Game 2024")
        self.clock = pygame.time.Clock()
        self.running = True
        self.fps = FPS
        
    def _load_assets(self):
        self._load_fonts()
        self._load_sounds()
        
    def _load_fonts(self):
        global title_font, font_large, font_medium, font_small, font_tiny
        try:
            title_font = pygame.font.Font("assets/fonts/RetroGaming.ttf", 72)
            font_large = pygame.font.Font("assets/fonts/RetroGaming.ttf", 48)
            font_medium = pygame.font.Font("assets/fonts/RetroGaming.ttf", 36)
            font_small = pygame.font.Font("assets/fonts/RetroGaming.ttf", 24)
            font_tiny = pygame.font.Font("assets/fonts/RetroGaming.ttf", 18)
        except:
            print("Custom fonts not found, using system fonts")
            title_font = pygame.font.SysFont("arial", 72, bold=True)
            font_large = pygame.font.SysFont("arial", 48)
            font_medium = pygame.font.SysFont("arial", 36)
            font_small = pygame.font.SysFont("arial", 24)
            font_tiny = pygame.font.SysFont("arial", 18)
            
    def _load_sounds(self):
        self.sound_system = SoundSystem()
        try:
            # Basic sounds
            self.sound_system.load_sound("click", "assets/sounds/click.wav")
            self.sound_system.load_sound("eat", "assets/sounds/eat.wav")
            self.sound_system.load_sound("crash", "assets/sounds/crash.wav")
            self.sound_system.load_sound("powerup", "assets/sounds/powerup.wav")
            self.sound_system.load_sound("negative", "assets/sounds/negative.wav")
            self.sound_system.load_sound("coin", "assets/sounds/coin.wav")
            self.sound_system.load_sound("special", "assets/sounds/special.wav")
            
            # Music tracks
            self.sound_system.load_music("menu", "assets/music/menu.mp3")
            self.sound_system.load_music("background", "assets/music/background.mp3")
            self.sound_system.load_music("gameplay", "assets/music/gameplay.mp3")
        except Exception as e:
            print(f"Sound files not found, continuing without sound: {e}")
            
    def _setup_game_objects(self):
        self.snake = Snake()
        self.food = FoodSystem(count=3)  # Multiple food items
        self.obstacle = Obstacle()
        self.particle_system = ParticleSystem()
        self.state = GameState.MENU
        self.game_mode = GameMode.CLASSIC
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.lives = 3
        self.coins = 0  # Currency for shop
        self.combo = 0
        self.combo_timer = 0
        self.difficulty = "NORMAL"
        self.backgrounds = [
            COLORS["BLACK"], 
            (30, 30, 30),
            (10, 10, 20),
            (20, 10, 10),
            (10, 20, 10),
            (5, 5, 15),
        ]
        self.current_bg = 0
        self.grid_visible = False
        self.settings = {
            "sound_volume": 0.7,
            "music_volume": 0.5,
            "show_fps": True,
            "snake_skin": 0,
            "difficulty": "NORMAL",
            "background": 0,
            "controls": "arrows",  # or "wasd"
        }
        self.time_attack_time = 180  # 3 minutes in seconds
        self.campaign_levels = [
            {"obstacles": 5, "food": 2, "time": 120, "target": 20},
            {"obstacles": 10, "food": 3, "time": 150, "target": 30},
            {"obstacles": 15, "food": 4, "time": 180, "target": 50},
            # Add more levels as needed
        ]
        self.current_campaign_level = 0
        self.level_start_time = 0
        
    def _setup_ui(self):
        button_width, button_height = 300, 60
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        
        self.menu_buttons = [
            Button(center_x, 250, button_width, button_height, "Start Game", 
                  COLORS["PURPLE"], COLORS["DEEP_PURPLE"], sound="click"),
            Button(center_x, 330, button_width, button_height, "Mode Select", 
                  COLORS["BLUE"], COLORS["DARK_BLUE"], sound="click"),
            Button(center_x, 410, button_width, button_height, "Settings", 
                  COLORS["GREEN"], COLORS["DARK_GREEN"], sound="click"),
            Button(center_x, 490, button_width, button_height, "Shop", 
                  COLORS["GOLD"], COLORS["DARK_ORANGE"], sound="coin"),
            Button(center_x, 570, button_width, button_height, "Quit", 
                  COLORS["RED"], COLORS["DARK_RED"], sound="click"),
        ]
        
        self.mode_select_buttons = [
            Button(center_x, 200, button_width, button_height, "Classic", 
                  COLORS["GREEN"], COLORS["DARK_GREEN"], sound="click"),
            Button(center_x, 280, button_width, button_height, "Time Attack", 
                  COLORS["BLUE"], COLORS["DARK_BLUE"], sound="click"),
            Button(center_x, 360, button_width, button_height, "Survival", 
                  COLORS["RED"], COLORS["DARK_RED"], sound="click"),
            Button(center_x, 440, button_width, button_height, "Campaign", 
                  COLORS["PURPLE"], COLORS["DEEP_PURPLE"], sound="click"),
            Button(center_x, 520, button_width, button_height, "Back", 
                  COLORS["GRAY"], COLORS["DARK_GRAY"], sound="click"),
        ]
        
        self.settings_sliders = [
            Slider(center_x + 100, 250, 200, 30, 0, 1, self.settings["sound_volume"],
                  COLORS["GRAY"], COLORS["BLUE"], COLORS["WHITE"]),
            Slider(center_x + 100, 330, 200, 30, 0, 1, self.settings["music_volume"],
                  COLORS["GRAY"], COLORS["PURPLE"], COLORS["WHITE"]),
        ]
        
        self.settings_buttons = [
            Button(center_x, 410, button_width, button_height, 
                  f"Controls: {self.settings['controls'].upper()}", 
                  COLORS["GREEN"], COLORS["DARK_GREEN"], sound="click"),
            Button(center_x, 490, button_width, button_height, 
                  f"Background: {self.current_bg + 1}/{len(self.backgrounds)}", 
                  COLORS["BLUE"], COLORS["DARK_BLUE"], sound="click"),
            Button(center_x, 570, button_width, button_height, "Back", 
                  COLORS["GRAY"], COLORS["DARK_GRAY"], sound="click"),
        ]
        
        self.pause_buttons = [
            Button(center_x, 300, button_width, button_height, "Resume", 
                  COLORS["GREEN"], COLORS["DARK_GREEN"], sound="click"),
            Button(center_x, 380, button_width, button_height, "Restart", 
                  COLORS["BLUE"], COLORS["DARK_BLUE"], sound="click"),
            Button(center_x, 460, button_width, button_height, "Settings", 
                  COLORS["PURPLE"], COLORS["DEEP_PURPLE"], sound="click"),
            Button(center_x, 540, button_width, button_height, "Quit to Menu", 
                  COLORS["RED"], COLORS["DARK_RED"], sound="click"),
        ]
        
        self.game_over_buttons = [
            Button(center_x, 400, button_width, button_height, "Play Again", 
                  COLORS["GREEN"], COLORS["DARK_GREEN"], sound="click"),
            Button(center_x, 480, button_width, button_height, "Main Menu", 
                  COLORS["BLUE"], COLORS["DARK_BLUE"], sound="click"),
        ]
        
        self.shop_buttons = [
            Button(50, 100, 200, 60, "Back", 
                  COLORS["GRAY"], COLORS["DARK_GRAY"], sound="click"),
            Button(SCREEN_WIDTH - 250, 100, 200, 60, f"Coins: {self.coins}", 
                  COLORS["GOLD"], COLORS["DARK_ORANGE"], sound="coin"),
        ]
        
        # Create skin purchase buttons
        self.skin_buttons = []
        for i, skin in enumerate(self.snake.skins):
            if not skin.unlocked:
                self.skin_buttons.append(
                    Button(150 + (i % 3) * 350, 200 + (i // 3) * 150, 300, 100,
                          f"{skin.name} - {skin.price} coins",
                          COLORS["GRAY"], COLORS["PURPLE"],
                          COLORS["WHITE"], font_medium)
                )
            else:
                self.skin_buttons.append(
                    Button(150 + (i % 3) * 350, 200 + (i // 3) * 150, 300, 100,
                          f"{skin.name} (OWNED)",
                          COLORS["DARK_GREEN"], COLORS["GREEN"],
                          COLORS["WHITE"], font_medium)
                )
        
    def _load_save_data(self):
        self._load_highscore()
        self._load_settings()
        self._load_player_data()
        
    def _load_highscore(self):
        try:
            with open("highscore.dat", "r") as f:
                self.high_score = int(f.read())
        except:
            self.high_score = 0
            
    def _save_highscore(self):
        with open("highscore.dat", "w") as f:
            f.write(str(max(self.score, self.high_score)))
            
    def _load_settings(self):
        try:
            with open("settings.json", "r") as f:
                loaded_settings = json.load(f)
                # Only update settings that exist in our current settings
                for key in self.settings:
                    if key in loaded_settings:
                        self.settings[key] = loaded_settings[key]
                
                self.current_bg = self.settings.get("background", 0)
                self.difficulty = self.settings.get("difficulty", "NORMAL")
                self.snake.skin_index = self.settings.get("snake_skin", 0)
                
                # Update sound volumes
                self.sound_system.set_sound_volume(self.settings["sound_volume"])
                self.sound_system.set_music_volume(self.settings["music_volume"])
        except Exception as e:
            print(f"Error loading settings: {e}")
            self._save_settings()
            
    def _save_settings(self):
        self.settings["background"] = self.current_bg
        self.settings["snake_skin"] = self.snake.skin_index
        self.settings["difficulty"] = self.difficulty
        self.settings["sound_volume"] = self.sound_system.sound_volume
        self.settings["music_volume"] = self.sound_system.music_volume
        
        with open("settings.json", "w") as f:
            json.dump(self.settings, f)
            
    def _load_player_data(self):
        try:
            with open("player.json", "r") as f:
                player_data = json.load(f)
                self.coins = player_data.get("coins", 0)
                # Unlock skins that have been purchased
                for i, skin in enumerate(self.snake.skins):
                    if f"skin_{i}_unlocked" in player_data and player_data[f"skin_{i}_unlocked"]:
                        self.snake.skins[i].unlocked = True
        except:
            self._save_player_data()
            
    def _save_player_data(self):
        player_data = {
            "coins": self.coins
        }
        # Save skin unlock status
        for i, skin in enumerate(self.snake.skins):
            player_data[f"skin_{i}_unlocked"] = skin.unlocked
            
        with open("player.json", "w") as f:
            json.dump(player_data, f)
            
    def reset(self):
        self.snake.reset()
        self.food = FoodSystem(count=3 if self.game_mode in [GameMode.SURVIVAL, GameMode.CAMPAIGN] else 1)
        self.obstacle.generate()
        self.score = 0
        self.level = 1
        self.lives = 3
        self.combo = 0
        self.combo_timer = 0
        self.time_attack_time = 180  # Reset timer for time attack
        
        if self.game_mode == GameMode.CAMPAIGN:
            level_data = self.campaign_levels[self.current_campaign_level]
            self.obstacle.generate(level_data["obstacles"])
            self.food = FoodSystem(count=level_data["food"])
            self.time_attack_time = level_data["time"]
            self.level_start_time = pygame.time.get_ticks()
        
        if self.difficulty == "EASY":
            self.snake.speed = BASE_SPEED - 5
            self.obstacle.moving = False
        elif self.difficulty == "NORMAL":
            self.snake.speed = BASE_SPEED
            self.obstacle.moving = True
        elif self.difficulty == "HARD":
            self.snake.speed = BASE_SPEED + 5
            self.obstacle.moving = True
            self.obstacle.generate(15)  # More obstacles
            
    def run(self):
        self.sound_system.play_music("menu", fade_ms=1000)
        
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(self.fps)
            
        pygame.quit()
        sys.exit()
        
    def _handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        
        for event in pygame.event.get():
            if event.type == QUIT:
                self._save_highscore()
                self._save_settings()
                self._save_player_data()
                self.running = False
                
            if event.type == KEYDOWN:
                self._handle_key_event(event)
                
            if event.type == pygame.VIDEORESIZE:
                # Handle window resizing
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
                self._setup_ui()  # Recreate UI elements for new size
                
        self._handle_button_clicks(mouse_pos, mouse_click)
        
    def _handle_key_event(self, event):
        if self.state == GameState.PLAYING:
            if event.key == K_ESCAPE or event.key == K_p:
                self.state = GameState.PAUSED
                self.sound_system.play_sound("click")
            elif event.key == K_RIGHT or event.key == K_d:
                self.snake.change_direction(Direction.RIGHT)
            elif event.key == K_LEFT or event.key == K_a:
                self.snake.change_direction(Direction.LEFT)
            elif event.key == K_UP or event.key == K_w:
                self.snake.change_direction(Direction.UP)
            elif event.key == K_DOWN or event.key == K_s:
                self.snake.change_direction(Direction.DOWN)
            elif event.key == K_g:
                self.grid_visible = not self.grid_visible
            elif event.key == K_b:
                self.current_bg = (self.current_bg + 1) % len(self.backgrounds)
                self.settings["background"] = self.current_bg
        elif self.state == GameState.PAUSED:
            if event.key == K_ESCAPE or event.key == K_p:
                self.state = GameState.PLAYING
                self.sound_system.play_sound("click")
        elif self.state == GameState.MENU:
            if event.key == K_RETURN:
                self.state = GameState.PLAYING
                self.reset()
                self.sound_system.play_music("gameplay")
                self.sound_system.play_sound("click")
        elif self.state == GameState.GAME_OVER:
            if event.key == K_RETURN:
                self.state = GameState.PLAYING
                self.reset()
                self.sound_system.play_music("gameplay")
                
    def _handle_button_clicks(self, mouse_pos, mouse_click):
        if self.state == GameState.MENU:
            if self.menu_buttons[0].update(mouse_pos, mouse_click):  # Start Game
                self.state = GameState.PLAYING
                self.game_mode = GameMode.CLASSIC
                self.reset()
                self.sound_system.play_music("gameplay")
            elif self.menu_buttons[1].update(mouse_pos, mouse_click):  # Mode Select
                self.state = GameState.MODE_SELECT
            elif self.menu_buttons[2].update(mouse_pos, mouse_click):  # Settings
                self.state = GameState.SETTINGS
            elif self.menu_buttons[3].update(mouse_pos, mouse_click):  # Shop
                self.state = GameState.SHOP
            elif self.menu_buttons[4].update(mouse_pos, mouse_click):  # Quit
                self.running = False
                
        elif self.state == GameState.MODE_SELECT:
            if self.mode_select_buttons[0].update(mouse_pos, mouse_click):  # Classic
                self.game_mode = GameMode.CLASSIC
                self.state = GameState.PLAYING
                self.reset()
                self.sound_system.play_music("gameplay")
            elif self.mode_select_buttons[1].update(mouse_pos, mouse_click):  # Time Attack
                self.game_mode = GameMode.TIME_ATTACK
                self.state = GameState.PLAYING
                self.reset()
                self.sound_system.play_music("gameplay")
            elif self.mode_select_buttons[2].update(mouse_pos, mouse_click):  # Survival
                self.game_mode = GameMode.SURVIVAL
                self.state = GameState.PLAYING
                self.reset()
                self.sound_system.play_music("gameplay")
            elif self.mode_select_buttons[3].update(mouse_pos, mouse_click):  # Campaign
                self.game_mode = GameMode.CAMPAIGN
                self.current_campaign_level = 0
                self.state = GameState.PLAYING
                self.reset()
                self.sound_system.play_music("gameplay")
            elif self.mode_select_buttons[4].update(mouse_pos, mouse_click):  # Back
                self.state = GameState.MENU
                
        elif self.state == GameState.SETTINGS:
            # Update sliders
            sound_changed = self.settings_sliders[0].update(mouse_pos, mouse_click)
            music_changed = self.settings_sliders[1].update(mouse_pos, mouse_click)
            
            if sound_changed:
                self.sound_system.set_sound_volume(self.settings_sliders[0].value)
            if music_changed:
                self.sound_system.set_music_volume(self.settings_sliders[1].value)
                
            # Update buttons
            if self.settings_buttons[0].update(mouse_pos, mouse_click):  # Controls
                self.settings["controls"] = "wasd" if self.settings["controls"] == "arrows" else "arrows"
                self.settings_buttons[0].set_text(f"Controls: {self.settings['controls'].upper()}")
            elif self.settings_buttons[1].update(mouse_pos, mouse_click):  # Background
                self.current_bg = (self.current_bg + 1) % len(self.backgrounds)
                self.settings["background"] = self.current_bg
                self.settings_buttons[1].set_text(f"Background: {self.current_bg + 1}/{len(self.backgrounds)}")
            elif self.settings_buttons[2].update(mouse_pos, mouse_click):  # Back
                self.state = GameState.MENU
                self._save_settings()
                
        elif self.state == GameState.PAUSED:
            if self.pause_buttons[0].update(mouse_pos, mouse_click):  # Resume
                self.state = GameState.PLAYING
            elif self.pause_buttons[1].update(mouse_pos, mouse_click):  # Restart
                self.state = GameState.PLAYING
                self.reset()
            elif self.pause_buttons[2].update(mouse_pos, mouse_click):  # Settings
                self.state = GameState.SETTINGS
            elif self.pause_buttons[3].update(mouse_pos, mouse_click):  # Quit to Menu
                self.state = GameState.MENU
                self.sound_system.play_music("menu")
                
        elif self.state == GameState.GAME_OVER:
            if self.game_over_buttons[0].update(mouse_pos, mouse_click):  # Play Again
                self.state = GameState.PLAYING
                self.reset()
                self.sound_system.play_music("gameplay")
            elif self.game_over_buttons[1].update(mouse_pos, mouse_click):  # Main Menu
                self.state = GameState.MENU
                self.sound_system.play_music("menu")
                
        elif self.state == GameState.SHOP:
            if self.shop_buttons[0].update(mouse_pos, mouse_click):  # Back
                self.state = GameState.MENU
            elif self.shop_buttons[1].update(mouse_pos, mouse_click):  # Coins (just visual)
                pass
                
            # Handle skin purchases
            for i, button in enumerate(self.skin_buttons):
                if button.update(mouse_pos, mouse_click):
                    skin = self.snake.skins[i]
                    if not skin.unlocked and self.coins >= skin.price:
                        self.coins -= skin.price
                        skin.unlocked = True
                        self.snake.skin_index = i
                        self.settings["snake_skin"] = i
                        self.shop_buttons[1].set_text(f"Coins: {self.coins}")
                        button.set_text(f"{skin.name} (OWNED)")
                        button.color = COLORS["DARK_GREEN"]
                        button.hover_color = COLORS["GREEN"]
                        self.sound_system.play_sound("coin")
                    elif skin.unlocked:
                        self.snake.skin_index = i
                        self.settings["snake_skin"] = i
                        self.sound_system.play_sound("click")
                        
    def _update(self):
        if self.state == GameState.PLAYING:
            self._update_game()
            
    def _update_game(self):
        self.snake.move()
        self.food.update()
        self.obstacle.move()
        self.particle_system.update()
        self._update_combo()
        
        if self._check_collision():
            self._handle_collision()
            
        self._check_food_collision()
        
        # Update time attack timer
        if self.game_mode == GameMode.TIME_ATTACK or self.game_mode == GameMode.CAMPAIGN:
            elapsed = (pygame.time.get_ticks() - self.level_start_time) // 1000
            remaining = max(0, self.time_attack_time - elapsed)
            
            if remaining <= 0:
                self.state = GameState.GAME_OVER
                if self.game_mode == GameMode.CAMPAIGN and self.score >= self.campaign_levels[self.current_campaign_level]["target"]:
                    self.current_campaign_level += 1
                    if self.current_campaign_level >= len(self.campaign_levels):
                        self.state = GameState.LEVEL_COMPLETE
                    else:
                        self.reset()
                
    def _update_combo(self):
        if self.combo > 0:
            self.combo_timer += 1
            if self.combo_timer > 180:  # 3 seconds at 60 FPS
                self.combo = 0
                self.combo_timer = 0
                
    def _check_collision(self) -> bool:
        head = self.snake.body[0]
        
        # Check wall collision
        if (head[0] < 0 or head[0] >= SCREEN_WIDTH or 
            head[1] < 0 or head[1] >= SCREEN_HEIGHT):
            return True
            
        # Check self collision
        for block in self.snake.body[1:]:
            if head[0] == block[0] and head[1] == block[1]:
                return True
                
        # Check obstacle collision
        for block in self.obstacle.blocks:
            if head[0] == block[0] and head[1] == block[1]:
                if not self.snake.invincible and not self.snake.shield:
                    return True
                else:
                    # Break the obstacle if invincible or shielded
                    self.obstacle.blocks.remove(block)
                    self.particle_system.add_explosion(
                        block[0] + BLOCK_SIZE//2, block[1] + BLOCK_SIZE//2,
                        COLORS["GRAY"], 15
                    )
                    return False
                    
        return False
        
    def _handle_collision(self):
        if self.snake.shield:
            self.snake.shield = False
            self.particle_system.add_explosion(
                self.snake.body[0][0] + BLOCK_SIZE//2, 
                self.snake.body[0][1] + BLOCK_SIZE//2,
                COLORS["LIGHT_BLUE"], 30
            )
            return
            
        self.sound_system.play_sound("crash")
        self.particle_system.add_explosion(
            self.snake.body[0][0] + BLOCK_SIZE//2, 
            self.snake.body[0][1] + BLOCK_SIZE//2,
            COLORS["RED"], 50
        )
        
        if self.game_mode == GameMode.SURVIVAL:
            self.lives -= 1
            if self.lives <= 0:
                self.state = GameState.GAME_OVER
                self._save_highscore()
            else:
                # Respawn snake
                self.snake.reset()
        else:
            self.state = GameState.GAME_OVER
            self._save_highscore()
            
    def _check_food_collision(self):
        head = self.snake.body[0]
        
        for i, food in enumerate(self.food.food_items):
            if head[0] == food["pos"][0] and head[1] == food["pos"][1]:
                self._apply_food_effect(food)
                self.food.respawn(i)
                
                # Add coins for golden and rainbow food
                if food["type"] == "golden":
                    self.coins += 1
                elif food["type"] == "rainbow":
                    self.coins += 5
                    
                # Play appropriate sound
                if food.get("sound"):
                    self.sound_system.play_sound(food["sound"])
                else:
                    self.sound_system.play_sound("eat")
                    
                # Add eating particles
                self.particle_system.add_explosion(
                    head[0] + BLOCK_SIZE//2, 
                    head[1] + BLOCK_SIZE//2,
                    food["color"], 15
                )
                
    def _apply_food_effect(self, food):
        value = food["value"]
        
        # Apply combo multiplier if active
        if self.combo > 1:
            value = int(value * (1 + self.combo * 0.2))
            
        self.score += max(0, value)  # Don't subtract from score for negative foods
        
        if food["effect"] == "speed_boost":
            self.snake.speed = min(self.snake.speed + 3, MAX_SPEED)
            self.snake.glow_effect = True
        elif food["effect"] == "slow_down":
            self.snake.speed = max(self.snake.speed - 3, MIN_SPEED)
        elif food["effect"] == "invincible":
            self.snake.invincible = True
            pygame.time.set_timer(USEREVENT + 1, food["duration"])  # Timer to disable invincibility
        elif food["effect"] == "shield":
            self.snake.shield = True
            pygame.time.set_timer(USEREVENT + 2, food["duration"])  # Timer to disable shield
        elif food["effect"] == "glow":
            self.snake.glow_effect = True
            pygame.time.set_timer(USEREVENT + 3, food["duration"])  # Timer to disable glow
        elif food["effect"] == "score_multiplier":
            self.snake.score_multiplier = 2.0
            pygame.time.set_timer(USEREVENT + 4, food["duration"])  # Timer to disable multiplier
        elif food["effect"] == "shrink":
            self.snake.shrink(2)
        elif food["effect"] == "combo_boost":
            self.combo += 1
            self.combo_timer = 0
        elif food["effect"] == "bomb":
            # Remove 3 segments and slow down
            self.snake.shrink(3)
            self.snake.speed = max(self.snake.speed - 2, MIN_SPEED)
            
        if value > 0:  # Only grow for positive food
            self.snake.grow(value)
            
    def _draw(self):
        self.screen.fill(self.backgrounds[self.current_bg])
        
        if self.state == GameState.MENU:
            self._draw_menu()
        elif self.state == GameState.MODE_SELECT:
            self._draw_mode_select()
        elif self.state == GameState.PLAYING:
            self._draw_game()
        elif self.state == GameState.PAUSED:
            self._draw_game()
            self._draw_pause_menu()
        elif self.state == GameState.GAME_OVER:
            self._draw_game()
            self._draw_game_over()
        elif self.state == GameState.SETTINGS:
            self._draw_settings()
        elif self.state == GameState.SHOP:
            self._draw_shop()
        elif self.state == GameState.LEVEL_COMPLETE:
            self._draw_level_complete()
            
        pygame.display.flip()
        
    def _draw_menu(self):
        # Draw animated background
        for i in range(20):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(2, 5)
            alpha = random.randint(50, 150)
            pygame.draw.circle(
                self.screen, (*COLORS["PURPLE"], alpha), 
                (x, y), size
            )
        
        title_text = title_font.render("ULTIMATE SNAKE", True, COLORS["PURPLE"])
        shadow_text = title_font.render("ULTIMATE SNAKE", True, COLORS["BLACK"])
        version_text = font_tiny.render("Version 2.0", True, COLORS["WHITE"])
        
        self.screen.blit(shadow_text, (SCREEN_WIDTH//2 - title_text.get_width()//2 + 3, 100 + 3))
        self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 100))
        self.screen.blit(version_text, (SCREEN_WIDTH - version_text.get_width() - 10, SCREEN_HEIGHT - 20))
        
        # Draw menu buttons
        for button in self.menu_buttons:
            button.draw(self.screen)
            
        # Draw a sample snake in the menu
        sample_snake = Snake()
        sample_snake.body = [[SCREEN_WIDTH//2 - i * BLOCK_SIZE, 180] for i in range(5)]
        sample_snake.direction = Direction.RIGHT
        sample_snake.next_direction = Direction.RIGHT
        sample_snake.draw(self.screen)
            
    def _draw_mode_select(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        title_text = font_large.render("SELECT GAME MODE", True, COLORS["WHITE"])
        self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 120))
        
        # Draw mode select buttons
        for button in self.mode_select_buttons:
            button.draw(self.screen)
            
        # Draw mode descriptions
        desc_y = 200
        modes = [
            "Classic: Grow as long as possible",
            "Time Attack: Score as much as you can in 3 minutes",
            "Survival: 3 lives to survive as long as possible",
            "Campaign: Complete challenging levels"
        ]
        
        for desc in modes:
            desc_text = font_small.render(desc, True, COLORS["WHITE"])
            self.screen.blit(desc_text, (SCREEN_WIDTH//2 - desc_text.get_width()//2, desc_y))
            desc_y += 30
            
    def _draw_game(self):
        if self.grid_visible:
            self._draw_grid()
            
        self.food.draw(self.screen)
        self.obstacle.draw(self.screen)
        self.snake.draw(self.screen)
        self.particle_system.draw(self.screen)
        self._draw_hud()
        
        if self.combo > 1:
            self._draw_combo()
            
    def _draw_grid(self):
        for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
            pygame.draw.line(self.screen, (*COLORS["GRAY"], 30), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
            pygame.draw.line(self.screen, (*COLORS["GRAY"], 30), (0, y), (SCREEN_WIDTH, y))
            
    def _draw_hud(self):
        score_text = font_small.render(f"Score: {self.score}", True, COLORS["WHITE"])
        high_score_text = font_small.render(f"High Score: {self.high_score}", True, COLORS["YELLOW"])
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(high_score_text, (10, 40))
        
        if self.game_mode == GameMode.SURVIVAL:
            lives_text = font_small.render(f"Lives: {self.lives}", True, COLORS["WHITE"])
            self.screen.blit(lives_text, (10, 70))
            
        if self.game_mode in [GameMode.TIME_ATTACK, GameMode.CAMPAIGN]:
            elapsed = (pygame.time.get_ticks() - self.level_start_time) // 1000
            remaining = max(0, self.time_attack_time - elapsed)
            mins, secs = divmod(remaining, 60)
            time_text = font_small.render(f"Time: {mins:02d}:{secs:02d}", True, COLORS["WHITE"])
            self.screen.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - 10, 10))
            
            if self.game_mode == GameMode.CAMPAIGN:
                target_text = font_small.render(
                    f"Target: {self.campaign_levels[self.current_campaign_level]['target']}", 
                    True, COLORS["WHITE"])
                self.screen.blit(target_text, (SCREEN_WIDTH - target_text.get_width() - 10, 40))
                
        if self.settings["show_fps"]:
            fps_text = font_tiny.render(f"FPS: {int(self.clock.get_fps())}", True, COLORS["WHITE"])
            self.screen.blit(fps_text, (SCREEN_WIDTH - fps_text.get_width() - 10, SCREEN_HEIGHT - 30))
            
        # Draw powerup indicators
        indicator_y = SCREEN_HEIGHT - 30
        if self.snake.invincible:
            inv_text = font_tiny.render("INVINCIBLE", True, COLORS["GOLD"])
            self.screen.blit(inv_text, (10, indicator_y))
            indicator_y -= 20
        if self.snake.shield:
            shield_text = font_tiny.render("SHIELD", True, COLORS["LIGHT_BLUE"])
            self.screen.blit(shield_text, (10, indicator_y))
            indicator_y -= 20
        if self.snake.score_multiplier > 1:
            multi_text = font_tiny.render(f"x{self.snake.score_multiplier} SCORE", True, COLORS["PURPLE"])
            self.screen.blit(multi_text, (10, indicator_y))
            indicator_y -= 20
        if self.snake.glow_effect:
            glow_text = font_tiny.render("GLOW", True, COLORS["PURPLE"])
            self.screen.blit(glow_text, (10, indicator_y))
            
    def _draw_combo(self):
        combo_text = font_medium.render(f"COMBO x{self.combo}!", True, COLORS["ORANGE"])
        text_rect = combo_text.get_rect(center=(SCREEN_WIDTH//2, 30))
        
        # Add pulsing effect
        scale = 1.0 + 0.1 * math.sin(pygame.time.get_ticks() / 200)
        scaled_text = pygame.transform.scale_by(combo_text, scale)
        scaled_rect = scaled_text.get_rect(center=text_rect.center)
        
        self.screen.blit(scaled_text, scaled_rect)
        
    def _draw_pause_menu(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Draw pause text
        pause_text = font_large.render("PAUSED", True, COLORS["WHITE"])
        self.screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, 200))
        
        # Draw pause menu buttons
        for button in self.pause_buttons:
            button.draw(self.screen)
            
    def _draw_game_over(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Draw game over text
        game_over_text = font_large.render("GAME OVER", True, COLORS["RED"])
        self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 200))
        
        # Draw final score
        score_text = font_medium.render(f"Final Score: {self.score}", True, COLORS["WHITE"])
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 280))
        
        # Draw high score if beaten
        if self.score > self.high_score:
            new_high_text = font_medium.render("NEW HIGH SCORE!", True, COLORS["YELLOW"])
            self.screen.blit(new_high_text, (SCREEN_WIDTH//2 - new_high_text.get_width()//2, 330))
            
        # Draw game over buttons
        for button in self.game_over_buttons:
            button.draw(self.screen)
            
    def _draw_settings(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Draw settings title
        title_text = font_large.render("SETTINGS", True, COLORS["WHITE"])
        self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 120))
        
        # Draw sound volume slider
        sound_text = font_medium.render("Sound Volume:", True, COLORS["WHITE"])
        self.screen.blit(sound_text, (SCREEN_WIDTH//2 - 200, 250))
        self.settings_sliders[0].draw(self.screen)
        
        # Draw music volume slider
        music_text = font_medium.render("Music Volume:", True, COLORS["WHITE"])
        self.screen.blit(music_text, (SCREEN_WIDTH//2 - 200, 330))
        self.settings_sliders[1].draw(self.screen)
        
        # Draw settings buttons
        for button in self.settings_buttons:
            button.draw(self.screen)
            
    def _draw_shop(self):
        # Draw shop background
        self.screen.fill(COLORS["BLACK_OLIVE"])
        
        # Draw shop title
        title_text = font_large.render("SNAKE SKIN SHOP", True, COLORS["GOLD"])
        self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 40))
        
        # Draw shop buttons
        for button in self.shop_buttons:
            button.draw(self.screen)
            
        # Draw skin buttons and previews
        for i, button in enumerate(self.skin_buttons):
            button.draw(self.screen)
            
            # Draw skin preview
            preview_x = button.rect.x + button.rect.width + 20
            preview_y = button.rect.y + button.rect.height//2
            
            skin = self.snake.skins[i]
            
            # Draw head
            pygame.draw.rect(
                self.screen, skin.head,
                (preview_x, preview_y - BLOCK_SIZE//2, BLOCK_SIZE, BLOCK_SIZE),
                border_radius=6
            )
            
            # Draw body segment
            pygame.draw.rect(
                self.screen, skin.body,
                (preview_x + BLOCK_SIZE + 10, preview_y - BLOCK_SIZE//2, BLOCK_SIZE, BLOCK_SIZE),
                border_radius=4
            )
            
            # Draw special effect indicator
            if skin.special_effect:
                effect_text = font_tiny.render(f"Effect: {skin.special_effect}", True, COLORS["WHITE"])
                self.screen.blit(effect_text, (preview_x + BLOCK_SIZE*2 + 20, preview_y - effect_text.get_height()//2))
                
    def _draw_level_complete(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Draw congratulations text
        congrats_text = font_large.render("CAMPAIGN COMPLETE!", True, COLORS["GOLD"])
        self.screen.blit(congrats_text, (SCREEN_WIDTH//2 - congrats_text.get_width()//2, 200))
        
        # Draw final score
        score_text = font_medium.render(f"Final Score: {self.score}", True, COLORS["WHITE"])
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 280))
        
        # Draw reward
        reward_text = font_medium.render("You earned 100 coins!", True, COLORS["YELLOW"])
        self.screen.blit(reward_text, (SCREEN_WIDTH//2 - reward_text.get_width()//2, 330))
        
        # Add coins
        self.coins += 100
        self._save_player_data()
        
        # Draw continue button
        continue_button = Button(
            SCREEN_WIDTH//2 - 150, 400, 300, 60, "Continue", 
            COLORS["GREEN"], COLORS["DARK_GREEN"], sound="coin"
        )
        
        if continue_button.update(pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0]):
            self.state = GameState.MENU
            self.sound_system.play_music("menu")
            
        continue_button.draw(self.screen)

if __name__ == "__main__":
    game = Game()
    game.run()
