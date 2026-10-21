from manim import *

# Катеты и сторона большого квадрата
A = 2.0
B = 3.4
S = A + B

TRI_COLOR = BLUE_D
C_COLOR = YELLOW
A_COLOR = GREEN
B_COLOR = RED

# Левый нижний угол большого квадрата
ORIGIN_SQ = np.array([-S / 2, -S / 2 + 0.6, 0])


def p(x, y):
    """Точка в координатах большого квадрата."""
    return ORIGIN_SQ + np.array([x, y, 0])


def triangle(*pts):
    return Polygon(*pts, color=WHITE, stroke_width=3,
                   fill_color=TRI_COLOR, fill_opacity=0.85)


def make_caption(text):
    t = VGroup(*[Text(line, font_size=40) for line in text.split("\n")]).arrange(DOWN, buff=0.18)
    if t.width > 7.2:
        t.scale_to_fit_width(7.2)
    return t.move_to(DOWN * 4.0)


class Pythagoras(Scene):
    def set_caption(self, text, *anims):
        new = make_caption(text)
        if self.caption is None:
            self.play(FadeIn(new, shift=UP * 0.2), *anims)
        else:
            self.play(FadeOut(self.caption, shift=UP * 0.2), FadeIn(new, shift=UP * 0.2), *anims)
        self.caption = new

    def construct(self):
        self.caption = None
        # --- 1. Хук ---
        title = Text("Теорема Пифагора", font_size=48).to_edge(UP, buff=1.0)
        formula = MathTex("a^2", "+", "b^2", "=", "c^2", font_size=110)
        formula[0].set_color(A_COLOR)
        formula[2].set_color(B_COLOR)
        formula[4].set_color(C_COLOR)
        question = Text("Но почему это правда?", font_size=44).next_to(formula, DOWN, buff=0.8)

        self.play(Write(title), run_time=1)
        self.play(Write(formula), run_time=1.5)
        self.play(FadeIn(question, shift=UP * 0.3))
        self.wait(1)
        self.play(FadeOut(formula), FadeOut(question))

        # --- 2. Один треугольник с подписями ---
        big = VGroup()
        t0 = triangle(p(0, 0), p(0, B), p(A, 0))  # прямой угол в начале координат
        t0_big = t0.copy().scale(1.5).move_to(UP * 0.6)
        v = t0_big.get_vertices()
        ux, uy = RIGHT * 0.35, UP * 0.35
        right_angle = VMobject(color=WHITE, stroke_width=3).set_points_as_corners(
            [v[0] + ux, v[0] + ux + uy, v[0] + uy])
        lab_a = MathTex("a", color=A_COLOR, font_size=60).next_to(Line(v[0], v[2]), DOWN)
        lab_b = MathTex("b", color=B_COLOR, font_size=60).next_to(Line(v[0], v[1]), LEFT)
        lab_c = MathTex("c", color=C_COLOR, font_size=60).move_to(
            (v[1] + v[2]) / 2 + 0.4 * normalize(np.array([B, A, 0])))
        big.add(t0_big, right_angle, lab_a, lab_b, lab_c)

        self.set_caption("Возьмём прямоугольный\nтреугольник", DrawBorderThenFill(t0_big))
        self.play(Create(right_angle), Write(lab_a), Write(lab_b), Write(lab_c))
        self.wait(1.2)

        # --- 3. Четыре копии в квадрате (a+b) x (a+b) ---
        self.set_caption(
            "Сложим 4 таких\nтреугольника",
            FadeOut(VGroup(right_angle, lab_a, lab_b, lab_c)),
            Transform(t0_big, t0),
        )
        self.remove(t0_big)
        self.add(t0)

        center = p(S / 2, S / 2)
        t_tl = t0.copy()
        t_tr = t0.copy()
        t_br = t0.copy()
        self.play(Rotate(t_tl, -PI / 2, about_point=center), run_time=0.8)
        self.play(Rotate(t_tr, -PI, about_point=center), run_time=0.8)
        self.play(Rotate(t_br, -3 * PI / 2, about_point=center), run_time=0.8)
        t_bl = t0

        outline = Square(S, color=WHITE, stroke_width=4).move_to(center)
        # Подписи сторон: снизу a|b, справа a|b (подходят для обеих раскладок)
        side_labels = VGroup(
            MathTex("a", font_size=56, color=A_COLOR).next_to(Line(p(0, 0), p(A, 0)), DOWN),
            MathTex("b", font_size=56, color=B_COLOR).next_to(Line(p(A, 0), p(S, 0)), DOWN),
            MathTex("a", font_size=56, color=A_COLOR).next_to(Line(p(S, 0), p(S, A)), RIGHT),
            MathTex("b", font_size=56, color=B_COLOR).next_to(Line(p(S, A), p(S, S)), RIGHT),
        )
        ticks = VGroup(
            Line(p(A, -0.12), p(A, 0.12)),
            Line(p(S - 0.12, A), p(S + 0.12, A)),
        )
        self.play(Create(outline), FadeIn(side_labels), Create(ticks))
        self.wait(0.5)

        # --- 4. Пустое место = квадрат c^2 ---
        c_square = Polygon(p(A, 0), p(S, A), p(B, S), p(0, B),
                           stroke_width=0, fill_color=C_COLOR, fill_opacity=0.8)
        c_label = MathTex("c^2", font_size=80, color=BLACK).move_to(center)
        self.set_caption("Пустое место —\nквадрат со стороной c")
        self.play(FadeIn(c_square), Write(c_label))
        self.wait(0.8)

        memo_c = MathTex("c^2", color=C_COLOR, font_size=70).move_to(DOWN * 5.4 + LEFT * 2.0)
        self.play(TransformFromCopy(c_label, memo_c))
        self.wait(0.5)

        # --- 5. Переставляем треугольники ---
        self.set_caption("Теперь переставим\nтреугольники", FadeOut(c_square), FadeOut(c_label))
        self.play(t_bl.animate.shift(UP * A), run_time=1)
        self.play(t_tr.animate.shift(LEFT * B), run_time=1)
        self.play(t_tl.animate.shift(RIGHT * A + DOWN * B), run_time=1)
        self.wait(0.4)

        # --- 6. Пустое место = a^2 + b^2 ---
        a_square = Square(A, stroke_width=0, fill_color=A_COLOR, fill_opacity=0.8).move_to(p(A / 2, A / 2))
        b_square = Square(B, stroke_width=0, fill_color=B_COLOR, fill_opacity=0.8).move_to(p(A + B / 2, A + B / 2))
        a_label = MathTex("a^2", font_size=64, color=BLACK).move_to(a_square)
        b_label = MathTex("b^2", font_size=80, color=BLACK).move_to(b_square)
        self.set_caption("Пустое место —\nдва квадрата: a и b")
        self.play(FadeIn(a_square), Write(a_label))
        self.play(FadeIn(b_square), Write(b_label))
        self.wait(0.8)

        memo_ab = MathTex("a^2", "+", "b^2", font_size=70).move_to(DOWN * 5.4 + RIGHT * 1.2)
        memo_ab[0].set_color(A_COLOR)
        memo_ab[2].set_color(B_COLOR)
        self.play(TransformFromCopy(a_label, memo_ab[0]), TransformFromCopy(b_label, memo_ab[2]), Write(memo_ab[1]))
        self.wait(0.5)

        # --- 7. Вывод ---
        self.set_caption("Тот же квадрат, те же\nтреугольники — значит")
        eq = MathTex("=", font_size=70).move_to((memo_c.get_right() + memo_ab.get_left()) / 2)
        self.play(Write(eq))
        self.wait(1)

        final = MathTex("a^2", "+", "b^2", "=", "c^2", font_size=110).move_to(DOWN * 4.6)
        final[0].set_color(A_COLOR)
        final[2].set_color(B_COLOR)
        final[4].set_color(C_COLOR)
        box = SurroundingRectangle(final, color=WHITE, buff=0.3)
        self.play(
            FadeOut(self.caption),
            *[ReplacementTransform(src, dst) for src, dst in
              zip([memo_ab[0], memo_ab[1], memo_ab[2], eq, memo_c], final)],
        )
        self.play(Create(box))
        self.play(Indicate(final, scale_factor=1.1, color=WHITE))
        self.wait(2)
