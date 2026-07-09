import pygame
import time
import random
import os

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

display = pygame.display.set_mode((400, 600))
pygame.display.set_caption("Rhythm Squared")
frame = pygame.time.Clock()

gray = (45,45,45)
textc = (255,255,255)
boxc = (99,75,7)

play_minigame = 0
play_game = 0

rowvalues = 0, 0, 0, 0
rowheights = 0, 0, 0, 0

eqmiss = random.randint(1,9)
eqtype = random.randint(1,4)
eqknow = random.randint(1,9)
eqans = ""

font = pygame.font.SysFont('Arial', 50, bold=True)
buttonfont = pygame.font.SysFont("Arial", 30, bold=True)

equation_text = font.render("6+_=13", True, textc)
equation_box = equation_text.get_rect()
equation_box.topleft = (20, 0)

ministart = pygame.Rect(75, 500, 250, 60)
start_text = buttonfont.render("Play Minigame (:", True, textc)
startrect = start_text.get_rect()
startrect.center = ministart.center

gamestart = pygame.Rect(75, 100, 250, 60)
play_text = buttonfont.render("Play Game", True, textc)
playrect = play_text.get_rect()
playrect.center = gamestart.center

button = pygame.Rect(60, 515, 50, 50)
button2 = pygame.Rect(150, 515, 50, 50)
button3 = pygame.Rect(240, 515, 50, 50)
button4 = pygame.Rect(330, 515, 50, 50)

score = 0

score_text = font.render(str(score), True, textc)
score_box = score_text.get_rect()
score_box.topleft = (270, 0)

words = font.render(str(random.randint(1,9)), True, textc)
wordsbox = words.get_rect()
wordsx = 5
wordsbox.topleft = (wordsx, 0)

words2 = font.render(str(random.randint(1,9)), True, textc)
wordsbox2 = words2.get_rect()
wordsx2 = 5
wordsbox2.topleft = (wordsx, 0)

words3 = font.render(str(random.randint(1,9)), True, textc)
wordsbox3 = words3.get_rect()
wordsx3 = 5
wordsbox3.topleft = (wordsx, 0)

words4 = font.render(str(random.randint(1,9)), True, textc)
wordsbox4 = words4.get_rect()
wordsx4 = 5
wordsbox4.topleft = (wordsx, 0)

height = 50
height2 = 50
height3 = 50
height4 = 50
box = pygame.Rect(0, 500, 100, 50)

boxhit_offset = -15
x_range_min = 5
x_range_max = 360
speed = 4

caught = ""
spawned = 0
spawned2 = 0
spawned3 = 0

scircle = (0,0,0)

boxhit = pygame.Rect(0, 500 - boxhit_offset, 100, 50)

wordsx = random.randint(x_range_min, x_range_max)
wordsx2 = random.randint(x_range_min, x_range_max)
wordsx3 = random.randint(x_range_min, x_range_max)

operate = ""

Song = "song.mp3"
notes = "song.nt"

keyrow = {1:3,2:2,3:1,4:0}
rowkey = {3: pygame.K_u, 2: pygame.K_i, 1: pygame.K_o, 0: pygame.K_p}
hit_area_top = 470
hit_area_bottom = 560

offset_just_in_case_I_care_about_it = 0

music_start = False
game_start_time = None
song_index = 0
music_playing = False

def load_song(path):
    events = []
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    t_str, lane_str = line.split(",")
                    events.append((float(t_str), int(lane_str)))
                except ValueError:
                    continue
    events.sort(key=lambda e: e[0])
    return events

song_events = load_song(notes)

def start_moosic():
    global game_start_time, music_playing
    game_start_time = pygame.time.get_ticks()
    music_playing = False
    if os.path.exists(Song):
        try:
            pygame.mixer.music.load(Song)
            pygame.mixer.music.play()
            music_playing = True
        except pygame.error:
            pass

def get_song_elapsed():
    if music_playing:
        pos_ms = pygame.mixer.music.get_pos()
        if pos_ms >= 0:
            return (pos_ms / 1000) - offset_just_in_case_I_care_about_it
    return ((pygame.time.get_ticks() - game_start_time) / 1000) - offset_just_in_case_I_care_about_it

def reset_song():
    global song_index, music_start, last_filler
    for row in rows:
        row.clear()
    red_lines.clear()
    song_index = 0
    music_start = False
    last_filler = 0

fakes_per_real = 2

