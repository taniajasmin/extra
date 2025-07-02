import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()

# Screen setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Corporate Carnage")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
PURPLE = (128, 0, 128)
SILVER = (192, 192, 192)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)

# Game state
player = {
    'x': 400,
    'y': 500,
    'width': 32,
    'height': 32,
    'speed': 5,
    'has_bat': False,
    'animation': 'idle',
    'frame': 0,
    'frame_count': {'idle': 2, 'attack': 4},
    'frame_timer': 0,
    'frame_duration': 8  # Frames per animation frame (~7.5 FPS at 60 FPS)
}
score = 0
rage = 0
phase = 1
boss = {'x': 400, 'y': 100, 'width': 50, 'height': 50, 'health': 100, 'panicked': False}
allies = []
game_over = False
ending = ''

# Game elements
emails = []
paperwork = []
coworkers = []
coffee_traps = []
hr_drones = []
staplers = []
lasers = []

# Load sprite (placeholder for now)
player_sprite = None
if os.path.exists('player.png'):
    player_sprite = pygame.image.load('player.png')  # 128x32 sprite sheet (4 columns: 2 idle, 2 attack)
    player_sprite = pygame.transform.scale(player_sprite, (128, 32))

# Helper functions
def random_range(min_val, max_val):
    return random.randint(min_val, max_val)

def collides(a, b):
    return (a['x'] < b['x'] + b['width'] and
            a['x'] + a['width'] > b['x'] and
            a['y'] < b['y'] + b['height'] and
            a['y'] + a['height'] > b['y'])

# Obstacle generators
def spawn_email():
    emails.append({'x': random_range(0, SCREEN_WIDTH - 20), 'y': 0, 'width': 20, 'height': 10, 'speed': 4})

def spawn_paperwork():
    paperwork.append({'x': 0, 'y': random_range(0, SCREEN_HEIGHT - 50), 'width': SCREEN_WIDTH, 'height': 50, 'speed': 2})

def spawn_coworker():
    coworkers.append({'x': random_range(0, SCREEN_WIDTH - 30), 'y': random_range(0, SCREEN_HEIGHT - 30),
                      'width': 30, 'height': 30, 'speed': random_range(1, 3)})

def spawn_coffee_trap():
    coffee_traps.append({'x': random_range(0, SCREEN_WIDTH - 20), 'y': random_range(0, SCREEN_HEIGHT - 20),
                         'width': 20, 'height': 20})

def spawn_hr_drone():
    hr_drones.append({'x': random_range(0, SCREEN_WIDTH - 25), 'y': 0, 'width': 25, 'height': 25, 'speed': 3})

def spawn_stapler():
    staplers.append({'x': boss['x'] + 25, 'y': boss['y'], 'width': 15, 'height': 15, 'speed': 5})

def spawn_laser():
    lasers.append({'x': boss['x'], 'y': boss['y'] + 50, 'width': 100, 'height': 10, 'speed': 1})

# Ally recruitment
def recruit_ally(ally_type):
    global score
    cost = 0
    ally = {'x': player['x'], 'y': player['y'], 'width': 30, 'height': 30}
    if ally_type == 'intern':
        cost = 50
        ally['strength'] = 1
        ally['health'] = 10
    elif ally_type == 'seniorDev':
        cost = 200
        ally['strength'] = 3
        ally['health'] = 50
        ally['ranged'] = True
    elif ally_type == 'gossip':
        cost = 100
        ally['strength'] = 0
        ally['health'] = 20
        ally['distract'] = True
    elif ally_type == 'unionRep':
        cost = 150
        ally['strength'] = 2
        ally['health'] = 100
    if score >= cost:
        score -= cost
        allies.append(ally)

# Font for UI
font = pygame.font.SysFont('Arial', 24)

