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

class GameMode(Enum):
    CLASSIC = auto()
    TIME_ATTACK = auto()
    SURVIVAL = auto()
    MULTIPLAYER = auto()

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    
    @staticmethod
    def opposite(dir1, dir2) -> bool:
        return (dir1.value[0] + dir2.value[0] == 0) and (dir1.value[1] + dir2.value[1] == 0)

# Color system with 150+ colors (simplified for brevity)
COLORS = {
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    # ... (keep your existing color definitions)
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
    
    def __post_init__(self):
        self.max_lifetime = self.lifetime
        
    def update(self):
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.velocity[1] += self.gravity
        self.lifetime -= 1
        self.alpha = int(255 * (self.lifetime / self.max_lifetime))
        
    def draw(self, surface):
        if self.lifetime > 0:
            alpha_color = (*self.color[:3], self.alpha) if len(self.color) == 4 else (*self.color, self.alpha)
            pygame.gfxdraw.filled_circle(surface, int(self.pos[0]), int(self.pos[1]), int(self.size), alpha_color)

class ParticleSystem:
    def __init__(self):
        self.particles: List[Particle] = []
        
    def add_particle(self, particle: Particle):
        self.particles.append(particle)
        
    def add_explosion(self, x: float, y: float, color: Tuple[int, int, int], count: int = 20):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 3)
            velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            lifetime = random.randint(30, 90)
            size = random.randint(2, 5)
            self.particles.append(Particle([x, y], velocity, color, lifetime, size, 0.1))
            
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
        
    def load_sound(self, name: str, path: str) -> None:
        try:
            self.sounds[name] = pygame.mixer.Sound(path)
            self.sounds[name].set_volume(self.volume)
        except Exception as e:
            print(f"Failed to load sound {path}: {e}")
            
    def load_music(self, name: str, path: str) -> None:
        self.music_tracks[name] = path
        
    def play_sound(self, name: str, loops: int = 0) -> None:
        if not self.muted and name in self.sounds:
            self.sounds[name].play(loops)
            
    def play_music(self, name: str, loops: int = -1) -> None:
        if not self.muted and name in self.music_tracks:
            pygame.mixer.music.load(self.music_tracks[name])
            pygame.mixer.music.set_volume(self.volume * 0.7)
            pygame.mixer.music.play(loops)
            self.current_music = name
            
    def stop_music(self) -> None:
        pygame.mixer.music.stop()
        self.current_music = None
        
    def toggle_mute(self) -> None:
        self.muted = not self.muted
        pygame.mixer.music.set_volume(0 if self.muted else self.volume * 0.7)
        for sound in self.sounds.values():
            sound.set_volume(0 if self.muted else self.volume)
            
    def set_volume(self, volume: float) -> None:
        self.volume = max(0, min(1, volume))
        if not self.muted:
            pygame.mixer.music.set_volume(self.volume * 0.7)
            for sound in self.sounds.values():
                sound.set_volume(self.volume)

@dataclass
class SnakeSkin:
    body: Tuple[int, int, int]
    head: Tuple[int, int, int]
    eye: Tuple[int, int, int] = COLORS["WHITE"]
    pupil: Tuple[int, int, int] = COLORS["BLACK"]
    unlocked: bool = True

