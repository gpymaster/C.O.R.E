# -*- coding: utf-8 -*-
import os
import sys
import time
import math
from typing import List

# ANSI color codes for JARVIS blue aesthetic
class Colors:
    BLUE = '\033[94m'
    LIGHT_BLUE = '\033[96m'
    DARK_BLUE = '\033[34m'
    BLACK = '\033[30m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

class JARVISAnimation:
    """Iconic JARVIS-style waveform animation from Iron Man"""

    def __init__(self, width: int = 80, height: int = 20):
        self.width = width
        self.height = height
        self.frame = 0

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')

    def draw_border(self) -> str:
        """Draw a sleek JARVIS-style border"""
        top = Colors.BLUE + "T" + "P" * (self.width - 2) + "W" + Colors.RESET
        bottom = Colors.BLUE + "Z" + "P" * (self.width - 2) + "]" + Colors.RESET
        return top, bottom

    def generate_waveform(self, phase: float) -> List[str]:
        """Generate a waveform with smooth sine wave animation"""
        lines = []

        for y in range(self.height):
            line = ""
            for x in range(self.width - 2):
                # Calculate wave using sine function
                wave_height = (self.height / 2) - 1
                normalized_x = (x - (self.width - 2) / 2) / (self.width / 4)

                # Multiple sine waves for complex pattern
                wave1 = math.sin(normalized_x + phase) * wave_height
                wave2 = math.sin(normalized_x * 0.5 + phase * 1.5) * (wave_height * 0.5)
                wave_value = wave1 + wave2

                # Calculate distance from waveform
                distance = abs(y - (self.height / 2 - 1 + wave_value))

                # Color intensity based on distance from wave
                if distance < 1.5:
                    line += Colors.LIGHT_BLUE + "█" + Colors.RESET
                elif distance < 2.5:
                    line += Colors.BLUE + "▓" + Colors.RESET
                elif distance < 3.5:
                    line += Colors.DARK_BLUE + "░" + Colors.RESET
                else:
                    line += " "

            lines.append(line)

        return lines

    def draw_frequency_bars(self, phase: float) -> str:
        """Draw animated frequency bars at the bottom"""
        bars = ""
        num_bars = 12

        for i in range(num_bars):
            # Create frequency-like animation
            height = int(5 + 3 * abs(math.sin(phase + i * 0.3)))
            bar = Colors.LIGHT_BLUE + "█" * height + Colors.RESET
            bars += bar.ljust(8)

        return bars

    def draw_corner_indicators(self) -> tuple:
        """Draw corner system indicators"""
        phase_cycle = int((self.frame % 20) / 10)
        indicator = Colors.LIGHT_BLUE + "●" + Colors.RESET if phase_cycle == 0 else Colors.DARK_BLUE + "○" + Colors.RESET

        top_left = f"{Colors.DIM}SYS{Colors.RESET} {indicator}"
        top_right = f"{indicator} {Colors.DIM}ACTIVE{Colors.RESET}"

        return top_left, top_right

    def render_frame(self) -> str:
        """Render a single frame of the animation"""
        output = ""
        phase = self.frame * 0.15

        # Draw border
        top_border, bottom_border = self.draw_border()
        output += top_border + "\n"

        # Draw corner indicators
        top_left, top_right = self.draw_corner_indicators()
        padding = self.width - len(top_left) - len(top_right) - 4
        output += Colors.BLUE + "Q" + Colors.RESET + top_left + " " * padding + top_right + Colors.BLUE + "Q" + Colors.RESET + "\n"

        # Draw waveform
        waveform = self.generate_waveform(phase)
        for line in waveform:
            output += Colors.BLUE + "Q" + Colors.RESET + line + Colors.BLUE + "Q" + Colors.RESET + "\n"

        # Draw frequency bars
        bars = self.draw_frequency_bars(phase)
        output += Colors.BLUE + "Q" + Colors.RESET + bars + Colors.BLUE + "Q" + Colors.RESET + "\n"

        # Draw bottom border
        output += bottom_border + "\n"

        # Draw status text
        status = "J.A.R.V.I.S. MONITORING SYSTEM ONLINE"
        status_line = Colors.LIGHT_BLUE + status.center(self.width) + Colors.RESET
        output += status_line + "\n"

        return output

    def animate(self, duration: float = None, fps: int = 30):
        """Run the animation loop"""
        frame_duration = 1 / fps
        start_time = time.time()

        try:
            while True:
                if duration and (time.time() - start_time) > duration:
                    break

                self.clear_screen()
                print(self.render_frame())

                self.frame += 1
                time.sleep(frame_duration)

        except KeyboardInterrupt:
            self.clear_screen()
            print(Colors.LIGHT_BLUE + "System shutting down..." + Colors.RESET)
            sys.exit(0)


def main():
    """Run the JARVIS animation"""
    animation = JARVISAnimation(width=80, height=15)
    animation.animate()


if __name__ == "__main__":
    main()
