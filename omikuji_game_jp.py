"""
おみくじゲーム (Omikuji Game)
Developed using Amazon Q Developer CLI

Copyright (c) 2025 hepts
Licensed under MIT License
"""

import pygame
import sys
import random
import math
import os

# 初期化
pygame.init()

# 画面設定
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("おみくじゲーム")

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)        # 明るすぎない赤
GREEN = (50, 180, 50)      # 明るすぎない緑
BLUE = (50, 50, 220)       # 明るすぎない青
GOLD = (218, 165, 32)      # 金色
ORANGE = (255, 140, 0)     # オレンジ
PURPLE = (147, 112, 219)   # 紫
BROWN = (139, 69, 19)      # 茶色
LIGHT_BROWN = (205, 133, 63)  # 明るい茶色
CREAM = (255, 253, 208)    # クリーム色
PAPER = (252, 246, 225)    # 和紙色

# 背景画像の作成
def create_background_texture():
    # 和紙風の背景テクスチャを作成
    texture = pygame.Surface((WIDTH, HEIGHT))
    texture.fill(PAPER)
    
    # ランダムな模様を追加
    for _ in range(5000):
        x = random.randint(0, WIDTH-1)
        y = random.randint(0, HEIGHT-1)
        color_var = random.randint(-10, 10)
        color = (245 + color_var, 240 + color_var, 220 + color_var)
        size = random.randint(1, 3)
        pygame.draw.circle(texture, color, (x, y), size)
    
    return texture

# 背景テクスチャを作成
background_texture = create_background_texture()

# macOSの日本語フォントパスを探す
font_paths = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
    "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc",
    "/System/Library/Fonts/AppleGothic.ttf",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/Library/Fonts/Osaka.ttf"
]

# 利用可能なフォントを探す
font_path = None
for path in font_paths:
    if os.path.exists(path):
        font_path = path
        break

# フォント設定
if font_path:
    try:
        font_large = pygame.font.Font(font_path, 48)
        font_medium = pygame.font.Font(font_path, 36)
        font_small = pygame.font.Font(font_path, 24)
        print(f"日本語フォントを読み込みました: {font_path}")
    except:
        print("日本語フォントの読み込みに失敗しました。デフォルトフォントを使用します。")
        font_large = pygame.font.SysFont(None, 72)
        font_medium = pygame.font.SysFont(None, 48)
        font_small = pygame.font.SysFont(None, 36)
else:
    print("日本語フォントが見つかりませんでした。デフォルトフォントを使用します。")
    font_large = pygame.font.SysFont(None, 72)
    font_medium = pygame.font.SysFont(None, 48)
    font_small = pygame.font.SysFont(None, 36)

# おみくじの結果
omikuji_results = [
    {"result": "大吉", "color": RED, "description": "とても良い運勢です！", "points": 10},
    {"result": "中吉", "color": GREEN, "description": "良い運勢です。", "points": 5},
    {"result": "小吉", "color": BLUE, "description": "まあまあの運勢です。", "points": 3},
    {"result": "吉", "color": GOLD, "description": "普通の運勢です。", "points": 1},
    {"result": "末吉", "color": ORANGE, "description": "少し注意が必要かもしれません。", "points": 0},
    {"result": "凶", "color": PURPLE, "description": "今日は慎重に行動しましょう。", "points": -1},
    {"result": "大凶", "color": BROWN, "description": "とても注意が必要な日です。", "points": -5}
]

# ゲーム状態
class GameState:
    def __init__(self):
        self.state = "title"  # title, drawing, result, triple_result
        self.result = None
        self.triple_results = []  # 3連用の結果を格納
        self.current_triple_index = 0  # 3連表示中のインデックス
        self.total_points = 0  # 3連引きの合計ポイント
        self.animation_timer = 0
        self.shake_amount = 0
        self.paper_y = -300  # 紙の初期位置（画面外）
        self.paper_speed = 0
        self.paper_rotation = 0
        self.paper_scale = 0.1
        self.result_alpha = 0  # 結果テキストの透明度
        self.particles = []  # パーティクル効果用
        
game = GameState()

# パーティクルクラス
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(3, 8)
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-5, -1)
        self.life = random.randint(30, 90)  # フレーム単位の寿命
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += 0.1  # 重力
        self.life -= 1
        self.size = max(0, self.size - 0.05)
        
    def draw(self, surface):
        if self.life > 0 and self.size > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