class Snake:
    def __init__(self, player_num: int = 1):
        self.reset()
        self.player_num = player_num
        self.skin_index = 0
        self.skins = [
            SnakeSkin(COLORS["PURPLE"], COLORS["DEEP_PURPLE"]),
            SnakeSkin(COLORS["CYAN"], COLORS["DARK_CYAN"]),
            # ... (other skins)
        ]
        self.tongue_out = False
        self.tongue_timer = 0
        self.tail_history = deque(maxlen=10)
        self.glow_effect = False
        self.glow_timer = 0
        self.glow_colors = [COLORS["RED"], COLORS["ORANGE"], COLORS["YELLOW"], 
                          COLORS["GREEN"], COLORS["BLUE"], COLORS["INDIGO"], COLORS["VIOLET"]]
        self.trail_particles = []
        
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
                    self.trail_particles.append({
                        'pos': tail.copy(),
                        'timer': 15,
                        'color': self.skins[self.skin_index].body,
                        'size': BLOCK_SIZE // 2
                    })
                self.body.pop()
                
        self.tongue_timer = (self.tongue_timer + 1) % 60
        self.tongue_out = self.tongue_timer < 10
        
        if self.glow_effect:
            self.glow_timer = (self.glow_timer + 1) % len(self.glow_colors)
            
        for p in self.trail_particles:
            p['timer'] -= 1
            p['size'] = max(0, p['size'] - 0.5)
        self.trail_particles = [p for p in self.trail_particles if p['timer'] > 0]
        
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
        if self.glow_effect and index % 5 == 0:
            glow_color = self.glow_colors[self.glow_timer]
            pygame.gfxdraw.filled_circle(
                surface, 
                pos[0] + BLOCK_SIZE // 2, 
                pos[1] + BLOCK_SIZE // 2, 
                BLOCK_SIZE // 2 + 2, 
                (*glow_color, 100)
            
        pygame.draw.rect(surface, skin.body, (pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE), border_radius=4)
        
        inner_size = BLOCK_SIZE - 4
        inner_color = (
            min(skin.body[0] + 30, 255),
            min(skin.body[1] + 30, 255),
            min(skin.body[2] + 30, 255)
        )
        pygame.draw.rect(
            surface, inner_color, 
            (pos[0] + 2, pos[1] + 2, inner_size, inner_size),
            border_radius=2
        )
        
    def _draw_head(self, surface, pos, skin):
        pygame.draw.rect(
            surface, skin.head, 
            (pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE),
            border_radius=6
        )
        
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

class FoodSystem:
    def __init__(self, count: int = 1):
        self.food_items: List[Dict[str, Any]] = []
        self.types = [
            FoodType("normal", COLORS["GREEN"], 1, 60),
            FoodType("speed", COLORS["CYAN"], 2, 15, "speed_boost"),
            # ... (other food types)
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
                return {
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
                    "duration": food_type.duration
                }
            upto += food_type.rarity
        return self._create_food()  # Fallback
        
    def respawn(self, index: int = 0) -> None:
        if index < len(self.food_items):
            self.food_items[index] = self._create_food()
            
    def update(self) -> None:
        for food in self.food_items:
            if food["type"] == "rainbow":
                food["current_color_index"] = (food.get("current_color_index", 0) + 1) % len(self.rainbow_colors)
                food["color"] = self.rainbow_colors[food["current_color_index"]]
                
            if food["spawn_animation"]:
                food["animation_timer"] += 1
                if food["animation_timer"] > 30:
                    food["spawn_animation"] = False
                    
            if food.get("expires", False):
                if pygame.time.get_ticks() - food["spawn_time"] > food.get("duration", 10000):
                    self.respawn(self.food_items.index(food))
                    
    def draw(self, surface) -> None:
        for food in self.food_items:
            size = BLOCK_SIZE
            
            if food["spawn_animation"]:
                size = int(BLOCK_SIZE * (food["animation_timer"] / 30))
                
            x, y = food["pos"][0] + (BLOCK_SIZE - size) // 2, food["pos"][1] + (BLOCK_SIZE - size) // 2
            
            if food["type"] == "golden":
                pygame.draw.rect(surface, food["color"], (x, y, size, size), border_radius=size//2)
                center_x, center_y = x + size//2, y + size//2
                pygame.draw.line(
                    surface, COLORS["YELLOW"], 
                    (center_x - size//4, center_y - size//4),
                    (center_x + size//4, center_y + size//4), 
                    2
                )
                pygame.draw.line(
                    surface, COLORS["YELLOW"], 
                    (center_x + size//4, center_y - size//4),
                    (center_x - size//4, center_y + size//4), 
                    2
                )
            elif food["type"] == "rainbow":
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
            else:
                pygame.draw.rect(surface, food["color"], (x, y, size, size), border_radius=size//2)
                
                if food["type"] in ["speed", "slow", "invincible", "shield", "glow", "multiplayer"]:
                    symbol_size = size // 2
                    symbol_x, symbol_y = x + (size - symbol_size) // 2, y + (size - symbol_size) // 2
                    
                    if food["type"] == "speed":
                        pygame.draw.polygon(
                            surface, COLORS["WHITE"], 
                            [(symbol_x, symbol_y), 
                             (symbol_x + symbol_size, symbol_y + symbol_size//2),
                             (symbol_x, symbol_y + symbol_size)]
                        )
                    # ... (other symbols)

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 color: Tuple[int, int, int], hover_color: Tuple[int, int, int], 
                 text_color: Tuple[int, int, int] = COLORS["WHITE"], font=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font or font_medium
        self.is_hovered = False
        self.clicked = False
        self.border_radius = 10
        
    def draw(self, surface) -> None:
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, COLORS["WHITE"], self.rect, 2, border_radius=self.border_radius)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def update(self, mouse_pos: Tuple[int, int], mouse_click: bool) -> bool:
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.clicked = self.is_hovered and mouse_click
        return self.clicked
        
    def set_text(self, new_text: str) -> None:
        self.text = new_text

class Game:
    def __init__(self):
        self._initialize_pygame()
        self._load_assets()
        self._setup_game_objects()
        self._setup_ui()
        self._load_save_data()
        
    def _initialize_pygame(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)
        pygame.display.set_caption("Ultimate Snake Game 2024")
        self.clock = pygame.time.Clock()
        
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
            title_font = pygame.font.SysFont("arial", 72, bold=True)
            font_large = pygame.font.SysFont("arial", 48)
            font_medium = pygame.font.SysFont("arial", 36)
            font_small = pygame.font.SysFont("arial", 24)
            font_tiny = pygame.font.SysFont("arial", 18)
            
    def _load_sounds(self):
        self.sound_system = SoundSystem()
        try:
            self.sound_system.load_sound("eat", "assets/sounds/eat.wav")
            self.sound_system.load_sound("crash", "assets/sounds/crash.wav")
            self.sound_system.load_music("background", "assets/music/background.mp3")
        except:
            print("Sound files not found, continuing without sound")
            
    def _setup_game_objects(self):
        self.snake = Snake()
        self.food = FoodSystem()
        self.obstacle = Obstacle()
        self.particle_system = ParticleSystem()
        self.state = GameState.MENU
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.lives = 3
        self.combo = 0
        self.combo_timer = 0
        self.difficulty = "NORMAL"
        self.backgrounds = [
            COLORS["BLACK"], 
            (30, 30, 30),
            # ... (other backgrounds)
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
        
    def _setup_ui(self):
        self.menu_buttons = [
            Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100, 300, 60, "Start Game", 
                  COLORS["PURPLE"], COLORS["DEEP_PURPLE"]),
            # ... (other buttons)
        ]
        
    def _load_save_data(self):
        self._load_highscore()
        self._load_settings()
        
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
                self.settings = json.load(f)
                self.current_bg = self.settings.get("background", 0)
                self.difficulty = self.settings.get("difficulty", "NORMAL")
                self.snake.skin_index = self.settings.get("snake_skin", 0)
        except:
            self._save_settings()
            
    def _save_settings(self):
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
        
        if self.difficulty == "EASY":
            self.snake.speed = BASE_SPEED - 5
            self.obstacle.moving = False
        elif self.difficulty == "NORMAL":
            self.snake.speed = BASE_SPEED
            self.obstacle.moving = True
        elif self.difficulty == "HARD":
            self.snake.speed = BASE_SPEED + 5
            self.obstacle.moving = True
            self.obstacle.generate()
            
    def run(self):
        self.sound_system.play_music("menu")
        
        while True:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)
            
    def _handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        
        for event in pygame.event.get():
            if event.type == QUIT:
                self._save_highscore()
                self._save_settings()
                pygame.quit()
                sys.exit()
                
            if event.type == KEYDOWN:
                self._handle_key_event(event)
                
        self._handle_button_clicks(mouse_pos, mouse_click)
        
    def _handle_key_event(self, event):
        if self.state == GameState.PLAYING:
            if event.key == K_ESCAPE or event.key == K_p:
                self.state = GameState.PAUSED
                self.sound_system.play_sound("click")
            elif event.key == K_RIGHT or event.key == K_d:
                self.snake.change_direction(Direction.RIGHT)
            # ... (other key controls)
            
    def _handle_button_clicks(self, mouse_pos, mouse_click):
        if self.state == GameState.MENU:
            if self.menu_buttons[0].update(mouse_pos, mouse_click):  # Start Game
                self.state = GameState.PLAYING
                self.reset()
                self.sound_system.play_music("background")
                self.sound_system.play_sound("click")
            # ... (other button handlers)
            
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
        
    def _draw(self):
        self.screen.fill(self.backgrounds[self.current_bg])
        
        if self.state == GameState.MENU:
            self._draw_menu()
        elif self.state == GameState.PLAYING:
            self._draw_game()
            
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
        
        self.screen.blit(shadow_text, (SCREEN_WIDTH//2 - title_text.get_width()//2 + 3, 100 + 3))
        self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 100))
        
        # Draw menu buttons
        for button in self.menu_buttons:
            button.draw(self.screen)
            
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
        
        if self.settings["show_fps"]:
            fps_text = font_tiny.render(f"FPS: {int(self.clock.get_fps())}", True, COLORS["WHITE"])
            self.screen.blit(fps_text, (SCREEN_WIDTH - fps_text.get_width() - 10, SCREEN_HEIGHT - 30))

if __name__ == "__main__":
    game = Game()
    game.run()
