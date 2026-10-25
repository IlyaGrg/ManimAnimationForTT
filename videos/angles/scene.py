from manim import *
# Отличное качество
# Безопасная зона TikTok: сверху интерфейс вкладок, снизу описание ролика,
# Справа кнопки. Важное держим в |x| < 3.5 и -4.3 < y < 5.8.
TITLE_Y = 5.4
CAPTION_Y = -3.9

A_COLOR = RED
B_COLOR = TEAL
C_COLOR = YELLOW
TRI_COLORS = [BLUE_D, PURPLE_C, GREEN_D, GOLD_D]
EXT_COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE]


def make_caption(text):
    t = VGroup(*[Text(line, font_size=40) for line in text.split("\n")]).arrange(DOWN, buff=0.18)
    if t.width > 7.2:
        t.scale_to_fit_width(7.2)
    return t.move_to(UP * CAPTION_Y)


def make_title(text):
    t = Text(text, font_size=52, weight=BOLD)
    if t.width > 7.2:
        t.scale_to_fit_width(7.2)
    return t.move_to(UP * TITLE_Y)


def direction_angle(v):
    return np.arctan2(v[1], v[0])


def corner_angle(V, P, Q):
    """Угол при вершине V от луча VP к лучу VQ против часовой стрелки: (начало, величина)."""
    a0 = direction_angle(P - V)
    return a0, (direction_angle(Q - V) - a0) % TAU


def corner(V, P, Q, color, r=0.6, opacity=0.85):
    a0, sweep = corner_angle(V, P, Q)
    return Sector(radius=r, start_angle=a0, angle=sweep, arc_center=V,
                  fill_color=color, fill_opacity=opacity, stroke_width=0)


def corner_label_pos(V, P, Q, r):
    a0, sweep = corner_angle(V, P, Q)
    mid = a0 + sweep / 2
    return V + r * np.array([np.cos(mid), np.sin(mid), 0])


def polygon(points, **kwargs):
    style = dict(stroke_color=WHITE, stroke_width=5, fill_opacity=0)
    style.update(kwargs)
    return Polygon(*points, **style)


