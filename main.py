import pygame
from pygame import mixer
import random
import mido
import os
from numba import jit
from scamp import *
import numpy as np

pygame.init()

BLACK = (0, 0, 0)
GREY = (128, 128, 128)
YELLOW = (255, 255,0)
GREEN = (0,255,0)

WIDTH, HEIGHT = 700,700
TILE_SIZE = 10
GRID_WIDTH = WIDTH // TILE_SIZE
GRID_HEIGHT = HEIGHT // TILE_SIZE
FPS = 60


screen = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()

note_grid = []
key_seed = 69

s = Session()
s.tempo = 60

note_lenght = 0.1
note_volume = 0.3

#newborn, right_most
snd_filter_mode = [True,True]


#session.print_default_soundfont_presets()

piano = s.new_part("piano")

piano.play_note(60, 1, 1.0)

c_major = ([])

mouse_pressed = False

def gen(num):
    return set([(random.randrange(0,GRID_WIDTH),random.randrange(0, GRID_HEIGHT)) for _ in range(num)])

def draw_grid(positions,old_positions):
    for position in positions:
        if position in old_positions:
            col, row = position
            top_left = (col * TILE_SIZE, row * TILE_SIZE)
            pygame.draw.rect(screen, YELLOW, (*top_left,TILE_SIZE,TILE_SIZE))
        
        else:
            col, row = position
            top_left = (col * TILE_SIZE, row * TILE_SIZE)
            pygame.draw.rect(screen, GREEN, (*top_left,TILE_SIZE,TILE_SIZE))
            

    for row in range(GRID_HEIGHT):
        pygame.draw.line(screen, BLACK, (0,row * TILE_SIZE),(WIDTH,row * TILE_SIZE))
        
    for col in range(GRID_WIDTH):
        pygame.draw.line(screen, BLACK, (col * TILE_SIZE,0),(col * TILE_SIZE,HEIGHT))

def adjust_grid(positions):

    all_neighbors = set()
    new_positions = set()
    old_positions = positions
    new_born = set()
    
    
    for position in positions:

        neighbors = get_neighbors(position)
        all_neighbors. update(neighbors)
        
        neighbors = list(filter(lambda x: x in positions, neighbors))
        
        if len(neighbors) in [2,3]:
            new_positions.add(position)
    
    for position in all_neighbors:
        neighbors = get_neighbors(position)
        neighbors = list(filter(lambda x: x in positions, neighbors))
        
        if len(neighbors) == 3:
            new_positions.add(position)
            if position not in old_positions:
                new_born.add(position)
            
    
    play_note_func(new_positions,new_born)
    print(clock.get_fps())
    return new_positions, old_positions,
    

def get_neighbors(pos):

    x, y = pos

    neighbors = []

    for dx in [-1, 0, 1]:

        if x + dx < 0:

            x += GRID_WIDTH

        elif x + dx == GRID_WIDTH:

            x -= GRID_WIDTH

        for dy in [-1, 0, 1]:

            if y + dy < 0:

                y += GRID_HEIGHT

            elif y + dy == GRID_HEIGHT:

                y -= GRID_HEIGHT

            if dx == 0 and dy == 0:

                continue



            neighbors.append((x + dx, y + dy))



    return neighbors






