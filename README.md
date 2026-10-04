# Cerussite Cast

Full-colour Python 3 neon foundry-pour arcade for ElbowOS.

Slide a ladle and pour molten cerussite into teal, copper, and violet molds riding a belt. Fill a mold to cast it. Pour outside a mold and the streak breaks.

Left / Right (or A / D) slide the ladle. Space / W / Up pours. R restarts.

## Play

```bash
pip install -r requirements.txt
python3 cerussite_cast.py --play
```

## Record a 9:16 reel

```bash
python3 cerussite_cast.py --record
```

Writes a 1080x1920 h264 clip (15s @ 30fps, yuv420p, CRF 20, +faststart) with title, score, and `x.com/ElbowOS` burned into the frames.

- Featured account: https://x.com/ElbowOS
- Drive reel: https://drive.google.com/file/d/1YY-RR9Xe_Avp0s4DVVcQJfYtFVuBg3VR/view

Not a Nintendo ROM and not an emulator. Original foundry rules and art.