# ボタンクラス
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.scale = 1.0
        self.target_scale = 1.0
        self.angle = 0  # 装飾用の角度
        
    def draw(self, surface):
        # アニメーション効果（ホバー時に少し大きくなる）
        self.scale += (self.target_scale - self.scale) * 0.2
        self.angle = (self.angle + 1) % 360  # 装飾アニメーション用
        
        # スケールに基づいて拡大されたボタンの矩形を計算
        scaled_width = self.rect.width * self.scale
        scaled_height = self.rect.height * self.scale
        scaled_x = self.rect.centerx - scaled_width / 2
        scaled_y = self.rect.centery - scaled_height / 2
        scaled_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
        
        # ボタンの影
        shadow_rect = pygame.Rect(scaled_x + 4, scaled_y + 4, scaled_width, scaled_height)
        pygame.draw.rect(surface, (100, 100, 100, 150), shadow_rect, border_radius=15)
        
        # ボタン本体
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, scaled_rect, border_radius=15)
        pygame.draw.rect(surface, (100, 60, 20), scaled_rect, 3, border_radius=15)
        
        # 装飾（和風の模様）
        if self.is_hovered:
            # 四隅に小さな装飾
            corner_size = 8
            offset = math.sin(self.angle * 0.05) * 2
            
            # 左上
            pygame.draw.circle(surface, (255, 215, 0), 
                              (int(scaled_rect.left + corner_size), 
                               int(scaled_rect.top + corner_size + offset)), 3)
            # 右上
            pygame.draw.circle(surface, (255, 215, 0), 
                              (int(scaled_rect.right - corner_size), 
                               int(scaled_rect.top + corner_size + offset)), 3)
            # 左下
            pygame.draw.circle(surface, (255, 215, 0), 
                              (int(scaled_rect.left + corner_size), 
                               int(scaled_rect.bottom - corner_size - offset)), 3)
            # 右下
            pygame.draw.circle(surface, (255, 215, 0), 
                              (int(scaled_rect.right - corner_size), 
                               int(scaled_rect.bottom - corner_size - offset)), 3)
        
        # テキスト
        text_surface = font_medium.render(self.text, True, (60, 30, 10))
        text_rect = text_surface.get_rect(center=scaled_rect.center)
        surface.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(pos)
        
        # ホバー状態が変わったらスケールのターゲットを変更
        if self.is_hovered and not was_hovered:
            self.target_scale = 1.1
        elif not self.is_hovered and was_hovered:
            self.target_scale = 1.0
            
        return self.is_hovered
        
    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