class Angles(Scene):
    def set_caption(self, text, *anims):
        new = make_caption(text)
        if self.caption is None:
            self.play(FadeIn(new, shift=UP * 0.2), *anims)
        else:
            self.play(FadeOut(self.caption, shift=UP * 0.2), FadeIn(new, shift=UP * 0.2), *anims)
        self.caption = new

    def set_title(self, text):
        new = make_title(text)
        if self.title is None:
            self.play(Write(new))
        else:
            self.play(FadeOut(self.title, shift=UP * 0.2), FadeIn(new, shift=UP * 0.2))
        self.title = new

    def construct(self):
        self.caption = None
        self.title = None
        self.hook()
        self.proof()
        self.polygons()
        self.exterior()
        self.outro()

    # ------------------------------------------------------------------
    def hook(self):
        self.set_title("Сумма углов")

        A = Dot([-2.5, -0.5, 0], radius=0.07)
        B = Dot([2.5, -0.5, 0], radius=0.07)
        C = Dot([0.4, 3.2, 0], radius=0.07)

        def pts():
            return A.get_center(), B.get_center(), C.get_center()

        tri = always_redraw(lambda: polygon(pts()))
        sectors = always_redraw(lambda: VGroup(
            corner(pts()[0], pts()[1], pts()[2], A_COLOR),
            corner(pts()[1], pts()[2], pts()[0], B_COLOR),
            corner(pts()[2], pts()[0], pts()[1], C_COLOR),
        ))

        def degrees():
            a, b, c = pts()
            alpha = round(np.degrees(corner_angle(a, b, c)[1]))
            beta = round(np.degrees(corner_angle(b, c, a)[1]))
            return alpha, beta, 180 - alpha - beta

        def angle_labels():
            a, b, c = pts()
            vals = degrees()
            return VGroup(*[
                MathTex(rf"{v}^\circ", color=col, font_size=44).move_to(corner_label_pos(V, P, Q, 1.05))
                for v, col, (V, P, Q) in zip(vals, [A_COLOR, B_COLOR, C_COLOR], [(a, b, c), (b, c, a), (c, a, b)])
            ])

        def sum_line():
            al, be, ga = degrees()
            line = MathTex(rf"{al}^\circ", "+", rf"{be}^\circ", "+", rf"{ga}^\circ", "=", r"180^\circ", font_size=64)
            line[0].set_color(A_COLOR)
            line[2].set_color(B_COLOR)
            line[4].set_color(C_COLOR)
            if line.width > 6.8:
                line.scale_to_fit_width(6.8)
            return line.move_to(DOWN * 2.2)

        labels = always_redraw(angle_labels)
        total = always_redraw(sum_line)

        self.play(Create(tri), FadeIn(VGroup(A, B, C)))
        self.play(FadeIn(sectors), FadeIn(labels))
        self.play(FadeIn(total, shift=UP * 0.2))
        self.set_caption("Меняем форму треугольника…")

        # Целевые позиции вершин; .animate создаём прямо перед play —
        # заранее созданные билдеры одной точки перезаписывают друг другу цель
        moves = [
            {C: [-1.6, 2.8, 0]},
            {A: [-2.8, 0.4, 0], C: [2.0, 3.0, 0]},
            {B: [1.8, -0.9, 0], C: [-0.4, 3.6, 0]},
            {A: [-2.2, -0.8, 0], B: [2.8, 0.2, 0], C: [0.9, 2.0, 0]},
        ]
        for i, move in enumerate(moves):
            if i == 2:
                self.set_caption("…а сумма углов\nвсегда 180°!")
            self.play(*[dot.animate.move_to(pos) for dot, pos in move.items()], run_time=1.6)
        self.wait(0.5)

        question = make_caption("Но почему?")
        self.play(FadeOut(self.caption, shift=UP * 0.2), FadeIn(question, shift=UP * 0.2))
        self.caption = question
        self.wait(0.8)

        for m in (tri, sectors, labels, total):
            m.clear_updaters()
        self.play(FadeOut(VGroup(tri, sectors, labels, total, A, B, C)))

    # ------------------------------------------------------------------
    def proof(self):
        A = np.array([-2.7, -0.6, 0])
        B = np.array([2.5, -0.6, 0])
        C = np.array([-0.5, 2.6, 0])

        tri = polygon([A, B, C])
        alpha = corner(A, B, C, A_COLOR, r=0.75)
        beta = corner(B, C, A, B_COLOR, r=0.75)
        gamma = corner(C, A, B, C_COLOR, r=0.75)
        lab_a = MathTex(r"\alpha", color=A_COLOR, font_size=60).move_to(corner_label_pos(A, B, C, 1.15))
        lab_b = MathTex(r"\beta", color=B_COLOR, font_size=60).move_to(corner_label_pos(B, C, A, 1.15))
        lab_c = MathTex(r"\gamma", color=C_COLOR, font_size=60).move_to(corner_label_pos(C, A, B, 1.15))

        self.set_caption("Возьмём любой\nтреугольник", Create(tri))
        self.play(FadeIn(VGroup(alpha, beta, gamma)), Write(VGroup(lab_a, lab_b, lab_c)))
        self.wait(0.5)

        parallel = Line([-3.7, C[1], 0], [3.7, C[1], 0], color=GREY_B, stroke_width=4)
        self.set_caption("Проведём через вершину\nпрямую, параллельную низу", Create(parallel))
        self.wait(0.6)

        # Поворот на 180° вокруг середины стороны переносит угол точно к вершине C
        alpha_copy = alpha.copy()
        beta_copy = beta.copy()
        mid_ac = (A + C) / 2
        mid_bc = (B + C) / 2
        self.set_caption("Повернём угол α вокруг\nсередины стороны")
        self.play(Flash(mid_ac, color=A_COLOR, flash_radius=0.25), run_time=0.6)
        self.play(Rotate(alpha_copy, PI, about_point=mid_ac), run_time=1.6)
        lab_a2 = MathTex(r"\alpha", color=A_COLOR, font_size=60).move_to(
            corner_label_pos(C, C + LEFT, A, 1.15))
        self.play(TransformFromCopy(lab_a, lab_a2))

        self.set_caption("То же с углом β")
        self.play(Flash(mid_bc, color=B_COLOR, flash_radius=0.25), run_time=0.6)
        self.play(Rotate(beta_copy, PI, about_point=mid_bc), run_time=1.6)
        lab_b2 = MathTex(r"\beta", color=B_COLOR, font_size=60).move_to(
            corner_label_pos(C, B, C + RIGHT, 1.15))
        self.play(TransformFromCopy(lab_b, lab_b2))
        self.wait(0.5)

        # Три угла вместе — развёрнутый угол
        arc = Arc(radius=1.05, start_angle=PI, angle=-PI, arc_center=C, color=WHITE, stroke_width=4)
        self.set_caption("Вместе они дают\nразвёрнутый угол — 180°")
        self.play(Indicate(VGroup(alpha_copy, gamma, beta_copy), scale_factor=1.15), Create(arc))
        result = MathTex(r"\alpha", "+", r"\beta", "+", r"\gamma", "=", r"180^\circ", font_size=90).move_to(DOWN * 2.2)
        result[0].set_color(A_COLOR)
        result[2].set_color(B_COLOR)
        result[4].set_color(C_COLOR)
        self.play(Write(result))
        box = SurroundingRectangle(result, color=WHITE, buff=0.2)
        self.play(Create(box))
        self.wait(1.5)

        self.play(FadeOut(VGroup(tri, alpha, beta, gamma, lab_a, lab_b, lab_c, parallel, alpha_copy, beta_copy,
                                 lab_a2, lab_b2, arc, result, box)))

    # ------------------------------------------------------------------
    def polygons(self):
        self.set_title("А если углов больше?")

        shapes = [
            [(-2.4, -0.6), (2.2, -0.9), (2.7, 2.2), (-1.6, 3.0)],
            [(-2.5, -0.4), (1.6, -0.9), (3.0, 1.6), (0.4, 3.4), (-2.4, 2.4)],
            [(-2.2, -0.8), (1.2, -1.0), (3.0, 0.9), (2.2, 3.0), (-0.8, 3.5), (-2.9, 1.6)],
        ]
        names = ["Четырёхугольник", "Пятиугольник", "Шестиугольник"]
        outline = None
        for shape, name in zip(shapes, names):
            pts = [np.array([x, y, 0]) for x, y in shape]
            n = len(pts)
            new_outline = polygon(pts)
            if outline is None:
                self.set_caption(name, Create(new_outline))
            else:
                self.set_caption(name, ReplacementTransform(outline, new_outline))
            outline = new_outline

            diagonals = VGroup(*[DashedLine(pts[0], pts[i], color=WHITE, stroke_width=3) for i in range(2, n - 1)])
            triangles = VGroup(*[
                Polygon(pts[0], pts[i], pts[i + 1], stroke_width=0,
                        fill_color=TRI_COLORS[(i - 1) % len(TRI_COLORS)], fill_opacity=0.7)
                for i in range(1, n - 1)
            ])
            if len(diagonals):
                self.play(Create(diagonals), run_time=0.8)
            count = MathTex(rf"{n - 2}", r"\cdot", r"180^\circ", "=", rf"{(n - 2) * 180}^\circ",
                            font_size=84).move_to(DOWN * 2.2)
            counter = MathTex("0", font_size=84).move_to(count[0])
            self.play(FadeIn(counter))
            for k, t in enumerate(triangles, start=1):
                self.play(FadeIn(t, scale=0.6), Transform(counter, MathTex(rf"{k}", font_size=84).move_to(count[0])),
                          run_time=0.5)
            self.remove(counter)
            self.add(count[0])
            self.play(Write(count[1:]))
            self.wait(0.8)
            self.play(FadeOut(VGroup(diagonals, triangles, count)))

        general = MathTex("(n-2)", r"\cdot", r"180^\circ", font_size=100).move_to(DOWN * 2.2)
        self.set_caption("Любой n-угольник режется\nна n − 2 треугольника", Write(general))
        self.play(Circumscribe(general, color=YELLOW))
        self.wait(1.5)
        self.play(FadeOut(VGroup(outline, general)))

    # ------------------------------------------------------------------
    def exterior(self):
        self.set_title("Фокус с внешними углами")

        base = [np.array([x, y, 0]) for x, y in
                [(-2.0, -0.4), (1.4, -0.8), (2.6, 1.6), (0.3, 3.2), (-2.3, 2.1)]]
        center = sum(base) / len(base)
        s = ValueTracker(1.0)
        n = len(base)

        def verts():
            return [center + s.get_value() * (p - center) for p in base]

        def shape():
            return polygon(verts())

        def rays():
            v = verts()
            return VGroup(*[
                DashedLine(v[i], v[i] + 1.4 * normalize(base[i] - base[i - 1]), color=GREY_B, stroke_width=3)
                for i in range(n)
            ])

        def ext_sectors():
            v = verts()
            out = VGroup()
            for i in range(n):
                # Направления сторон берём у исходной фигуры — при сжатии они не меняются
                d_in = base[i] - base[i - 1]
                d_out = base[(i + 1) % n] - base[i]
                a0 = direction_angle(d_in)
                sweep = (direction_angle(d_out) - a0) % TAU
                out.add(Sector(radius=0.9, start_angle=a0, angle=sweep, arc_center=v[i],
                               fill_color=EXT_COLORS[i], fill_opacity=0.85, stroke_width=0))
            return out

        poly = always_redraw(shape)
        ray_group = always_redraw(rays)
        sectors = always_redraw(ext_sectors)

        self.set_caption("Продлим стороны\nпятиугольника", Create(poly))
        self.play(Create(ray_group))
        self.set_caption("Это внешние углы")
        self.play(FadeIn(sectors, lag_ratio=0.3), run_time=1.5)
        self.wait(0.6)

        self.set_caption("А теперь сожмём\nмногоугольник в точку…")
        self.play(s.animate.set_value(0.0), run_time=3.5, rate_func=smooth)
        self.wait(0.4)

        full = MathTex(r"360^\circ", font_size=96).move_to(DOWN * 1.9)
        self.set_caption("Внешние углы сложились\nв полный круг!", Write(full))
        self.play(Circumscribe(full, color=YELLOW, shape=Circle))
        self.wait(1)

        self.set_caption("Для любого многоугольника\nсумма внешних углов — 360°")
        self.play(s.animate.set_value(1.0), run_time=2.5, rate_func=smooth)
        self.wait(1.2)

        for m in (poly, ray_group, sectors):
            m.clear_updaters()
        self.play(FadeOut(VGroup(poly, ray_group, sectors, full, self.caption, self.title)))
        self.caption = None
        self.title = None

    # ------------------------------------------------------------------
    def outro(self):
        tri = polygon([[-0.5, 0, 0], [0.5, 0, 0], [0.1, 0.8, 0]], stroke_width=4, fill_color=A_COLOR, fill_opacity=0.6)
        pent = RegularPolygon(5, radius=0.5, stroke_color=WHITE, stroke_width=4,
                              fill_color=TRI_COLORS[0], fill_opacity=0.6)
        circ = VGroup(*[Sector(radius=0.5, start_angle=i * TAU / 5, angle=TAU / 5, fill_color=EXT_COLORS[i],
                               fill_opacity=0.85, stroke_width=0) for i in range(5)])

        rows = VGroup(
            VGroup(tri, MathTex(r"180^\circ", font_size=80)),
            VGroup(pent, MathTex(r"(n-2)\cdot 180^\circ", font_size=80)),
            VGroup(circ, MathTex(r"360^\circ", font_size=80)),
        )
        for row in rows:
            row.arrange(RIGHT, buff=0.6)
        rows.arrange(DOWN, buff=1.0, aligned_edge=LEFT).move_to(UP * 1.0)
        captions = VGroup(
            Text("углы треугольника", font_size=30, color=GREY_B),
            Text("углы n-угольника", font_size=30, color=GREY_B),
            Text("внешние углы", font_size=30, color=GREY_B),
        )
        for cap, row in zip(captions, rows):
            cap.next_to(row[1], DOWN, buff=0.15, aligned_edge=LEFT)

        for row, cap in zip(rows, captions):
            self.play(FadeIn(row[0], scale=0.5), Write(row[1]), FadeIn(cap), run_time=0.9)
        self.wait(2.5)
