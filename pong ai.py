import pygame, os, sys, random, neat, pickle
from pygame.locals import *

# Define NEAT parameters
max_generations = 50 #How many generations will the simulation run
local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'config.txt')

pygame.init()

letra50 = pygame.font.SysFont("Arial", 50)
letra30 = pygame.font.SysFont("Arial", 30)

# Create NEAT configuration
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     config_path)

def update_ai_paddle(paddle_y, ball_y, ball_distance, net, fitness):
    
    paddle_y_normalized = paddle_y / 700
    ball_y_normalized = ball_y / 700
    ball_distance_normalized = ball_distance / 900 
    
    player1Y = paddle_y
    
    output = net.activate([paddle_y_normalized, ball_y_normalized, ball_distance_normalized])
    
    # Interpret outputs
    if output[0] > output[1] and output[0] > output[2]:
        # Move paddle up
        player1Y -= 10
    elif output[1] > output[0] and output[1] > output[2]:
        # Stay in place
        fitness -= 0.1
        pass  # No movement
    elif output[2] > output[0] and output[2] > output[1]:
        # Move paddle down
        player1Y += 10
    
    return player1Y, fitness
    
def simulate_game(neural_network):
    # Your implementation of the game simulation using the neural network
    # It should return a fitness score based on the performance in the game
    fpsClock = pygame.time.Clock()

    player_score = 0
    machine_score = 0
    dificultad = 9

    width,height = 1000,700
    mainSurface = pygame.display.set_mode((width,height))
    pygame.display.set_caption('pong');
    black = pygame.Color(0, 0, 0)

    # bat init
    bat1 = pygame.image.load('pong_bat.png')
    bat2 = pygame.image.load('pong_bat.png')
    player1Y = height/2
    player2Y = height/2
    player1X = 50
    player2X = width-50
    batRect1 = bat1.get_rect()
    batRect2 = bat2.get_rect()

    # ball init
    VELOCIDAD = 8
    ball = pygame.image.load('ball.png')
    ballRect = ball.get_rect()
    ballStartY = 300
    ballSpeed = VELOCIDAD
    bx, by = (100, ballStartY)
    sx, sy = (ballSpeed, ballSpeed)
    ballRect.center = (bx, by)
    ballserved = False
    twoplayer = False

    batRect1.midtop = (player1X, player1Y)
    batRect2.midtop = (player2X, player2Y)
    
    fitness = 0
    right_hits = 0
    
    run = True
    while run:
        ballserved = True
        mainSurface.fill(black)
        # events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse = pygame.mouse.get_pos()
                    
    #     keys = pygame.key.get_pressed()
    #     if keys[K_UP]:
    #         player2Y -= 10
    #         batRect2.midtop = (player2X, player2Y)
    #         ballserved = True
    #     if keys[K_DOWN]:
    #         player2Y += 10
    #         batRect2.midtop = (player2X, player2Y)
    #         ballserved = True
    #     if keys[K_w]:
    #         player1Y -= 10
    #         batRect1.midtop = (player1X, player1Y)
    #         ballserved = True
    #     if keys[K_s]:
    #         player1Y += 10
    #         batRect1.midtop = (player1X, player1Y)
    #         ballserved = True
        
    #     if batRect1.center[1] <= 30:
    #         batRect1.center = (player1X, 30)
    #     if batRect1.center[1] >= height-30:
    #         batRect1.center = (player1X, height-30)

        if batRect2.center[1] <= 30:
            batRect2.center = (player2X, 30)
        if batRect2.center[1] >= height-30:
            batRect2.center = (player2X, height-30)
        
        if ballserved:
            bx += sx
            by += sy
            ballRect.center = (bx, by)
        
        player1Y, fitness = update_ai_paddle(player1Y, by, (bx-batRect1.center[0]) / 900 , neural_network, fitness)
        
        if player1Y < 0 or player1Y > height-57:
            fitness -= 1
            
        batRect1.center = (player1X,player1Y)
        
        diferencia2 = (batRect2.center[1]-by) + (-1 if sy<0 else 1) * random.randint(0,20)
        if diferencia2 == 0:
            diferencia2 = 1
        if sx == abs(sx) and abs(diferencia2) > 5:
            batRect2.center = (player2X, batRect2.center[1]-(dificultad*diferencia2/abs(diferencia2)))
        
        if (bx <= 0):
            direction = -1
            bx, by = (500, random.randint(10,height-10))
            ballSpeed = VELOCIDAD
            sx, sy = (ballSpeed, ballSpeed)
            ballRect.center = (bx, by)
            player_score += 1
            ballserved = False
            player1Y = height/2
            player2Y = height/2
            batRect1.center = (player1X, player1Y)
            batRect2.center = (player2X, player2Y)
            sy *= (-1)**player_score
            
        if (bx >= width - 8):
            direction = 1
            bx, by = (500, random.randint(10,height-10))
            ballSpeed = VELOCIDAD
            sx, sy = (-ballSpeed, -ballSpeed)
            ballRect.center = (bx, by)
            machine_score += 1
            ballserved = False
            player1Y = height/2
            player2Y = height/2
            batRect1.center = (player1X, player1Y)
            batRect2.midtop = (player2X, player2Y)
            sy *= (-1)**machine_score
            fitness += 20
            
        if (by <= 0):
            by = 0
            sy *= -1
        if (by >= height - 8):
            by = 700 - 8
            sy *= -1
        
        if ballRect.colliderect(batRect1):
            bx = player1X + 12
            sx *= -1
            sy = (by-batRect1.center[1])/3
            fitness += 10
        if ballRect.colliderect(batRect2):
            bx = player2X - 12
            sx *= -1
            sy = (by-batRect2.center[1])/3
            right_hits += 1
            
        if player_score == 1 or machine_score == 5 or right_hits >= 30:
            run = False
            
        score_text = letra50.render(f"{machine_score}       {player_score}", True, (200,200,200))
        
        mainSurface.blit(score_text, (425,50))
        mainSurface.blit(ball, ballRect)
        mainSurface.blit(bat1, batRect1)
        mainSurface.blit(bat2, batRect2)
        pygame.draw.line(mainSurface,(255,255,255), (width/2, 0), (width/2, height))

        pygame.display.update()
    
    return fitness

