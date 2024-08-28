import random

import pygame as pg
import pytmx

pg.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600

TILE_SCALE = 1.88

font = pg.font.Font(None, 36)


class Bird(pg.sprite.Sprite):
    def __init__(self):
        super(Bird, self).__init__()

        self.load_anim()
        self.image = self.anim[0]
        self.current_image = 0

        self.rect = self.image.get_rect()
        self.rect.center = (-100, 100)  # Начальное положение персонажа

        # Начальная скорость и гравитация
        self.velocity_x = 1
        self.velocity_y = 0
        self.gravity = 0.3
        self.is_jumping = False

        self.timer = pg.time.get_ticks()
        self.interval = 200

        self.hp = 1

    def load_anim(self):
        tile_size = 16
        tile_scale = 3.5

        self.anim = []

        num_images = 4
        spritesheet = pg.image.load("D:\SkySmart\Проект Flappy Bird\Flappy Bird Assets\Player\StyleBird1\Bird1-1.png")

        for i in range(num_images):
            x = i * tile_size
            y = 0
            rect = pg.Rect(x, y, tile_size, tile_size)
            image = spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_size * tile_scale // 2, tile_size * tile_scale // 2))
            self.anim.append(image)

    def update(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_SPACE]:
            self.jump()

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        self.rect.x += self.velocity_x

        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1
            if self.current_image >= len(self.anim):
                self.current_image = 0
            self.image = self.anim[self.current_image]
            self.timer = pg.time.get_ticks()

    def jump(self):
        self.velocity_y = -3


class Tower(pg.sprite.Sprite):
    def __init__(self, image, x, y, width, height):
        super(Tower, self).__init__()

        self.image = pg.transform.scale(image, (width * TILE_SCALE, height * TILE_SCALE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SCALE
        self.rect.y = y * TILE_SCALE


class Game:

    def __init__(self):
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Flappy Bird")
        self.all_sprites = pg.sprite.Group()
        self.towers = pg.sprite.Group()

        self.player = Bird()
        self.all_sprites.add(self.player)
        self.tower_images = []
        num_image = 3
        spritesheet = pg.image.load("D:\SkySmart\Проект Flappy Bird\Flappy Bird Assets\Tiles\Style 2\PipeStyle2.png")
        for i in range(num_image):
            x = 0
            y = i * 16
            rect = pg.Rect(x, y, 32, 16)
            image = spritesheet.subsurface(rect)
            self.tower_images.append(image)

        self.background = pg.image.load("D:\SkySmart\Проект Flappy Bird\Flappy Bird Assets\Background\Background5.png")
        self.background = pg.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.setup()

    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.mode = "game"

        self.point_cord = 421.12
        self.points = 0

        self.clock = pg.time.Clock()

        self.tmx_map = pytmx.load_pygame("D:\SkySmart\Проект Flappy Bird\Flappy Bird Assets\level.tmx")

        for layer in self.tmx_map:
            for x, y, gid in layer:
                tile = self.tmx_map.get_tile_image_by_gid(gid)

                if tile:
                    height = random.randint(1, 16)
                    for block in range(height):
                        if height - block != 1:
                            tower = Tower(self.tower_images[1], x * self.tmx_map.tilewidth, y * self.tmx_map.tileheight,
                                          self.tmx_map.tilewidth,
                                          self.tmx_map.tileheight)
                        else:
                            tower = Tower(self.tower_images[2], x * self.tmx_map.tilewidth, y * self.tmx_map.tileheight,
                                          self.tmx_map.tilewidth,
                                          self.tmx_map.tileheight)
                        self.all_sprites.add(tower)
                        self.towers.add(tower)

                        y -= 1

                    height = 20 - height - 3
                    y = 0
                    for block in range(height):
                        if height - block != 1:
                            tower = Tower(self.tower_images[1], x * self.tmx_map.tilewidth, y * self.tmx_map.tileheight,
                                          self.tmx_map.tilewidth,
                                          self.tmx_map.tileheight)
                        else:
                            tower = Tower(self.tower_images[2], x * self.tmx_map.tilewidth, y * self.tmx_map.tileheight,
                                          self.tmx_map.tilewidth,
                                          self.tmx_map.tileheight)
                        self.all_sprites.add(tower)
                        self.towers.add(tower)
                        y += 1

        self.camera_x = 0
        self.camera_y = 0

        self.run()

    # noinspection PyAttributeOutsideInit

    def run(self):
        self.is_running = True
        while self.is_running:
            self.event()
            self.update()
            self.draw()
            self.clock.tick(60)
        pg.quit()
        quit()

    def event(self):
        global TILE_SCALE
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_running = False

    def update(self):
        if self.player.hp <= 0:
            self.mode = "game over"
            return
        if 0 > self.player.rect.y or self.player.rect.y > SCREEN_HEIGHT:
            self.player.hp -= 1

        self.player.update()

        self.camera_x = self.player.rect.x - SCREEN_WIDTH // 2

        hits = pg.sprite.spritecollide(self.player, self.towers, False)
        for hit in hits:
            self.player.hp -= 1
        if self.player.rect.x >= self.point_cord:
            self.points += 1
            self.point_cord += 4 * TILE_SCALE * 32

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, sprite.rect.move(-self.camera_x, -self.camera_y))

        if self.mode == "game over":
            text = font.render("Вы проиграли", True, (255, 0, 0))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text, text_rect)

        point_text = font.render(f"{self.points}", True, (0, 200, 0))
        point_text_rect = point_text.get_rect()
        point_text_rect.x = 0
        point_text_rect.y = 0
        self.screen.blit(point_text, point_text_rect)

        pg.display.flip()


if __name__ == "__main__":
    game = Game()
