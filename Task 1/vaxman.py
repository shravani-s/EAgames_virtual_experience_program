
import random
import pygame

black = (0, 0, 0)
white = (255, 255, 255)
blue = (0, 0, 255)
green = (0, 255, 0)
red = (255, 0, 0)                                                                                          
purple = (255, 0, 255)
yellow   = (255, 255, 0)

pacicon=pygame.image.load('images/pacman.png')
pygame.display.set_icon(pacicon)

#Add music
pygame.mixer.init()
pygame.mixer.music.load('pacman.mp3')
pygame.mixer.music.play(-1, 0.0)

# This class represents the bar at the bottom that the player controls
class Wall(pygame.sprite.Sprite):

    def __init__(self, x: int, y: int, width: int, height: int, color: tuple):

        # Call the parent's constructor
        super().__init__()
  
        # Make a blue wall, of the size specified in the parameters
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
  
        # Make our top-left corner the passed-in location.
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.left = x

# This creates all the walls in room 1
def setupRoomOne(all_sprites_group):
    # Make the walls. (x_pos, y_pos, width, height)
    wall_group=pygame.sprite.RenderPlain()
     
    # This is a list of walls. Each is in the form [x, y, width, height]
    walls = [ [0,0,6,600],
              [0,0,600,6],
              [0,600,606,6],
              [600,0,6,606],
              [300,0,6,66],
              [60,60,186,6],
              [360,60,186,6],
              [60,120,66,6],
              [60,120,6,126],
              [180,120,246,6],
              [300,120,6,66],
              [480,120,66,6],
              [540,120,6,126],
              [120,180,126,6],
              [120,180,6,126],
              [360,180,126,6],
              [480,180,6,126],
              [180,240,6,126],
              [180,360,246,6],
              [420,240,6,126],
              [240,240,42,6],
              [324,240,42,6],
              [240,240,6,66],
              [240,300,126,6],
              [360,240,6,66],
              [0,300,66,6],
              [540,300,66,6],
              [60,360,66,6],
              [60,360,6,186],
              [480,360,66,6],
              [540,360,6,186],
              [120,420,366,6],
              [120,420,6,66],
              [480,420,6,66],
              [180,480,246,6],
              [300,480,6,66],
              [120,540,126,6],
              [360,540,126,6]
            ]
     
    # Loop through the list. Create the wall, add it to the list
    for item in walls:
        wall=Wall(item[0],item[1],item[2],item[3],blue)
        wall_group.add(wall)
        all_sprites_group.add(wall)
         
    # return our new list
    return wall_group

def setupGate(all_sprites_group):
      gate = pygame.sprite.RenderPlain()
      gate.add(Wall(282,242,42,2,white))
      all_sprites_group.add(gate)
      return gate

class Block(pygame.sprite.Sprite):

     
    # Constructor. Pass in the color of the block, 
    # and its x and y position
    def __init__(self, width: int, height: int, color: tuple):

        # Call the parent class (Sprite) constructor
        super().__init__()
 
        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.image = pygame.Surface([width, height])
        self.image.fill(white)
        self.image.set_colorkey(white)
        pygame.draw.ellipse(self.image, color, [0, 0, width, height])
 
        # Fetch the rectangle object that has the dimensions of the image
        # image.
        # Update the position of this object by setting the values 
        # of rect.x and rect.y
        self.rect = self.image.get_rect()

class Intersection(Block):


    @staticmethod
    def switcher(subset: set, superset1: set, superset2: set) -> set:


        if subset.issubset(superset1):
            return superset1
        elif subset.issubset(superset2):
            return superset2
        else:
            return subset

    horizontals = frozenset({'left', 'right'})
    verticals = frozenset({'up', 'down'})
    switch = {horizontals:   verticals,
              verticals  : horizontals}

    def __init__(self, width: int, directions: set, color=black):

        super().__init__(width, width, color)
        self.directions = directions

    def choose_dir(self, current_dir: str) -> str:

        #debug
        #print('intersection, current:', current_dir, 'possible:', self.directions)

        cls = Intersection
        change = random.choice([True, False])
        if change:
            new_dir = cls.switch[cls.switcher(set({current_dir}),
                                              cls.horizontals, cls.verticals)]
            new_dir &= self.directions
            if len(new_dir) > 1:
                return random.choice(list(new_dir))
            else:
                return set(new_dir).pop()
        else:
            return current_dir

