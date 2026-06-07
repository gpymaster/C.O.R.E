import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import threading
import time
import math
import os
from collections import deque
import random

is_speaking = False
current_amplitude = 0.0
amplitude_history = deque(maxlen=30)

class AudioAnalyzer:
    def __init__(self):
        self.amplitude = 0.0
        self.smoothed_amplitude = 0.0
        self.smooth_factor = 0.2
        self.running = False
        self.beat_threshold = 0.6
        self.last_beat_time = 0

    def start_monitoring(self):
        self.running = True
        thread = threading.Thread(target=self._monitor_loop, daemon=True)
        thread.start()

    def _monitor_loop(self):
        global current_amplitude, is_speaking, amplitude_history
        while self.running:
            if is_speaking and pygame.mixer.music.get_busy():
                vol = pygame.mixer.music.get_volume()
                raw_amp = min(1.0, vol * np.random.uniform(0.7, 1.0))

                noise = np.random.uniform(0.3, 0.9)
                self.amplitude = raw_amp * noise
                current_amplitude = self.amplitude
                amplitude_history.append(self.amplitude)

                if self.amplitude > self.beat_threshold:
                    self.last_beat_time = time.time()
            else:
                self.amplitude = 0.0
                current_amplitude = 0.0
                amplitude_history.append(0.0)

            self.smoothed_amplitude += (self.amplitude - self.smoothed_amplitude) * self.smooth_factor
            time.sleep(0.016)

    def get_amplitude(self):
        return self.smoothed_amplitude

    def is_beat(self):
        return (time.time() - self.last_beat_time) < 0.1

class Particle:
    def __init__(self):
        self.reset()

    def reset(self):
        self.theta = np.random.uniform(0, np.pi)
        self.phi = np.random.uniform(0, 2 * np.pi)
        self.speed = np.random.uniform(0.01, 0.04)
        self.life = 1.0
        self.decay = np.random.uniform(0.008, 0.02)
        self.radius = np.random.uniform(0.3, 0.8)
        self.size = np.random.uniform(1.5, 3.5)
        self.spiral = np.random.choice([True, False])
        self.spiral_speed = np.random.uniform(0.05, 0.15)

    def update(self, boost=1.0):
        self.radius += self.speed * boost
        if self.spiral:
            self.phi += self.spiral_speed
        self.life -= self.decay
        if self.life <= 0 or self.radius > 4.0:
            self.reset()

    def get_position(self):
        x = self.radius * np.sin(self.theta) * np.cos(self.phi)
        y = self.radius * np.sin(self.theta) * np.sin(self.phi)
        z = self.radius * np.cos(self.theta)
        return x, y, z