def spawn_filler_for(real_row_i):
    other_lanes = [i for i in range(4) if i != real_row_i]
    chosen = random.sample(other_lanes, min(fakes_per_real, len(other_lanes)))
    for row_i in chosen:
        n = createnum(row_x[row_i], real=False, value=random_fake())
        render(n)
        rows[row_i].append(n)

def update_spawns(elapsed):
    global song_index
    travel_time = (590 - 50) / (speed * 60)
    while song_index < len(song_events):
        hit_time, lane = song_events[song_index]
        spawn_time = hit_time - travel_time
        if elapsed >= spawn_time:
            if lane == 5:
                spawn_lines()
            else:
                row_i = keyrow.get(lane)
                if row_i is not None:
                    n = createnum(row_x[row_i], real=True, value=eqmiss)
                    n["y"] = 50
                    render(n)
                    rows[row_i].append(n)
                    spawn_filler_for(row_i)
            song_index += 1
        else:
            break

def update_notes():
    for row in rows:
        for n in row[:]:
            n["y"] += speed
            if n["y"] >= 590:
                row.remove(n)

def hangle_key(key):
    global score, scircle
    row_i = None
    for r_i, expected_key in rowkey.items():
        if key == expected_key:
            row_i = r_i
            break
    if row_i is None:
        return
    
    row = rows[row_i]
    candidates = [n for n in row if hit_area_top <= n["y"] <= hit_area_bottom]
    hit_note = None

    for n in candidates:
        if n["real"]:
            hit_note = n
            break

    if hit_note is None and candidates:
        hit_note = candidates[0]

    if hit_note is not None:
        row.remove(hit_note)
        if hit_note["real"]:
            score += 1
            scircle = (0, 255, 0)
        else:
            score -= 1
            scircle = (255,0,0)
    else:
        score -= 1 
        scircle = (255,0,0)

red_lines = []

def spawn_lines():
    red_lines.append({"y": 50})

def update_lines():
    for line in red_lines[:]:
        line["y"] += speed
        if line["y"] >= hit_area_top:
            generateeq()
            red_lines.remove(line)

filler_time = 0.2
last_filler = 0

def random_fake():
    choices = [i for i in range(1,10) if i != eqmiss]
    return random.choice(choices)

def update_filler(elapsed):
    global last_filler
    if elapsed - last_filler >= filler_time:
        last_filler = elapsed
        row_i = random.randint(0,3)
        n = createnum(row_x[row_i], real=False, value=random_fake())
        render(n)
        rows[row_i].append(n)

def generateeq():
    global operate
    global eqans
    global eqmiss
    global eqtype
    global eqknow
    eqmiss = random.randint(1,9)
    eqtype = random.randint(1,4)
    eqknow = random.randint(1,9)
    if eqtype == 1:
        eqans = eqknow + eqmiss
        operate = "+"
    elif eqtype == 2:
        eqans = eqknow - eqmiss
        operate = "-"
    elif eqtype == 3:
        eqans = eqknow * eqmiss
        operate = "x"
    elif eqtype == 4:
        eqans = eqknow * eqmiss
        save = eqknow
        eqknow = eqans
        eqans = save
        operate = "/"

def checknum():
    global caught
    global score
    global eqans
    global spawned
    global spawned2
    global spawned3
    global height
    global height2
    global height3
    global wordsx
    global x_range_max
    global x_range_min
    global words
    global words2
    global words3
    global wordsx2
    global wordsx3
    global words4
    global wordsx4
    global height4
    if play_minigame == 1:
        if height >= 590:
            height = random.randint(45,65)
            wordsx = random.randint(x_range_min, x_range_max)
            spawned = random.randint(1,9)
            words = font.render(str(spawned), True, textc)
        height += speed
        if wordsbox.colliderect(boxhit):
            height = random.randint(45,65)
            wordsx = random.randint(x_range_min, x_range_max)
            caught = spawned
            if caught != eqans:
                score -= 1
            spawned = random.randint(1,9)
            words = font.render(str(spawned), True, textc)

        if height2 >= 590:
            height2 = random.randint(45,65)
            wordsx2 = random.randint(x_range_min, x_range_max)
            spawned2 = random.randint(1,9)
            words2 = font.render(str(spawned2), True, textc)
        height2 += speed
        if wordsbox2.colliderect(boxhit):
            height2 = random.randint(45,65)
            wordsx2 = random.randint(x_range_min, x_range_max)
            caught = spawned2
            if caught != eqans:
                score -= 1
            spawned2 = random.randint(1,9)
            words2 = font.render(str(spawned2), True, textc)

        if height3 >= 590:
            height3 = random.randint(45,65)
            wordsx3 = random.randint(x_range_min, x_range_max)
            spawned3 = random.randint(1,9)
            words3 = font.render(str(spawned3), True, textc)
        height3 += speed
        if wordsbox3.colliderect(boxhit):
            height3 = random.randint(45,65)
            wordsx3 = random.randint(x_range_min, x_range_max)
            caught = spawned3
            if caught != eqans:
                score -= 1
            spawned3 = random.randint(1,9)
            words3 = font.render(str(spawned3), True, textc)
    
    if play_game == 1:
        for row_i, row in enumerate(rows):
            for n in row:
                n["y"] += speed
                rect = pygame.Rect(n["x"], n["y"], n["numtext"].get_width(), n["numtext"].get_height())
                if n["y"] >= 590:
                    n["y"] = 50
                    n["value"] = random.randint(1,9)
                    render(n)
    

