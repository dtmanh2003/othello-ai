# -*- coding: utf-8 -*-
import pygame
import sys
import time
import math
import random

# ── Constants ─────────────────────────────────────────────────────────────────
SIZE   = 8
CELL   = 76
MARGIN = 44
INFO_H = 130
WIN_W  = SIZE * CELL + MARGIN * 2
WIN_H  = SIZE * CELL + MARGIN * 2 + INFO_H

EMPTY = 0; BLACK = 1; WHITE = 2

# Palette
C_BG       = (12,  14,  20)
C_BOARD    = (34, 130,  65)
C_BOARD2   = (30, 118,  58)
C_GRID     = (22,  95,  44)
C_DOT      = (18,  80,  36)
C_BLACK_P  = (18,  18,  18)
C_WHITE_P  = (242, 242, 242)
C_HINT     = (120, 230, 140, 160)
C_LAST     = (255, 230,  60, 100)
C_TEXT     = (220, 220, 220)
C_GOLD     = (255, 200,  50)
C_GREEN    = (70,  200,  90)
C_RED      = (220,  60,  60)
C_PANEL    = (18,  20,  30)
C_PANEL2   = (28,  30,  46)
C_BORDER   = (50,  55,  80)

DX = [-1,-1,-1, 0, 0, 1, 1, 1]
DY = [-1, 0, 1,-1, 1,-1, 0, 1]

CORNER_WEIGHT = [
    [120,-20, 20,  5,  5, 20,-20,120],
    [-20,-40, -5, -5, -5, -5,-40,-20],
    [ 20, -5, 15,  3,  3, 15, -5, 20],
    [  5, -5,  3,  3,  3,  3, -5,  5],
    [  5, -5,  3,  3,  3,  3, -5,  5],
    [ 20, -5, 15,  3,  3, 15, -5, 20],
    [-20,-40, -5, -5, -5, -5,-40,-20],
    [120,-20, 20,  5,  5, 20,-20,120],
]

# ── Game logic ─────────────────────────────────────────────────────────────────
def make_board():
    b = [[EMPTY]*SIZE for _ in range(SIZE)]
    b[3][3]=WHITE; b[3][4]=BLACK
    b[4][3]=BLACK; b[4][4]=WHITE
    return b

def copy_board(b):
    return [row[:] for row in b]

def is_valid(board, r, c, player):
    if board[r][c] != EMPTY: return False
    opp = WHITE if player==BLACK else BLACK
    for d in range(8):
        nr,nc = r+DX[d], c+DY[d]; found=False
        while 0<=nr<SIZE and 0<=nc<SIZE and board[nr][nc]==opp:
            nr+=DX[d]; nc+=DY[d]; found=True
        if found and 0<=nr<SIZE and 0<=nc<SIZE and board[nr][nc]==player:
            return True
    return False

def get_flipped(board, r, c, player):
    opp = WHITE if player==BLACK else BLACK
    flipped = []
    for d in range(8):
        nr,nc = r+DX[d], c+DY[d]; line=[]
        while 0<=nr<SIZE and 0<=nc<SIZE and board[nr][nc]==opp:
            line.append((nr,nc)); nr+=DX[d]; nc+=DY[d]
        if line and 0<=nr<SIZE and 0<=nc<SIZE and board[nr][nc]==player:
            flipped.extend(line)
    return flipped

def get_valid_moves(board, player):
    return [(r,c) for r in range(SIZE) for c in range(SIZE) if is_valid(board,r,c,player)]

def apply_move(board, r, c, player):
    flipped = get_flipped(board, r, c, player)
    board[r][c] = player
    for fr,fc in flipped:
        board[fr][fc] = player
    return flipped

def count_pieces(board, player):
    return sum(board[r][c]==player for r in range(SIZE) for c in range(SIZE))

# ── AI: Minimax + Alpha-Beta ───────────────────────────────────────────────────
def evaluate(board, player):
    opp = WHITE if player==BLACK else BLACK
    score = 0
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c]==player:   score += CORNER_WEIGHT[r][c]
            elif board[r][c]==opp:    score -= CORNER_WEIGHT[r][c]
    score += 5*(len(get_valid_moves(board,player)) - len(get_valid_moves(board,opp)))
    return score