class Collision(Exception):

    def __init__(self, sprites: list, *args: object) -> None:


        self.sprite = sprites[0]
        self.collided_with = sprites[1]

        super().__init__(*args)

class IntersectionCollision(Collision):
    """An exception thrown during collisions with Intersection objects."""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class WallCollision(Collision):
    """An exception to throw during collisions with Wall objects."""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class Player(pygame.sprite.Sprite):

  
    # Set speed vector
    change_x = 0
    change_y = 0
  
    def __init__(self, x: int, y: int, filename: str, groups: list) -> None:

        #TODO: remove groups and pass the groups to the Sprite constructor instead.

        super().__init__()
   
        # Set height, width
        self.image = pygame.image.load(filename).convert()

        # preserve filename
        self.filename = filename
  
        # Make our top-left corner the passed-in location.
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.prev_x = x
        self.prev_y = y

        for group in groups:
            group.add(self)

    def changespeed(self, x: int, y: int):

        self.change_x += x
        self.change_y += y
          
    def update(self, walls, gate, intersections=False):

        # Get the old position, in case we need to go back to it
        old_x = self.rect.left
        old_y = self.rect.top

        # Determine new positions
        new_x = old_x + self.change_x
        self.rect.left = new_x
        new_y = old_y + self.change_y
        self.rect.top = new_y

        gate_hit = False
        intersection = False

        # Check for collisions
        collide = pygame.sprite.spritecollide(self, walls, False)
        if gate != False:
            gate_hit = pygame.sprite.spritecollide(self, gate, False)
        if intersections:
            intersection = pygame.sprite.spritecollide(self, intersections,
                        False, collided=pygame.sprite.collide_rect_ratio(.25))
        if collide or gate_hit or intersection:
            if not intersection:
                self.rect.left = old_x
                self.rect.top = old_y

            # Raise Collision exception if the calling object is a Ghost
            try:
                if type(self) is Ghost:
                    if intersection:
                        raise IntersectionCollision([self, intersection])
                    else:
                        raise WallCollision(
                                      [self, collide if collide else gate_hit])
            except NameError:
                pass

#Inheritime Player klassist
class Ghost(Player):

    speed = 30
    all_dirs = {'left', 'right', 'up', 'down'}
    move_dict = {'left' :  (speed, 0),
                 'right': (-speed, 0),
                 'up'   :  (0, speed),
                 'down' : (0, -speed)}

    def __init__(self, x: int, y: int, filename: str, groups):


        self.last_intersection = None
        self.prev_dirs = {'down'}
        self.current_dir = 'right'
        self.changespeed(*Ghost.move_dict[self.current_dir])

        super().__init__(x, y, filename, groups)

    def choose_dir(self, prev_dirs, all_dirs) -> str:

        #debug
        #print('wall', prev_dirs)

        dir_choices = list(all_dirs.difference(prev_dirs))
        if len(dir_choices) > 0:
            return random.choice(dir_choices)
        else:
            #print('error')
            self.prev_dirs = set()
            return random.choice(list(all_dirs))

    def __mul__(self, num: int) -> list:

        new_ghosts = []
        if num > 0:
            new_ghosts.append(self)
            for i in range(num - 1):
                new_ghosts.append(Ghost(self.rect.left, self.rect.top,
                                                 self.filename, self.groups()))
        return new_ghosts

intersections = [(0, 2, {'up', 'down', 'right'}),
                 (4, 2, {'down', 'left', 'right'}),
                 (8, 2, {'up', 'left', 'right'}),
                 (10, 2, {'up', 'left', 'right'}),
                 (14, 2, {'down', 'left', 'right'}),
                 (18, 2, {'up', 'down', 'left'}),
                 (4, 4, {'up', 'left', 'right'}),
                 (14, 4, {'up', 'left', 'right'}),
                 (6, 6, {'down', 'left', 'right'}),
                 (8, 6, {'up', 'left', 'right'}),
                 (10, 6, {'up', 'left', 'right'}),
                 (12, 6, {'down', 'left', 'right'}),
                 (2, 8, {'up', 'down', 'left'}),
                 (9, 8, {'up', 'left', 'right'}),
                 (16, 8, {'up', 'down', 'right'}),
                 (2, 10, {'up', 'left', 'right'}),
                 (4, 10, {'up', 'down', 'left'}),
                 (14, 10, {'up', 'down', 'right'}),
                 (16, 10, {'up', 'left', 'right'}),
                 (4, 12, {'up', 'left', 'right'}),
                 (14, 12, {'up', 'left', 'right'}),
                 (2, 16, {'up', 'down', 'right'}),
                 (4, 16, {'up', 'left', 'right'}),
                 (14, 16, {'up', 'left', 'right'}),
                 (16, 16, {'up', 'down', 'left'}),
                 (2, 18, {'up', 'left', 'right'}),
                 (8, 18, {'up', 'left', 'right'}),
                 (10, 18, {'up', 'left', 'right'}),
                 (16, 18, {'up', 'left', 'right'})]