class JarvisOrb:
    def __init__(self, audio_analyzer):
        pygame.init()
        pygame.mixer.init()

        self.width, self.height = 900, 900
        self.display = pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("JARVIS Interface")

        self.audio = audio_analyzer
        self.rotation = 0.0
        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.rotation_z = 0.0
        self.camera_angle = 0.0
        self.pulse = 1.0
        self.glow_intensity = 0.3
        self.ring_rotation = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.ring_speeds = [0.5, -0.7, 0.9, -1.1, 0.6, -0.8]
        self.particles = [Particle() for _ in range(500)]
        self.energy_burst = 0.0
        self.vertex_noise = []
        for _ in range(100):
            self.vertex_noise.append(np.random.uniform(-0.05, 0.05))

        self.arc_segments = []
        for _ in range(50):
            self.arc_segments.append({
                'angle': np.random.uniform(0, 2 * np.pi),
                'tilt': np.random.uniform(0, 180),
                'speed': np.random.uniform(0.2, 0.8),
                'radius': np.random.uniform(1.2, 2.5),
                'phase': np.random.uniform(0, 2 * np.pi)
            })

        self.setup_gl()

    def setup_gl(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_POINT_SMOOTH)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

        glMatrixMode(GL_PROJECTION)
        gluPerspective(50, (self.width / self.height), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)

    def draw_sphere(self, radius, slices=32, stacks=32, color=(1.0, 0.65, 0.0, 0.15)):
        glColor4f(*color)
        quadric = gluNewQuadric()
        gluQuadricDrawStyle(quadric, GLU_FILL)
        gluSphere(quadric, radius, slices, stacks)
        gluDeleteQuadric(quadric)

    def draw_ring(self, radius, segments=64, thickness=0.03, color=(1.0, 0.75, 0.0, 0.6)):
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glColor4f(*color)
        for i in range(segments):
            theta = 2.0 * np.pi * i / segments
            x = radius * np.cos(theta)
            y = radius * np.sin(theta)
            glVertex3f(x, y, 0)
        glEnd()

    def draw_ring_3d(self, radius, tilt_x=0, tilt_y=0, tilt_z=0, segments=64, color=(1.0, 0.75, 0.0, 0.5)):
        glPushMatrix()
        glRotatef(tilt_x, 1, 0, 0)
        glRotatef(tilt_y, 0, 1, 0)
        glRotatef(tilt_z, 0, 0, 1)
        self.draw_ring(radius, segments, color=color)
        glPopMatrix()

    def draw_particles(self):
        for size in [4.0, 3.0, 2.0, 1.0]:
            glPointSize(size)
            glBegin(GL_POINTS)
            for p in self.particles:
                if abs(p.size - size) < 1.2:
                    x, y, z = p.get_position()
                    alpha = p.life * 1.0
                    brightness = 0.8 + p.life * 0.2

                    if p.radius < 1.0:
                        glColor4f(1.0, 1.0, 0.9, alpha * 1.2)
                    elif p.radius < 2.0:
                        glColor4f(1.0, 0.85, 0.4, alpha)
                    else:
                        glColor4f(1.0 * brightness, 0.6 * brightness, 0.15, alpha * 0.6)

                    glVertex3f(x, y, z)
            glEnd()

    def draw_energy_trails(self):
        glLineWidth(1.5)
        for i in range(0, len(self.particles), 2):
            p = self.particles[i]
            if p.life > 0.6:
                x, y, z = p.get_position()
                glBegin(GL_LINES)
                glColor4f(1.0, 0.9, 0.5, p.life * 0.6)
                glVertex3f(0, 0, 0)
                glColor4f(1.0, 0.7, 0.2, 0.0)
                glVertex3f(x, y, z)
                glEnd()

    def draw_arc_segments(self):
        glLineWidth(2.0)
        for arc in self.arc_segments:
            angle = arc['angle'] + self.rotation * arc['speed']
            tilt = arc['tilt']
            radius = arc['radius'] * self.pulse
            phase = arc['phase'] + time.time() * arc['speed']

            glPushMatrix()
            glRotatef(np.degrees(angle), 0, 1, 0)
            glRotatef(tilt, 1, 0, 0)

            glBegin(GL_LINE_STRIP)
            segments = 32
            arc_length = np.random.uniform(0.3, 0.8)
            for i in range(segments):
                t = i / segments
                if t > arc_length:
                    break
                theta = t * np.pi * 2

                wave = np.sin(theta * 3 + phase) * 0.1
                r = radius + wave
                x = r * np.cos(theta)
                y = r * np.sin(theta)

                alpha = (1.0 - t / arc_length) * 0.7
                brightness = 0.8 + np.sin(phase + t * 5) * 0.2
                glColor4f(1.0, 0.7 * brightness, 0.1, alpha)
                glVertex3f(x, y, 0)
            glEnd()
            glPopMatrix()

    def draw_glow_layers(self, intensity):
        for i in range(12):
            alpha = intensity * 0.035 * (12 - i)
            size = self.pulse * (1.0 + i * 0.12)
            color_shift = i * 0.02

            if i < 4:
                self.draw_sphere(size, 24, 24, (1.0, 0.95 - color_shift, 0.7 - color_shift * 2, alpha * 1.5))
            elif i < 8:
                self.draw_sphere(size, 20, 20, (1.0, 0.8 - color_shift, 0.3 - color_shift * 2, alpha))
            else:
                self.draw_sphere(size, 18, 18, (1.0, 0.6 - color_shift, 0.1, alpha * 0.7))

        if self.energy_burst > 0:
            burst_size = self.pulse * (1.0 + self.energy_burst * 0.5)
            self.draw_sphere(burst_size, 28, 28, (1.0, 0.95, 0.8, self.energy_burst * 0.4))

    def draw_geometric_patterns(self):
        ring_configs = [
            (0, 1.4, 0, 0, 0, (1.0, 0.85, 0.3, 0.9)),
            (1, 1.7, 60, 0, 0, (1.0, 0.8, 0.25, 0.85)),
            (2, 2.0, 0, 60, 0, (1.0, 0.75, 0.2, 0.8)),
            (3, 2.3, 45, 45, 0, (1.0, 0.7, 0.15, 0.7)),
            (4, 2.6, 30, 60, 45, (1.0, 0.65, 0.1, 0.6)),
            (5, 2.9, 75, 30, 60, (1.0, 0.6, 0.08, 0.5)),
        ]

        for idx, radius, tilt_x, tilt_y, tilt_z, color in ring_configs:
            glPushMatrix()
            glRotatef(self.ring_rotation[idx], 1 if idx % 2 == 0 else 0.5,
                     1 if idx % 3 == 0 else 0.5,
                     1 if idx % 2 == 1 else 0.5)

            glLineWidth(2.5)
            self.draw_ring_3d(radius, tilt_x, tilt_y, tilt_z, 80, color)
            glPopMatrix()

    def draw_outer_connections(self):
        glLineWidth(1.5)
        num_radial = 24
        for i in range(num_radial):
            angle = (2 * np.pi * i) / num_radial
            glPushMatrix()
            glRotatef(np.degrees(angle), 0, 1, 0)
            glRotatef(np.sin(time.time() + i * 0.5) * 10, 0, 0, 1)

            glBegin(GL_LINE_STRIP)
            segments = 15
            for j in range(segments):
                t = j / segments
                r = self.pulse * 1.5 + t * 1.5
                z = np.sin(t * np.pi * 2 + time.time()) * 0.2
                alpha = (1.0 - t) * 0.5

                glColor4f(1.0, 0.7, 0.15, alpha)
                glVertex3f(r, 0, z)
            glEnd()
            glPopMatrix()

    def draw_cross_connections(self):
        glLineWidth(1.2)
        num_connections = 32
        for i in range(num_connections):
            angle1 = (2 * np.pi * i) / num_connections
            angle2 = (2 * np.pi * (i + 8)) / num_connections

            r1 = 2.2 * self.pulse
            r2 = 2.5 * self.pulse

            x1 = r1 * np.cos(angle1 + self.rotation * 0.5)
            y1 = r1 * np.sin(angle1 + self.rotation * 0.5)
            x2 = r2 * np.cos(angle2 - self.rotation * 0.5)
            y2 = r2 * np.sin(angle2 - self.rotation * 0.5)

            glBegin(GL_LINES)
            glColor4f(1.0, 0.65, 0.1, 0.25)
            glVertex3f(x1, y1, 0.1)
            glColor4f(1.0, 0.6, 0.08, 0.1)
            glVertex3f(x2, y2, -0.1)
            glEnd()

    def draw_core_details(self):
        glLineWidth(2.0)
        num_meridians = 20
        for i in range(num_meridians):
            angle = (2 * np.pi * i) / num_meridians
            glPushMatrix()
            glRotatef(np.degrees(angle), 0, 1, 0)
            glBegin(GL_LINE_STRIP)
            segments = 64
            for j in range(segments + 1):
                theta = np.pi * j / segments - np.pi / 2
                noise = self.vertex_noise[j % len(self.vertex_noise)]
                radius_mod = self.pulse * 0.9 + noise
                x = radius_mod * np.cos(theta)
                z = radius_mod * np.sin(theta)

                t = j / segments
                alpha = 0.5 * (1.0 - abs(t - 0.5) * 2)
                glColor4f(1.0, 0.85, 0.4, alpha)
                glVertex3f(x, 0, z)
            glEnd()
            glPopMatrix()

        for i in range(num_meridians):
            angle = (2 * np.pi * i) / num_meridians
            glPushMatrix()
            glRotatef(np.degrees(angle), 1, 0, 0)
            glBegin(GL_LINE_STRIP)
            segments = 64
            for j in range(segments + 1):
                theta = np.pi * j / segments - np.pi / 2
                noise = self.vertex_noise[(j + 50) % len(self.vertex_noise)]
                radius_mod = self.pulse * 0.9 + noise
                y = radius_mod * np.cos(theta)
                z = radius_mod * np.sin(theta)

                t = j / segments
                alpha = 0.45 * (1.0 - abs(t - 0.5) * 2)
                glColor4f(1.0, 0.75, 0.2, alpha)
                glVertex3f(0, y, z)
            glEnd()
            glPopMatrix()

    def draw_hexagonal_grid(self):
        glLineWidth(1.0)
        grid_radius = self.pulse * 1.1

        for z_offset in [-0.3, 0, 0.3]:
            for layer in range(3):
                radius = grid_radius + layer * 0.2
                segments = 6
                glBegin(GL_LINE_LOOP)
                alpha = (0.3 - layer * 0.08) * (1.0 - abs(z_offset) * 0.5)
                glColor4f(1.0, 0.75, 0.2, alpha)
                for i in range(segments):
                    angle = (2 * np.pi * i) / segments
                    x = radius * np.cos(angle)
                    y = radius * np.sin(angle)
                    glVertex3f(x, y, z_offset)
                glEnd()

                if z_offset == 0:
                    for i in range(segments):
                        angle = (2 * np.pi * i) / segments
                        x = radius * np.cos(angle)
                        y = radius * np.sin(angle)
                        glBegin(GL_LINES)
                        glColor4f(1.0, 0.7, 0.15, 0.25 - layer * 0.06)
                        glVertex3f(0, 0, 0)
                        glVertex3f(x, y, 0)
                        glEnd()

    def draw_data_streams(self):
        glLineWidth(1.5)
        num_streams = 16
        for i in range(num_streams):
            angle = (2 * np.pi * i) / num_streams
            glPushMatrix()
            glRotatef(np.degrees(angle), 0, 1, 0)
            glRotatef(np.sin(time.time() + i) * 15, 1, 0, 0)

            glBegin(GL_LINE_STRIP)
            segments = 30
            for j in range(segments):
                t = j / segments
                r = self.pulse * 1.3 + t * 1.8
                y = (t - 0.5) * 2.5
                offset = np.sin(t * np.pi * 6 + time.time() * 3 + i) * 0.15
                alpha = (1.0 - t) * 0.55

                brightness = 0.9 + np.sin(time.time() * 2 + i + t * 10) * 0.1
                glColor4f(1.0, 0.75 * brightness, 0.15, alpha)
                glVertex3f(r + offset, y, 0)
            glEnd()
            glPopMatrix()

    def update(self, dt):
        global is_speaking, amplitude_history

        amplitude = self.audio.get_amplitude()
        is_beat = self.audio.is_beat()

        if is_speaking:
            target_pulse = 1.0 + amplitude * 0.25
            if is_beat:
                target_pulse += 0.15
                self.energy_burst = min(1.0, self.energy_burst + 0.4)

            target_glow = 0.9 + amplitude * 0.3
            target_speeds = [
                1.8 + amplitude * 3,
                -2.5 - amplitude * 3,
                3.0 + amplitude * 3.5,
                -2.2 - amplitude * 2.8,
                1.6 + amplitude * 2.5,
                -1.9 - amplitude * 2.2
            ]

            particle_boost = 1.0 + amplitude * 2.0
        else:
            breath = 0.08 * np.sin(time.time() * 1.5)
            target_pulse = 1.0 + breath
            target_glow = 0.35
            target_speeds = [0.5, -0.7, 0.9, -1.1, 0.6, -0.8]
            particle_boost = 1.0

        self.pulse += (target_pulse - self.pulse) * 0.2
        self.glow_intensity += (target_glow - self.glow_intensity) * 0.12
        self.energy_burst *= 0.90

        for i in range(len(self.ring_speeds)):
            self.ring_speeds[i] += (target_speeds[i] - self.ring_speeds[i]) * 0.08
            self.ring_rotation[i] += self.ring_speeds[i] * dt

        for i, p in enumerate(self.particles):
            boost = particle_boost if i % 2 == 0 else particle_boost * 0.7
            p.update(boost)

        self.rotation += 0.3 * dt
        self.rotation_x += 0.15 * dt
        self.rotation_y += 0.25 * dt
        self.rotation_z += 0.1 * dt
        self.camera_angle += 0.05 * dt

        for i in range(len(self.vertex_noise)):
            self.vertex_noise[i] += np.random.uniform(-0.01, 0.01)
            self.vertex_noise[i] = np.clip(self.vertex_noise[i], -0.1, 0.1)

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        camera_x = np.sin(self.camera_angle) * 0.5
        camera_y = np.cos(self.camera_angle * 0.7) * 0.3
        glTranslatef(camera_x, camera_y, -7)

        glRotatef(15 + np.sin(self.camera_angle) * 5, 1, 0, 0)
        glRotatef(self.rotation_y * 20, 0, 1, 0)
        glRotatef(np.sin(self.rotation_z) * 3, 0, 0, 1)

        self.draw_glow_layers(self.glow_intensity)

        glPushMatrix()
        glRotatef(self.rotation * 15, 0, 0, 1)
        self.draw_hexagonal_grid()
        glPopMatrix()

        self.draw_data_streams()
        self.draw_arc_segments()
        self.draw_outer_connections()
        self.draw_cross_connections()
        self.draw_energy_trails()
        self.draw_geometric_patterns()
        self.draw_particles()
        self.draw_core_details()

        self.draw_sphere(self.pulse * 0.7, 36, 36, (1.0, 0.95, 0.7, 0.4))
        self.draw_sphere(self.pulse * 0.55, 32, 32, (1.0, 0.9, 0.5, 0.5))
        self.draw_sphere(self.pulse * 0.4, 28, 28, (1.0, 0.8, 0.3, 0.6))
        self.draw_sphere(self.pulse * 0.25, 24, 24, (1.0, 0.7, 0.15, 0.7))

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            dt = clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False

            self.update(dt)
            self.render()

        pygame.quit()

def speak(text, audio_file="output.mp3"):
    global is_speaking

    if not os.path.exists(audio_file):
        print(f"Audio file {audio_file} not found")
        return

    try:
        pygame.mixer.music.load(audio_file)
        is_speaking = True
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        is_speaking = False

    except Exception as e:
        print(f"Error playing audio: {e}")
        is_speaking = False

def main():
    audio_analyzer = AudioAnalyzer()
    audio_analyzer.start_monitoring()

    orb = JarvisOrb(audio_analyzer)

    def test_speech():
        time.sleep(2)
        speak("Initializing JARVIS interface", "output.mp3")

    speech_thread = threading.Thread(target=test_speech, daemon=True)
    speech_thread.start()

    orb.run()

if __name__ == "__main__":
    main()
