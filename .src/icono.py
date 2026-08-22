#!/usr/bin/env python3
"""Icono de NutriScan, a todo color.

Dos objetos y nada mas: el brocoli (el alimento) y la ficha con sus datos
(el analisis). El de referencia traia tres elementos y un circulo punteado;
a 60 px, que es el tamano real en la pantalla de inicio, eso se convierte
en una mancha, asi que se queda lo que se distingue.
"""
import math
from PIL import Image, ImageDraw, ImageFilter

S = 1024                                   # lienzo maestro
FONDO_A = (247, 253, 246)                  # crema verdosa
FONDO_B = (198, 236, 208)                  # menta
VERDE_OSC = (46, 125, 50)
VERDE_MED = (76, 175, 80)
VERDE_CLA = (129, 199, 132)
TALLO = (124, 179, 66)
TINTA = (33, 48, 40)


def lerp(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def fondo():
    im = Image.new("RGB", (S, S))
    px = im.load()
    for y in range(S):
        for x in range(S):
            # diagonal suave, mas claro arriba-izquierda
            t = min(1.0, max(0.0, (x / S) * 0.35 + (y / S) * 0.65))
            px[x, y] = lerp(FONDO_A, FONDO_B, t ** 1.15)
    return im


def sombra(mascara, desplaz=(0, 14), difuso=18, fuerza=70):
    """Sombra suave a partir de una mascara, para que los objetos despeguen."""
    s = Image.new("L", (S, S), 0)
    s.paste(mascara, desplaz)
    s = s.filter(ImageFilter.GaussianBlur(difuso))
    return Image.eval(s, lambda v: int(v * fuerza / 255))


def brocoli(im):
    """Ramillete: circulos superpuestos arriba, tallo con dos ramas abajo."""
    cx, cy = 330, 430
    mask = Image.new("L", (S, S), 0)
    md = ImageDraw.Draw(mask)

    # tallo y ramas, primero para que las flores lo tapen
    tronco = [(cx - 26, cy + 40), (cx + 26, cy + 40), (cx + 22, cy + 250), (cx - 22, cy + 250)]
    md.polygon(tronco, fill=255)
    md.line([cx, cy + 150, cx - 120, cy + 40], fill=255, width=40)
    md.line([cx, cy + 170, cx + 122, cy + 55], fill=255, width=40)

    flores = [(cx, cy - 120, 132), (cx - 140, cy - 40, 108), (cx + 140, cy - 40, 108),
              (cx - 72, cy - 150, 96), (cx + 74, cy - 148, 96), (cx, cy - 10, 104)]
    for fx, fy, r in flores:
        md.ellipse([fx - r, fy - r, fx + r, fy + r], fill=255)

    im.paste((0, 0, 0), (0, 0), sombra(mask, (6, 16), 20, 62))

    # tallo
    tallo = Image.new("L", (S, S), 0)
    td = ImageDraw.Draw(tallo)
    td.polygon(tronco, fill=255)
    td.line([cx, cy + 150, cx - 120, cy + 40], fill=255, width=40)
    td.line([cx, cy + 170, cx + 122, cy + 55], fill=255, width=40)
    im.paste(TALLO, (0, 0), tallo)

    # flores, de la mas oscura al brillo
    for i, (fx, fy, r) in enumerate(flores):
        cap = Image.new("L", (S, S), 0)
        ImageDraw.Draw(cap).ellipse([fx - r, fy - r, fx + r, fy + r], fill=255)
        im.paste(VERDE_MED if i % 2 else VERDE_OSC, (0, 0), cap)
        bri = Image.new("L", (S, S), 0)
        ImageDraw.Draw(bri).ellipse(
            [fx - r * 0.55, fy - r * 0.8, fx + r * 0.15, fy - r * 0.2], fill=255)
        im.paste(VERDE_CLA, (0, 0), Image.eval(bri.filter(ImageFilter.GaussianBlur(14)),
                                               lambda v: int(v * 0.55)))
    return im


def ficha(im):
    """Ficha blanca con la miniatura del alimento y sus renglones de datos."""
    x0, y0, x1, y1 = 470, 300, 940, 720
    r = 46
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).rounded_rectangle([x0, y0, x1, y1], radius=r, fill=255)
    im.paste((0, 0, 0), (0, 0), sombra(m, (8, 18), 20, 78))
    im.paste((255, 255, 255), (0, 0), m)

    d = ImageDraw.Draw(im)
    # miniatura del producto
    d.rounded_rectangle([x0 + 44, y0 + 60, x0 + 168, y0 + 184], radius=26, fill=(226, 243, 228))
    d.ellipse([x0 + 74, y0 + 84, x0 + 138, y0 + 148], fill=VERDE_MED)
    d.ellipse([x0 + 62, y0 + 112, x0 + 106, y0 + 156], fill=VERDE_OSC)

    # renglones: dos grises y dos con el semaforo del analisis
    renglones = [(0.00, 210, (176, 190, 183)), (0.20, 150, (176, 190, 183))]
    for i, (dy, ancho, col) in enumerate(renglones):
        yy = y0 + 78 + i * 62
        d.rounded_rectangle([x0 + 208, yy, x0 + 208 + ancho, yy + 26], radius=13, fill=col)

    # barras de resultado, el «semaforo» que da la app
    barras = [(VERDE_MED, 232), ((255, 179, 0), 176), ((229, 57, 53), 120)]
    for i, (col, ancho) in enumerate(barras):
        yy = y0 + 240 + i * 58
        d.rounded_rectangle([x0 + 44, yy, x0 + 44 + ancho, yy + 34], radius=17, fill=col)
        d.ellipse([x0 + 300, yy + 2, x0 + 330, yy + 32], fill=col)
    return im


def construir():
    im = fondo()
    im = brocoli(im)
    im = ficha(im)
    return im


if __name__ == "__main__":
    base = construir()
    base.resize((512, 512), Image.LANCZOS).save("../icon-512.png")
    base.resize((180, 180), Image.LANCZOS).save("../icon-180.png")
    print("icon-180.png e icon-512.png regenerados")