def minimax(board, depth, alpha, beta, maximizing, player, opp):
    moves = get_valid_moves(board, player if maximizing else opp)
    if depth==0 or (not moves and not get_valid_moves(board, opp if maximizing else player)):
        return evaluate(board, player), None

    if not moves:
        v, _ = minimax(board, depth-1, alpha, beta, not maximizing, player, opp)
        return v, None

    best_move = None
    if maximizing:
        best = -99999
        for r,c in moves:
            b2 = copy_board(board)
            apply_move(b2, r, c, player)
            v, _ = minimax(b2, depth-1, alpha, beta, False, player, opp)
            if v > best: best=v; best_move=(r,c)
            alpha = max(alpha, best)
            if beta <= alpha: break
        return best, best_move
    else:
        best = 99999
        for r,c in moves:
            b2 = copy_board(board)
            apply_move(b2, r, c, opp)
            v, _ = minimax(b2, depth-1, alpha, beta, True, player, opp)
            if v < best: best=v; best_move=(r,c)
            beta = min(beta, best)
            if beta <= alpha: break
        return best, best_move

def ai_best_move(board, player, depth=4):
    opp = WHITE if player==BLACK else BLACK
    _, move = minimax(board, depth, -99999, 99999, True, player, opp)
    return move

# ── Sound (generated beeps) ───────────────────────────────────────────────────
def make_sound(freq=440, duration=0.05, volume=0.3, wave="sine"):
    import numpy as np
    sr = 22050
    n  = int(sr * duration)
    t  = [i/sr for i in range(n)]
    if wave=="sine":
        samples = [int(32767 * volume * math.sin(2*math.pi*freq*x)) for x in t]
    else:
        samples = [int(32767 * volume * (1 if math.sin(2*math.pi*freq*x)>0 else -1)) for x in t]
    # Fade out
    for i in range(min(n, int(sr*0.01))):
        samples[n-1-i] = int(samples[n-1-i] * i / (sr*0.01))
    buf = bytearray()
    for s in samples:
        s = max(-32768, min(32767, s))
        buf += s.to_bytes(2, 'little', signed=True)
        buf += s.to_bytes(2, 'little', signed=True)
    sound = pygame.sndarray.make_sound(
        __import__('numpy').frombuffer(bytes(buf), dtype='<i2').reshape(-1, 2))
    return sound

def init_sounds():
    try:
        import numpy
        pygame.mixer.init(22050, -16, 2, 512)
        return {
            "place": make_sound(600, 0.06, 0.25),
            "flip":  make_sound(400, 0.04, 0.15),
            "win":   make_sound(880, 0.18, 0.3),
            "skip":  make_sound(220, 0.1,  0.2),
            "click": make_sound(800, 0.03, 0.15),
        }
    except Exception:
        return {}

def play(sounds, key):
    s = sounds.get(key)
    if s:
        try: s.play()
        except: pass

# ── Drawing ────────────────────────────────────────────────────────────────────
def board_to_px(r, c):
    return MARGIN + c*CELL + CELL//2, MARGIN + r*CELL + CELL//2

def draw_rounded_rect(surf, color, rect, r=8, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=r)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=r)