def main():
    update_freq = 10
    note_set_up()
    running = True
    playing = False
    count = 0 
    FPS = 60
    volume = 0.3
    positions = set()
    old_positions = set()
    recording = False
    
    while running:
        clock.tick(FPS)
        
        if playing:
            count += 1
            
        
        if count >= update_freq:
            count = 0
            positions ,old_positions = adjust_grid(positions)
        
        pygame.display.set_caption("Playing process rate= " + str(FPS//update_freq)  + " update freq = " + str(update_freq) + " FPS = "  +str(FPS) if playing else "Paused process rate = " + str(FPS//update_freq)  + " update freq = " + str(update_freq) + " FPS = "  +str(FPS))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                
                x, y = pygame.mouse.get_pos()
                col = x // TILE_SIZE
                row = y // TILE_SIZE
                pos = (col, row)
                
                if bool(pos in positions) and event.button == 3:
                    positions.remove(pos)
                else:
                    positions.add(pos)
                    
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    playing = not playing
                
                if event.key == pygame.K_c:
                    positions = set()
                    playing = False

                if event.key == pygame.K_g:
                    positions = gen(random.randrange(40,100) * GRID_WIDTH)
                    count = 0
                    playing = False
                    
                
                if event.key == pygame.K_h:
                    FPS = 60
                    update_freq = 10
                
                if event.key == pygame.K_w:
                    volume += 0.1
                    note_volume = volume
                
                if event.key == pygame.K_s:
                    volume -= 0.1
                    note_volume = volume
                
                if event.key == pygame.K_RIGHT:
                    if update_freq > 1:
                        update_freq -= 1
                
                if event.key == pygame.K_LEFT:
                    update_freq += 1
                
                if event.key == pygame.K_UP:
                    if FPS > 1:
                        FPS = FPS//2
                
                if event.key == pygame.K_DOWN:
                    FPS =  FPS*2
                    
                
                if event.key == pygame.K_m:
                    if  recording:
                        s.stop_transcribing().to_score(title = 'machine jarble', composer = 'life').show_xml()
                    else:
                        s.start_transcribing()
                    recording = not recording


            
        screen.fill(GREY)
        draw_grid(positions,old_positions)
        pygame.display.update()
        
        
        
    
    pygame.QUIT
    
def draw_new_cells(positions_sent):
    positions = positions_sent
    x, y = pygame.mouse.get_pos()
    col = x // TILE_SIZE
    row = y // TILE_SIZE
    pos = (col, row)
    if pos in positions:
        positions.remove(pos)
    else:
        positions.add(pos)
    return positions
    
    
def play_note_func(new_positions,new_born):
    valid_notes = []
    for pos in new_positions:
    
        if  snd_filter_mode[0] == False & snd_filter_mode[1] == False :
            valid_notes.append(pos)
            continue
        
        if snd_filter_mode[0] & snd_filter_mode[1]:
            if pos in new_born:
                if len(valid_notes) == 0:
                    valid_notes.append(pos)
                else:
                    for v_pos in valid_notes:
                        v_x,v_y = v_pos
                        x, y = pos
                        if v_y == y:
                            if x > v_x:
                                valid_notes.remove(v_pos)
                                valid_notes.append(pos)
            continue
        if snd_filter_mode[0] == True:
            if pos in new_born:
                valid_notes.append(pos)
        if snd_filter_mode[1]:
            if len(valid_notes) == 0:
                valid_notes.append[pos]
            else:
                for v_pos in valid_notes:
                    v_x,v_y = v_pos
                    x, y = pos
                    if v_y == y:
                        if x > v_x:
                            valid_notes.remove(v_pos)
                            valid_notes.append(pos)
                    
                    
                    
            
            note_num = x + y * (GRID_WIDTH-1)
            s.fork(piano.play_note,(note_grid[note_num], note_volume, note_lenght))
            
    if len(valid_notes) > 0:
            for v_pos in valid_notes:
                x, y = v_pos
                note_num = x + y * (GRID_WIDTH-1)
                s.fork(piano.play_note,(note_grid[note_num], note_volume, note_lenght))
    


def note_set_up():
    #distances between notes in a major scale
    major_scale_diff = np.array([0,2,4,5,7,9,11])
    minor_scale_diff = np.array([0,2,4,5,7,9,11])
    major_scale = np.array([])
    minor_scale = np.array([])
    
    major_scale = np.append (major_scale_diff, [[major_scale_diff+12*i] for i in range(1,9)])
    print(len(major_scale))
    print(major_scale)
    
    piano_range = range(21,109)
    
    
    c_major = 12 + major_scale

    for note in c_major:
        if note in piano_range:
            #piano.play_note(note, 1.0, note_lenght)
            pass
        else:
            c_major = np.delete(c_major, np.where(c_major == note))
            
    print(c_major)
    #random.Random(key_seed).shuffle(c_major)
    #print("shuffled")
    #print(c_major)
    while len(note_grid) < GRID_WIDTH * GRID_HEIGHT:
        for note in c_major:
            note_grid.append(note)

if __name__ == "__main__":
    #note_set_up()    
    main()