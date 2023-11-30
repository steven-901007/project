import pygame as pg
import os
import random

#變數區

#大寫英文 = 遊戲中不會變的變數
FPS = 90
WattackE = (0,0,0) #背景顏色 
c_Airplane = (0,255,0) #Airplane顏色
c_Rock = (255,0,0)#Rock顏色
c_Bullet = (255,255,0)
WIDTH = 500 #畫面寬度
HEIGHT = 600 #畫面高度
# 背景座標(0,0)定位一律在左上
fullingspeed = random.randint(2,5)

#變數區


pg.init() #遊戲初始化
pg.mixer.init()
screen = pg.display.set_mode((WIDTH,HEIGHT)) #創建視窗(寬度,高度)
clock = pg.time.Clock() #控制時間
pg.display.set_caption('第一個遊戲') #視窗title
running = True

#載入圖片
bakeground_img = pg.image.load(os.path.join('遊戲製作/圖片','bakeground.jfif')).convert() #os.path = pathon目前檔案位置 convert = pygame比較容易讀取格式
airplane_img = pg.image.load(os.path.join('遊戲製作/圖片','基德.png')).convert()
# rock_img = pg.image.load(os.path.join('遊戲製作/圖片','小黑.png')).convert()
bullet_img = pg.image.load(os.path.join('遊戲製作/圖片','poker.jfif')).convert() 
rock_imgs = {}
rock_imgs['black0'] = pg.image.load(os.path.join('遊戲製作/圖片','小黑-0.png')).convert()
rock_imgs['black1'] = pg.image.load(os.path.join('遊戲製作/圖片','小黑-1.png')).convert()
rock_imgs['conan'] = pg.image.load(os.path.join('遊戲製作/圖片','小黑-2.png')).convert()

font_name = pg.font.match_font('Microsoft JhengHei') #從電腦引入字體

def drow_text(surf,text,size,x,y):
    font = pg.font.Font(font_name,size) #Font(字體,文字大小)
    text_surface = font.render(text,True,(255,255,255)) #渲染文字(渲染文字,要不要用anti-aliasing(反鋸齒),文字顏色)
    text_rect = text_surface.get_rect()#定位
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface,text_rect) #畫文字(畫的文字,畫的位置)

power_imgs = {}
power_imgs['shield'] = pg.image.load(os.path.join('遊戲製作/圖片','defand.png')).convert()
power_imgs['flash'] = pg.image.load(os.path.join('遊戲製作/圖片','flash.png')).convert()

#載入音樂
pg.mixer.music.load(os.path.join('遊戲製作/音效','bakeground.mp3')) #持續撥放音樂的引入方式
pg.mixer.music.set_volume(0.05)#控制背景音量

shoot_sound = pg.mixer.Sound(os.path.join('遊戲製作/音效','shoot.wav')) #音效的引入方式
hit_sound = pg.mixer.Sound(os.path.join('遊戲製作/音效','hit-0.wav'))

def new_rock():
    rock = Rock()
    all_sprites.add(rock)
    rocks.add(rock)  

def drow_health(surf,hp,x,y): #surf=所畫平面
    if hp < 0:
        hp =0
    bar_length = 100 #生命條長度
    bar_height = 10 #生命條高度
    fill = (hp/100)*bar_length
    outline_rect = pg.Rect(x,y,bar_length,bar_height) #pygame內建矩形(位置座標x,位置座標y,矩形長度,矩形高度)
    fill_rect = pg.Rect(x,y,fill,bar_height)
    pg.draw.rect(surf,(0,255,0),fill_rect) #rect(所畫平面,塗滿顏色,畫啥) 沒寫第4個變數 = 外框
    pg.draw.rect(surf,(0,0,0),outline_rect,2) #rect(所畫平面,塗滿顏色,畫啥,多少像素(填滿)) 

def drow_init():
    drow_text(screen,'爆打小黑',64,WIDTH/2,HEIGHT/4)
    drow_text(screen,'←↑→↓ or awds 移動飛船 、 空白艦發射子彈',22,WIDTH/2,WIDTH/2)
    drow_text(screen,'按任意鍵開始遊戲',18,WIDTH/2,HEIGHT*3/4)
    pg.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return True
            elif event.type == pg.KEYUP: #按完按鍵
                waiting = False
                return False

