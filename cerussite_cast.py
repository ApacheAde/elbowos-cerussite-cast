#!/usr/bin/env python3
"""Cerussite Cast — neon foundry-pour arcade for ElbowOS. Python 3 + pygame."""
import math, os, random, subprocess, sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/workspace/artifacts/CERUSSITE_CAST_ElbowOS.mp4")
CX = W // 2
INK, COPPER, TEAL = (18, 10, 12), (255, 154, 72), (46, 214, 196)
MOLT, CREAM, ROSE = (255, 214, 120), (255, 246, 220), (255, 92, 128)
VIOLET, GOLD = (176, 112, 255), (255, 208, 64)

class Mold:
    def __init__(self, x, kind):
        self.x, self.kind, self.fill, self.done, self.pop = x, kind, 0.0, False, 0
        self.w = (168, 228, 300)[kind]
        self.need = (1.0, 1.35, 1.7)[kind]
        self.col = ((72, 220, 206), (255, 176, 72), (186, 120, 255))[kind]

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            self.screen = pygame.Surface((W, H))
        self.surf = self.screen
        self.font = pygame.font.SysFont("dejavusans", 64, bold=True)
        self.mid = pygame.font.SysFont("dejavusans", 36, bold=True)
        self.small = pygame.font.SysFont("dejavusans", 28, bold=True)
        self.reset()

    def reset(self):
        self.t = 0
        self.nozzle = 540.0
        self.score = 0
        self.combo = 0
        self.spill = 0.0
        self.sparks = []
        self.molds = [Mold(180 + i * 340, i % 3) for i in range(4)]
        self.pour = True
        self.flash = 0

    def spawn_spark(self, x, y, col, n=8):
        for _ in range(n):
            a = random.random() * math.tau
            s = random.uniform(2, 9)
            self.sparks.append([x, y, math.cos(a) * s, math.sin(a) * s - 2, col, 18])

    def update(self, left, right, dump):
        self.t += 1
        self.pour = dump
        self.nozzle += (8.5 if right else 0) - (8.5 if left else 0)
        self.nozzle = max(120, min(W - 120, self.nozzle))
        hit = None
        for m in self.molds:
            m.x += 3.4
            if m.x > W + 180:
                m.x = -200
                m.fill, m.done, m.pop, m.kind = 0.0, False, 0, random.randrange(3)
                m.w = (168, 228, 300)[m.kind]
                m.need = (1.0, 1.35, 1.7)[m.kind]
                m.col = ((72, 220, 206), (255, 176, 72), (186, 120, 255))[m.kind]
            if m.pop:
                m.pop -= 1
            bay = 980 < m.x < W - 80 and abs((m.x + m.w / 2) - self.nozzle) < m.w * 0.46
            if self.pour and bay and not m.done:
                m.fill += 0.018
                if random.random() < 0.45:
                    self.spawn_spark(self.nozzle, 1240 - m.fill * 90, m.col, 2)
                if m.fill >= m.need:
                    m.done = True
                    m.pop = 16
                    self.combo += 1
                    self.score += 120 + 40 * self.combo + m.kind * 30
                    self.flash = 8
                    self.spawn_spark(m.x + m.w / 2, 1180, CREAM, 16)
                hit = m
        if self.pour and hit is None:
            self.spill = min(1, self.spill + 0.01)
            self.combo = 0
            if random.random() < 0.3:
                self.spawn_spark(self.nozzle, 1320, ROSE, 1)
        else:
            self.spill = max(0, self.spill - 0.004)
        if self.flash:
            self.flash -= 1
        alive = []
        for s in self.sparks:
            s[0] += s[2]
            s[1] += s[3]
            s[3] += 0.18
            s[5] -= 1
            if s[5] > 0:
                alive.append(s)
        self.sparks = alive

    def auto(self):
        best, bd = None, 1e9
        for m in self.molds:
            if m.done:
                continue
            cx = m.x + m.w / 2
            if cx < 40 or cx > W - 40:
                continue
            d = abs(cx - self.nozzle) + max(0, 900 - m.x) * 0.15
            if d < bd:
                bd, best = d, m
        left = right = False
        if best:
            cx = best.x + best.w / 2
            left, right = cx < self.nozzle - 10, cx > self.nozzle + 10
        return left, right, True

    def draw_bg(self):
        self.surf.fill(INK)
        for i in range(18):
            y = 220 + i * 78
            c = 28 + (i % 3) * 6
            pygame.draw.line(self.surf, (c, 14, 18), (0, y), (W, y + 20), 2)
        glow = pygame.Surface((W, 420), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (255, 120, 40, 50), (self.nozzle - 220, 200, 440, 360))
        self.surf.blit(glow, (0, 180))
        pygame.draw.rect(self.surf, (42, 24, 22), (0, 1360, W, 220))
        for i in range(14):
            x = (i * 90 + self.t * 4) % (W + 90) - 45
            pygame.draw.rect(self.surf, (70, 42, 32), (x, 1410, 54, 18), border_radius=4)

    def draw_mold(self, m):
        y = 1125
        h = 210
        pygame.draw.rect(self.surf, (32, 48, 52), (m.x - 8, y - 8, m.w + 16, h + 16), border_radius=16)
        pygame.draw.rect(self.surf, (18, 28, 32), (m.x, y, m.w, h), border_radius=12)
        fh = int(min(1, m.fill / m.need) * (h - 16))
        if fh > 4:
            pygame.draw.rect(self.surf, m.col, (m.x + 8, y + h - 8 - fh, m.w - 16, fh), border_radius=8)
            pygame.draw.rect(self.surf, CREAM, (m.x + 8, y + h - 12 - fh, m.w - 16, 8), border_radius=4)
        pygame.draw.rect(self.surf, COPPER, (m.x, y, m.w, h), 4, border_radius=12)
        if m.pop:
            pygame.draw.circle(self.surf, GOLD, (int(m.x + m.w / 2), y + 40), 18 + m.pop)

    def draw_stream(self):
        x = self.nozzle
        pygame.draw.polygon(self.surf, (90, 54, 40), [(x - 70, 250), (x + 70, 250), (x + 36, 330), (x - 36, 330)])
        pygame.draw.circle(self.surf, COPPER, (int(x), 318), 28)
        if not self.pour:
            return
        end = 1320
        for m in self.molds:
            if 980 < m.x < W - 80 and abs((m.x + m.w / 2) - x) < m.w * 0.46 and not m.done:
                end = 1125 + 210 - int(min(1, m.fill / m.need) * 194)
                break
        pts = []
        for i in range(16):
            t = i / 15
            yy = 330 + (end - 330) * t
            wob = math.sin(self.t * 0.4 + i) * (6 + 10 * t)
            pts.append((x + wob, yy))
        pygame.draw.lines(self.surf, (255, 120, 40), False, pts, 22)
        pygame.draw.lines(self.surf, MOLT, False, pts, 12)
        pygame.draw.lines(self.surf, CREAM, False, pts, 4)
        pygame.draw.circle(self.surf, CREAM, (int(pts[-1][0]), int(pts[-1][1])), 12)

    def draw(self):
        self.draw_bg()
        for m in self.molds:
            if -40 < m.x < W + 40:
                self.draw_mold(m)
        self.draw_stream()
        for s in self.sparks:
            pygame.draw.circle(self.surf, s[4], (int(s[0]), int(s[1])), max(1, s[5] // 5))
        bar = pygame.Surface((W, 200), pygame.SRCALPHA)
        bar.fill((10, 6, 10, 170))
        self.surf.blit(bar, (0, 0))
        title = self.font.render("CERUSSITE CAST", True, COPPER)
        self.surf.blit(title, title.get_rect(center=(CX, 70)))
        sub = self.small.render("FOUNDRY POUR", True, TEAL)
        self.surf.blit(sub, sub.get_rect(center=(CX, 124)))
        sc = self.mid.render(f"SCORE  {self.score}", True, CREAM if not self.flash else GOLD)
        self.surf.blit(sc, sc.get_rect(center=(CX, 172)))
        foot = pygame.Surface((W, 140), pygame.SRCALPHA)
        foot.fill((10, 6, 10, 180))
        self.surf.blit(foot, (0, H - 140))
        tag = self.mid.render("x.com/ElbowOS", True, TEAL)
        self.surf.blit(tag, tag.get_rect(center=(CX, H - 78)))
        hint = self.small.render("SLIDE THE LADLE  ·  FILL THE MOLDS", True, (220, 180, 160))
        self.surf.blit(hint, hint.get_rect(center=(CX, H - 32)))
        if self.spill > 0.04:
            pygame.draw.rect(self.surf, ROSE, (140, 200, int(800 * self.spill), 10), border_radius=4)

    def record(self):
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
               "-r", str(FPS), "-i", "pipe:0", "-c:v", "libx264", "-pix_fmt", "yuv420p",
               "-crf", "20", "-movflags", "+faststart", "-an", OUT]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        frames = FPS * SECS
        try:
            for _ in range(frames):
                left, right, dump = self.auto()
                self.update(left, right, dump)
                self.draw()
                proc.stdin.write(pygame.image.tobytes(self.surf, "RGB"))
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1200:]}")
        print("wrote", OUT)
        pygame.quit()

    def play_interactive(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            left = right = False
            dump = False
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                    self.reset()
            keys = pygame.key.get_pressed()
            left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            dump = keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]
            self.update(left, right, dump)
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()

def main():
    g = Game()
    if PLAY and not RECORD:
        g.play_interactive()
    else:
        g.record()

if __name__ == "__main__":
    main()
