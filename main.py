import pygame
import sys
import block_3d

pygame.init()
W, H = 1000, 700
screen = pygame.display.set_mode((W,H))
pygame.display.set_caption("三视图积木游戏 - 主界面")
WHITE = (255,255,255)
GRAY = (200,200,200)
DARK_GRAY = (100,100,100)

class Button:
    def __init__(self,x,y,w,h):
        self.rect = pygame.Rect(x,y,w,h)
    def draw(self):
        pygame.draw.rect(screen,GRAY,self.rect)
        pygame.draw.rect(screen,DARK_GRAY,self.rect,2)
    def is_click(self,pos):
        return self.rect.collidepoint(pos)

btn_start = Button(380,580,240,60)

# 加载按钮文字图片
try:
    btn_text_img = pygame.image.load("start_text.png").convert_alpha()
    btn_text_img = pygame.transform.scale(btn_text_img, (200,45))
except:
    btn_text_img = None

try:
    img_front = pygame.image.load("level_img/l1_front.png").convert()
    img_side = pygame.image.load("level_img/l1_side.png").convert()
    img_top = pygame.image.load("level_img/l1_top.png").convert()
    img_front = pygame.transform.scale(img_front,(260,260))
    img_side = pygame.transform.scale(img_side,(260,260))
    img_top = pygame.transform.scale(img_top,(260,260))
except Exception as e:
    img_front = None
    img_side = None
    img_top = None

running = True
while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if btn_start.is_click(event.pos):
                block_3d.start_3d_game(1)

    # 绘制三张三视图图片
    if img_front:
        screen.blit(img_front,(20,60))
        screen.blit(img_side,(360,60))
        screen.blit(img_top,(700,60))

    btn_start.draw()
    # 在按钮中间贴START GAME图片
    if btn_text_img:
        img_rect = btn_text_img.get_rect(center=btn_start.rect.center)
        screen.blit(btn_text_img, img_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()