# Game loop
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if game_over:
        screen.fill(WHITE)
        text = font.render(f'Game Over: {ending}', True, RED)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        continue

    # Player movement
    keys = pygame.key.get_pressed()
    speed = player['speed']
    for trap in coffee_traps:
        if collides(player, trap):
            speed = player['speed'] / 2
    if keys[pygame.K_LEFT] and player['x'] > 0:
        player['x'] -= speed
    if keys[pygame.K_RIGHT] and player['x'] < SCREEN_WIDTH - player['width']:
        player['x'] += speed
    if keys[pygame.K_UP] and player['y'] > 0:
        player['y'] -= speed
    if keys[pygame.K_DOWN] and player['y'] < SCREEN_HEIGHT - player['height']:
        player['y'] += speed

    # Animation handling
    player['frame_timer'] += 1
    if player['frame_timer'] >= player['frame_duration']:
        player['frame_timer'] = 0
        player['frame'] = (player['frame'] + 1) % player['frame_count'][player['animation']]
    if keys[pygame.K_SPACE] and player['has_bat'] and phase == 2 and collides(player, boss):
        player['animation'] = 'attack'
    else:
        player['animation'] = 'idle'

    # Phase 1: Stealth
    if phase == 1:
        if random.random() < 0.02:
            spawn_email()
        if random.random() < 0.01:
            spawn_paperwork()
        if random.random() < 0.015:
            spawn_coworker()
        if random.random() < 0.01:
            spawn_coffee_trap()

        # Check for bat
        bat = {'x': 700, 'y': 500, 'width': 20, 'height': 20}
        if collides(player, bat):
            player['has_bat'] = True
            phase = 2
            boss['panicked'] = True

        # Update obstacles
        for email in emails[:]:
            email['y'] += email['speed']
            if collides(player, email):
                game_over = True
                ending = 'You Got Fired'
        for paper in paperwork[:]:
            paper['x'] += paper['speed']
            if collides(player, paper):
                game_over = True
                ending = 'You Got Fired'
        for cw in coworkers[:]:
            cw['x'] += cw['speed'] * (1 if random.random() > 0.5 else -1)
            if collides(player, cw):
                game_over = True
                ending = 'You Got Fired'

    # Phase 2: Beatdown
    if phase == 2:
        if random.random() < 0.02:
            spawn_hr_drone()
        if random.random() < 0.03:
            spawn_stapler()
        if random.random() < 0.01:
            spawn_laser()

        # Attack boss
        if keys[pygame.K_SPACE] and player['has_bat'] and collides(player, boss):
            boss['health'] -= 1
            score += 10
            rage += 5
            if rage >= 100:
                rage = 0
                boss['health'] -= 20  # Rage Mode: Mass Resignation Wave
            if boss['health'] <= 0:
                phase = 3

        # Update obstacles
        for drone in hr_drones[:]:
            drone['y'] += drone['speed']
            if collides(player, drone):
                game_over = True
                ending = 'You Got Fired'
        for stapler in staplers[:]:
            stapler['y'] += stapler['speed']
            if collides(player, stapler):
                game_over = True
                ending = 'You Got Fired'
        for laser in lasers[:]:
            laser['x'] += laser['speed']
            if collides(player, laser):
                game_over = True
                ending = 'You Got Fired'

    # Phase 3: Allies
    if phase == 3:
        if keys[pygame.K_b]:
            if random.random() < 0.25:
                recruit_ally('intern')
            elif random.random() < 0.5:
                recruit_ally('seniorDev')
            elif random.random() < 0.75:
                recruit_ally('gossip')
            else:
                recruit_ally('unionRep')

        for ally in allies[:]:
            if ally.get('ranged'):
                staplers.append({'x': ally['x'], 'y': ally['y'], 'width': 15, 'height': 15, 'speed': -5})
            if ally.get('distract'):
                for drone in hr_drones:
                    drone['speed'] *= 0.5
            for drone in hr_drones:
                if collides(ally, drone):
                    ally['health'] -= 10
                    if ally['health'] <= 0:
                        allies.remove(ally)

        if len(allies) >= 5:
            game_over = True
            ending = 'You Unionized the Office'
        if boss['health'] <= -50:
            game_over = True
            ending = 'You Became the Boss'

    # Rendering
    screen.fill(WHITE)
    # Draw player
    if player_sprite:
        frame_x = 0 if player['animation'] == 'idle' else 64
        frame_x += player['frame'] * 32
        screen.blit(player_sprite, (player['x'], player['y']),
                    (frame_x, 0, 32, 32))
    else:
        pygame.draw.rect(screen, BLUE, (player['x'], player['y'], player['width'], player['height']))
    # Draw boss
    pygame.draw.rect(screen, RED, (boss['x'], boss['y'], boss['width'], boss['height']))
    # Draw phase 1 elements
    if phase == 1:
        pygame.draw.rect(screen, YELLOW, (700, 500, 20, 20))  # Bat
        for email in emails:
            pygame.draw.rect(screen, GRAY, (email['x'], email['y'], email['width'], email['height']))
        for paper in paperwork:
            pygame.draw.rect(screen, GRAY, (paper['x'], paper['y'], paper['width'], paper['height']))
        for cw in coworkers:
            pygame.draw.rect(screen, GRAY, (cw['x'], cw['y'], cw['width'], cw['height']))
        for trap in coffee_traps:
            pygame.draw.rect(screen, GRAY, (trap['x'], trap['y'], trap['width'], trap['height']))
    # Draw phase 2+ elements
    if phase >= 2:
        for drone in hr_drones:
            pygame.draw.rect(screen, PURPLE, (drone['x'], drone['y'], drone['width'], drone['height']))
        for stapler in staplers:
            pygame.draw.rect(screen, SILVER, (stapler['x'], stapler['y'], stapler['width'], stapler['height']))
        for laser in lasers:
            pygame.draw.rect(screen, ORANGE, (laser['x'], laser['y'], laser['width'], laser['height']))
    # Draw allies
    for ally in allies:
        pygame.draw.rect(screen, GREEN, (ally['x'], ally['y'], ally['width'], ally['height']))

    # Draw UI
    phase_text = font.render(f'Phase: {"Stealth" if phase == 1 else "Beatdown" if phase == 2 else "Allies"}', True, (0, 0, 0))
    score_text = font.render(f'Score: {score}', True, (0, 0, 0))
    rage_text = font.render(f'Rage: {rage}', True, (0, 0, 0))
    screen.blit(phase_text, (10, 10))
    screen.blit(score_text, (10, 40))
    screen.blit(rage_text, (10, 70))

    pygame.display.flip()
    clock.tick(60)