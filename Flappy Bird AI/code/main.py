import pygame
import random
import os
import neat
pygame.init()

WIN_WIDTH = 600
WIN_HEIGHT = 800
FLOOR = 730
STAT_FONT = pygame.font.Font("font/FlappyBird.ttf", 50)
END_FONT = pygame.font.Font("font/FlappyBird.ttf", 70)
DRAW_LINES = False

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird AI")

pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("images","pipe.png")).convert_alpha())
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("images","bg.png")).convert_alpha(), (600, 900))
bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("images","bird" + str(x) + ".png"))) for x in range(1,4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("images","base.png")).convert_alpha())

gen = 0

class Bird:
    # Bird Class is Representing the Flappy Bird.
    MAX_ROTATION = 25
    IMGS = bird_images
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        """
        Initialize the object
        :param x: starting x pos (int)
        :param y: starting y pos (int)
        :return: None
        """
        self.x = x
        self.y = y
        self.tilt = 0  # Degrees to tilt
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        # Make the Bird Jump
        # return: None
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        # Make the Bird Move
        # return: None
        
        self.tick_count += 1

        # For Downward Acceleration
        displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2  # Calculate Displacement

        # Terminal Velocity
        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:  # Tilt Up
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:  # Tilt Down
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        # Draw the Bird
        # :param win: pygame window or surface
        # return: None
        
        self.img_count += 1

        # For Animation of the Bird, Loop Through Three Images.
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # So When Bird is Nose Diving It Isn't Flapping.
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2


        # Tilt the Bird
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        # Gets the Mask For the Current Image of the Bird
        # return: None
        
        return pygame.mask.from_surface(self.img)


class Pipe():
    # Represents a Pipe Object
    
    GAP = 200
    VEL = 5

    def __init__(self, x):
        
        # Initialize the Pipe Object
        # param x: int
        # param y: int
        # return: None
        
        self.x = x
        self.height = 0

        # Where the Top and Bottom of the Pipe Is
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        self.passed = False

        self.set_height()

    def set_height(self):
        # Set the Height of the Pipe, From the Top of the Screen
        # return: None
        
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        # Move Pipe Based on Velocity
        # return: None
        
        self.x -= self.VEL

    def draw(self, win):
        # Draw the Both of the Top and the Bottom of the Pipe
        # param win: pygame window/surface
        # return: None
        
        # Draw the Top
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # Draw the Bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    def collide(self, bird, win):
        # Returns If a Point Is Colliding with the Pipe
        # param bird: Bird object
        # return: Bool
        
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True

        return False

class Base:
    # Represnts the Moving Floor of the Game
    
    VEL = 5
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y):
        # Initialize the Object
        # param y: int
        # return: None
        
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        # Move Floor so It Looks Like It's Scrolling
        # return: None
        
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        # Draw the Floor. These are the Two Images that Moves Together.
        :param win: the pygame surface/window
        :return: None
        
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def blitRotateCenter(surf, image, topleft, angle):
    # Rotate a Surface and Blit It to the Window
    # param surf: the surface to blit to
    # param image: the image surface to rotate
    # param topLeft: the top left position of the image
    # param angle: a float value for angle
    # return: None
    
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def draw_window(win, birds, pipes, base, score, gen, pipe_ind):
    # Draws the Windows For the Main Game Loop
    # param win: pygame window surface
    # param bird: a Bird object
    # param pipes: List of pipes
    # param score: score of the game (int)
    # param gen: current generation
    # param pipe_ind: index of closest pipe
    # return: None
    
    if gen == 0:
        gen = 1
    win.blit(bg_img, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
        # Draw the Lines From Bird to Pipe
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
            except:
                pass
        # Draw Bird
        bird.draw(win)

    # Score
    score_label = STAT_FONT.render("Score: " + str(score),1,(255, 255, 255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    # Generations
    score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255, 255, 255))
    win.blit(score_label, (10, 10))

    # Alive
    score_label = STAT_FONT.render("Alive: " + str(len(birds)),1,(255, 255 ,255))
    win.blit(score_label, (10, 50))

    pygame.display.update()


def eval_genomes(genomes, config):
    # Runs the Simulation of the Current Population of the Birds and Sets Their Fitness Based on the Distance They Reach In the Game.
    
    global WIN, gen
    win = WIN
    gen += 1

    # Start by Creating Lists Holding the Genome Itself, the Neural Network Associated with the Genome and the Bird Object that Uses that Network to Play.
    nets = []
    birds = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # Start with Fitness Level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230,350))
        ge.append(genome)

    base = Base(FLOOR)
    pipes = [Pipe(700)]
    score = 0

    clock = pygame.time.Clock()

    run = True
    while run and len(birds) > 0:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():  # Determine Whether to Use the First or Second
                pipe_ind = 1                                                                # Pipe on the Screen for Neural Network Input

        for x, bird in enumerate(birds):  # Give Each Bird a Fitness of 0.1 For Each Frame It Stays Alive
            ge[x].fitness += 0.1
            bird.move()

            # Send the Bird Location, Top Pipe Location and Bottom Pipe Location and Determine From Network Whether to Jump or Not
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:  # We Use a Tanh Activation Function So Result Will be Between -1 and 1. If Over 0.5 Jump
                bird.jump()

        base.move()

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            # Check For Collision
            for bird in birds:
                if pipe.collide(bird, win):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            # Can Add This Line to Give More Reward for Passing Through a Pipe [not required]
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        for bird in birds:
            if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        draw_window(WIN, birds, pipes, base, score, gen, pipe_ind)

        # Break If Score Gets to 20
        # if score > 20:
        #   pickle.dump(nets[0],open("best.pickle", "wb"))
        #   break'''


def run(config_file):
    # Runs the NEAT Algorithm to Train a Neural Network to Play Flappy Bird.
    # param config_file: config-path
    # return: None
    
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the Population, Which Is the Top-Level Object For a NEAT Run.
    p = neat.Population(config)

    # Add a StdOut Reporter to Show Progress in the Terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # p.add_reporter(neat.Checkpointer(5))

    # Run For Up to 50 Generations.
    winner = p.run(eval_genomes, 50)

    # Show Final Stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine Path to Configuration File. This Path Manipulation Is Here So That the Script will Run Successfully Regardless of the Current Working Directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