# Call this function so the Pygame library can initialize itself
pygame.init()
  
# Create an 606x606 sized screen
screen = pygame.display.set_mode([606, 606])

# This is a list of 'sprites.' Each block in the program is
# added to this list. The list is managed by a class called 'RenderPlain.'


# Set the title of the window
pygame.display.set_caption('Pacman')

# Create a surface we can draw on
background = pygame.Surface(screen.get_size())

# Used for converting color maps and such
background = background.convert()
  
# Fill the screen with a black background
background.fill(black)


clock = pygame.time.Clock()

pygame.font.init()
font = pygame.font.Font("freesansbold.ttf", 24)

#default locations for Pacman and monstas
w = 303-16 #Width
p_h = (7*60)+19 #Pacman height
m_h = (4*60)+19 #Monster height
b_h = (3*60)+19 #Binky height
i_w = 303-16-32 #Inky width
c_w = 303+(32-16) #Clyde width

def startGame():

    # construct level
    

    # Construct the pygame.sprite.Group containers for holding the sprites.
    all_sprites_group = pygame.sprite.RenderPlain()
    block_group = pygame.sprite.RenderPlain()
    intersection_group = pygame.sprite.RenderPlain()
    monsta_group = pygame.sprite.RenderPlain()
    pacman_collide = pygame.sprite.RenderPlain()
    wall_group = setupRoomOne(all_sprites_group)

    gate = setupGate(all_sprites_group)

    # Create all moving sprites
    Pacman = Player( w, p_h, "images/pacman.png",
                                           [all_sprites_group, pacman_collide])
    # Blinky
    Ghost(w, b_h, "images/Blinky.png", [monsta_group, all_sprites_group])
    # Pinky
    Ghost(w, m_h, "images/Pinky.png", [monsta_group, all_sprites_group])
    # Inky
    Ghost(i_w, m_h, "images/Inky.png", [monsta_group, all_sprites_group])
    # Clyde
    Ghost(c_w, m_h, "images/Clyde.png", [monsta_group, all_sprites_group])

    num_ghosts = len(monsta_group)

    # Place Intersections (for ghost movement)
    for isect in intersections:
        intersection = Intersection(6, isect[2])
        intersection.rect.x = 30 * isect[0] + 32
        intersection.rect.y = 30 * isect[1] + 32
        intersection_group.add(intersection)
        all_sprites_group.add(intersection)

    # Draw the grid
    for row in range(19):
        for column in range(19):

            # Don't spawn blocks/dots behind the gate (ghost spawn area)
            if (row in (7, 8)) and (column in (8, 9, 10)):
                continue
            else:
                # Spawn the blocks/dots
                block = Block(4, 4, yellow)
  
                # Set the block positions so that they are spaced out
                block.rect.x = 30 * column + 32
                block.rect.y = 30 * row + 32
  
                # Don't spawn a block/dot where the walls or player is
                b_collide = pygame.sprite.spritecollide(block, wall_group, False)
                p_collide = pygame.sprite.spritecollide(
                                                    block, pacman_collide, False)
                if b_collide:
                    continue
                elif p_collide:
                    continue
                else:
                    # Add the block to the list of objects
                    block_group.add(block)
                    all_sprites_group.add(block)

    block_count = len(block_group)
    score = 0
    done = False
  
    # Fire a ghost_timer event every 30 seconds
    ghost_timer_id = pygame.event.custom_type()
    pygame.event.Event(ghost_timer_id)
    pygame.time.set_timer(ghost_timer_id, 30000)

    while done == False:
        # ALL EVENT PROCESSING SHOULD GO BELOW THIS COMMENT
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done=True

            #debug
            #if event.type == pygame.MOUSEBUTTONDOWN:
            #    print(event.pos)
            #if event.type == pygame.MOUSEBUTTONUP:
            #    print(event.pos)
          
            # Increase the speed of the player once when a key is pressed
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    Pacman.changespeed(-30,0)
                if event.key == pygame.K_RIGHT:
                    Pacman.changespeed(30,0)
                if event.key == pygame.K_UP:
                    Pacman.changespeed(0,-30)
                if event.key == pygame.K_DOWN:
                    Pacman.changespeed(0,30)

            # Decrease the speed when the key is released
            # TODO: Make a Player method to reset speed (just set change_x, etc 
            # to 0)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    Pacman.changespeed(30,0)
                if event.key == pygame.K_RIGHT:
                    Pacman.changespeed(-30,0)
                if event.key == pygame.K_UP:
                    Pacman.changespeed(0,30)
                if event.key == pygame.K_DOWN:
                    Pacman.changespeed(0,-30)
      
            # Multiply ghosts every 30 seconds
            if event.type == ghost_timer_id:
                for ghost in monsta_group.sprites():
                    ghost * 2
                #debug
                #print(len(monsta_group))
          
        # ALL EVENT PROCESSING SHOULD GO ABOVE THIS COMMENT
   
        # ALL GAME LOGIC SHOULD GO BELOW THIS COMMENT
        Pacman.update(wall_group, gate)

        for ghost in monsta_group:
            try:
                ghost.update(wall_group, False, intersection_group)
  
            except Collision as collision:
                # Stop moving in current direction
                x, y = Ghost.move_dict[ghost.current_dir]
                x *= -1
                y *= -1
                ghost.changespeed(x, y)

                if type(collision) is IntersectionCollision:
                    # Move in new direction
                    if (ghost.last_intersection is not 
                                                   collision.collided_with[0]):
                        ghost.current_dir = (
                            collision.collided_with[0].choose_dir(
                                                            ghost.current_dir)
                            )
                        ghost.changespeed(*Ghost.move_dict[ghost.current_dir])
                        ghost.last_intersection = collision.collided_with[0]

                elif type(collision) is WallCollision:
                    # Move in new direction
                    ghost.prev_dirs.add(ghost.current_dir)
                    ghost.current_dir = ghost.choose_dir(
                                              ghost.prev_dirs, Ghost.all_dirs)
                    ghost.changespeed(*Ghost.move_dict[ghost.current_dir])
                    ghost.last_intersection = None

            else:
                ghost.prev_dirs = set()
                ghost.last_intersection = None

        # See if the Pacman block has collided with any blocks/dots
        blocks_hit_list = pygame.sprite.spritecollide(Pacman, block_group,
                                                                         True)
       
        # Update the score based on the list of collisions.
        if len(blocks_hit_list) > 0:
            score += len(blocks_hit_list)
      
        # ALL GAME LOGIC SHOULD GO ABOVE THIS COMMENT
   
        # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
        screen.fill(black)
        
        all_sprites_group.draw(screen)

        text=font.render("Score: "+str(score)+"/"+str(block_count), True, red)
        screen.blit(text, [10, 10])

        if score == block_count:
          doNext("Congratulations, you won!", 145,
                            all_sprites_group, block_group,
                                monsta_group, pacman_collide, wall_group, gate)

        monsta_hit_list = pygame.sprite.spritecollide(Pacman, monsta_group,
                                                                        True)

        if len(monsta_group) >= 32 * num_ghosts:
            doNext("Game Over", 235, all_sprites_group,
                                block_group, monsta_group,
                                             pacman_collide, wall_group, gate)

        # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
      
        pygame.display.flip()
    
        clock.tick(10)

def doNext(message, left, all_sprites_group, block_group,
                              monsta_group, pacman_collide, wall_group, gate):
    while True:
        # ALL EVENT PROCESSING SHOULD GO BELOW THIS COMMENT
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                if event.key == pygame.K_RETURN:
                    del all_sprites_group
                    del block_group
                    #TODO: del intersection_group?
                    del monsta_group
                    del pacman_collide
                    del wall_group
                    del gate
                    startGame()

        #Grey background
        w = pygame.Surface((400,200))  # the size of your rect
        w.set_alpha(10)                # alpha level
        w.fill((128,128,128))           # this fills the entire surface
        screen.blit(w, (100,200))    # (0,0) are the top-left coordinates

        #Won or lost
        text1=font.render(message, True, white)
        screen.blit(text1, [left, 233])

        text2=font.render("To play again, press ENTER.", True, white)
        screen.blit(text2, [135, 303])
        text3=font.render("To quit, press ESCAPE.", True, white)
        screen.blit(text3, [165, 333])

        pygame.display.flip()

        clock.tick(10)

startGame()

pygame.quit()