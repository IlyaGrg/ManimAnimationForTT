from manim import *

# Безопасная зона TikTok: сверху интерфейс вкладок, снизу описание ролика,
# справа кнопки. Важное держим в |x| < 3.5 и -4.3 < y < 5.8.
TITLE_Y = 5.4
CAPTION_Y = -3.9

C_COLOR = YELLOW
R_COLOR = RED
D_COLOR = GREEN
TOP_COLOR = BLUE_D
BOTTOM_COLOR = ORANGE


def make_caption(text):
    t = VGroup(*[Text(line, font_size=40) for line in text.split("\n")]).arrange(DOWN, buff=0.18)
    if t.width > 7.2:
        t.scale_to_fit_width(7.2)
    return t.move_to(UP * CAPTION_Y)


def make_title(text):
    return Text(text, font_size=52, weight=BOLD).move_to(UP * TITLE_Y)


def rigid_move(mob, angle, about, shift):
    """Поворот вокруг точки about и сдвиг — без искажения формы."""
    start = mob.copy()

    def update(m, alpha):
        m.become(start.copy().rotate(angle * alpha, about_point=about).shift(shift * alpha))

    return UpdateFromAlphaFunc(mob, update)


def wrap_angle(a):
    return (a + PI) % TAU - PI


class CircleFormulas(Scene):
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
        self.circumference()
        self.area()
        self.outro()

    # ------------------------------------------------------------------
    def hook(self):
        c_formula = MathTex("C", "=", "2", r"\pi", "r", font_size=110)
        s_formula = MathTex("S", "=", r"\pi", "r^2", font_size=110)
        c_formula[0].set_color(C_COLOR)
        s_formula[0].set_color(TOP_COLOR)
        VGroup(c_formula, s_formula).arrange(DOWN, buff=0.8).move_to(UP * 1.5)
        question = Text("Откуда здесь π?", font_size=56).move_to(DOWN * 1.8)

        self.play(Write(c_formula), run_time=1.2)
        self.play(Write(s_formula), run_time=1.2)
        self.play(FadeIn(question, shift=UP * 0.3))
        self.play(Indicate(c_formula[3]), Indicate(s_formula[2]))
        self.wait(0.8)
        self.play(FadeOut(VGroup(c_formula, s_formula, question)))

    # ------------------------------------------------------------------
    def circumference(self):
        self.set_title("Длина окружности")

        # Радиус и диаметр на большом круге
        R = 2.2
        center = UP * 1.2
        circle = Circle(radius=R, color=WHITE, stroke_width=5).move_to(center)
        dot = Dot(center, radius=0.07)
        radius = Line(center, center + R * RIGHT, color=R_COLOR, stroke_width=6)
        r_label = MathTex("r", color=R_COLOR, font_size=64).next_to(radius, UP, buff=0.15)

        self.play(Create(circle), FadeIn(dot))
        self.set_caption("Радиус r — от центра\nдо края", Create(radius), Write(r_label))
        self.wait(0.6)

        diameter = Line(center + R * LEFT, center + R * RIGHT, color=D_COLOR, stroke_width=6)
        d_label = MathTex("d", "=", "2r", font_size=64).next_to(diameter, DOWN, buff=0.2)
        d_label[0].set_color(D_COLOR)
        self.set_caption("Диаметр — два радиуса", Create(diameter), Write(d_label))
        self.wait(0.8)

        # Прокатываем маленький круг на один оборот
        r = 0.9
        ground_y = 0.9
        x_start = -PI * r
        ground = Line(LEFT * 3.9, RIGHT * 3.9, color=GREY_B, stroke_width=3).set_y(ground_y)
        small_center = np.array([x_start, ground_y + r, 0])

        self.play(
            FadeOut(VGroup(dot, radius, r_label, d_label)),
            circle.animate.scale(r / R).move_to(small_center),
            diameter.animate.scale(r / R).move_to(small_center),
            Create(ground),
        )
        self.remove(circle, diameter)

        t = ValueTracker(0)

        def roll_center():
            return np.array([x_start + TAU * r * t.get_value(), ground_y + r, 0])

        def rolling():
            c = roll_center()
            a = t.get_value()
            base = Circle(radius=r, color=GREY_C, stroke_width=4).move_to(c)
            # Ещё «не прокатанная» часть окружности — жёлтая
            left = Arc(radius=r, start_angle=-PI / 2, angle=max(TAU * (1 - a), 1e-3),
                       arc_center=c, color=C_COLOR, stroke_width=9)
            phi = -PI / 2 - TAU * a
            mark = c + r * np.array([np.cos(phi), np.sin(phi), 0])
            diam = Line(c - (mark - c), mark, color=D_COLOR, stroke_width=5)
            return VGroup(base, left, diam, Dot(mark, color=R_COLOR, radius=0.09))

        def trace():
            x = x_start + TAU * r * t.get_value()
            return Line([x_start, ground_y, 0], [x + 1e-4, ground_y, 0], color=C_COLOR, stroke_width=10)

        roller = always_redraw(rolling)
        trail = always_redraw(trace)
        self.add(trail, roller)
        self.set_caption("Прокатим круг\nровно на один оборот")
        self.play(t.animate.set_value(1), run_time=4, rate_func=linear)
        self.wait(0.4)

        roller.clear_updaters()
        trail.clear_updaters()
        c_label = MathTex("C", color=C_COLOR, font_size=80).next_to(trail, UP, buff=0.25).shift(LEFT * 1.0)
        self.set_caption("След — это длина\nокружности C", Write(c_label))
        self.wait(0.6)

        # Сколько диаметров помещается в C
        d = 2 * r
        seg_y = ground_y - 0.45
        segs = VGroup()
        d_labels = VGroup()
        for i in range(3):
            seg = Line([x_start + i * d, seg_y, 0], [x_start + (i + 1) * d, seg_y, 0],
                       color=D_COLOR if i % 2 == 0 else GREEN_A, stroke_width=8)
            segs.add(seg)
            d_labels.add(MathTex("d", color=D_COLOR, font_size=72).next_to(seg, DOWN, buff=0.15))
        rest = Line([x_start + 3 * d, seg_y, 0], [x_start + TAU * r, seg_y, 0], color=R_COLOR, stroke_width=8)
        rest_label = MathTex(r"0.14d", color=R_COLOR, font_size=48).next_to(rest, DOWN, buff=0.15).shift(RIGHT * 0.1)

        self.set_caption("Сколько диаметров\nв ней помещается?", FadeOut(roller))
        for seg, lab in zip(segs, d_labels):
            self.play(Create(seg), FadeIn(lab, shift=DOWN * 0.1), run_time=0.6)
        self.play(Create(rest), FadeIn(rest_label), run_time=0.6)
        self.wait(0.4)

        pi_value = MathTex(r"C", r"\approx", r"3.14159\ldots", r"\cdot", r"d", font_size=80).move_to(DOWN * 1.4)
        pi_value[0].set_color(C_COLOR)
        pi_value[4].set_color(D_COLOR)
        self.set_caption("Чуть больше трёх —\nдля любого круга!", Write(pi_value))
        self.wait(1)

        pi_name = MathTex(r"\pi", r"=", r"3.14159\ldots", font_size=80).move_to(pi_value)
        self.set_caption("Это число и назвали π")
        self.play(TransformMatchingTex(pi_value, pi_name))
        self.wait(1)

        c_formula = MathTex("C", "=", r"\pi", "d", "=", "2", r"\pi", "r", font_size=100).move_to(DOWN * 1.4)
        c_formula[0].set_color(C_COLOR)
        c_formula[3].set_color(D_COLOR)
        c_formula[7].set_color(R_COLOR)
        self.set_caption("Значит, длина окружности:", FadeOut(pi_name), FadeIn(c_formula[:4]))
        self.play(Write(c_formula[4:]))
        box = SurroundingRectangle(c_formula, color=C_COLOR, buff=0.25)
        self.play(Create(box))
        self.wait(1.5)

        self.play(FadeOut(VGroup(ground, trail, c_label, segs, d_labels, rest, rest_label,
                                 c_formula, box, self.caption)))
        self.caption = None

    # ------------------------------------------------------------------
    @staticmethod
    def circle_sectors(n, R, center):
        theta = TAU / n
        sectors = VGroup()
        for k in range(n):
            phi = (k + 0.5) * theta
            sectors.add(Sector(radius=R, start_angle=k * theta, angle=theta, arc_center=center,
                               fill_color=TOP_COLOR if phi < PI else BOTTOM_COLOR,
                               fill_opacity=0.9, stroke_color=WHITE, stroke_width=2 if n <= 16 else 0.8))
        return sectors

    @staticmethod
    def row_layout(n, R, y0):
        """Для каждого сектора k: (поворот, вершина в ряду). Порядок — как в circle_sectors."""
        theta = TAU / n
        c = 2 * R * np.sin(theta / 2)
        h = R * np.cos(theta / 2)
        width = (n / 2) * c + c / 2
        x0 = -width / 2
        top = sorted([k for k in range(n) if (k + 0.5) * theta < PI], key=lambda k: -k)
        bottom = sorted([k for k in range(n) if (k + 0.5) * theta > PI])
        layout = {}
        for j, k in enumerate(top):
            phi = (k + 0.5) * theta
            layout[k] = (wrap_angle(PI / 2 - phi), np.array([x0 + c / 2 + j * c, y0, 0]))
        for j, k in enumerate(bottom):
            phi = (k + 0.5) * theta
            layout[k] = (wrap_angle(3 * PI / 2 - phi), np.array([x0 + c + j * c, y0 + h, 0]))
        return layout

    def row_sectors(self, n, R, center, y0):
        sectors = self.circle_sectors(n, R, center)
        for k, (angle, apex) in self.row_layout(n, R, y0).items():
            sectors[k].rotate(angle, about_point=center).shift(apex - center)
        return sectors

    def area(self):
        self.set_title("Площадь круга")

        R = 2.0
        center = UP * 2.85
        y0 = -2.6

        circle = Circle(radius=R, color=WHITE, stroke_width=4).move_to(center)
        r_line = Line(center, center + R * RIGHT, color=R_COLOR, stroke_width=6)
        r_label = MathTex("r", color=R_COLOR, font_size=60).next_to(r_line, UP, buff=0.12)
        self.play(Create(circle))
        self.play(Create(r_line), Write(r_label))

        n = 8
        sectors = self.circle_sectors(n, R, center)
        self.set_caption("Разрежем круг\nна 8 секторов", FadeIn(sectors), FadeOut(r_line), FadeOut(r_label))
        self.wait(0.5)

        ghost = circle.copy().set_stroke(GREY_D, width=3, opacity=0.6)
        self.add(ghost)
        self.remove(circle)

        self.set_caption("Разложим их «ёлочкой»")
        layout = self.row_layout(n, R, y0)
        for k in sorted(layout, key=lambda k: layout[k][1][0]):
            angle, apex = layout[k]
            self.play(rigid_move(sectors[k], angle, center, apex - center), run_time=0.45)
        self.wait(0.6)

        self.set_caption("Чем больше секторов,\nтем ровнее фигура")
        for m in (16, 32, 64):
            new = self.row_sectors(m, R, center, y0)
            self.play(ReplacementTransform(sectors, new), run_time=1.2)
            sectors = new
            self.wait(0.3)

        self.set_caption("Почти прямоугольник!")
        self.wait(0.6)

        # Стороны прямоугольника
        top_brace = Brace(sectors, UP, buff=0.15)
        half_c = MathTex(r"\tfrac{1}{2}", "C", font_size=60).next_to(top_brace, UP, buff=0.12)
        half_c[1].set_color(C_COLOR)
        self.set_caption("Сверху — дуги верхней\nполовины окружности", GrowFromCenter(top_brace), Write(half_c))
        self.wait(0.8)

        pi_r = MathTex(r"\tfrac{1}{2}", r"\cdot", "2", r"\pi", "r", font_size=60).move_to(half_c)
        pi_r_short = MathTex(r"\pi", "r", font_size=60).move_to(half_c)
        self.play(TransformMatchingTex(half_c, pi_r))
        self.wait(0.4)
        self.play(TransformMatchingTex(pi_r, pi_r_short))
        self.wait(0.6)

        left_brace = Brace(sectors, LEFT, buff=0.12)
        r_side = MathTex("r", color=R_COLOR, font_size=60).next_to(left_brace, LEFT, buff=0.12)
        self.set_caption("Высота — радиус r", GrowFromCenter(left_brace), Write(r_side))
        self.wait(0.8)

        s_formula = MathTex("S", "=", r"\pi r", r"\cdot", "r", "=", r"\pi", "r^2", font_size=96).move_to(center)
        s_formula[0].set_color(TOP_COLOR)
        s_formula[4].set_color(R_COLOR)
        self.set_caption("Площадь = ширина × высота", FadeOut(ghost))
        self.play(
            TransformFromCopy(pi_r_short, s_formula[2]),
            TransformFromCopy(r_side, s_formula[4]),
            FadeIn(s_formula[:2]), FadeIn(s_formula[3]),
        )
        self.play(Write(s_formula[5:]))
        box = SurroundingRectangle(s_formula, color=TOP_COLOR, buff=0.25)
        self.play(Create(box))
        self.wait(1.5)

        self.play(FadeOut(VGroup(sectors, top_brace, pi_r_short, left_brace, r_side,
                                 s_formula, box, self.caption, self.title)))
        self.caption = None
        self.title = None

    # ------------------------------------------------------------------
    def outro(self):
        c_formula = MathTex("C", "=", "2", r"\pi", "r", font_size=120)
        s_formula = MathTex("S", "=", r"\pi", "r^2", font_size=120)
        c_formula[0].set_color(C_COLOR)
        s_formula[0].set_color(TOP_COLOR)
        c_text = Text("длина окружности", font_size=40, color=GREY_B)
        s_text = Text("площадь круга", font_size=40, color=GREY_B)
        c_group = VGroup(c_formula, c_text).arrange(DOWN, buff=0.3)
        s_group = VGroup(s_formula, s_text).arrange(DOWN, buff=0.3)
        VGroup(c_group, s_group).arrange(DOWN, buff=1.2).move_to(UP * 0.8)

        self.play(FadeIn(c_group, shift=UP * 0.3))
        self.play(FadeIn(s_group, shift=UP * 0.3))
        self.play(Indicate(c_formula[3]), Indicate(s_formula[2]))
        self.wait(2.5)