def test_ai(neural_network):
    
    fpsClock = pygame.time.Clock()

    player_score = 0
    machine_score = 0
    dificultad = 9

    width,height = 1000,700
    mainSurface = pygame.display.set_mode((width,height))
    pygame.display.set_caption('pong');
    black = pygame.Color(0, 0, 0)

    facil_text_pos = (width/2-272,height/2-100,200,100)
    dificil_text_pos = (width/2+114,height/2-100,200,100)
    twoplayer_text_pos = (width/2-215,height/2+100,200,100)

    facil_button_pos = (width/2-300,height/2-120,200,100)
    dificil_button_pos = (width/2+100,height/2-120,200,100)
    twoplayer_button_pos = (width/2-300,height/2+80,600,100)

    # bat init
    bat1 = pygame.image.load('pong_bat.png')
    bat2 = pygame.image.load('pong_bat.png')
    player1Y = height/2
    player2Y = height/2
    player1X = 50
    player2X = width-50
    batRect1 = bat1.get_rect()
    batRect2 = bat2.get_rect()

    # ball init
    VELOCIDAD = 8
    ball = pygame.image.load('ball.png')
    ballRect = ball.get_rect()
    ballStartY = 300
    ballSpeed = VELOCIDAD
    bx, by = (100, ballStartY)
    sx, sy = (ballSpeed, ballSpeed)
    ballRect.center = (bx, by)
    ballserved = False
    twoplayer = False

    batRect1.midtop = (player1X, player1Y)
    batRect2.midtop = (player2X, player2Y)
    
    run = True
    while run:
        ballserved = True
        mainSurface.fill(black)
        # events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse = pygame.mouse.get_pos()
                    
        keys = pygame.key.get_pressed()
        if keys[K_UP]:
            player2Y -= 10
            batRect2.midtop = (player2X, player2Y)
            ballserved = True
        if keys[K_DOWN]:
            player2Y += 10
            batRect2.midtop = (player2X, player2Y)
            ballserved = True
        if keys[K_w]:
            player1Y -= 10
            batRect1.midtop = (player1X, player1Y)
            ballserved = True
        if keys[K_s]:
            player1Y += 10
            batRect1.midtop = (player1X, player1Y)
            ballserved = True
        