def draw_piece_at(surf, cx, cy, player, radius=30, squish=1.0):
    # Shadow
    s = pygame.Surface((radius*2+10, radius*2+10), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0,0,0,90),
        (4, 10, int(radius*2*squish)+2, max(1,int((radius*2-6)*abs(squish)))))
    surf.blit(s, (cx-radius-5+2, cy-radius-5+5))

    if squish == 0: return
    color = C_BLACK_P if player==BLACK else C_WHITE_P
    sx = max(1, int(radius*2*abs(squish)))
    sy = radius*2
    piece = pygame.Surface((sx, sy), pygame.SRCALPHA)
    pygame.draw.ellipse(piece, color, (0, 0, sx, sy))
    # Gloss
    gcolor = (60,60,60) if player==BLACK else (255,255,255)
    gr = max(2, radius//4)
    gx = sx//2 - sx//4
    gy = sy//4
    pygame.draw.ellipse(piece, gcolor, (gx-gr, gy-gr//2, gr*2, gr))
    surf.blit(piece, (cx - sx//2, cy - radius))

def draw_board(surf, board, hints, last_move, flip_cells, flip_t):
    # Board background
    pygame.draw.rect(surf, (22, 100, 48),
        (MARGIN-4, MARGIN-4, SIZE*CELL+8, SIZE*CELL+8), border_radius=6)

    for r in range(SIZE):
        for c in range(SIZE):
            col = C_BOARD if (r+c)%2==0 else C_BOARD2
            pygame.draw.rect(surf, col,
                (MARGIN+c*CELL, MARGIN+r*CELL, CELL, CELL))

    # Grid
    for i in range(SIZE+1):
        pygame.draw.line(surf, C_GRID,
            (MARGIN+i*CELL, MARGIN), (MARGIN+i*CELL, MARGIN+SIZE*CELL), 1)
        pygame.draw.line(surf, C_GRID,
            (MARGIN, MARGIN+i*CELL), (MARGIN+SIZE*CELL, MARGIN+i*CELL), 1)

    # Star dots
    for pr,pc in [(2,2),(2,6),(6,2),(6,6)]:
        cx,cy = board_to_px(pr,pc)
        pygame.draw.circle(surf, C_DOT, (cx,cy), 4)

    # Last move glow
    if last_move:
        lr,lc = last_move
        s = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
        s.fill(C_LAST)
        surf.blit(s, (MARGIN+lc*CELL, MARGIN+lr*CELL))

    # Hints
    hs = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
    pygame.draw.circle(hs, C_HINT, (CELL//2,CELL//2), 12)
    for r,c in hints:
        surf.blit(hs, (MARGIN+c*CELL, MARGIN+r*CELL))

    # Pieces
    radius = CELL//2 - 6
    for r in range(SIZE):
        for c in range(SIZE):
            p = board[r][c]
            if p == EMPTY: continue
            cx,cy = board_to_px(r,c)
            if (r,c) in flip_cells:
                t = flip_t.get((r,c), 1.0)
                # t: 0→1, first half shrink old color, second half grow new color
                if t < 0.5:
                    squish = 1.0 - t*2
                    old_p = WHITE if p==BLACK else BLACK
                    draw_piece_at(surf, cx, cy, old_p, radius, squish)
                else:
                    squish = (t - 0.5)*2
                    draw_piece_at(surf, cx, cy, p, radius, squish)
            else:
                draw_piece_at(surf, cx, cy, p, radius)

    # Labels
    font_lbl = pygame.font.SysFont("consolas", 15, bold=True)
    cols = "abcdefgh"
    for i in range(SIZE):
        lbl = font_lbl.render(cols[i], True, (130,190,130))
        surf.blit(lbl, (MARGIN+i*CELL+CELL//2-lbl.get_width()//2, MARGIN-22))
        lbl = font_lbl.render(str(i+1), True, (130,190,130))
        surf.blit(lbl, (MARGIN-20, MARGIN+i*CELL+CELL//2-lbl.get_height()//2))

def draw_info(surf, board, current, pnames, mode, message, font, font_sm, anim_t):
    py = MARGIN*2 + SIZE*CELL
    pygame.draw.rect(surf, C_PANEL, (0, py, WIN_W, INFO_H))
    pygame.draw.line(surf, C_BORDER, (0,py), (WIN_W,py), 2)

    bc = count_pieces(board, BLACK)
    wc = count_pieces(board, WHITE)
    cx = WIN_W//2

    # Score bar
    bw = 240; bh = 20; bx = cx-bw//2; by = py+16
    total = bc+wc or 1
    bs = int(bw*bc/total)
    pygame.draw.rect(surf, C_BLACK_P, (bx, by, bs, bh), border_radius=4)
    pygame.draw.rect(surf, C_WHITE_P, (bx+bs, by, bw-bs, bh), border_radius=4)
    pygame.draw.rect(surf, C_BORDER, (bx, by, bw, bh), 2, border_radius=4)

    # Piece counts
    b_active = current==BLACK
    w_active = current==WHITE
    pulse = 0.5 + 0.5*math.sin(anim_t*4)

    bl = font.render(f"X {pnames[BLACK]}  {bc}", True, C_GOLD if b_active else C_TEXT)
    wl = font.render(f"{wc}  {pnames[WHITE]} O", True, C_GOLD if w_active else C_TEXT)
    surf.blit(bl, (bx - bl.get_width() - 10, by - 2))
    surf.blit(wl, (bx + bw + 10, by - 2))

    # Turn indicator with pulse
    turn_col = tuple(int(c*(0.7+0.3*pulse)) for c in C_GREEN)
    tl = font_sm.render(f"{'[X] Black' if current==BLACK else '[O] White'} TURN", True, turn_col)
    surf.blit(tl, (cx-tl.get_width()//2, by+bh+8))

    # Message
    if message:
        ml = font_sm.render(message, True, C_GOLD)
        surf.blit(ml, (cx-ml.get_width()//2, by+bh+32))

    # Mode + ESC tip
    ml2 = font_sm.render(("vs CPU" if mode==2 else "2P") + "  |  ESC: Menu", True, (70,70,100))
    surf.blit(ml2, (WIN_W-ml2.get_width()-8, py+6))

# ── Button helper ──────────────────────────────────────────────────────────────
def draw_btn(surf, rect, text, font, hover=False, active=False):
    bg = (55,60,95) if active else ((42,45,72) if hover else C_PANEL2)
    bc = C_GOLD if active else (C_GREEN if hover else C_BORDER)
    draw_rounded_rect(surf, bg, rect, 10, 2, bc)
    lbl = font.render(text, True, C_GOLD if active else (C_TEXT if hover else (180,180,200)))
    surf.blit(lbl, (rect.centerx-lbl.get_width()//2, rect.centery-lbl.get_height()//2))

# ── Menu ───────────────────────────────────────────────────────────────────────
def menu_screen(surf, clock, fonts):
    font_big, font, font_sm = fonts
    mode = 0; names = ["",""]; active_input = -1
    player_color = BLACK  # BLACK=先手, WHITE=後手

    btn_2p  = pygame.Rect(WIN_W//2-150, 240, 136, 48)
    btn_cpu = pygame.Rect(WIN_W//2+14,  240, 136, 48)
    btn_blk = pygame.Rect(WIN_W//2-150, 310, 136, 40)
    btn_wht = pygame.Rect(WIN_W//2+14,  310, 136, 40)
    inp = [pygame.Rect(WIN_W//2-140, 400, 280, 42),
           pygame.Rect(WIN_W//2-140, 454, 280, 42)]
    placeholders = ["Your Name", "Player 2"]
    start = pygame.Rect(WIN_W//2-110, 530, 220, 50)

    t0 = time.time()
    while True:
        dt = time.time()-t0
        mx,my = pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type==pygame.MOUSEBUTTONDOWN:
                if btn_2p.collidepoint(mx,my):  mode=1
                if btn_cpu.collidepoint(mx,my): mode=2
                if mode==2:
                    if btn_blk.collidepoint(mx,my): player_color=BLACK
                    if btn_wht.collidepoint(mx,my): player_color=WHITE
                for i,b in enumerate(inp):
                    if b.collidepoint(mx,my): active_input=i
                    elif active_input==i: active_input=-1
                if start.collidepoint(mx,my) and mode>0:
                    n1 = names[0].strip() or "Player"
                    n2 = names[1].strip() or ("Player 2" if mode==1 else "CPU")
                    return mode, n1, n2, 6, player_color
            if ev.type==pygame.KEYDOWN and active_input>=0:
                if ev.key==pygame.K_BACKSPACE: names[active_input]=names[active_input][:-1]
                elif ev.key==pygame.K_TAB: active_input=1-active_input
                elif ev.key==pygame.K_RETURN: active_input=-1
                elif len(names[active_input])<14: names[active_input]+=ev.unicode

        surf.fill(C_BG)

        # Title
        glow = 0.5+0.5*math.sin(dt*1.5)
        tc = (int(200+55*glow), int(160+40*glow), 40)
        t1 = font_big.render("OTHELLO", True, tc)
        surf.blit(t1, (WIN_W//2-t1.get_width()//2, 75))
        t2 = font_sm.render("Othello  -  Pygame Edition", True, (120,130,170))
        surf.blit(t2, (WIN_W//2-t2.get_width()//2, 138))

        # Decorative board preview (mini)
        for ri in range(4):
            for ci in range(4):
                col_ = C_BOARD if (ri+ci)%2==0 else C_BOARD2
                pygame.draw.rect(surf, col_, (WIN_W//2-38+ci*20, 165+ri*20, 20, 20))

        # Mode
        hl = font_sm.render("Game Mode", True, (140,150,190))
        surf.blit(hl, (WIN_W//2-hl.get_width()//2, 215))
        draw_btn(surf, btn_2p,  "[ 2 Player ]", font, btn_2p.collidepoint(mx,my),  mode==1)
        draw_btn(surf, btn_cpu, "[ vs CPU   ]", font, btn_cpu.collidepoint(mx,my), mode==2)

        # Color choice (only vs CPU)
        if mode==2:
            hl_c = font_sm.render("Your Color", True, (140,150,190))
            surf.blit(hl_c, (WIN_W//2-hl_c.get_width()//2, 290))
            draw_btn(surf, btn_blk, "X  Black (1st)", font_sm,
                     btn_blk.collidepoint(mx,my), player_color==BLACK)
            draw_btn(surf, btn_wht, "O  White (2nd)", font_sm,
                     btn_wht.collidepoint(mx,my), player_color==WHITE)
            # Draw piece preview inside buttons
            pygame.draw.circle(surf, C_BLACK_P, (btn_blk.x+14, btn_blk.centery), 7)
            pygame.draw.circle(surf, C_WHITE_P, (btn_wht.x+14, btn_wht.centery), 7)

        # Name inputs
        hl2 = font_sm.render("Player Names", True, (140,150,190))
        surf.blit(hl2, (WIN_W//2-hl2.get_width()//2, 376))
        for i,box in enumerate(inp):
            if mode==2 and i==1:
                draw_rounded_rect(surf, (22,24,38), box, 8, 2, (40,42,60))
                ai_label = "CPU  (goes 1st)" if player_color==WHITE else "CPU  (goes 2nd)"
                lb = font_sm.render(ai_label, True, (80,80,110))
                surf.blit(lb, (box.x+12, box.centery-lb.get_height()//2))
                continue
            border = C_GREEN if active_input==i else C_BORDER
            draw_rounded_rect(surf, C_PANEL2, box, 8, 2, border)
            ph = placeholders[i] if mode==1 else ("Your Name" if i==0 else "Player 2")
            display = names[i] if names[i] else ph
            color = C_TEXT if names[i] else (90,90,120)
            lb = font_sm.render(display, True, color)
            surf.blit(lb, (box.x+12, box.centery-lb.get_height()//2))
            if active_input==i and int(dt*2)%2==0:
                tx = box.x+12+(lb.get_width() if names[i] else 0)
                pygame.draw.line(surf, C_TEXT, (tx,box.y+8),(tx,box.bottom-8),2)

        # Start
        sc = (45,155,70) if mode>0 else (30,35,55)
        bc2 = C_GREEN if mode>0 else C_BORDER
        draw_rounded_rect(surf, sc, start, 12, 2, bc2)
        sl = font.render(">> START <<", True, C_TEXT if mode>0 else (60,65,90))
        surf.blit(sl, (start.centerx-sl.get_width()//2, start.centery-sl.get_height()//2))

        pygame.display.flip(); clock.tick(60)

# ── Result screen ──────────────────────────────────────────────────────────────
def result_screen(surf, clock, board, pnames, fonts):
    font_big, font, font_sm = fonts
    b = count_pieces(board,BLACK); w = count_pieces(board,WHITE)
    if b>w:   winner=f"*** {pnames[BLACK]} (Black) WIN! ***"; wc=C_GREEN
    elif w>b: winner=f"*** {pnames[WHITE]} (White) WIN! ***"; wc=C_GREEN
    else:     winner="*** DRAW! ***"; wc=C_GOLD

    btn_again = pygame.Rect(WIN_W//2-160, 430, 140, 48)
    btn_menu  = pygame.Rect(WIN_W//2+20,  430, 140, 48)
    btn_quit  = pygame.Rect(WIN_W//2-70,  496, 140, 44)
    t0=time.time()
    while True:
        dt=time.time()-t0
        mx,my=pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type==pygame.MOUSEBUTTONDOWN:
                if btn_again.collidepoint(mx,my): return "again"
                if btn_menu.collidepoint(mx,my):  return "menu"
                if btn_quit.collidepoint(mx,my):  return "quit"

        surf.fill(C_BG)

        # Overlay board (blurred by darkening)
        overlay = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        overlay.fill((0,0,0,160)); surf.blit(overlay,(0,0))

        # Card
        card = pygame.Rect(WIN_W//2-200, 130, 400, 290)
        draw_rounded_rect(surf, C_PANEL, card, 16, 2, C_BORDER)

        # Title
        tl = font_big.render("GAME  OVER", True, C_GOLD)
        surf.blit(tl, (card.centerx-tl.get_width()//2, card.y+18))

        pulse = 0.7+0.3*math.sin(dt*3)
        wcolor = tuple(int(c*pulse) for c in wc)
        wl = font.render(winner, True, wcolor)
        surf.blit(wl, (card.centerx-wl.get_width()//2, card.y+80))

        # Scores
        draw_piece_at(surf, card.x+60, card.y+155, BLACK, 20)
        sl1 = font.render(f"{pnames[BLACK]}  :  {b}", True, C_TEXT)
        surf.blit(sl1, (card.x+90, card.y+145))

        draw_piece_at(surf, card.x+60, card.y+200, WHITE, 20)
        sl2 = font.render(f"{pnames[WHITE]}  :  {w}", True, C_TEXT)
        surf.blit(sl2, (card.x+90, card.y+190))

        # Score bar
        bw=280; bh=16; bx=card.x+60; by=card.y+242; total=b+w or 1
        bs=int(bw*b/total)
        pygame.draw.rect(surf, C_BLACK_P, (bx, by, bs, bh), border_radius=4)
        pygame.draw.rect(surf, C_WHITE_P, (bx+bs, by, bw-bs, bh), border_radius=4)
        pygame.draw.rect(surf, C_BORDER, (bx, by, bw, bh), 2, border_radius=4)

        draw_btn(surf, btn_again, "Again",  font,    btn_again.collidepoint(mx,my))
        draw_btn(surf, btn_menu,  "Menu",   font,    btn_menu.collidepoint(mx,my))
        draw_btn(surf, btn_quit,  "Quit",   font_sm, btn_quit.collidepoint(mx,my))

        pygame.display.flip(); clock.tick(60)

# ── Game loop ──────────────────────────────────────────────────────────────────
FLIP_DURATION = 0.35   # seconds per flip animation
AI_THINK_MS   = 600

def game_loop(surf, clock, mode, pnames, depth, fonts, sounds, player_color=BLACK):
    font_big, font, font_sm = fonts
    board     = make_board()
    current   = BLACK
    last_move = None
    message   = ""
    anim_t    = 0.0

    # Flip animation state
    flip_cells   = {}   # (r,c) -> True
    flip_t       = {}   # (r,c) -> 0..1
    flip_queue   = []   # list of (r,c) to animate
    flip_active  = False
    flip_start   = 0.0

    ai_thinking  = False
    ai_timer     = 0
    skip_flash   = 0.0

    def start_flip(flipped, player):
        nonlocal flip_active, flip_start, flip_queue
        flip_queue = list(flipped)
        flip_cells.clear(); flip_t.clear()
        for pos in flip_queue:
            flip_cells[pos] = True
            flip_t[pos] = 0.0
        flip_active = True
        flip_start = time.time()

    def do_move(r, c, player):
        nonlocal current, last_move, message, ai_thinking, ai_timer
        flipped = get_flipped(board, r, c, player)
        apply_move(board, r, c, player)
        play(sounds, "place")
        last_move = (r,c)
        message = ""
        if flipped: start_flip(flipped, player)
        current = WHITE if player==BLACK else BLACK

    while True:
        dt = clock.tick(60) / 1000.0
        anim_t += dt

        # Flip animation update
        if flip_active:
            elapsed = time.time() - flip_start
            t = min(1.0, elapsed / FLIP_DURATION)
            for pos in list(flip_cells.keys()):
                flip_t[pos] = t
            if t >= 1.0:
                flip_cells.clear(); flip_t.clear()
                flip_active = False
                play(sounds, "flip")

        valid = get_valid_moves(board, current) if not flip_active else []
        b_moves = get_valid_moves(board, BLACK)
        w_moves = get_valid_moves(board, WHITE)

        # Game over
        if not flip_active and not b_moves and not w_moves:
            draw_frame(surf, board, current, pnames, mode, [], last_move,
                       flip_cells, flip_t, message, fonts, anim_t)
            pygame.display.flip()
            play(sounds, "win")
            pygame.time.wait(700)
            return result_screen(surf, clock, board, pnames, fonts)

        # Pass
        if not flip_active and not valid:
            message = f"{pnames[current]}: No moves - SKIP"
            play(sounds, "skip")
            current = WHITE if current==BLACK else BLACK
            valid = []

        # AI
        is_human_turn = (mode==1) or (mode==2 and current==player_color)
        if not flip_active and not is_human_turn and valid:
            ai_timer += dt*1000
            if ai_timer >= AI_THINK_MS:
                move = ai_best_move(board, current, depth)
                if move: do_move(*move, current)
                ai_timer = 0

        # Events
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_ESCAPE: return "menu"
            if ev.type==pygame.MOUSEBUTTONDOWN and is_human_turn and not flip_active:
                mx,my = pygame.mouse.get_pos()
                c_ = (mx-MARGIN)//CELL; r_ = (my-MARGIN)//CELL
                if 0<=r_<SIZE and 0<=c_<SIZE:
                    if is_valid(board,r_,c_,current):
                        do_move(r_, c_, current)
                    else:
                        play(sounds, "click")

        # Draw
        draw_frame(surf, board, current, pnames, mode, valid, last_move,
                   flip_cells, flip_t, message, fonts, anim_t)

        # AI thinking indicator
        if not is_human_turn and valid and not flip_active:
            dots = "." * (int(anim_t*3)%4)
            tl = font_sm.render(f"CPU thinking{dots}", True, C_GOLD)
            surf.blit(tl, (WIN_W//2-tl.get_width()//2, MARGIN//2-8))

        pygame.display.flip()

def draw_frame(surf, board, current, pnames, mode, hints, last_move,
               flip_cells, flip_t, message, fonts, anim_t):
    _, font, font_sm = fonts
    surf.fill(C_BG)
    draw_board(surf, board, hints, last_move, flip_cells, flip_t)
    draw_info(surf, board, current, pnames, mode, message, font, font_sm, anim_t)

# ── Entry point ────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    surf  = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Othello - Pygame Edition")
    clock = pygame.time.Clock()

    # Try emoji-capable font, fallback to system font
    def try_font(names, size, bold=False):
        for name in names:
            try:
                f = pygame.font.SysFont(name, size, bold=bold)
                if f: return f
            except: pass
        return pygame.font.SysFont(None, size, bold=bold)

    font_big = try_font(["consolas","couriernew","arial"], 50, bold=True)
    font     = try_font(["consolas","couriernew","arial"], 22, bold=True)
    font_sm  = try_font(["consolas","couriernew","arial"], 18)
    fonts    = (font_big, font, font_sm)

    sounds = init_sounds()

    pnames = {BLACK:"Player 1", WHITE:"Player 2"}
    depth  = 4
    player_color = BLACK

    while True:
        mode, n1, n2, depth, player_color = menu_screen(surf, clock, fonts)
        # vs CPU: assign names by color
        if mode == 2:
            ai_color = WHITE if player_color == BLACK else BLACK
            pnames = {player_color: n1, ai_color: "CPU"}
        else:
            pnames = {BLACK: n1, WHITE: n2}
        while True:
            result = game_loop(surf, clock, mode, pnames, depth, fonts, sounds, player_color)
            if result == "again": continue
            if result == "menu": break
            if result == "quit":
                pygame.quit(); sys.exit()
            break

if __name__ == "__main__":
    main()
