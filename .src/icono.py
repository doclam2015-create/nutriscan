#!/usr/bin/env python3
"""Icono de NutriScan: una hoja recortada sobre barras de codigo.

La idea es que el icono diga lo que hace la app sin texto: las barras
son el escaneo, la hoja es el alimento. Se dibuja a 1024 y se reduce,
que es lo unico que se ve nitido en la retina del telefono.
"""
import math
from PIL import Image, ImageDraw, ImageFilter

S = 1024                      # lienzo maestro
UBAR = 19.0                   # unidad de barra: S/UBAR
CX, CY = S / 2, S / 2

FONDO_A = (10, 15, 22)        # casi negro azulado, el de la app
FONDO_B = (17, 34, 32)        # verde muy apagado hacia abajo
VERDE_A = (134, 239, 172)     # punta clara
VERDE_B = (22, 163, 74)       # base profunda


def lerp(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def fondo():
    """Degradado vertical suave, mas un halo verde detras de la hoja."""
    im = Image.new("RGB", (S, S))
    px = im.load()
    for y in range(S):
        c = lerp(FONDO_A, FONDO_B, (y / S) ** 1.3)
        for x in range(S):
            px[x, y] = c

    halo = Image.new("L", (S, S), 0)
    ImageDraw.Draw(halo).ellipse(
        [CX - S * 0.38, CY - S * 0.38, CX + S * 0.38, CY + S * 0.38], fill=105
    )
    halo = halo.filter(ImageFilter.GaussianBlur(S * 0.11))
    im.paste(Image.new("RGB", (S, S), (16, 92, 60)), (0, 0), halo)
    return im


def hoja_mascara(largo, ancho, giro, centro, sup=4):
    """Hoja = interseccion de dos circunferencias (vesica), girada.

    Cada arco pasa por las dos puntas con flecha W/2, asi que su radio es
    r = h/2 + L^2/(8h). El circulo se dibuja con su bbox real (2r de lado);
    usar el ancho de la hoja como bbox daba una elipse achatada y por eso
    antes salian los lados rectos.
    """
    L, W = float(largo), float(ancho)
    h = W / 2.0
    r = h / 2.0 + (L * L) / (8.0 * h)
    lienzo = int(math.hypot(L, W)) + 40

    def arco(signo):
        m = Image.new("L", (lienzo * sup, lienzo * sup), 0)
        cx, cy = lienzo / 2.0, lienzo / 2.0
        # centro del circulo, desplazado al lado contrario del arco
        oy = cy + signo * (r - h)
        bb = [(cx - r) * sup, (oy - r) * sup, (cx + r) * sup, (oy + r) * sup]
        ImageDraw.Draw(m).ellipse(bb, fill=255)
        return m

    m = Image.composite(arco(+1), Image.new("L", (lienzo * sup, lienzo * sup), 0), arco(-1))
    m = m.resize((lienzo, lienzo), Image.LANCZOS)          # bordes suaves
    m = m.rotate(giro, resample=Image.BICUBIC, center=(lienzo / 2, lienzo / 2))
    out = Image.new("L", (S, S), 0)
    out.paste(m, (int(centro[0] - lienzo / 2), int(centro[1] - lienzo / 2)))
    return out


def barras(giro=0):
    """Barras de anchos irregulares; giradas hacen de nervaduras."""
    D = int(S * 1.6)
    im = Image.new("L", (D, D), 0)
    d = ImageDraw.Draw(im)
    anchos = [3, 1, 2, 1, 4, 1, 2, 3, 1, 1, 3, 2, 1, 4, 1, 2, 1, 3, 2, 1,
              1, 3, 1, 2, 4, 1, 2, 1, 3, 1, 2, 2, 1, 3, 1, 4, 2, 1, 1, 3]
    u = S / UBAR
    x, i, tinta = 0.0, 0, True
    while x < D:
        w = anchos[i % len(anchos)] * u
        if tinta:
            d.rectangle([x, 0, x + w, D], fill=255)
        x += w
        tinta = not tinta
        i += 1
    if giro:
        im = im.rotate(giro, resample=Image.BICUBIC, center=(D / 2, D / 2))
    return im.crop(((D - S) // 2, (D - S) // 2, (D - S) // 2 + S, (D - S) // 2 + S))


def degradado_verde():
    im = Image.new("RGB", (S, S))
    px = im.load()
    for y in range(S):
        for x in range(S):
            # diagonal: claro arriba-derecha, profundo abajo-izquierda
            t = ((x / S) * 0.45 + (1 - y / S) * 0.55)
            px[x, y] = lerp(VERDE_B, VERDE_A, min(1, max(0, t)))
    return im


def construir():
    im = fondo()

    largo, ancho, giro = S * 0.80, S * 0.42, -40
    hoja = hoja_mascara(largo, ancho, giro, (CX, CY + S * 0.012))

    g = math.radians(giro)
    dx, dy = math.cos(g) * largo / 2, -math.sin(g) * largo / 2

    # el nervio central parte la hoja: se resta una banda fina girada
    nervio = Image.new("L", (S, S), 0)
    nd = ImageDraw.Draw(nervio)
    nd.line([CX - dx, CY + S * 0.012 - dy, CX + dx, CY + S * 0.012 + dy],
            fill=255, width=int(S * 0.017))
    hoja = Image.composite(Image.new("L", (S, S), 0), hoja, nervio)

    # tallo: sin el, la hoja se lee como un balon
    tallo = Image.new("L", (S, S), 0)
    td = ImageDraw.Draw(tallo)
    px, py = CX - dx, CY + S * 0.012 - dy          # punta de abajo-izquierda
    td.line([px, py, px - math.cos(g) * S * 0.15, py + math.sin(g) * S * 0.15],
            fill=255, width=int(S * 0.055))
    td.ellipse([px - S * .027, py - S * .027, px + S * .027, py + S * .027], fill=255)

    # hoja rellena de barras, mas el tallo macizo
    relleno = Image.composite(barras(giro), Image.new("L", (S, S), 0), hoja)
    relleno = Image.composite(Image.new("L", (S, S), 255), relleno, tallo)
    im.paste(degradado_verde(), (0, 0), relleno)

    # brillo tenue en el borde superior de la hoja, para que no se vea plana
    borde = hoja.filter(ImageFilter.MaxFilter(9))
    borde = Image.composite(borde, Image.new("L", (S, S), 0),
                            Image.eval(hoja, lambda v: 255 - v))
    im.paste(Image.new("RGB", (S, S), (190, 255, 215)),
             (0, 0), Image.eval(borde, lambda v: int(v * 0.16)))
    return im


if __name__ == "__main__":
    base = construir()
    base.resize((512, 512), Image.LANCZOS).save("../icon-512.png")
    base.resize((180, 180), Image.LANCZOS).save("../icon-180.png")
    base.resize((512, 512), Image.LANCZOS).save("../icono-preview.png")
    print("icon-180.png e icon-512.png regenerados")