# ボタン作成
draw_button = Button(WIDTH//2 - 160, HEIGHT - 100, 300, 60, "おみくじを引く", (255, 230, 200), (255, 200, 150))
triple_button = Button(WIDTH//2 + 160, HEIGHT - 100, 300, 60, "3連で引く", (230, 255, 200), (200, 255, 150))
back_button = Button(WIDTH//2, HEIGHT - 100, 300, 60, "タイトルに戻る", (255, 230, 200), (255, 200, 150))
next_button = Button(WIDTH//2 + 160, HEIGHT - 100, 150, 60, "次へ ▶", (230, 230, 255), (200, 200, 255))

# おみくじを引く関数
def draw_omikuji(triple=False):
    game.state = "drawing"
    game.animation_timer = 0
    game.shake_amount = 0
    game.paper_y = -300
    game.paper_speed = 0
    game.paper_rotation = 0
    game.paper_scale = 0.1
    game.result_alpha = 0
    game.particles = []
    game.result = None
    
    # 3連引きの場合は空の配列を作成、通常引きの場合はNoneに設定
    if triple:
        game.triple_results = []  # 空の配列で初期化
        game.current_triple_index = 0
        print("3連引きモード開始")
    else:
        game.triple_results = None  # 通常引きの場合はNoneに設定
        print("通常引きモード開始")

# おみくじ箱を描画する関数
def draw_omikuji_box(x, y, width, height, shake=0, is_title=False):
    # 箱の位置をシェイク量に応じて調整
    box_x = x
    if shake > 0:
        box_x += random.uniform(-shake, shake)
    
    # 箱の本体 - タイトル画面ではより豪華な見た目に
    if is_title:
        # グラデーション風の効果を出すために複数の長方形を描画
        for i in range(5):
            offset = i * 2
            shade = max(0, 205 - i * 10)  # だんだん暗くなる
            pygame.draw.rect(screen, (shade, shade * 0.65, shade * 0.3), 
                           (box_x + offset, y + offset, width - offset*2, height - offset*2), 0, 15)
        
        # 箱の縁取り - 金色の装飾
        pygame.draw.rect(screen, GOLD, (box_x, y, width, height), 5, 15)
        pygame.draw.rect(screen, (100, 50, 0), (box_x + 3, y + 3, width - 6, height - 6), 2, 15)
        
        # 箱の装飾パターン - 和風の模様
        current_time = pygame.time.get_ticks()
        for i in range(4):
            for j in range(3):
                pattern_x = box_x + width * (i + 1) / 5
                pattern_y = y + height * (j + 1) / 4
                pattern_size = 8 + math.sin(current_time * 0.001 + i * j) * 2
                pygame.draw.circle(screen, (180, 120, 40), (pattern_x, pattern_y), pattern_size)
                pygame.draw.circle(screen, (220, 180, 80), (pattern_x, pattern_y), pattern_size * 0.6)
        
        # 箱の上部 - 豪華な屋根
        roof_height = 40
        pygame.draw.polygon(screen, (160, 80, 30), [
            (box_x - 20, y),
            (box_x + width + 20, y),
            (box_x + width * 0.8, y - roof_height),
            (box_x + width * 0.2, y - roof_height)
        ])
        pygame.draw.polygon(screen, (100, 50, 0), [
            (box_x - 20, y),
            (box_x + width + 20, y),
            (box_x + width * 0.8, y - roof_height),
            (box_x + width * 0.2, y - roof_height)
        ], 3)
        
        # 屋根の装飾
        pygame.draw.line(screen, GOLD, 
                       (box_x + width * 0.5, y - roof_height), 
                       (box_x + width * 0.5, y - roof_height * 1.3), 4)
        pygame.draw.circle(screen, GOLD, 
                         (box_x + width * 0.5, y - roof_height * 1.4), 8)
        
        # 箱の中の穴 - 神秘的な光を放つ
        hole_color = (40, 20, 0)
        hole_x = box_x + width/4
        hole_y = y + 40
        hole_width = width/2
        hole_height = height/3
        
        # 穴の周りに光の効果
        glow_radius = 20 + math.sin(current_time * 0.002) * 5
        for r in range(int(glow_radius), 0, -2):
            alpha = 150 - r * 5
            if alpha > 0:
                s = pygame.Surface((hole_width + r*2, hole_height + r*2), pygame.SRCALPHA)
                pygame.draw.ellipse(s, (255, 200, 100, alpha), 
                                  (0, 0, hole_width + r*2, hole_height + r*2))
                screen.blit(s, (hole_x - r, hole_y - r))
        
        # 穴本体
        pygame.draw.ellipse(screen, hole_color, (hole_x, hole_y, hole_width, hole_height))
        
        # おみくじの棒が少し見える
        stick_count = 5
        for i in range(stick_count):
            stick_x = hole_x + hole_width * (i + 1) / (stick_count + 1)
            stick_height = random.randint(10, 25)
            pygame.draw.line(screen, (240, 230, 210), 
                           (stick_x, hole_y + hole_height * 0.3),
                           (stick_x, hole_y + hole_height * 0.3 - stick_height), 3)
    else:
        # 通常のおみくじ箱（ゲームプレイ中）
        # 箱の本体
        pygame.draw.rect(screen, LIGHT_BROWN, (box_x, y, width, height))
        pygame.draw.rect(screen, (100, 50, 0), (box_x, y, width, height), 5)
        
        # 箱の装飾
        pygame.draw.rect(screen, (180, 100, 50), (box_x + width/4, y - 20, width/2, 20))
        pygame.draw.rect(screen, (100, 50, 0), (box_x + width/4, y - 20, width/2, 20), 3)
        
        # 箱の中の穴
        hole_color = (50, 25, 0)
        pygame.draw.ellipse(screen, hole_color, (box_x + width/4, y + 30, width/2, height/3))

# 3連引きの進行状況を表示するテキスト
def draw_triple_progress_text(screen, current_count):
    # 和風の装飾付きテキスト背景
    text = f"{current_count}/3回目"
    progress_text = font_small.render(text, True, (100, 60, 20))
    
    # 背景の装飾枠
    text_width = progress_text.get_width()
    text_height = progress_text.get_height()
    padding = 10
    
    bg_rect = pygame.Rect(WIDTH - text_width - padding*2 - 10, 20, 
                         text_width + padding*2, text_height + padding)
    pygame.draw.rect(screen, (255, 250, 240), bg_rect, border_radius=8)
    pygame.draw.rect(screen, (150, 100, 50), bg_rect, 2, border_radius=8)
    
    # 角の装飾
    corner_size = 5
    pygame.draw.line(screen, (150, 100, 50), 
                    (bg_rect.left + 3, bg_rect.top + corner_size), 
                    (bg_rect.left + corner_size, bg_rect.top + 3), 2)
    pygame.draw.line(screen, (150, 100, 50), 
                    (bg_rect.right - 3, bg_rect.top + corner_size), 
                    (bg_rect.right - corner_size, bg_rect.top + 3), 2)
    pygame.draw.line(screen, (150, 100, 50), 
                    (bg_rect.left + 3, bg_rect.bottom - corner_size), 
                    (bg_rect.left + corner_size, bg_rect.bottom - 3), 2)
    pygame.draw.line(screen, (150, 100, 50), 
                    (bg_rect.right - 3, bg_rect.bottom - corner_size), 
                    (bg_rect.right - corner_size, bg_rect.bottom - 3), 2)
    
    # テキストを描画
    screen.blit(progress_text, (WIDTH - text_width - padding - 10, 20 + padding//2))

# 装飾的な和風の背景要素を描画する関数
def draw_decorative_elements(screen):
    # 桜の花びらのような装飾
    current_time = pygame.time.get_ticks()
    for i in range(8):
        x = (current_time // 50 + i * 200) % (WIDTH + 100) - 50
        y = HEIGHT - 100 + math.sin(current_time * 0.001 + i) * 20
        size = 20 + math.sin(current_time * 0.002 + i * 0.5) * 5
        pygame.draw.circle(screen, (255, 230, 240), (int(x), int(y)), int(size))
        pygame.draw.circle(screen, (255, 200, 220), (int(x), int(y)), int(size * 0.7))
    
    # 上部の装飾
    for i in range(6):
        x = (current_time // 70 + i * 180) % (WIDTH + 100) - 50
        y = 50 + math.sin(current_time * 0.001 + i) * 10
        size = 15 + math.sin(current_time * 0.002 + i * 0.5) * 3
        pygame.draw.circle(screen, (230, 255, 240), (int(x), int(y)), int(size))
        pygame.draw.circle(screen, (200, 240, 220), (int(x), int(y)), int(size * 0.7))
    
    # 和風の装飾ライン
    line_y = HEIGHT - 30
    line_wave = math.sin(current_time * 0.001) * 5
    points = []
    for x in range(0, WIDTH, 20):
        y = line_y + math.sin(x * 0.05 + current_time * 0.001) * 5
        points.append((x, y))
    
    if len(points) > 1:
        pygame.draw.lines(screen, (150, 100, 50), False, points, 2)

# メインループ
clock = pygame.time.Clock()
running = True

while running:
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左クリック
                mouse_click = True
    
    # 和紙風の背景を描画
    screen.blit(background_texture, (0, 0))
    
    # 装飾的な背景要素を描画
    draw_decorative_elements(screen)
    
    # タイトル画面
    if game.state == "title":
        # 背景に和風の装飾を追加
        for i in range(0, WIDTH, 50):
            for j in range(0, HEIGHT, 50):
                if (i + j) % 100 == 0:
                    size = 3 + math.sin(pygame.time.get_ticks() * 0.001 + i * 0.1 + j * 0.1) * 2
                    pygame.draw.circle(screen, (245, 240, 220), (i, j), size)
        
        # おみくじ箱を描画 - 右側に配置（タイトル画面用の豪華バージョン）
        box_x = WIDTH - 350
        box_y = HEIGHT//2 - 150
        draw_omikuji_box(box_x, box_y, 300, 250, shake=0, is_title=True)
        
        # おみくじ箱から出る光の効果
        current_time = pygame.time.get_ticks()
        light_points = 8
        for i in range(light_points):
            angle = i * (2 * math.pi / light_points) + current_time * 0.0005
            length = 50 + math.sin(current_time * 0.001 + i) * 20
            start_x = box_x + 150
            start_y = box_y + 100
            end_x = start_x + math.cos(angle) * length
            end_y = start_y + math.sin(angle) * length
            
            # グラデーションの光線
            for j in range(10):
                progress = j / 10
                point_x = start_x + (end_x - start_x) * progress
                point_y = start_y + (end_y - start_y) * progress
                size = 5 * (1 - progress)
                alpha = int(200 * (1 - progress))
                s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 220, 100, alpha), (size, size), size)
                screen.blit(s, (point_x - size, point_y - size))
        
        # タイトルテキストをアニメーション（左側に配置、和風デザイン）
        title_y_offset = math.sin(pygame.time.get_ticks() * 0.002) * 8
        
        # 影付きの装飾枠
        frame_rect = pygame.Rect(50, HEIGHT//4 - 30, 350, 120)
        pygame.draw.rect(screen, (220, 200, 180), frame_rect, border_radius=15)
        pygame.draw.rect(screen, (150, 100, 50), frame_rect, 4, border_radius=15)
        
        # 装飾的な角の模様
        corner_size = 15
        pygame.draw.line(screen, (150, 100, 50), (frame_rect.left + 5, frame_rect.top + corner_size), 
                        (frame_rect.left + corner_size, frame_rect.top + 5), 3)
        pygame.draw.line(screen, (150, 100, 50), (frame_rect.right - 5, frame_rect.top + corner_size), 
                        (frame_rect.right - corner_size, frame_rect.top + 5), 3)
        pygame.draw.line(screen, (150, 100, 50), (frame_rect.left + 5, frame_rect.bottom - corner_size), 
                        (frame_rect.left + corner_size, frame_rect.bottom - 5), 3)
        pygame.draw.line(screen, (150, 100, 50), (frame_rect.right - 5, frame_rect.bottom - corner_size), 
                        (frame_rect.right - corner_size, frame_rect.bottom - 5), 3)
        
        # タイトルテキスト
        title_text = font_large.render("おみくじゲーム", True, (120, 60, 30))
        screen.blit(title_text, (frame_rect.centerx - title_text.get_width()//2, 
                                frame_rect.centery - title_text.get_height()//2 + title_y_offset))
        
        # サブタイトル
        subtitle_text = font_small.render("～運命の神様～", True, (150, 100, 50))
        screen.blit(subtitle_text, (frame_rect.centerx - subtitle_text.get_width()//2, 
                                    frame_rect.bottom + 10))
        
        # ボタンを下部に配置
        draw_button.rect.center = (WIDTH//2 - 160, HEIGHT - 100)
        triple_button.rect.center = (WIDTH//2 + 160, HEIGHT - 100)
        
        draw_button.check_hover(mouse_pos)
        draw_button.draw(screen)
        
        triple_button.check_hover(mouse_pos)
        triple_button.draw(screen)
        
        if draw_button.is_clicked(mouse_pos, mouse_click):
            draw_omikuji(triple=False)
            
        if triple_button.is_clicked(mouse_pos, mouse_click):
            draw_omikuji(triple=True)
    
    # おみくじを引いている途中
    elif game.state == "drawing":
        game.animation_timer += 1
        
        # シェイクアニメーション
        if game.animation_timer < 60:
            game.shake_amount = min(10, game.animation_timer / 6)
        else:
            game.shake_amount = max(0, 10 - (game.animation_timer - 60) / 3)
        
        # おみくじ箱を描画（シェイク効果付き）
        draw_omikuji_box(WIDTH//2 - 150, HEIGHT//2 - 200, 300, 250, game.shake_amount, is_title=False)
        
        # 3連引きの場合、進行状況を表示
        if game.triple_results is not None and len(game.triple_results) < 3:
            draw_triple_progress_text(screen, len(game.triple_results) + 1)
        
        # パーティクル効果（箱が揺れているときに発生）
        if game.shake_amount > 5 and random.random() < 0.3:
            box_center_x = WIDTH//2
            box_bottom_y = HEIGHT//2 + 50
            for _ in range(2):
                particle_color = random.choice([RED, GREEN, BLUE, GOLD, ORANGE, PURPLE])
                game.particles.append(Particle(box_center_x, box_bottom_y, particle_color))
        
        # パーティクルの更新と描画
        for particle in game.particles[:]:
            particle.update()
            if particle.life <= 0:
                game.particles.remove(particle)
            else:
                particle.draw(screen)
        
        # アニメーション（おみくじ紙が出てくる）
        if game.animation_timer > 90:  # 約1.5秒後
            # 結果がまだ決まっていない場合
            if not game.result:
                game.result = random.choice(omikuji_results)
                
                # 3連引きモードの場合、結果を配列に追加
                if game.triple_results is not None:
                    game.triple_results.append(game.result)
                    print(f"結果を追加: {game.result['result']}, 現在 {len(game.triple_results)} 枚")
            
            # おみくじ紙が箱から出てくるアニメーション
            if game.paper_y < HEIGHT//2 - 50:
                game.paper_speed += 0.5
                game.paper_y += game.paper_speed
                game.paper_rotation += 5
                game.paper_scale = min(1.0, game.paper_scale + 0.05)
            else:
                # 3連引きモードの場合
                if game.triple_results is not None:
                    if len(game.triple_results) < 3:
                        # まだ3回引いていない場合、次の引きへ
                        print(f"3連引き中: {len(game.triple_results)}回目完了")
                        game.state = "drawing"
                        game.animation_timer = 0
                        game.shake_amount = 0
                        game.paper_y = -300
                        game.paper_speed = 0
                        game.paper_rotation = 0
                        game.paper_scale = 0.1
                        game.result = None
                    else:
                        # 3回引き終わった場合、結果画面へ
                        print("3連引き完了:", [r["result"] for r in game.triple_results])
                        game.state = "triple_result"
                        game.animation_timer = 0
                        game.current_triple_index = 0
                        game.result_alpha = 0
                else:
                    # 通常の1回引きの場合
                    game.state = "result"
                    game.animation_timer = 0
            
            # おみくじ紙を描画
            paper_surface = pygame.Surface((300, 150), pygame.SRCALPHA)
            pygame.draw.rect(paper_surface, (255, 250, 240), (0, 0, 300, 150), border_radius=10)
            pygame.draw.rect(paper_surface, BLACK, (0, 0, 300, 150), 2, border_radius=10)
            
            # 紙を回転・拡大縮小して描画
            scaled_paper = pygame.transform.rotozoom(paper_surface, game.paper_rotation, game.paper_scale)
            paper_rect = scaled_paper.get_rect(center=(WIDTH//2, game.paper_y))
            screen.blit(scaled_paper, paper_rect)
        
        drawing_text = font_medium.render("おみくじを引いています...", True, BLACK)
        screen.blit(drawing_text, (WIDTH//2 - drawing_text.get_width()//2, HEIGHT//2 + 150))
    
    # 結果画面
    elif game.state == "result":
        game.animation_timer += 1
        
        # おみくじ箱を描画
        draw_omikuji_box(WIDTH//2 - 150, HEIGHT//2 - 300, 300, 250, is_title=False)
        
        # おみくじの紙 - 白っぽい背景
        paper_color = (255, 250, 240)
        
        # 紙の位置と回転のアニメーション
        paper_y_offset = math.sin(pygame.time.get_ticks() * 0.003) * 5
        paper_rotation = math.sin(pygame.time.get_ticks() * 0.002) * 2
        
        # 回転した紙を描画
        paper_surface = pygame.Surface((400, 200), pygame.SRCALPHA)
        pygame.draw.rect(paper_surface, paper_color, (0, 0, 400, 200), border_radius=10)
        pygame.draw.rect(paper_surface, BLACK, (0, 0, 400, 200), 2, border_radius=10)
        
        rotated_paper = pygame.transform.rotate(paper_surface, paper_rotation)
        paper_rect = rotated_paper.get_rect(center=(WIDTH//2, HEIGHT//2 + paper_y_offset))
        screen.blit(rotated_paper, paper_rect)
        
        # 結果テキストのフェードイン
        if game.animation_timer < 30:
            game.result_alpha = min(255, game.result_alpha + 8)
        
        # 結果テキスト - 常に黒で表示して視認性を確保
        result_text = font_large.render(game.result["result"], True, BLACK)
        result_text.set_alpha(game.result_alpha)
        
        # 色付きの円で運勢を表現（パルス効果）- サイズを小さくして結果に連動
        # 結果のポイントに応じて基本サイズを変更（大吉ほど大きく）
        base_size = 10 + min(5, abs(game.result["points"])) * 1.2
        # アニメーションをおみくじの結果と連動させる（ポイントが高いほど速く動く）
        anim_speed = 0.01 + abs(game.result["points"]) * 0.002
        circle_size = base_size + math.sin(pygame.time.get_ticks() * anim_speed) * 2
        fortune_color = game.result["color"]
        # 紙の動きに合わせて円も動くように
        circle_y_offset = paper_y_offset + math.sin(pygame.time.get_ticks() * 0.003) * 3
        pygame.draw.circle(screen, fortune_color, (WIDTH//2, HEIGHT//2 - 70 + circle_y_offset), circle_size)
        pygame.draw.circle(screen, BLACK, (WIDTH//2, HEIGHT//2 - 70 + circle_y_offset), circle_size, 2)
        
        desc_text = font_small.render(game.result["description"], True, BLACK)
        desc_text.set_alpha(game.result_alpha)
        
        # ポイント表示
        points = game.result["points"]
        points_text = font_medium.render(f"{points:+d} pt", True, 
                                        (50, 180, 50) if points >= 0 else (180, 50, 50))
        points_text.set_alpha(game.result_alpha)
        
        # 結果に応じたパーティクル効果
        if game.animation_timer < 60 and game.animation_timer % 5 == 0:
            for _ in range(3):
                particle_x = WIDTH//2 + random.uniform(-150, 150)
                particle_y = HEIGHT//2 + random.uniform(-50, 50)
                game.particles.append(Particle(particle_x, particle_y, game.result["color"]))
        
        # パーティクルの更新と描画
        for particle in game.particles[:]:
            particle.update()
            if particle.life <= 0:
                game.particles.remove(particle)
            else:
                particle.draw(screen)
        
        # テキストを紙の上に描画
        text_y_offset = paper_y_offset  # 紙と同じオフセットを適用
        screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2 - 30 + text_y_offset))
        screen.blit(desc_text, (WIDTH//2 - desc_text.get_width()//2, HEIGHT//2 + 20 + text_y_offset))
        screen.blit(points_text, (WIDTH//2 - points_text.get_width()//2, HEIGHT//2 + 50 + text_y_offset))
        
        back_button.rect.center = (WIDTH//2, HEIGHT - 100)
        back_button.check_hover(mouse_pos)
        back_button.draw(screen)
        
        if back_button.is_clicked(mouse_pos, mouse_click):
            game.state = "title"
            
    # 3連結果画面
    elif game.state == "triple_result":
        game.animation_timer += 1
        
        # おみくじ箱を描画（上部に小さく）
        draw_omikuji_box(WIDTH//2 - 100, HEIGHT//4 - 100, 200, 150, is_title=False)
        
        # 現在表示中の結果
        current_result = game.triple_results[game.current_triple_index]
        
        # おみくじの紙 - 白っぽい背景
        paper_color = (255, 250, 240)
        
        # 紙の位置と回転のアニメーション
        paper_y_offset = math.sin(pygame.time.get_ticks() * 0.003) * 5
        paper_rotation = math.sin(pygame.time.get_ticks() * 0.002) * 2
        
        # 回転した紙を描画
        paper_surface = pygame.Surface((400, 200), pygame.SRCALPHA)
        pygame.draw.rect(paper_surface, paper_color, (0, 0, 400, 200), border_radius=10)
        pygame.draw.rect(paper_surface, BLACK, (0, 0, 400, 200), 2, border_radius=10)
        
        rotated_paper = pygame.transform.rotate(paper_surface, paper_rotation)
        paper_rect = rotated_paper.get_rect(center=(WIDTH//2, HEIGHT//2 + paper_y_offset))
        screen.blit(rotated_paper, paper_rect)
        
        # 結果テキストのフェードイン
        if game.animation_timer < 30:
            game.result_alpha = min(255, game.result_alpha + 8)
        
        # 結果テキスト - 常に黒で表示して視認性を確保
        result_text = font_large.render(current_result["result"], True, BLACK)
        result_text.set_alpha(game.result_alpha)
        
        # 色付きの円で運勢を表現（パルス効果）- サイズを小さくして結果に連動
        # 結果のポイントに応じて基本サイズを変更（大吉ほど大きく）
        base_size = 10 + min(5, abs(current_result["points"])) * 1.2
        # アニメーションをおみくじの結果と連動させる（ポイントが高いほど速く動く）
        anim_speed = 0.01 + abs(current_result["points"]) * 0.002
        circle_size = base_size + math.sin(pygame.time.get_ticks() * anim_speed) * 2
        fortune_color = current_result["color"]
        # 紙の動きに合わせて円も動くように
        circle_y_offset = paper_y_offset + math.sin(pygame.time.get_ticks() * 0.003) * 3
        pygame.draw.circle(screen, fortune_color, (WIDTH//2, HEIGHT//2 - 70 + circle_y_offset), circle_size)
        pygame.draw.circle(screen, BLACK, (WIDTH//2, HEIGHT//2 - 70 + circle_y_offset), circle_size, 2)
        
        desc_text = font_small.render(current_result["description"], True, BLACK)
        desc_text.set_alpha(game.result_alpha)
        
        # ポイント表示
        points = current_result["points"]
        points_text = font_medium.render(f"{points:+d} pt", True, 
                                        (50, 180, 50) if points >= 0 else (180, 50, 50))
        points_text.set_alpha(game.result_alpha)
        
        # 3連引きの合計ポイント計算
        if game.current_triple_index == 2:  # 最後の結果の時だけ合計を計算
            if game.total_points == 0:  # まだ計算していない場合
                game.total_points = sum(result["points"] for result in game.triple_results)
        
        # 結果に応じたパーティクル効果
        if game.animation_timer < 60 and game.animation_timer % 5 == 0:
            for _ in range(3):
                particle_x = WIDTH//2 + random.uniform(-150, 150)
                particle_y = HEIGHT//2 + random.uniform(-50, 50)
                game.particles.append(Particle(particle_x, particle_y, current_result["color"]))
        
        # パーティクルの更新と描画
        for particle in game.particles[:]:
            particle.update()
            if particle.life <= 0:
                game.particles.remove(particle)
            else:
                particle.draw(screen)
        
        # テキストを紙の上に描画
        text_y_offset = paper_y_offset  # 紙と同じオフセットを適用
        screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2 - 30 + text_y_offset))
        screen.blit(desc_text, (WIDTH//2 - desc_text.get_width()//2, HEIGHT//2 + 20 + text_y_offset))
        screen.blit(points_text, (WIDTH//2 - points_text.get_width()//2, HEIGHT//2 + 50 + text_y_offset))
        
        # 3連結果のインジケーター（中央上部に配置）- サイズを小さく調整
        indicator_y = HEIGHT//2 + 80
        for i in range(3):
            circle_color = (200, 200, 200)
            circle_size = 6  # 非選択時のサイズを小さく
            if i == game.current_triple_index:
                circle_color = current_result["color"]
                circle_size = 8  # 選択時のサイズも小さく
                # 選択中のインジケーターを脈動させる
                circle_size += math.sin(pygame.time.get_ticks() * 0.01) * 1
            pygame.draw.circle(screen, circle_color, (WIDTH//2 - 30 + i * 30, indicator_y), circle_size)
            pygame.draw.circle(screen, BLACK, (WIDTH//2 - 30 + i * 30, indicator_y), circle_size, 1)
        
        # 最後の結果の場合、合計ポイントを表示
        if game.current_triple_index == 2:
            total_text = font_medium.render(f"合計: {game.total_points:+d} pt", True, 
                                          (50, 180, 50) if game.total_points >= 0 else (180, 50, 50))
            total_text.set_alpha(game.result_alpha)
            screen.blit(total_text, (WIDTH//2 - total_text.get_width()//2, indicator_y + 40))
        
        # ナビゲーションボタンを下部に配置（重ならないように）
        button_y = HEIGHT - 80
        
        # 「タイトルに戻る」ボタンは中央下部に
        back_button.rect.center = (WIDTH//2, button_y)
        back_button.check_hover(mouse_pos)
        back_button.draw(screen)
        
        # 「次へ」ボタンは右下に（最後の結果では表示しない）
        if game.current_triple_index < 2:
            next_button.rect.center = (WIDTH * 3//4, button_y)
            next_button.check_hover(mouse_pos)
            next_button.draw(screen)
            
            if next_button.is_clicked(mouse_pos, mouse_click):
                game.current_triple_index += 1
                game.animation_timer = 0
                game.result_alpha = 0
        
        if back_button.is_clicked(mouse_pos, mouse_click):
            game.state = "title"
            game.total_points = 0  # ポイントをリセット
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
