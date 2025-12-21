import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()

player_pos = pygame.Vector2(300, 300)
running = True
red_img = pygame.image.load('assets/images/Title_Screen_button.png').convert_alpha()
red_img = pygame.transform.scale(red_img,
                                (red_img.get_width() / 2,
                                red_img.get_height() / 2))


delta_time = 0.1
while running:
    screen.fill((255, 10, 255))
    screen.blit(red_img, player_pos)
    player_pos[0] += 1

    hit_box = pygame.Rect(player_pos[0], player_pos[1], red_img.get_width(), red_img.get_height())

    mpos = pygame.mouse.get_pos()

    target = pygame.Rect(300, 100, 160, 280)
    collision = hit_box.colliderect(target)
    m_collision = target.collidepoint(mpos)
    pygame.draw.rect(screen, (255 * collision, 255 * m_collision, 0), target)

    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if m_collision:
                    print(m_collision)


    pygame.display.flip()
    delta_time = clock.tick(60) / 1000
    delta_time = max(0.001, min(0.1, delta_time))


pygame.quit()

        # font_path = 'assets/fonts/Dalek.ttf'
        # self.title_font = self.initialize_font(font_path, font_size=20)
        # text_color = (0, 0, 0)
        # self.text_surface = self.title_font.render("MAIN MENU", True, text_color)
        # self.text_rect = self.text_surface.get_rect()
        # self.text_rect.center = (self._screen_size[0] // 2, self._screen_size[1] // 2)
        