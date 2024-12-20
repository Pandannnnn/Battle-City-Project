import pyxel
import pyxelgrid
import random
from stage import Tank,Bullet,Cell,Stages
from stage import TANK_WIDTH,TANK_LENGTH,DIM,ROW,COL


#these two functions help in comparing whether two intervals are overlapping, often used in collision logic
def is_disjoint(a: tuple[int,int]|tuple[float,float], b: tuple[int,int]|tuple[float,float]):
    assert(a[0] <= a[1]) and (b[0] <= b[1])
    return (a[0] > b[1]) or (b[0] > a[1])
def intersects(a: tuple[int,int]|tuple[float,float], b: tuple[int,int]|tuple[float,float]):
    return not is_disjoint(a,b)

class MyGame(pyxelgrid.PyxelGrid[int]):

    def __init__(self):
        super().__init__(r=ROW, c=COL, dim=DIM)  
    def init(self) -> None:
        # called once at initialization time, initializes every variable needed
        self.stage=Stages()
        #the list of stages from the class Stages in stage file is stored in self.initial
        #the stage the will be currently played is stored in self.gamestate
        self.initial=self.stage.stages
        self.stageindex=0
        self.gamestate = self.initial[self.stageindex]
        self.player_lives=2
        self.initalenemies=sum(1 for tank in self.gamestate.tanks if tank.state=="enemy")+len(self.gamestate.enemytanks)
        self.tanks_appended=0
        self.tanks:list[Tank]=self.gamestate.tanks
        self.Cell:list[Cell]=self.gamestate.cells
        self.enemymovement=4
        #storage of two kinds of tank
        self.normaltanks:list[Tank]=[]
        self.buffedtanks:list[Tank]=[]
        #code for obtaining cells with none positions for the random powerup block to spawn
        self.all_positions = {(x, y) for x in range(COL) for y in range(ROW)}
        self.defined_positions = {(cell.i, cell.j) for cell in self.Cell}
        self.no_state_positions = self.all_positions - self.defined_positions
        #powerup variables
        self.powerup:list[str]=["speed","life","nocd"]
        self.power=None
        self.spawn_powerup=True
        self.has_powerup=False
        self.speedup=False
        self.nodelay=False
        self.powerup_cooldown=1000
        #randomizing the initial tanks
        for tank in self.tanks:
            if tank.state=="enemy":
                number=random.randint(1,2)
                if number==1:
                    self.normaltanks.append(tank)
                else:
                    self.buffedtanks.append(tank)
        #assertion that all cells initialize in the stage file are within bounds
        for cell in self.Cell:
            assert 0<=cell.i<self.r and 0<=cell.j<self.c, f"{cell} is out of bounds"
        self.bullets:list[Bullet]=[]
        self.direction=["north","south","west","east"]
        self.vy=[-1,1,0,0]
        self.vx=[0,0,-1,1]
        self.bulletspeed=3
        self.bullet_speed_y=[-1*self.bulletspeed,1*self.bulletspeed,0,0]
        self.bullet_speed_x=[0,0,-1*self.bulletspeed,1*self.bulletspeed]
        self.black_screen=[Cell for Cell in self.Cell if Cell.black_screen]
        self.movement=1
        self.cooldown=25
        self.recent_button: int = 0  
        self.recent_button_timer: int = 0
        self.bullet_per_every_frame=10
        self.bullet_radius=2
        self.complete_game=False
        #stores the list of (i,j) row,col or (x,y) plane coordinates which contains the explosion coordinatess
        self.explosion:list[tuple[float,float]]=[] #(i,j)
        self.tank_explosion:list[tuple[float,float]]=[] #(x,y)
        #time(frames) to render explosion
        self.explosioncooldown=20 #for self.explosion
        self.explosioncooldown2=20 #for self.tank_explosion
        self.usedcheatcode=False
        self.sequence_state=0
        pyxel.load("test.pyxres")
        pyxel.mouse(visible=True)
    
    #used when resetting the game from stage one
    def init_state(self):
        return Stages()
    
    #code for transitioning to the next stage after winning the previous stage
    #this sets up everything in the next stage and resetting some variables
    #some variables are retained when changing stages, thus is not in set_stage
    def set_stage(self,n:int):
        self.stageindex=n
        self.gamestate = self.initial[self.stageindex]
        self.tanks_appended=0
        self.initalenemies=sum(1 for tank in self.gamestate.tanks if tank.state=="enemy")+len(self.gamestate.enemytanks)
        self.tanks:list[Tank]=self.gamestate.tanks
        self.Cell:list[Cell]=self.gamestate.cells
        self.bullets:list[Bullet]=[]
        self.normaltanks:list[Tank]=[]
        self.buffedtanks:list[Tank]=[] 
        for tank in self.tanks:
            if tank.state=="enemy":
                number=random.randint(1,2)
                if number==1:
                    self.normaltanks.append(tank)
                else:
                    self.buffedtanks.append(tank)
        self.complete_game=False
        self.all_positions = {(x, y) for x in range(COL) for y in range(ROW)}
        self.defined_positions = {(cell.i, cell.j) for cell in self.Cell}
        self.no_state_positions = self.all_positions - self.defined_positions
        self.spawn_powerup=True
    
    def reset_game(self):
        self.stage=self.init_state()
       
        self.initial=self.stage.stages
        self.stageindex=0
        self.gamestate = self.initial[self.stageindex]
        self.initalenemies=sum(1 for tank in self.gamestate.tanks if tank.state=="enemy")+len(self.gamestate.enemytanks)
        self.tanks_appended=0
        self.tanks:list[Tank]=self.gamestate.tanks
        self.Cell:list[Cell]=self.gamestate.cells
        self.bullets:list[Bullet]=[]
        self.complete_game=False
        self.player_lives=2 
        self.normaltanks:list[Tank]=[]
        self.buffedtanks:list[Tank]=[] 
        for tank in self.tanks:
            if tank.state=="enemy":
                number=random.randint(1,2)
                if number==1:
                    self.normaltanks.append(tank)
                else:
                    self.buffedtanks.append(tank)
        self.all_positions = {(x, y) for x in range(COL) for y in range(ROW)}
        self.defined_positions = {(cell.i, cell.j) for cell in self.Cell}
        self.no_state_positions = self.all_positions - self.defined_positions
        self.spawn_powerup=True
        self.has_powerup=False
        self.speedup=False
        self.nodelay=False
        self.powerup_cooldown=1000
        self.gamestate.win=False
        self.usedcheatcode=False
        self.reset_sequence()


    """
     The collision detection takes into account the tank's direction (north, south, east, west)
        and adjusts the bounding box of the tank accordingly:
            - For north or south direction: The tank's width is along the x-axis and length along the y-axis.
            - For east or west direction: The tank's length is along the x-axis and width along the y-axis.
        The method returns True if there is any intersection between the tank's bounds and 
        an impassable cell's bounds, indicating a collision. Otherwise, it returns False.
     It also raises a runtime error if the tank's direction is not valid
    """
    def tank_cell_collision(self,tank:Tank):
        Cell=self.Cell
        for stone in Cell:
            if stone.state is not None and stone.state!="forest" and stone.state!="random":
                i,j=stone.i,stone.j
                start_height,end_height=((i)*self.dim),((i+1)*self.dim)
                
                start_width,end_width=((j)*self.dim),((j+1)*self.dim)
                if tank.direction in ["north", "south"]:
                    if intersects((start_width,end_width), ((tank.x),(tank.x+TANK_WIDTH-1))) \
                        and intersects((start_height,end_height), ((tank.y),(tank.y+TANK_LENGTH-1))):
                        return True
                elif tank.direction in ["east", "west"]:
                    if intersects((start_width,end_width), ((tank.x),(tank.x+TANK_LENGTH-1))) \
                        and intersects((start_height,end_height), ((tank.y),(tank.y+TANK_WIDTH-1))):
                        return True
                else:
                    raise RuntimeError
        return False

    
    #similar to the tank_cell_collision function but it checks whether the player tank gets to the random block
    #If true,it returns (i,j) of the powerup_cell for removal usage
    def powerup_cell_collision(self,tank:Tank):
        Cell=self.Cell
        if tank.state=="player":
            for stone in Cell:
                if stone.state=="random":
                    i,j=stone.i,stone.j
                    start_height,end_height=((i)*self.dim),((i+1)*self.dim)
                    
                    start_width,end_width=((j)*self.dim),((j+1)*self.dim)
                    if tank.direction in ["north", "south"]:
                        if intersects((start_width,end_width), ((tank.x),(tank.x+TANK_WIDTH-1))) \
                            and intersects((start_height,end_height), ((tank.y),(tank.y+TANK_LENGTH-1))):
                            return True,(i,j)
                    elif tank.direction in ["east", "west"]:
                        if intersects((start_width,end_width), ((tank.x),(tank.x+TANK_LENGTH-1))) \
                            and intersects((start_height,end_height), ((tank.y),(tank.y+TANK_WIDTH-1))):
                            
                            return True,(i,j)
                    else:
                        raise RuntimeError
            return False
    def tank_inbounds(self,tank:Tank)->bool:
        return not ((tank.x>=self.width-16 or tank.y>=self.height-16 or tank.x<=0 or tank.y<=0) or self.tank_cell_collision(tank))
    
    def move_tank(self,direction:str,tank:Tank):
        vy=self.vy
        vx=self.vx
        tank.direction=direction
        tank.vy=vy[self.direction.index(tank.direction)]
        tank.vx=vx[self.direction.index(tank.direction)]
        if tank.state=="player":
            tank.y+=tank.vy*self.movement
            tank.x+=tank.vx*self.movement
        if tank.state=="enemy":
            tank.y+=tank.vy*self.enemymovement
            tank.x+=tank.vx*self.enemymovement
        if not self.tank_inbounds(tank) and tank.state=="player":
            tank.y-=tank.vy*self.movement
            tank.x-=tank.vx*self.movement
        if not self.tank_inbounds(tank) and tank.state=="enemy":
            tank.y-=tank.vy*self.enemymovement
            tank.x-=tank.vx*self.enemymovement
    
   
    def bullet_cell_collision(self,bullet:Bullet)->bool|tuple[bool,tuple[int,int]]:
        Cell=self.Cell
        vx,vy=bullet.vx,bullet.vy
        for material in Cell:
            if  material.state not in ["southmirror","northmirror","water","forest","random"] and material.state is not None:
                i,j=material.i,material.j
                
                start_height,end_height=((i)*self.dim),((i+1)*self.dim)
                start_width,end_width=((j)*self.dim),((j+1)*self.dim)
                 #checks if the bullet is within bounds of a cell block
                if start_width<=bullet.x<=end_width and start_height<=bullet.y<=end_height:

                    #we decided that the bullet explodes besides the block it collides
                    if vx<0:
                        self.explosion.append((i,j+1))
                    elif vx>0:
                        self.explosion.append((i,j-1))
                    elif vy<0:
                        self.explosion.append((i+1,j))
                    elif vy>0:
                        self.explosion.append((i-1,j))
                    #since it would be too loud if the other enemies has a sound when shooting,we decided that only 
                    #the player has a sound when a bullet has collided
                    if bullet.origin=="player":
                        pyxel.play(1,1)
                    return True,(i,j)
        return False
    #iterates through all bullets and checks if the current bullet collides with any other bullet in the game using the intersects function
    #if yes, stores the bullets (x,y) coordinates then add to the explosion variable
    #then remove the bullets to make an illusion that it explodes
    def check_bullet_to_bullet_collision(self,bullet:Bullet):
        for bullets in self.bullets:
            if bullets!=bullet:
                if intersects((bullet.x-self.bullet_radius+self.bulletspeed,bullet.x+self.bullet_radius+self.bulletspeed),
                              (bullets.x-self.bullet_radius+self.bulletspeed,bullets.x+self.bullet_radius+self.bulletspeed)) \
                              and intersects((bullet.y-self.bullet_radius+self.bulletspeed,bullet.y+self.bullet_radius+self.bulletspeed),
                              (bullets.y-self.bullet_radius+self.bulletspeed,bullets.y+self.bullet_radius+self.bulletspeed)):
                    x1,y1=bullets.x,bullets.y
                    x2,y2=bullet.x,bullet.y
                    self.tank_explosion.append((x1,y1))
                    self.tank_explosion.append((x2,y2))
                    pyxel.play(1,1)
                    self.bullets.remove(bullet)
                    self.bullets.remove(bullets)

    #since the mirror is like a line, we can use a simple point-line bounds checker
    def mirror_bounds(self,x1:int,x2:int,y1:int,y2:float,x:float,y:float)->bool:
        return min(x1,x2)<=x<=max(x1,x2) and min(y1,y2)<=y<=max(y1,y2)
                    
    def mirror_bullet_collision(self,bullet:Bullet)->None:
        Cell=self.Cell
        vx,vy=bullet.vx,bullet.vy
        #code for determining the bullet direction by passing the index of the nonzero velocity component of the bullet
        direction_index=-1
        if vx!=0:
            direction_index=self.bullet_speed_x.index(vx)
        if vy!=0:
            direction_index=self.bullet_speed_y.index(vy)
        assert direction_index>=0
        bullet_direction=self.direction[direction_index]
        #iterates through every cell for convenience,then the if statement filters out the northmirror and southmirror cells
        for material in Cell:
            #for every mirror, there is a constant change in direction, thus we can use a dictionary for it
            #then determine the new_direction using the bullet direction
            #if the bullet is within bounds of the mirror, the vy and vx of the bullet changes according to the new direction
            #also for friendlyfire purposes and code logic, the bullet.origin if it is a player changes
            if material.state=="northmirror":
                change_of_dir:dict[str,str]={"north":"east","east":"north","south":"west","west":"south"}
                new_direction=change_of_dir[bullet_direction]
                direction_index = self.direction.index(new_direction)
                i,j=material.i,material.j
                start_height,end_height=((i)*self.dim),((i+1)*self.dim)
                start_width,end_width=((j)*self.dim),((j+1)*self.dim)
                if self.mirror_bounds(start_width,end_width,start_height,end_height,bullet.x,bullet.y):
                    if bullet.origin=="player":
                        bullet.origin="friendlyfire"
                    bullet.vy = self.bullet_speed_y[direction_index]
                    bullet.vx = self.bullet_speed_x[direction_index]
            elif material.state=="southmirror":
                change_of_dir:dict[str,str]={"east":"south","south":"east","west":"north","north":"west"}
                new_direction=change_of_dir[bullet_direction]
                direction_index = self.direction.index(new_direction)
                i,j=material.i,material.j
                start_height,end_height=((i)*self.dim),((i+1)*self.dim)
                start_width,end_width=((j)*self.dim),((j+1)*self.dim)
                if self.mirror_bounds(start_width,end_width,start_height,end_height,bullet.x,bullet.y):
                    if bullet.origin=="player":
                        bullet.origin="friendlyfire"
                    bullet.vy = self.bullet_speed_y[direction_index]
                    bullet.vx = self.bullet_speed_x[direction_index]

    
   
    def tank_bullet_collision(self,bullet:Bullet):
        tanks=self.tanks
        origin=bullet.origin
        #iterates through every tank, then checks whether the bullet is in bounds of the tank
        for tank in tanks:
            start_height,end_height=tank.y,tank.y+TANK_LENGTH-1
            start_width,end_width=tank.x,tank.x+TANK_WIDTH-1
            if start_width<=bullet.x<=end_width and start_height<=bullet.y<=end_height:
                #if the player hits an enemy, it will cause an explosion, thus the (x,y) of the enemy will be appended
                #if the tank.alive of a tank=False it simply disappears when it is an enemy
                #then in general, whether a player hits an enemy or an enemy hits a player, the bullet disappears
                if (origin=="player" or origin=="friendlyfire") and tank.state=="enemy" and tank.alive:
                    tank.alive=False
                    self.gamestate.enemies-=1
                    self.tank_explosion.append((tank.x,tank.y))
                    pyxel.play(1,1)
                    if self.bullets and bullet in self.bullets:
                        self.bullets.remove(bullet)
                elif (origin=="enemy" or origin=="friendlyfire") and tank.state=="player":
                    if tank.alive:
                        self.powerup_cooldown=0
                        self.player_lives-=1
                    tank.alive=False
                    if self.bullets and bullet in self.bullets:
                        self.bullets.remove(bullet)
    def reset_sequence(self):
        self.sequence_state=0
    """
    the cheatcode of our game is PAM, which when typed either wins the stage, or when it is the last stage, 
    it will win you the game!
    If the cheatcode is typed in order P-A-M the cheatcode will activate. Otherwise, you will have to type it again.
    The self.sequence_state variable will reset if the cheatcode is not typed properly.
    """
    def cheat_code(self):
         if not self.usedcheatcode:
            if self.sequence_state == 0:
                if pyxel.btnp(pyxel.KEY_P):
                    self.sequence_state = 1
                elif pyxel.btnp(pyxel.KEY_A) or pyxel.btnp(pyxel.KEY_M):
                    self.reset_sequence()  
            elif self.sequence_state == 1:
                if pyxel.btnp(pyxel.KEY_A):
                    self.sequence_state = 2
                elif pyxel.btnp(pyxel.KEY_P) or pyxel.btnp(pyxel.KEY_M):
                    self.reset_sequence()  
            elif self.sequence_state == 2:
                if pyxel.btnp(pyxel.KEY_M):
                    self.sequence_state = 3 
                elif pyxel.btnp(pyxel.KEY_P) or pyxel.btnp(pyxel.KEY_A):
                    self.reset_sequence()  
            if self.sequence_state == 3:
                if self.stageindex + 1 < len(self.initial):
                    self.gamestate.win = True
                    self.set_stage(self.stageindex + 1)
                    self.usedcheatcode = True
                else:
                    self.complete_game = True
                    self.gamestate.is_game_over = True
                    self.usedcheatcode = True           
    def shoot_bullets(self,tank:Tank)->None:
        #the bullet is initially at the center of the tank
        x = tank.x+TANK_WIDTH//2
        y = tank.y+TANK_LENGTH//2
        direction_index = self.direction.index(tank.direction)
        bullet_vy = self.bullet_speed_y[direction_index]
        bullet_vx = self.bullet_speed_x[direction_index]
        #then based on the direction of the bullet, the initial position of the bullet will be adjusted to the tip of the tank
        #then bullets are appended to self.bullets for drwaing
        if bullet_vy>0:
            y+=TANK_LENGTH//2
        if bullet_vy<0:
            y-=TANK_LENGTH//2
        if bullet_vx>0:
            x+=TANK_WIDTH//2
        if bullet_vx<0:
            x-=TANK_WIDTH//2
        #this line ensures that there is at most one bullet that originated from the player tank in the map at any time.
        if not any(bullet.origin== "player" for bullet in self.bullets) and not any(bullet.origin== "friendlyfire" for bullet in self.bullets) and tank.state=="player" :
            bullet=Bullet(x,y,bullet_vx,bullet_vy,tank.state)
            #plays a sound when a bullet is fired by the player
            if (bullet.origin=="player" or bullet.origin=="friendlyfire"):
                pyxel.play(0,0)
            self.bullets.append(bullet)
       
        elif tank.state=="enemy":
            bullet=Bullet(x,y,bullet_vx,bullet_vy,tank.state)
            self.bullets.append(bullet)
    
        
    def update(self) -> None:
        DIRECTION_KEYS = {
        pyxel.KEY_W: "north",
        pyxel.KEY_A: "west",
        pyxel.KEY_S: "south",
        pyxel.KEY_D: "east",
        }
        if not self.gamestate.is_game_over:
            #self.gamestate.enemytanks contains the tanks that will be spawned
            if pyxel.frame_count!=0 and pyxel.frame_count%150==0 and self.tanks_appended<len(self.gamestate.enemytanks):
                number=random.randint(1,2)
                if number==1:
                    self.normaltanks.append(self.gamestate.enemytanks[self.tanks_appended])
                else:
                    self.buffedtanks.append(self.gamestate.enemytanks[self.tanks_appended])
                self.gamestate.tanks.append(self.gamestate.enemytanks[self.tanks_appended])
                self.tanks_appended+=1
            for tank in self.tanks:
                """
                Movement Logic:

                1)Variables:
                -Given the self.cooldown variable, when a movement button is pressed, the recent_button_timer will be self.cooldown
                and will be decremented per frame.  
                -the self_recent_button stores the button previously pressed.
                2)Condition: The tank will move if either the recent_button is already the pressed one (indicating continuous movement) 
                or the recent_button_timer is 0 (indicating the cooldown has expired).
                """
                if tank.state=="player" and tank.alive:
                    if self.recent_button_timer > 0:
                        self.recent_button_timer -= 1
                    if pyxel.btnp(pyxel.KEY_W,hold=1,repeat=1):
                        if self.recent_button == pyxel.KEY_W or self.recent_button_timer == 0:
                            self.recent_button = pyxel.KEY_W
                            self.move_tank(DIRECTION_KEYS[pyxel.KEY_W],tank)
                        if self.recent_button_timer == 0:
                            self.recent_button_timer = self.cooldown
                    elif pyxel.btnp(pyxel.KEY_S,hold=1,repeat=1):
                        if self.recent_button == pyxel.KEY_S or self.recent_button_timer == 0:
                            self.recent_button = pyxel.KEY_S
                            self.move_tank(DIRECTION_KEYS[pyxel.KEY_S],tank)

                        if self.recent_button_timer == 0:
                            self.recent_button_timer = self.cooldown
        
                    elif pyxel.btnp(pyxel.KEY_A,hold=1,repeat=1):
                        if self.recent_button == pyxel.KEY_A or self.recent_button_timer == 0:
                            self.recent_button = pyxel.KEY_A
                            self.move_tank(DIRECTION_KEYS[pyxel.KEY_A],tank)

                        if self.recent_button_timer == 0:
                            self.recent_button_timer = self.cooldown
                    elif pyxel.btnp(pyxel.KEY_D,hold=1,repeat=1):
                        if self.recent_button == pyxel.KEY_D or self.recent_button_timer == 0:
                            self.recent_button = pyxel.KEY_D
                            self.move_tank(DIRECTION_KEYS[pyxel.KEY_D],tank)
                        if self.recent_button_timer == 0:
                            self.recent_button_timer = self.cooldown
                    
                    if pyxel.btnp(pyxel.KEY_SPACE,hold=1,repeat=self.bullet_per_every_frame):
                        self.shoot_bullets(tank)
                #Reviving the tank by pressing 2
                if tank.state=="player" and not tank.alive and self.player_lives!=0:
                    if pyxel.btnp(pyxel.KEY_2):
                        tank.alive=True
                #In general, the enemy can move,change direction, or fire depending per frame count that is set
                #The weights indicates the probability in which each choices can be made,which in this case is equal to every move.
                if tank.state=="enemy" and tank.alive and tank in self.normaltanks:
                    choices = ["direction", "move","fire"]
                    weights = [0.33, 0.33,0.33]
                    direction=self.direction
                    if pyxel.frame_count%20==0:
                        result = random.choices(choices, weights=weights, k=1)[0]
                        if result==choices[0]:
                            index=random.randint(0,3)
                            tank.direction=direction[index]
                        if result==choices[1]:
                            for _ in range(2):
                                self.move_tank(tank.direction,tank)
                        if result==choices[2]:
                            self.shoot_bullets(tank)
                if tank.state=="enemy" and tank.alive and tank in self.buffedtanks:
                    choices = ["direction", "move","fire"]
                    weights = [0.33, 0.33,0.33]
                    direction=self.direction
                    if pyxel.frame_count%10==0:
                        result = random.choices(choices, weights=weights, k=1)[0]
                        if result==choices[0]:
                            index=random.randint(0,3)
                            tank.direction=direction[index]
                        if result==choices[1]:
                            for _ in range(4):
                                self.move_tank(tank.direction,tank)
                        if result==choices[2]:
                            self.shoot_bullets(tank)
                #Code for rendering the explosion for a moment 
                #self.explosion=[] removes all explosion drawings instantly after the cooldown
                if self.explosion:
                    self.explosioncooldown-=1
                    if self.explosioncooldown<=0:
                        self.explosion=[]
                        self.explosioncooldown=20
                if self.tank_explosion:
                    self.explosioncooldown2-=1
                    if self.explosioncooldown2<=0:
                        self.tank_explosion=[]
                        self.explosioncooldown2=20
                
                is_powerup=self.powerup_cell_collision(tank) 
                if is_powerup and tank.state=="player":
                    x,y=is_powerup[1]
                    self.Cell.remove(Cell(x,y,self.dim,self.dim,"random",False))
                    self.power=random.choice(self.powerup)
                    self.powerup_cooldown=1000
                    self.has_powerup=True
            for bullet in self.bullets:
                """"
                for every frame, check every possible collisions of the bullet and change the state/direction of the bullet 
                depending on the result
                """
                self.check_bullet_to_bullet_collision(bullet)
                self.tank_bullet_collision(bullet)
                self.mirror_bullet_collision(bullet)
                if not self.bullet_cell_collision(bullet):
                    bullet.x+=bullet.vx
                    bullet.y+=bullet.vy
                elif self.bullet_cell_collision(bullet):
                    result=self.bullet_cell_collision(bullet)
                    assert  isinstance (result,tuple)
                    coordinate=result[1]
                    for cell in self.Cell:
                        if cell.i==coordinate[0] and cell.j==coordinate[1] and cell.state=="brick":
                            cell.state="halfbrick"
                        elif cell.i==coordinate[0] and cell.j==coordinate[1] and cell.state=="halfbrick":
                            self.no_state_positions.add((cell.i,cell.j))
                            cell.state=None
                        elif cell.i==coordinate[0] and cell.j==coordinate[1] and cell.state=="home":
                            cell.state=None
                            self.gamestate.is_game_over=True
                    if self.bullets:
                        self.bullets.remove(bullet)
            
            if self.gamestate.enemies==(self.initalenemies//2):
                if self.spawn_powerup:
                    x,y=random.choice(list(self.no_state_positions))
                    self.Cell.append(Cell(x,y,self.dim,self.dim,"random",False))
                    
                    self.spawn_powerup=False      
            if self.has_powerup and self.powerup_cooldown>0:
                if self.power==self.powerup[0]:
                    self.speedup=True
                if self.power==self.powerup[1]:
                    self.player_lives+=1
                    #since adding a life does not have a time limit
                    
                    self.powerup_cooldown=0
                if self.power==self.powerup[2]:
                    self.nodelay=True
                self.powerup_cooldown-=1
            if self.nodelay:
                self.cooldown=0
            else:
                self.cooldown=20
            if self.speedup:
                self.movement=2
            else:
                self.movement=1
            if self.powerup_cooldown==0:
                self.has_powerup=False
                self.speedup=False
                self.nodelay=False
                self.powerup_cooldown=1000
            if self.gamestate.enemies==0:
                self.gamestate.win=True
                if self.stageindex+1<len(self.initial):
                    self.set_stage(self.stageindex+1)
    
            if all(stage.win==True for stage in self.initial):
                self.gamestate.is_game_over=True
                self.complete_game=True
            if self.player_lives==0:
                self.gamestate.is_game_over=True
            self.cheat_code()
            if pyxel.btnp(pyxel.KEY_1):
                self.reset_game()
            
        if self.gamestate.is_game_over:
            if pyxel.btnp(pyxel.KEY_1):
                self.reset_game() 
    def draw_cell(self, i: int, j: int, x: int, y: int) -> None:
        for stone in self.Cell:
            if stone.i==i and stone.j==j and stone.state=="stone":
                pyxel.blt(x,y,0,32,48,self.dim,self.dim)
            if stone.i==i and stone.j==j and stone.state=="brick":
                pyxel.blt(x,y,0,32,32,self.dim,self.dim)
            if stone.i==i and stone.j==j and stone.state=="halfbrick":
                pyxel.blt(x,y,0,48,32,self.dim,self.dim)
            if stone.i==i and stone.j==j and stone.state=="northmirror":
                pyxel.blt(x,y,0,0,48,self.dim,self.dim,0)
            if stone.i==i and stone.j==j and stone.state=="southmirror":
                pyxel.blt(x,y,0,16,48,self.dim,self.dim,0)
            if stone.i==i and stone.j==j and stone.state=="water":
                pyxel.blt(x,y,0,0,64,self.dim,self.dim)
            if stone.i==i and stone.j==j and stone.state=="home":
                pyxel.blt(x,y,0,0,112,self.dim,self.dim)
            if stone.i==i and stone.j==j and stone.state=="forest":
                pyxel.blt(x,y,0,16,112,self.dim,self.dim,0)
            if stone.i==i and stone.j==j and stone.state=="random":
                pyxel.blt(x,y,0,32,112,self.dim,self.dim,0)
            if stone.i==i and stone.j==j and stone in self.black_screen:
                pyxel.rect(x,y,16,16,10)
        if (i,j) in self.explosion:
            pyxel.blt(x,y,0,16,80,w=self.dim,h=self.dim,colkey=0)
        pyxel.blt(273,103,0,32,80,16,16,0)
        pyxel.text(273,105,f"   Lives:{self.player_lives}",2)
        pyxel.blt(273,113,0,48,80,11,11,0)
        pyxel.text(273,115,f"   Enemies:{self.gamestate.enemies}",3)
        if self.has_powerup and self.powerup_cooldown>0:
            pyxel.text(273,125,f"Powerup:{self.power}",8)
    def pre_draw_grid(self) -> None:
        pyxel.cls(0)
        for (x,y) in self.tank_explosion:
            pyxel.blt(x,y,0,16,80,w=self.dim,h=self.dim,colkey=0)
        
        bullets=self.bullets
        for bullet in bullets:
            if bullet.origin=="player" or bullet.origin=="friendlyfire":
                pyxel.circ(bullet.x,bullet.y,self.bullet_radius,1)
            elif bullet.origin=="enemy":
                pyxel.circ(bullet.x,bullet.y,self.bullet_radius,2)
        for tank in self.tanks:
            if tank.state=="player" and tank.alive:
                if tank.direction=="north":
                    pyxel.blt(tank.x,tank.y,0,0,0,w=TANK_WIDTH,h=TANK_LENGTH,colkey=0)
                elif tank.direction=="south":
                    pyxel.blt(tank.x,tank.y,0,16,0,w=TANK_WIDTH,h=TANK_LENGTH,colkey=0)
                elif tank.direction=="east":
                    pyxel.blt(tank.x,tank.y,0,32,0,w=TANK_WIDTH,h=TANK_LENGTH,colkey=0)
                elif tank.direction=="west":
                    pyxel.blt(tank.x,tank.y,0,48,0,w=TANK_WIDTH,h=TANK_LENGTH,colkey=0)
            elif tank.state=="enemy" and tank.alive and tank in self.normaltanks:
                if tank.direction=="north":
                    pyxel.blt(tank.x,tank.y,0,0,16,w=TANK_WIDTH,h=TANK_LENGTH,colkey=0)
                elif tank.direction=="south":
                    pyxel.blt(tank.x,tank.y,0,16,16,w=TANK_WIDTH,h=TANK_LENGTH,colkey=0)
                elif tank.direction=="east":
                    pyxel.blt(tank.x,tank.y,0,32,16,w=TANK_WIDTH,h=TANK_LENGTH,colkey=0)
                elif tank.direction=="west":
                    pyxel.blt(tank.x,tank.y,0,48,16,w=TANK_WIDTH,h=TANK_LENGTH,colkey=0)
            elif tank.state=="enemy" and tank.alive and tank in self.buffedtanks:
                if tank.direction=="north":
                    pyxel.blt(tank.x,tank.y,0,0,96,w=TANK_WIDTH,h=TANK_LENGTH,colkey=0)
                elif tank.direction=="south":
                    pyxel.blt(tank.x,tank.y,0,16,96,w=TANK_WIDTH,h=TANK_LENGTH,colkey=0)
                elif tank.direction=="east":
                    pyxel.blt(tank.x,tank.y,0,32,96,w=TANK_WIDTH,h=TANK_LENGTH,colkey=0)
                elif tank.direction=="west":
                    pyxel.blt(tank.x,tank.y,0,48,96,w=TANK_WIDTH,h=TANK_LENGTH,colkey=0)
            elif tank.state=="player" and not tank.alive:
                pyxel.blt(tank.x,tank.y,0,0,32,w=TANK_WIDTH,h=TANK_LENGTH,colkey=0)
            
    def post_draw_grid(self) -> None:
        
        if self.gamestate.is_game_over and not self.complete_game:
            pyxel.text(100, 100, "Game Over!", pyxel.frame_count % 16)
        if self.complete_game and self.gamestate.is_game_over:
            pyxel.text(100, 100, "Congrats You Win!!!", pyxel.frame_count % 16)
        
    

my_game = MyGame()
my_game.run(title="Battle City", fps=60)
