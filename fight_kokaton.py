import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5 #  爆弾の個数
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
    imgs = {  # 0度から反時計回りに定義
        (+5, 0): img,  # 右
        (+5, -5): pg.transform.rotozoom(img, 45, 0.9),  # 右上
        (0, -5): pg.transform.rotozoom(img, 90, 0.9),  # 上
        (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
        (-5, 0): img0,  # 左
        (-5, +5): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
        (0, +5): pg.transform.rotozoom(img, -90, 0.9),  # 下
        (+5, +5): pg.transform.rotozoom(img, -45, 0.9),  # 右下
    }

    def __init__(self, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル
        """
        self.img = __class__.imgs[(+5, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy
        self.dire = (+5, 0)

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = __class__.imgs[tuple(sum_mv)]
            list(self.dire)
            self.dire = sum_mv
            tuple(self.dire)
        screen.blit(self.img, self.rct)


class Beam:
    """
    こうかとんが放つビームに関するクラス
    """
    def __init__(self, bird:"Bird"):
        """
        ビーム画像Surfaceを生成する
         引数 bird：ビームを放つこうかとん（Birdインスタンス）
        """
        self.img = pg.image.load(f"fig/beam.png")
        self.rct = self.img.get_rect()
        self.rct.centery = bird.rct.centery
        self.rct.left = bird.rct.right
        self.vx, self.vy = +5, 0
        vx = bird.dire[0]
        vy = bird.dire[1]

        self.vx, self.vy = bird.dire[0], bird.dire[1]
        theta_rad = math.atan2(-self.vy, self.vx)
        theta_deg = math.degrees(theta_rad)
        pg.transform.rotozoom(self.img, theta_deg, 1.0)
        self.rct.centerx = bird.rct.centerx+bird.rct.width*self.vx/5
        self.rct.centery = bird.rct.centery+bird.rct.height*self.vy/5

    def update(self, screen: pg.Surface):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        #画面内にあるかの判定
        if check_bound(self.rct) == (True, True):
             self.rct.move_ip(self.vx, self.vy)
             screen.blit(self.img, self.rct)   


class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Score:
    """"
    スコア表示のクラス
    """
    def __init__(self):
        self.fonto = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.img = self.fonto.render("0",0, (0, 0, 255))
        self.xy = (100, HEIGHT-50)
        self.score = 0

    def update(self, screen: pg.Surface):
        text = f"スコア：{self.score}"
        self.img = self.fonto.render(text,True, (0, 0, 255))
        screen.blit(self.img, self.xy)


class Explosion:
    def __init__(self, bomb:Bomb):
        self.img = pg.image.load("fig/explosion.gif")
        self.img2 =  pg.transform.flip(self.img, True, True)
        self.lst = [self.img, self.img2]
        self.img_rct = self.img.get_rect()
        self.img2_rct = self.img2.get_rect()
        # 爆発した爆弾のrct.centerに座標を設定
        self.img_rct.center = bomb.rct.center
        self.img2_rct.center = bomb.rct.center
        self.life = 6

    def update(self, screen:pg.Surface):
        self.life-=1
        if self.life>0:
            for i in range(self.life):
                if i % 2 == 0:
                    screen.blit(self.img, self.img_rct)
                else:
                    screen.blit(self.img2, self.img2_rct)

def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((300, 200))
    beam = None
    #bomb = Bomb((255, 0, 0), 10)
    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)]
    score = Score()
    beams = []
    ex = []
    clock = pg.time.Clock()
    tmr = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                # スペースキー押下でBeamクラスのインスタンス生成
                beam = Beam(bird)
                beams.append(beam)      
        screen.blit(bg_img, [0, 0])
        
        for bomb in bombs:
            if bird.rct.colliderect(bomb.rct):
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                #bird.change_img(8, screen)
                fonto = pg.font.Font(None, 80)
                txt = fonto.render("Game Over", True, (255, 0, 0))
                screen.blit(txt, [WIDTH/2-150, HEIGHT/2])
                pg.display.update()
                time.sleep(5)
                #time.sleep(1)
                return
        
        #ビームと爆弾の衝突判定
        #for i, bomb in enumerate(bombs):
        for i in range(len(bombs)):
            if beam is not None:
                if bombs[i].rct.colliderect(beam.rct):
                    bombs[i] = None
                    beam = None
                    score.score+=1
                    #爆発エフェクト
                    ex.append(Explosion(bombs))
                    for i ,hoge in enumerate(ex):
                        ex = [hoge for hoge in ex if hoge.life > 0]
                    #score.update(screen)
                    #爆弾を撃ち落としたらこうかとんが喜ぶ画像に切り替え
                    bird.change_img(6, screen)
                    #複数ビームの衝突判定
                    for i ,hoge in enumerate(beams):
                        if beam is not None: 
                            if hoge.rct.colliderect(bomb.rct):
                                beams[i] = None
        #リストの更新
        bombs = [bomb for bomb in bombs if bomb is not None]
        beams = [beam for beam in beams if beam is not None]

        for i ,hoge in enumerate(beams):
            if check_bound(hoge.rct) != (True, True):
                beams.remove(beams[i])


        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        if beam is not None:
            beam.update(screen)   
        for bomb in bombs:
            bomb.update(screen)
        for beam in beams: 
            beam.update(screen) 
        for exs in ex:
            exs.update(screen)
        score.update(screen)
        pg.display.update()
        tmr += 1 
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