generateeq()

def createnum(Xnum, real=True, value=None):
    return {
        "value": value if value is not None else random.randint(1,9),
        "numtext": None,
        "x": Xnum,
        "y": 50,
        "real": real
    }

def render(n):
    n["numtext"] = font.render(str(n["value"]), True, textc)

rows = [[] for _ in range(4)]
row_x = [340, 250, 160, 70]

hinga_dinga_per_durgen = 3



def Minigame():
    global womp, boxhit, speed, score
    boxx, womp = pygame.mouse.get_pos()
    wordsbox.topleft = (wordsx, height)
    wordsbox2.topleft = (wordsx2, height2)
    wordsbox3.topleft = (wordsx3, height3)
    box = pygame.Rect(boxx - 50, 500, 100, 50)
    boxhit = pygame.Rect(boxx - 50, 500 - boxhit_offset, 100, 50)

    checknum()

    if caught == eqmiss:
        generateeq()
        score += 2
    equation_text = font.render(f'{eqknow} {operate} _ = {eqans}', True, textc)
    score_text = font.render(str(score), True, textc)
    speed = 4 + (0.1 * score)
    display.fill(gray)
    display.blit(words, wordsbox)
    display.blit(words2, wordsbox2)
    display.blit(words3, wordsbox3)
    display.blit(score_text, score_box)
    display.blit(equation_text, equation_box)
    pygame.draw.rect(display, boxc, box)
    pygame.display.flip()

def Game():
    global music_start, hinga_dinga_per_durgen, scircle
    if not music_start:
        start_moosic()
        music_start = True
    
    elapsed = get_song_elapsed()
    update_spawns(elapsed)
    update_notes()
    update_lines()

    score_text = font.render(str(score), True, textc)
    equation_text = font.render(f'{eqknow} {operate} _ = {eqans}', True, textc)
    display.fill(gray)
    for row in rows:
        for n in row:
            display.blit(n["numtext"], (n["x"], n["y"]))
    for line in red_lines:
        pygame.draw.line(display, (255, 0, 0), (0, line["y"]), (400, line["y"]), 4)


    display.blit(score_text, score_box)
    display.blit(equation_text, equation_box)
    pygame.draw.circle(display, scircle, button.center, 25)
    pygame.draw.circle(display, scircle, button2.center, 25)
    pygame.draw.circle(display, scircle, button3.center, 25)
    pygame.draw.circle(display, scircle, button4.center, 25)
    scircle = (0,0,0)
    pygame.display.flip()


run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            run = False
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if ministart.collidepoint(event.pos) and play_game == 0:
                play_minigame = 1
            if gamestart.collidepoint(event.pos) and play_minigame == 0:
                play_game = 1
                reset_song()
        if event.type == pygame.KEYDOWN and play_game == 1:
            hangle_key(event.key)

    if play_minigame == 0 and play_game == 0:
            display.fill(gray)
            pygame.draw.rect(display, (37, 117, 232), ministart)
            pygame.draw.rect(display, (0,0,0), (75, 500, 250, 60), 5)
            pygame.draw.rect(display, (37, 117, 232), gamestart)
            pygame.draw.rect(display, (0,0,0), (75, 100, 250, 60), 5)
            display.blit(start_text, startrect)
            display.blit(play_text, playrect)
            pygame.display.flip()

    if play_game == 1:
        Game()
        frame.tick(60)
    
    if play_minigame == 1:
        Minigame()
        frame.tick(60)
