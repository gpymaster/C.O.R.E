import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import time
import math
import subprocess
import sys

class JarvisLogo:
    def __init__(self):
        pygame.init()
        self.width, self.height = 900, 900
        self.display = pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("C.O.R.E - JARVIS Interface")

        self.zoom = 1.0
        self.target_zoom = 1.0
        self.start_time = time.time()
        self.auto_start_delay = 3.0
        self.transition_complete = False
        self.rotation = 0.0
        self.ring_rotation = [0.0, 0.0, 0.0]
        self.glow_pulse = 0.0
        self.transition_started = False

        self.setup_gl()

    def setup_gl(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (self.width / self.height), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)

    def draw_circle(self, radius, segments=64, line_width=2.0, color=(1.0, 0.65, 0.0, 0.8)):
        glLineWidth(line_width)
        glBegin(GL_LINE_LOOP)
        glColor4f(*color)
        for i in range(segments):
            theta = 2.0 * np.pi * i / segments
            x = radius * np.cos(theta)
            y = radius * np.sin(theta)
            glVertex3f(x, y, 0)
        glEnd()

    def draw_arc(self, radius, start_angle, end_angle, segments=32, line_width=3.0, color=(1.0, 0.75, 0.0, 0.9)):
        glLineWidth(line_width)
        glBegin(GL_LINE_STRIP)
        glColor4f(*color)
        angle_range = end_angle - start_angle
        for i in range(segments + 1):
            t = i / segments
            theta = start_angle + angle_range * t
            x = radius * np.cos(theta)
            y = radius * np.sin(theta)
            alpha = color[3] * (0.5 + 0.5 * np.sin(t * np.pi))
            glColor4f(color[0], color[1], color[2], alpha)
            glVertex3f(x, y, 0)
        glEnd()

    def draw_tech_segments(self, radius, num_segments=12, rotation_offset=0, gap_ratio=0.15):
        segment_angle = 2 * np.pi / num_segments
        gap = segment_angle * gap_ratio
        arc_length = segment_angle - gap

        for i in range(num_segments):
            start = i * segment_angle + rotation_offset + gap / 2
            end = start + arc_length
            brightness = 0.8 + 0.2 * ((i % 3) / 3)
            self.draw_arc(radius, start, end, 20, 3.0, (1.0, 0.7 * brightness, 0.1, 0.85))

    def draw_tick_marks(self, radius, num_ticks=60, tick_length=0.08):
        glLineWidth(1.5)
        for i in range(num_ticks):
            angle = (2 * np.pi * i) / num_ticks
            inner_r = radius - tick_length if i % 5 == 0 else radius - tick_length * 0.5
            outer_r = radius

            x1 = inner_r * np.cos(angle)
            y1 = inner_r * np.sin(angle)
            x2 = outer_r * np.cos(angle)
            y2 = outer_r * np.sin(angle)

            glBegin(GL_LINES)
            if i % 5 == 0:
                glColor4f(1.0, 0.75, 0.2, 0.8)
            else:
                glColor4f(1.0, 0.65, 0.1, 0.5)
            glVertex3f(x1, y1, 0)
            glVertex3f(x2, y2, 0)
            glEnd()

    def draw_glow_ring(self, radius, intensity=1.0):
        for i in range(5):
            alpha = intensity * 0.15 * (5 - i)
            size = radius + i * 0.05
            self.draw_circle(size, 64, 1.5, (1.0, 0.8, 0.3, alpha))

    def draw_radial_lines(self, inner_radius, outer_radius, num_lines=24):
        glLineWidth(1.5)
        for i in range(num_lines):
            if i % 3 != 0:
                continue
            angle = (2 * np.pi * i) / num_lines
            x1 = inner_radius * np.cos(angle)
            y1 = inner_radius * np.sin(angle)
            x2 = outer_radius * np.cos(angle)
            y2 = outer_radius * np.sin(angle)

            glBegin(GL_LINES)
            glColor4f(1.0, 0.7, 0.15, 0.6)
            glVertex3f(x1, y1, 0)
            glColor4f(1.0, 0.65, 0.1, 0.2)
            glVertex3f(x2, y2, 0)
            glEnd()

    def draw_corner_brackets(self):
        bracket_size = 0.3
        bracket_offset = 1.8
        glLineWidth(2.0)

        positions = [
            (bracket_offset, bracket_offset),
            (-bracket_offset, bracket_offset),
            (bracket_offset, -bracket_offset),
            (-bracket_offset, -bracket_offset)
        ]

        for px, py in positions:
            glBegin(GL_LINE_STRIP)
            glColor4f(1.0, 0.65, 0.1, 0.6)
            glVertex3f(px, py, 0)
            glVertex3f(px - np.sign(px) * bracket_size, py, 0)
            glEnd()

            glBegin(GL_LINE_STRIP)
            glColor4f(1.0, 0.65, 0.1, 0.6)
            glVertex3f(px, py, 0)
            glVertex3f(px, py - np.sign(py) * bracket_size, 0)
            glEnd()

    def draw_text_placeholder(self):
        pass

    def draw_logo(self):
        pulse = 1.0 + 0.1 * np.sin(self.glow_pulse)

        self.draw_glow_ring(1.3 * pulse, 1.0)

        self.draw_circle(1.25, 80, 3.5, (1.0, 0.85, 0.3, 0.95))

        glPushMatrix()
        glRotatef(self.ring_rotation[0], 0, 0, 1)
        self.draw_tick_marks(1.38, 72, 0.06)
        glPopMatrix()

        glPushMatrix()
        glRotatef(self.ring_rotation[0], 0, 0, 1)
        self.draw_tech_segments(1.5, 24, 0, 0.12)
        glPopMatrix()

        glPushMatrix()
        glRotatef(self.ring_rotation[1], 0, 0, 1)
        self.draw_tech_segments(1.7, 16, np.pi / 16, 0.18)
        glPopMatrix()

        self.draw_circle(1.82, 96, 2.5, (1.0, 0.75, 0.2, 0.7))

        glPushMatrix()
        glRotatef(self.ring_rotation[2], 0, 0, 1)
        self.draw_tick_marks(1.95, 96, 0.08)
        glPopMatrix()

        glPushMatrix()
        glRotatef(-self.ring_rotation[0] * 0.5, 0, 0, 1)
        self.draw_tech_segments(2.1, 20, 0, 0.15)
        glPopMatrix()

        self.draw_radial_lines(0.9, 1.15, 32)

        self.draw_circle(0.85, 64, 3.0, (1.0, 0.8, 0.25, 0.85))

        for i in range(4):
            alpha = 0.4 - i * 0.08
            size = 0.75 - i * 0.15
            self.draw_circle(size, 48, 2.0, (1.0, 0.75, 0.2, alpha))

        self.draw_corner_brackets()

    def update(self, dt):
        self.rotation += 20 * dt
        self.ring_rotation[0] += 15 * dt
        self.ring_rotation[1] -= 25 * dt
        self.ring_rotation[2] += 10 * dt
        self.glow_pulse += 2 * dt

        elapsed_time = time.time() - self.start_time

        if elapsed_time >= self.auto_start_delay and not self.transition_started:
            self.transition_started = True
            self.target_zoom = 15.0

        if self.transition_started:
            zoom_speed = 8.0
            self.zoom += (self.target_zoom - self.zoom) * zoom_speed * dt

            if self.zoom > 12.0:
                self.transition_complete = True

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        z_pos = -3.0 / self.zoom
        glTranslatef(0, 0, z_pos)

        self.draw_logo()

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True

        font = pygame.font.Font(None, 72)
        small_font = pygame.font.Font(None, 36)

        while running:
            dt = clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                    return False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                        return False

            self.update(dt)
            self.render()

            surface = pygame.display.get_surface()

            if not self.transition_started:
                text = font.render("C.O.R.E", True, (255, 165, 0))
                text_rect = text.get_rect(center=(self.width // 2, self.height // 2 + 180))
                surface.blit(text, text_rect)

                elapsed = time.time() - self.start_time
                remaining = max(0, int(self.auto_start_delay - elapsed) + 1)
                subtitle = small_font.render(f"Initializing in {remaining}...", True, (255, 140, 0))
                subtitle_rect = subtitle.get_rect(center=(self.width // 2, self.height // 2 + 230))
                surface.blit(subtitle, subtitle_rect)

            pygame.display.flip()

            if self.transition_complete:
                running = False
                return True

        return False

def main():
    logo = JarvisLogo()
    should_start_orb = logo.run()
    pygame.quit()

    if should_start_orb:
        subprocess.run([sys.executable, "jarvis_orb.py"])

if __name__ == "__main__":
    main()
