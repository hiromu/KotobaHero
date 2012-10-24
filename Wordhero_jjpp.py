#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import pygame
import threading
import Queue
from time import time as get_time
from time import sleep
from pygame.locals import *
from random import randint as rr


WIDTH = 800
HEIGHT = 700
BOARD_SIZE = 550
LEAST_LEN = 3
LEAST_BONUS = 2
LONGEST_LEN = 6
PLAY_TIME = 100
SCORE_TIME = 20
RANK_TIME = 10
TOTAL_TIME = PLAY_TIME + SCORE_TIME + RANK_TIME
WHITE = (255, 255, 255)
GREEN = (200, 100, 10)
RED = (100, 200, 10)
YAMABUKI = (200, 200, 100)
DARK_BLUE = (200, 200, 255)
SKY_BLUE = (100, 100, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
VIOLET = (150, 100, 200)
LIGHT_BLUE = (150, 255, 255)
YELLOW = (255, 255, 100)
BACK_GROUND = BLACK
Dictfile = "dictionary/butadict"
characters = list( u"あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもがぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽやゆよわん" )
charo = [x + y  for x in "akstnhmgzdbp" for y in "aiueo"] + ["ya","yu","yo","wa","nn"]
point = [rr(1, 9) for x in characters]
HINSICOLOR = {u"名詞,形容動詞語幹":YAMABUKI,
              u"動詞,接尾":VIOLET,
              u"接続詞,*":LIGHT_BLUE,
              u"形容詞,自立":YELLOW,
              u"名詞,一般":RED,
              u"名詞,接尾":LIGHT_BLUE,
              u"記号,一般":YELLOW,
              u"動詞,非自立":GREEN,
              u"名詞,副詞可能":LIGHT_BLUE,
              u"記号,アルファベット":YELLOW,
              u"形容詞,非自立":YELLOW,
              u"形容詞,接尾":YELLOW,
              u"名詞,ナイ形容詞語幹":RED,
              u"副詞,助詞類接続":BLUE,
              u"副詞,一般":BLUE,
              u"名詞,サ変接続":RED,
              u"動詞,自立":GREEN,
              u"連体詞,*":RED,}
host = 'localhost'
port = 11123

##終了条件
def quitcheck():
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        if event.type == KEYDOWN and event.key  == K_ESCAPE:
            exit()


def get_name():
    inputs = ""
    keys = ['K_a','K_b','K_c','K_d','K_e','K_f','K_g','K_h','K_i','K_j','K_k','K_l','K_m','K_n','K_o','K_p','K_q','K_r','K_s','K_t','K_u','K_v','K_w','K_x','K_y','K_z','K_0','K_1','K_2','K_3','K_4','K_5','K_6','K_7','K_8','K_9']
    pressed = pygame.key.get_pressed()
    while True:
        now_pressed = pygame.key.get_pressed()
        screen.fill(BACK_GROUND)
        screen.blit(sysfont[2].render(u"名前:%s" % inputs, False, WHITE)
                    ,(100,100))
        for key in keys:
            if key == 'K_BACKSPACE':continue
            r = eval(key)
            if not pressed[r] and now_pressed[r]:
                g = key[-1]
                if now_pressed[K_RSHIFT] or now_pressed[K_LSHIFT]:
                    g = g.upper()
                inputs += g
        if not pressed[K_BACKSPACE] and now_pressed[K_BACKSPACE]:
            inputs = inputs[:-1]
        if now_pressed[K_RETURN] and inputs != "":
            break            
        pygame.display.flip()
        quitcheck()
        pressed = now_pressed[:]

    return inputs


##辞書作成
def makedic(filename):
    global WORD__, WORDLIST, WORDLIST_HINSI, WORDLIST_ORIGIN
    f = open(filename, "r")
    res = set()
    for x in f:
        x = x.strip()
        if len(x.decode('utf-8').split(',')[0]) >= LEAST_LEN :
            res.add(x.decode('utf-8'))
    WORD__ = sorted(list(set(res)))
    WORDLIST = map(lambda x:x.split(',')[0], WORD__)
    WORDLIST_HINSI = {}
    WORDLIST_ORIGIN = {}
    for x in WORD__:
        k = x.split(',',2)
        WORDLIST_HINSI[k[0]] = k[-1]
        WORDLIST_ORIGIN[k[0]] = k[1]

##16マスの隣接リスト
def sixteenmap():
    res=[[] for x in xrange(16)]
    for x in xrange(4):
        for y in xrange(4):
            for i in xrange(-1, 2):
                for j in xrange(-1, 2):
                    if i == j == 0:continue
                    if 0 <= x+i < 4 and 0 <= y+j < 4:
                        res[x * 4 + y].append((x + i) * 4 + y + j)
    return res
    



### 探索　1:みつかった 2:まだまだあるよ 3:つかった 4:見当違い
def search(word, wordlist, used = None):
    lists = wordlist
    down = 0
    up = len(lists) - 1
    while up > down + 2:
        mid = (up + down) / 2
        if lists[mid] < word :
            down = mid
        else:
            up = mid
    res = down
    while res < len(lists)-1 and lists[res] < word:
        res += 1
    if word == lists[res]:
        if used == None: 
            return 1
        if not used[res]:
            used[res] = True
            return 1
        else:
            return 3
    if word in lists[res]:
        return 2
    return 0


##文字列をスコアに変換
def wordpoint(word):
    return sum(point[characters.index(x)] for x in word) + (len(word)  ** 5) / 150



##なぞってる文字を出力
def putword(board, word):
    screen.blit(sysfont[6].render(ind_word(board, word), False, WHITE)
                                  ,((WIDTH - BOARD_SIZE) * 4 / 5, HEIGHT - (HEIGHT - BOARD_SIZE) * 4/ 5))




##正解した文字の表示と説明
def outputfoundword(lastword, pos):
    if(lastword == 'NIL'):return
    pos *= ((WIDTH - BOARD_SIZE) / 2) / 0.1
    pos = ((WIDTH - BOARD_SIZE) / 2) - pos
    pos = min(pos, (WIDTH - BOARD_SIZE) / 2)
    color = HINSICOLOR[WORDLIST_HINSI[lastword]]
    screen.blit(sysfont[2].render(u"読み:%s" % lastword, False, color)
                ,((WIDTH - BOARD_SIZE) / 2 - pos, HEIGHT - (HEIGHT - BOARD_SIZE) * 3/ 4 + 80))
    screen.blit(sysfont[4].render(WORDLIST_ORIGIN[lastword], False, color)
                ,((WIDTH - BOARD_SIZE) / 2 - pos, HEIGHT - (HEIGHT - BOARD_SIZE) * 3/ 4 + 30))
    screen.blit(sysfont[2].render(WORDLIST_HINSI[lastword], False, color)
                ,((WIDTH - BOARD_SIZE) / 2 - pos, HEIGHT - (HEIGHT - BOARD_SIZE) * 3/ 4 ))
    




###盤面上のます目の場所の配列から文字列への変換
def ind_word(board,indexes):
    return "".join(board[x] for x in indexes)

###残り時間出力
def timer(time,pos = (WIDTH - 150, 0)):
    time = int( time - get_time() )
    col = (100,100,255)
    if time < 10:
        col = (255,50,50)
    screen.blit(sysfont[2].render(u"残り%d秒"%time, False, col),
                pos)    

###現在のスコア出力
def pointer(points):
    screen.blit(sysfont[2].render(u"%04d点"%points, False, YAMABUKI),
                (150, 0))
    
    
###たてに文字を列挙　ポイントもしてくれる
def outputwords(words, pos, gap, size, color, limit= HEIGHT - (HEIGHT - BOARD_SIZE) * 3 / 4, used = None):
    height = 0
    k = 0
    while k < len(words) and pos[1] + height + (size + 1) * 10< limit:
        if words[k][0] == "Bonus":
            screen.blit(
                sysfont[size].render("%s %dpt" % (words[k][0],words[k][1]),
                                     False, (255, 100 + words[k][1], 100)),
            (pos[0], pos[1]+height))
        else:
            if(used != None and words[k][0] in used):
                colors = YAMABUKI
            elif(used != None):
                colors = color
            else:
                colors =  HINSICOLOR[WORDLIST_HINSI[words[k][0]]]
            screen.blit(
                sysfont[size].render(
                    "%s %dpt"%(words[k][0], wordpoint(words[k][0])),
                    False, colors)
                ,(pos[0],pos[1]+height))

                    
        height += size * 10 + gap
        k += 1

#開始待ち
def waitfor(time):
    gt = get_time()
    board, lists = 0,0   
    gotten = False
    while gt < time:
        gt = int(gt * 2)%4
        screen.fill(BACK_GROUND)
        screen.blit(sysfont[5].render("Pleas wait"+'.'*gt, False, DARK_BLUE),(100,100))
        timer(time)
        pygame.display.update()
        quitcheck()
        gt = get_time()
        if not gotten and   gt> time - SCORE_TIME:
            board, lists = getboard()
            gotten = True
    return board, lists

#次のゲームの開始時間
def next_time():
    time = get_time()
    g = int(time / TOTAL_TIME)
    return (g + 1) * TOTAL_TIME

###あそび
def play(board, countdown, wordlist):
    wordlists = sorted([x[0] for x in wordlist])
    nowword = []
    foundword = []
    mouse_pressed = False
    sx=sixteenmap()
    square = [swit(x / 4, x % 4, board[x], point[characters.index(board[x])], ((WIDTH - BOARD_SIZE) * 4 / 5, (HEIGHT - BOARD_SIZE) / 4)) for x in xrange(16)]
    used = [False] * len(wordlists)
    checking = False
    finish_time = get_time() + countdown 
    nowpoint = 0
    bonus1 = False
    bonus2 = False
    lastword = 'NIL'
    lastlimit = 0
    while get_time() < finish_time:
        gt = get_time()
        screen.fill(BACK_GROUND)
        clock.tick(60)
        timer(finish_time)
        mouse_press=pygame.mouse.get_pressed()[0]
        if mouse_pressed == True and mouse_press == False or checking:
            p=search(ind_word(board, nowword), wordlists, used)
            if p == 1:
                foundword = [["".join(board[x] for x in  nowword)]] + foundword
                nowpoint += wordpoint("".join(board[x] for x in nowword))
                lastword = ind_word(board, nowword)

                lastlimit = gt + 0.1
            for x in xrange(16):
                if square[x].mode == 1:
                    if p == 1:
                        square[x].mode = 102
                        square[x].limit = gt + 0.4
                        square[x].used += 1
                    elif p == 3:
                        square[x].mode = 104
                        square[x].limit = gt + 0.4
                    else:
                        square[x].mode = 103
                        square[x].limit = gt + 0.4
            nowword = []
            checking = False
        
        else:
            mouse_pressed = mouse_press
            if mouse_pressed:
                x, y = pygame.mouse.get_pos()
                x -= (WIDTH - BOARD_SIZE) * 4 / 5
                y -= (HEIGHT - BOARD_SIZE) / 4
                xx, yy = x, y
                x /= Square_size
                y /= Square_size
                xx %= Square_size
                yy %= Square_size
                if 0 <= x < 4 and 0 <= y < 4:
                    if 25 < xx < 125 and 25 < yy < 125:
                        if square[x*4+y].mode == 0:
                            while len(nowword) > 0 and x * 4 + y not in sx[nowword[-1]]:
                                square[nowword[-1]].mode = 0
                                del nowword[-1]                
                            square[x * 4 + y].mode = 1
                            nowword.append(x * 4 + y)
                        elif square[x * 4 + y].mode == 1:
                            if len(nowword) > 1 and nowword[-2] == x * 4 + y:
                                square[nowword[-1]].mode = 0
                                del nowword[-1]
                else:
                    checking = True
        if not bonus1:
            for x in xrange(16):
                if square[x].used == 0:break
            else:
                bonus1 = True
                nowpoint += 25
                foundword = [["Bonus", 25]] + foundword
        if bonus1 and not bonus2:
            for x in xrange(16):
                if square[x].used == 1:break
            else:
                bonus2 = True
                nowpoint += 100
                foundword = [["Bonus", 100]] + foundword
        for x in xrange(16):
            square[x].update(gt)
            square[x].draw(screen)
        pointer(nowpoint)
        putword(board, nowword)
        outputwords(foundword, (0, (HEIGHT - BOARD_SIZE) / 4 + 60), 10, 2, SKY_BLUE)
        outputfoundword(lastword, lastlimit - gt)
        pygame.display.update()
        quitcheck()
    return nowpoint, foundword


###スコア表示
def score(board, nowlist, points, foundword):
    square = [swit(x / 4, x % 4, board[x], point[characters.index(board[x])], (0, 0),50) for x in xrange(16)]
    finish_time = next_time() - RANK_TIME
    selected = 16
    mouse_pressed = False
    foundword = [x for x in foundword if x[0] != 'Bonus']
    foundword.sort(key = lambda x : wordpoint(x[0]),reverse = True)
    while get_time() < finish_time:
        gt = get_time()
        screen.fill(BACK_GROUND)
        clock.tick(60)
        timer(finish_time)
        mouse_press = pygame.mouse.get_pressed()[0]
        if mouse_pressed and not mouse_press:
            x,y = pygame.mouse.get_pos()       
            x /= 50
            y /= 50
            if 0 <= x < 4 and 0 <= y < 4:
                if square[x * 4 + y].mode == -3:
                    selected = 16
                    square[x * 4 + y].mode = 0
                else:
                    selected = x * 4 + y
                    square[x * 4 + y].mode = -3
                    for j in xrange(16):
                        if j != x*4+y:
                            square[j].mode = 0
        mouse_pressed = mouse_press
        for x in xrange(16):
            square[x].update(gt)
            square[x].draw(screen)
        outputwords(nowlist[selected], (240,100), 10, 2, SKY_BLUE, used = map(lambda x:x[0] , foundword), limit = BOARD_SIZE * 6 / 5 )
        outputwords(foundword, (20,280), 10, 1, YAMABUKI, limit = BOARD_SIZE * 6/ 5)
        screen.blit(numfont[3].render("%dpt"%points, False, DARK_BLUE),
                    (20,220))
        quitcheck()
        pygame.display.flip()

###ランキングにデータを投稿してランキングを返してもらう
def get_ranking(foundword,point,q):
    maxpoint = 0
    maxword = u'None'
    for x in foundword:
        if(x[0] == 'Bonus'):continue
        p = wordpoint(x[0])
        if(p > maxpoint):
            maxpoint = p
            maxword = x[0]

    clientsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            clientsock.connect((host,port))
            break
        except:
            pass
    
    comand = u'sendscore|%s'%str([user_name,point,maxword])
    clientsock.sendall(comand)
    clientsock.close()
    sleep(5)
    clientsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            clientsock.connect((host,port))
            break
        except:
            pass
    comand = 'getranking'
    clientsock.sendall(comand)
    recm = clientsock.recv(1<<17)
    clientsock.close()
    q.put(eval(recm))
    
##ランキングの表示
def ranking(rank):
    finish_time = next_time()
    while get_time() < finish_time:
        screen.fill(BACK_GROUND)
        timer(finish_time)
        height = 0
        k = 0
        while k < len(rank) and 100 + height + 40 < HEIGHT - (HEIGHT - BOARD_SIZE) * 3 / 4:
            color = SKY_BLUE
            if rank[k][0] == user_name:
                color = YAMABUKI
            screen.blit(sysfont[1].render(u"%2d位" % (k + 1), False, color), (100, 110+height))
            screen.blit(sysfont[3].render(rank[k][0], False, color),(200, 100 + height))
            screen.blit(numfont[2].render(str(rank[k][1]),False,color),(450,110+height))
            k += 1
            height += 50
        quitcheck()
        pygame.display.flip()
    
        

###ボードの各盤のクラス
class swit(pygame.sprite.Sprite):
    def __init__ (self,x,y,char,point,(left,top),size = BOARD_SIZE / 4):
        pygame.sprite.Sprite.__init__(self)
        self.used = 0
	self.char = charo[characters.index(char)]
        self.color = (0, 0, 0)
        self.limit = 0
        self.norm = pygame.transform.scale(
                      pygame.image.load("images/%s.png"%self.char),
                      (size - 4,size - 4))
        self.blue = pygame.transform.scale(
                      pygame.image.load("images/%sBlue.png"%self.char),
                      (size - 4, size - 4))
        self.green = pygame.transform.scale(
                      pygame.image.load("images/%sGreen.png"%self.char),
                      (size - 4, size - 4))
        self.yellow = pygame.transform.scale(
                      pygame.image.load("images/%sYello.png"%self.char),
                      (size - 4, size - 4))
        self.red = pygame.transform.scale(
                      pygame.image.load("images/%sRed.png"%self.char),
                      (size - 4, size - 4))

        self.rect  = pygame.Rect(left + x * size + 2,top + y * size + 2, size, size)
        self.mode  = 0
        self.point = point
        self.size  = lambda x: x * size / 150
        self.image = self.norm
    
    def update(self, gtime):
        if(self.mode == 0): self.image = self.norm      #Nothing
        if(self.mode == 1): self.image = self.blue      #selected
        if(self.mode % 5 == 2): self.image = self.green     #correctword
        if(self.mode % 5 == 3): self.image = self.red       #wrong
        if(self.mode % 5 == 4): self.image = self.yellow    #wrong

        if(self.mode > 1 and self.limit < gtime):
                self.mode = 0

        self.image.blit(
            numfont[self.size(2)].render(str(self.point), False, WHITE),
            (self.size(10),self.size(120)))

        if(self.used > 0):
            pygame.draw.circle(self.image, GREEN,
                               (self.size(120), self.size(140)),
                               self.size(4))
        if(self.used > 1):
            pygame.draw.circle(self.image, RED,
                               (self.size(130), self.size(140)),
                               self.size(4))

    def draw(self, screen):
        screen.blit(self.image, self.rect)


def getboard(q=None):
    clientsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            clientsock.connect((host,port))
            break
        except:
            pass
    comand = 'getboard'
    clientsock.sendall(comand)
    recm = clientsock.recv(1<<17)
    clientsock.close()
    rcvmsg = recm.strip()
    board,wordlist = rcvmsg.split('|')
    if q == None:
        return eval(board), eval(wordlist)
    else:
        q.puts([eval(board), eval(wordlist)])
    

def main():
    global screen,sysfont,numfont,Square_size,clock,user_name
    makedic(Dictfile)
    pygame.init()
    screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
    pygame.display.set_caption("Kotoba Hero")
    sysfont =[ pygame.font.Font("font/ume-tgc5.ttf", x) for x in xrange(10, 200, 10)]
    numfont = [ pygame.font.Font("font/ipag.ttf", x ) for x in xrange(10, 200, 10)]
    clock = pygame.time.Clock()
    Square_size = BOARD_SIZE / 4
    user_name = get_name()
    board, lists = waitfor(next_time())
    q = Queue.Queue()
    while True:
        playpoint, foundword = play(board, PLAY_TIME, lists[16])
        p = threading.Thread(target = get_ranking,args = (foundword,playpoint,q,))
        p.start()
        score(board, lists, playpoint, foundword)
        rank = q.get()
        ranking(rank)
        board, lists = getboard()



if __name__ == "__main__" :
    main()