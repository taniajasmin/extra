import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BEAT THE BOSS")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Player
player_size = 40
player_x = WIDTH // 2
player_y = HEIGHT - 2 * player_size
player_speed = 5

# Bat
bat_size = 30
bat_x = random.randint(50, WIDTH - 50)
bat_y = random.randint(50, HEIGHT // 2)
has_bat = False

# Manager (BOSS)
manager_size = 50
manager_x = WIDTH // 2
manager_y = 50
manager_health = 100

# Coworkers
coworkers = []
coworker_cost = 50

# Obstacles (Emails)
emails = []
email_spawn_timer = 0

# Game stats
score = 0
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

def spawn_email():
    x = random.randint(0, WIDTH)
    y = 0
    speed = random.randint(3, 7)
    emails.append([x, y, speed])

def draw_objects():
    screen.fill(BLACK)
    
    # Draw player
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_size, player_size))
    
    # Draw bat if not collected
    if not has_bat:
        pygame.draw.rect(screen, WHITE, (bat_x, bat_y, bat_size, bat_size))
    
    # Draw manager
    pygame.draw.rect(screen, RED, (manager_x, manager_y, manager_size, manager_size))
    
    # Draw emails
    for email in emails:
        pygame.draw.rect(screen, GREEN, (email[0], email[1], 20, 15))
    
    # Draw coworkers
    for coworker in coworkers:
        pygame.draw.circle(screen, WHITE, (int(coworker[0]), int(coworker[1])), 15)
    
    # Draw UI
    score_text = font.render(f"Score: {score}", True, WHITE)
    health_text = font.render(f"Boss Health: {manager_health}", True, WHITE)
    bat_text = font.render(f"Bat: {'YES' if has_bat else 'NO'}", True, WHITE)
    coworker_text = font.render(f"Coworkers: {len(coworkers)} (Cost: {coworker_cost})", True, WHITE)
    
    screen.blit(score_text, (10, 10))
    screen.blit(health_text, (10, 50))
    screen.blit(bat_text, (10, 90))
    screen.blit(coworker_text, (10, 130))

def main():
    global player_x, player_y, has_bat, bat_x, bat_y, score, email_spawn_timer, manager_health, coworker_cost
    
    running = True
    while running:
        clock.tick(60)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and score >= coworker_cost:
                    coworkers.append([player_x, player_y])
                    score -= coworker_cost
                    coworker_cost += 25  # Increase cost each time
        
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_size:
            player_x += player_speed
        if keys[pygame.K_UP] and player_y > 0:
            player_y -= player_speed
        if keys[pygame.K_DOWN] and player_y < HEIGHT - player_size:
            player_y += player_speed
        
        # Bat collection
        if not has_bat:
            bat_rect = pygame.Rect(bat_x, bat_y, bat_size, bat_size)
            player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
            if player_rect.colliderect(bat_rect):
                has_bat = True
        
        # Punch manager if has bat
        if has_bat:
            manager_rect = pygame.Rect(manager_x, manager_y, manager_size, manager_size)
            player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
            if player_rect.colliderect(manager_rect) and keys[pygame.K_SPACE]:
                manager_health -= 1
                score += 10
        
        # Spawn emails
        email_spawn_timer += 1
        if email_spawn_timer >= 30:  # Spawn every 0.5 seconds
            spawn_email()
            email_spawn_timer = 0
        
        # Update emails
        for email in emails[:]:
            email[1] += email[2]
            if email[1] > HEIGHT:
                emails.remove(email)
            
            # Check collision with player
            email_rect = pygame.Rect(email[0], email[1], 20, 15)
            player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
            if player_rect.colliderect(email_rect):
                emails.remove(email)
                score = max(0, score - 5)
        
        # Update coworkers (they follow and attack manager)
        for coworker in coworkers[:]:
            # Simple follow logic
            if coworker[0] < manager_x:
                coworker[0] += 2
            elif coworker[0] > manager_x:
                coworker[0] -= 2
            
            if coworker[1] < manager_y:
                coworker[1] += 2
            elif coworker[1] > manager_y:
                coworker[1] -= 2
            
            # Check if coworker reaches manager
            coworker_rect = pygame.Rect(coworker[0], coworker[1], 15, 15)
            manager_rect = pygame.Rect(manager_x, manager_y, manager_size, manager_size)
            if coworker_rect.colliderect(manager_rect):
                manager_health -= 0.5
                score += 5
            
            # Check if coworker gets hit by email
            for email in emails[:]:
                email_rect = pygame.Rect(email[0], email[1], 20, 15)
                if coworker_rect.colliderect(email_rect):
                    coworkers.remove(coworker)
                    emails.remove(email)
                    break
        
        # Draw everything
        draw_objects()
        pygame.display.flip()
        
        # Game over check
        if manager_health <= 0:
            print(f"GAME OVER! Final Score: {score}")
            running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()