#          if batRect1.center[1] <= 30:
#              batRect1.center = (player1X, 30)
#          if batRect1.center[1] >= height-30:
#              batRect1.center = (player1X, height-30)

        if player2Y <= 10:
            player2Y = 10
        if player2Y >= height-65:
            player2Y = height-65
        
        if ballserved:
            bx += sx
            by += sy
            ballRect.center = (bx, by)
        
        paddle_y_normalized = player1Y / 700
        ball_y_normalized = by / 700
        ball_distance_normalized = (bx-batRect1.center[0]) / 900 
        
        output = neural_network.activate([paddle_y_normalized, ball_y_normalized, ball_distance_normalized])
        
        # Interpret outputs
        if output[0] > output[1] and output[0] > output[2]:
            # Move paddle up
            player1Y -= 10
        elif output[1] > output[0] and output[1] > output[2]:
            pass  # No movement
        elif output[2] > output[0] and output[2] > output[1]:
            # Move paddle down
            player1Y += 10

        batRect1.center = (player1X,player1Y)

        if (bx <= 0):
            direction = -1
            bx, by = (500, ballStartY)
            ballSpeed = VELOCIDAD
            sx, sy = (ballSpeed, ballSpeed)
            ballRect.center = (bx, by)
            player_score += 1
            ballserved = False
            player1Y = height/2
            player2Y = height/2
            batRect1.center = (player1X, player1Y)
            batRect2.center = (player2X, player2Y)
            sy *= (-1)**player_score
            
        if (bx >= width - 8):
            direction = 1
            bx, by = (500, ballStartY)
            ballSpeed = VELOCIDAD
            sx, sy = (-ballSpeed, -ballSpeed)
            ballRect.center = (bx, by)
            machine_score += 1
            ballserved = False
            player1Y = height/2
            player2Y = height/2
            batRect1.center = (player1X, player1Y)
            batRect2.midtop = (player2X, player2Y)
            sy *= (-1)**machine_score
            
        if (by <= 0):
            by = 0
            sy *= -1
        if (by >= height - 8):
            by = 700 - 8
            sy *= -1
        
        if ballRect.colliderect(batRect1):
            bx = player1X + 12
            sx *= -1
            sy = (by-batRect1.center[1])/3
        if ballRect.colliderect(batRect2):
            bx = player2X - 12
            sx *= -1
            sy = (by-batRect2.center[1])/3
        
        if player_score == 5 or machine_score == 5:
            player_score = 0
            machine_score = 0
            
        score_text = letra50.render(f"{machine_score}       {player_score}", True, (200,200,200))
        
        mainSurface.blit(score_text, (425,50))
        mainSurface.blit(ball, ballRect)
        mainSurface.blit(bat1, batRect1)
        mainSurface.blit(bat2, batRect2)
        pygame.draw.line(mainSurface,(255,255,255), (width/2, 0), (width/2, height))
        
        fpsClock.tick(60)
        pygame.display.update()
        
def eval_genome(genomes, config):
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        genome.fitness = simulate_game(net)
        
def run_neat(config):
    #population = neat.Checkpointer.restore_checkpoint('neat-checkpoint-1')
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    population.add_reporter(neat.Checkpointer(100))

    winner = population.run(eval_genome, max_generations) #How many generations it takes to create a checkpoint
    
    with open("best.pickle", "wb") as f: #best pickle will only be saved once max_generations are finished
        pickle.dump(winner, f)
        
def test_best_network(config):
    with open("best.pickle", "rb") as f:
        winner = pickle.load(f)
    winning_net = neat.nn.FeedForwardNetwork.create(winner, config)
    test_ai(winning_net)

# Choose one of the following, if you want to run the ai so it learns, mark "test_best_network" as a comment and run "run_neat".
# If you want to test the best ai network available do it the other way arround.

run_neat(config)
#test_best_network(config)