class Airplane(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self) #sprite初始函式
        # self.image = pg.Surface((50,40)) #imge = 顯示圖片 目前沒圖片 pg.Surface((50,40)) == 一個50*40的平面
        # self.image.fill(c_Airplane) #圖片顏色
        self.image = pg.transform.scale(airplane_img,(40,80)) #定義圖片大小
        self.image.set_colorkey((0,0,0)) #將某個顏色變透明
        self.rect = self.image.get_rect() #定位圖片
        # self.radius = 20
        # pg.draw.circle(self.image,(255,0,0),self.rect.center,self.radius) #畫圓形(畫在哪張圖片上?,用啥顏色畫,圓心在哪?,半徑是多少?)
        #定位物件的左上角座標add
        # self.rect.x = 400 #X座標
        # self.rect.y = 400 #Y座標
        #定位物件的中心座標
        # self.rect.center = (WIDTH/2,HEIGHT/2) #整個screen的中心
        self.rect.centerx =  WIDTH/2
        self.rect.bottom = HEIGHT-10
        self.speed = 8
        self.health = 100
        self.gun = 1
        self.gun_time = 0

    def update(self):
        key_pressed = pg.key.get_pressed()#回傳布林值
        # if key_pressed[pg.K_RIGHT]: #鍵盤'左'鍵
        #     self.rect.x += self.speed
        # if key_pressed[pg.K_LEFT]:
        #     self.rect.x -= self.speed
        # if key_pressed[pg.K_UP]: #鍵盤'上'鍵
        #     self.rect.y -= self.speed 
        # if key_pressed[pg.K_DOWN]:
        #     self.rect.y += self.speed

        if key_pressed[pg.K_UP]:
            self.rect.y -= self.speed
        if key_pressed[pg.K_DOWN]:
            self.rect.y += self.speed
        if key_pressed[pg.K_RIGHT]:
            self.rect.x += self.speed
        if key_pressed[pg.K_LEFT]:
            self.rect.x -= self.speed

        if self.rect.bottom >= HEIGHT: 
            self.rect.bottom = HEIGHT
        elif self.rect.top <= 0:
            self.rect.top =  0

        if self.rect.left <= 0: #不能用 =  (50+-8n永遠不會等於500)
            self.rect.left = 0
        elif self.rect.right >= WIDTH:
            self.rect.right = WIDTH  
        if self.gun >1 and pg.time.get_ticks() - self.gun_time > 3000:
            self.gun -= 1
            self.gun_time = pg.time.get_ticks()
  
    def shoot(self):
        if self.gun ==1:
            bullet = Bullet(self.rect.centerx,self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            shoot_sound.play()
        elif self.gun >= 2:
            bullet1 = Bullet(self.rect.left,self.rect.top)
            bullet2 = Bullet(self.rect.right,self.rect.top)
            all_sprites.add(bullet1)
            all_sprites.add(bullet2)
            bullets.add(bullet1)
            bullets.add(bullet2)
            shoot_sound.play()

    def gunup(self):
        self.gun +=1
        self.gun_time = pg.time.get_ticks()

class Rock(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self) #sprite初始函式
        self.type = random.choice(['black0','black1','conan'])
        self.image = pg.transform.scale(rock_imgs[self.type],(40,80)) #random.choice(rock_imgs) = 從列表中隨機選擇
        self.image.set_colorkey((237,28,36))
        self.rect = self.image.get_rect() #定位圖片
        self.rect.x = random.randrange(0,WIDTH-self.rect.width)
        self.rect.y = random.randrange(-100,-40)
        self.speedy = fullingspeed 
        self.speedx = random.randrange(-1,1)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top >= HEIGHT or self.rect.left >= WIDTH or self.rect.right <= 0 :
            self.rect.x = random.randrange(0,WIDTH-self.rect.width)
            self.rect.y = random.randrange(-200,-50)
            self.speedy = fullingspeed
            self.speedx = random.randrange(-3,3)

class Bullet(pg.sprite.Sprite):
    def __init__(self,x,y):
        pg.sprite.Sprite.__init__(self) #sprite初始函式
        # self.image_ori = pg.transform.scale(bullet_img,(40,80))
        # self.image = self.image_ori.copy()
        self.image = pg.transform.scale(bullet_img,(20,40))
        self.rect = self.image.get_rect() #定位圖片
        self.rect.centerx = x
        self.rect.top = y
        self.speedy = -10
        # self.total_degree = 0
        # self.rot_degree = random.randrange(-3,3)

    # def rotate(self):
    #     self.total_degree += self.rot_degree
    #     self.total_degree = self.total_degree%360 #對360取餘數
    #     self.image = pg.transform.rotate(self.image_ori,self.total_degree)#py內建程式旋轉圖片
    #     center = self.rect.center
    #     self.rect = self.image.get_rect() #重新定位?
    #     self.rect.center = center

    def update(self):
        # self.rotate()
        self.rect.y +=self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Power(pg.sprite.Sprite):
    def __init__(self,center):
        pg.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield','flash'])
        self.image =  pg.transform.scale(power_imgs[self.type],(40,80))
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top < 0:
            self.kill()



all_sprites = pg.sprite.Group() #創立群組
rocks = pg.sprite.Group()
bullets = pg.sprite.Group()
powers = pg.sprite.Group()   

airplane = Airplane() 

all_sprites.add(airplane) #加入群組


for i in range(7):
    new_rock()
pg.mixer.music.play(-1)#持續撥放的音樂  play(-1) = 一直重複撥放 
score  = 0



#遊戲迴圈
show_init = True
while running:
    if show_init:
        close = drow_init()
        if close:
            break
        show_init = False
        all_sprites = pg.sprite.Group() #創立群組
        rocks = pg.sprite.Group()
        bullets = pg.sprite.Group()
        powers = pg.sprite.Group()   

        airplane = Airplane() 

        all_sprites.add(airplane) #加入群組


        for i in range(7):
            new_rock()
        pg.mixer.music.play(-1)#持續撥放的音樂  play(-1) = 一直重複撥放 
        score  = 0
    clock.tick(FPS) #在1秒內最多執行FPS次(禎數) 
    #get input
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
            
        elif event.type == pg.KEYDOWN: #按下按鍵
            if event.key == pg.K_SPACE:
                airplane.shoot()
    #更新遊戲
    all_sprites.update() #執行群組內每個物件的update涵式
    attacks = pg.sprite.groupcollide(rocks,bullets,True,True) #groupcollide(A,B,A delet?,B delet?)==>判斷AB碰撞到要不要刪除  groupcollide回傳字典

    for attack in attacks:
        if random.random()>0.9:
            pow = Power(attack.rect.center)
            all_sprites.add(pow)
            powers.add(pow)
        if attack.type == 'black0':
            score += random.randrange(11,20)
        elif attack.type == 'black1':
            score += random.randrange(1,10)
        else :
            score += random.randrange(21,30)
        new_rock()

    hits = pg.sprite.spritecollide(airplane,powers,True)
    for hit in hits:
        if hit.type  == 'shield':
            airplane.health +=10
            if airplane.health>100:
                airplane.health = 100
        elif hit.type == 'flash':
            airplane.gunup()

    hits = pg.sprite.spritecollide(airplane,rocks,True) #spritecollide(A,B,B delet?,pg.sprite.collide_circle)==>判斷AB碰撞要不要刪除B spritecollide回傳列表 pg.sprite.collide_circle = 將碰撞判斷改為圓形
    
    for hit in hits:
        airplane.health -= random.randint(10,20)
        new_rock()       
        if airplane.health <= 0:
            show_init = True
    #畫面顯示
    # screen.fill(WattackE) #RGB調色盤
    screen.blit(bakeground_img,(0,0))
    all_sprites.draw(screen) #畫到screen上
    drow_text(screen,str(score),18,WIDTH/2,10)
    drow_health(screen,airplane.health,9,10)
    pg.display.update() #畫面更新


pg.quit()
