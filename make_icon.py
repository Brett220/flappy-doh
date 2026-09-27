import zlib, struct, math

def smooth(d, px):  # coverage from signed distance (negative = inside)
    return max(0.0, min(1.0, 0.5 - d / px))

def rr_sdf(x, y, cx, cy, hw, hh, r):
    qx, qy = abs(x - cx) - hw + r, abs(y - cy) - hh + r
    return math.hypot(max(qx, 0), max(qy, 0)) + min(max(qx, qy), 0) - r

def ell_sdf(x, y, cx, cy, rx, ry):
    return (math.hypot((x - cx) / rx, (y - cy) / ry) - 1) * min(rx, ry)

def hexc(h): return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))

def render(N):
    px = 1.0 / N
    out = bytearray()
    ink = hexc('#2a1f33')
    for j in range(N):
        out.append(0)
        for i in range(N):
            x, y = (i + 0.5) / N, (j + 0.5) / N
            # sky gradient
            t = y
            c = [126 + (217 - 126) * t, 200 + (241 - 200) * t, 240 + (255 - 240) * t]
            def over(col, a):
                for k in range(3): c[k] = c[k] * (1 - a) + col[k] * a
            # ground
            over(hexc('#7fd36a'), smooth(0.82 - y, px))
            over(hexc('#f5d58a'), smooth(0.86 - y, px))
            # cube body with outline
            d = rr_sdf(x, y, 0.5, 0.47, 0.29, 0.29, 0.12)
            over(ink, smooth(d - 0.018, px))
            g = (x + y) / 2
            body = (238 + (95 - 238) * g, 250 + (185 - 250) * g, 255 + (234 - 255) * g)
            over(body, smooth(d + 0.018, px))
            # highlight
            over((255, 255, 255), 0.6 * smooth(rr_sdf(x, y, 0.4, 0.28, 0.1, 0.035, 0.03), px))
            # eyes
            for s in (-1, 1):
                over(ink, smooth(ell_sdf(x, y, 0.5 + s * 0.1, 0.44, 0.04, 0.05), px))
                over((255, 255, 255), smooth(ell_sdf(x, y, 0.5 + s * 0.1 + 0.014, 0.425, 0.016, 0.016), px))
                over((255, 100, 150), 0.45 * smooth(ell_sdf(x, y, 0.5 + s * 0.175, 0.52, 0.04, 0.022), px))
            # smile
            dd = abs(math.hypot(x - 0.5, y - 0.5) - 0.04) - 0.009
            if y > 0.505: over(ink, smooth(dd, px))
            out += bytes(int(v) for v in c)
    return out

def png(N, path):
    raw = render(N)
    def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    data = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', N, N, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b'')
    open(path, 'wb').write(data)

png(180, 'icon-180.png')
png(512, 'icon-512.png')
