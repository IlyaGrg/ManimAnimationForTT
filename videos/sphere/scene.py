from manim import *

# Безопасная зона TikTok: сверху интерфейс вкладок, снизу описание ролика,
# справа кнопки. Важное держим в |x| < 3.5 и -4.3 < y < 5.8.
TITLE_Y = 5.4
CAPTION_Y = -3.9

HEMI_COLORS = [BLUE_D, BLUE_E]
HEMI_COLOR = BLUE_C
CYL_COLOR = ORANGE
CONE_COLOR = GREY_B
R_COLOR = RED
H_COLOR = YELLOW
RHO_COLOR = GREEN

PHI = 66 * DEGREES
THETA = -90 * DEGREES
ZOOM = 1.15
FRAME_CENTER = [0, 0, 1.5]

R = 1.45            # радиус полушария и цилиндра
LX, RX = -1.8, 1.8  # центры оснований тел
BIG_R = 2.0         # шар во вступлении
BIG_Z = 2.4         # высота центра шара во вступлении
LIFT_Z = 4.3        # куда поднимаем срезы
LIFT_SCALE = 0.8


def make_caption(text):
    t = VGroup(*[Text(line, font_size=40) for line in text.split("\n")]).arrange(DOWN, buff=0.18)
    if t.width > 7.2:
        t.scale_to_fit_width(7.2)
    return t.move_to(UP * CAPTION_Y)


def make_title(text):
    return Text(text, font_size=52, weight=BOLD).move_to(UP * TITLE_Y)


def hemisphere(r, base, opacity=0.6):
    dome = Sphere(radius=r, v_range=[PI / 2, PI], resolution=(12, 32), checkerboard_colors=HEMI_COLORS,
                  fill_opacity=opacity, stroke_width=0.4, stroke_color=BLUE_A)
    floor = Circle(radius=r, stroke_width=2, stroke_color=BLUE_A, fill_color=BLUE_E, fill_opacity=opacity)
    return VGroup(floor, dome).shift(base)


def cylinder_minus_cone(r, base):
    floor = Circle(radius=r, stroke_width=2, stroke_color=WHITE, fill_color=CYL_COLOR, fill_opacity=0.35)
    wall = Cylinder(radius=r, height=r, show_ends=False, resolution=(6, 32), checkerboard_colors=False,
                    fill_color=CYL_COLOR, fill_opacity=0.35, stroke_width=0.4, stroke_color=CYL_COLOR)
    wall.shift(OUT * r / 2)
    cone = Cone(base_radius=r, height=r, direction=-Z_AXIS, resolution=(6, 32), checkerboard_colors=False,
                fill_color=CONE_COLOR, fill_opacity=0.75, stroke_width=0.4, stroke_color=WHITE)
    rim = Circle(radius=r, stroke_width=3, stroke_color=WHITE).shift(OUT * r)
    body = VGroup(floor, wall, rim).shift(base)
    cone.shift(base)
    return body, cone


def rho_of(h):
    return np.sqrt(max(R ** 2 - h ** 2, 0))


def hemi_slice(h):
    return Circle(radius=max(rho_of(h), 0.01), stroke_color=H_COLOR, stroke_width=3,
                  fill_color=HEMI_COLOR, fill_opacity=1).move_to([LX, 0, h])


def cyl_slice(h):
    return Annulus(inner_radius=max(h, 0.01), outer_radius=R, stroke_color=H_COLOR, stroke_width=3,
                   fill_color=CYL_COLOR, fill_opacity=1).move_to([RX, 0, h])


def lifted(mob, x):
    """Срез, поднятый над телом и развёрнутый к зрителю."""
    return mob.scale(LIFT_SCALE).rotate(PHI, axis=RIGHT).move_to([x, 0, LIFT_Z])


class SphereVolume(ThreeDScene):
    def screen(self, point):
        """Где 3D-точка окажется на экране (для подписей, закреплённых в кадре)."""
        p = self.renderer.camera.project_points(np.array([point]))[0]
        return np.array([p[0], p[1], 0])

    def fixed(self, *mobs):
        self.add_fixed_in_frame_mobjects(*mobs)
        return mobs[0] if len(mobs) == 1 else mobs

    def set_caption(self, text, *anims):
        new = self.fixed(make_caption(text))
        if self.caption is None:
            self.play(FadeIn(new, shift=UP * 0.2), *anims)
        else:
            self.play(FadeOut(self.caption, shift=UP * 0.2), FadeIn(new, shift=UP * 0.2), *anims)
        self.caption = new

    def set_title(self, text):
        new = self.fixed(make_title(text))
        if self.title is None:
            self.play(Write(new))
        else:
            self.play(FadeOut(self.title, shift=UP * 0.2), FadeIn(new, shift=UP * 0.2))
        self.title = new

    def construct(self):
        self.caption = None
        self.title = None
        self.set_camera_orientation(phi=PHI, theta=THETA, zoom=ZOOM, frame_center=FRAME_CENTER)
        self.hook()
        self.ball()
        self.bodies()
        self.slices()
        self.volumes()
        self.outro()

    # ------------------------------------------------------------------
    def hook(self):
        formula = MathTex("V", "=", r"\frac{4}{3}", r"\pi", "r^3", font_size=130).move_to(UP * 1.2)
        formula[0].set_color(HEMI_COLOR)
        question = Text("Откуда здесь 4/3?", font_size=56).move_to(DOWN * 1.6)
        self.fixed(formula, question)
        self.remove(formula, question)

        self.play(Write(formula), run_time=1.5)
        self.play(FadeIn(question, shift=UP * 0.3))
        self.play(Indicate(formula[2], scale_factor=1.3))
        self.wait(0.8)
        self.play(FadeOut(formula), FadeOut(question))

    # ------------------------------------------------------------------
    def ball(self):
        self.set_title("Объём шара")

        c = np.array([0, 0, BIG_Z])
        top = hemisphere(BIG_R, c, opacity=0.85)[1]
        bottom = Sphere(radius=BIG_R, v_range=[0, PI / 2], resolution=(12, 32), checkerboard_colors=HEMI_COLORS,
                        fill_opacity=0.85, stroke_width=0.4, stroke_color=BLUE_A).shift(c)
        ball = VGroup(bottom, top)
        spin = lambda m, dt: m.rotate(0.4 * dt, axis=OUT, about_point=c)

        self.play(FadeIn(ball, scale=0.6), run_time=1.5)
        ball.add_updater(spin)
        r_line = Line(c, c + BIG_R * RIGHT, color=R_COLOR, stroke_width=6)
        r_label = self.fixed(MathTex("r", color=R_COLOR, font_size=64))
        r_label.move_to(self.screen(c + BIG_R * RIGHT / 2) + UP * 0.35)
        self.remove(r_label)
        self.set_caption("Шар радиуса r", Create(r_line), Write(r_label))
        self.wait(1.5)
        ball.clear_updaters()

        floor = Circle(radius=BIG_R, stroke_width=2, stroke_color=BLUE_A,
                       fill_color=BLUE_E, fill_opacity=0.85).move_to(c)
        self.set_caption("Найдём объём половинки,\nа потом удвоим", FadeOut(r_line), FadeOut(r_label))
        self.play(FadeIn(floor), top.animate.shift(OUT * 0.6), floor.animate.shift(OUT * 0.6),
                  bottom.animate.shift(IN * 0.6))
        self.play(FadeOut(bottom, shift=IN * 0.8))
        self.big_hemi = VGroup(floor, top)

    # ------------------------------------------------------------------
    def bodies(self):
        self.hemi = hemisphere(R, np.array([LX, 0, 0]))
        self.play(ReplacementTransform(self.big_hemi, self.hemi), run_time=1.5)

        self.cyl, self.cone = cylinder_minus_cone(R, np.array([RX, 0, 0]))
        self.set_caption("Рядом — цилиндр, из\nкоторого вырезали конус", FadeIn(self.cyl))
        self.play(FadeIn(self.cone, shift=OUT * 0.5))
        self.wait(0.5)

        # Размеры: радиус полушария, радиус и высота цилиндра
        hb, cb = np.array([LX, 0, 0]), np.array([RX, 0, 0])
        lines = VGroup(
            Line(hb, hb + R * RIGHT),
            Line(cb + R * UP + R * OUT, cb + R * RIGHT + R * OUT),
            Line(cb + R * LEFT, cb + R * LEFT + R * OUT),
        ).set_stroke(R_COLOR, 6)
        labels = VGroup(
            MathTex("r", color=R_COLOR, font_size=52).move_to(self.screen(hb + R * RIGHT / 2) + DOWN * 0.3),
            MathTex("r", color=R_COLOR, font_size=52).move_to(self.screen(cb + R * OUT + R * RIGHT / 2) + UP * 0.35),
            MathTex("r", color=R_COLOR, font_size=52).move_to(self.screen(cb + R * LEFT + R * OUT / 2) + LEFT * 0.3),
        )
        self.fixed(labels)
        self.remove(labels)
        self.dims = VGroup(lines, labels)
        self.set_caption("Радиус и высота у всех — r", Create(lines), FadeIn(labels))
        self.wait(1.2)

    # ------------------------------------------------------------------
    def slices(self):
        h = ValueTracker(0.6 * R)

        plane = always_redraw(lambda: Rectangle(
            width=8.4, height=3.6, stroke_color=H_COLOR, stroke_width=2,
            fill_color=H_COLOR, fill_opacity=0.12).move_to([0, 0, h.get_value()]))
        cut_l = always_redraw(lambda: hemi_slice(h.get_value()))
        cut_r = always_redraw(lambda: cyl_slice(h.get_value()))

        self.set_caption("Разрежем оба тела\nна одной высоте h", FadeOut(self.dims))
        self.play(FadeIn(plane))
        self.play(FadeIn(cut_l), FadeIn(cut_r))
        self.wait(0.5)

        # Радиус среза полушария — по теореме Пифагора (в вертикальной плоскости y = 0)
        h0 = 0.6 * R
        hb, cb = np.array([LX, 0, 0]), np.array([RX, 0, 0])
        top_pt = hb + OUT * h0
        edge_pt = top_pt + rho_of(h0) * RIGHT
        tri = VGroup(
            Line(hb, top_pt, color=H_COLOR, stroke_width=6),
            Line(top_pt, edge_pt, color=RHO_COLOR, stroke_width=6),
            Line(hb, edge_pt, color=R_COLOR, stroke_width=6),
        )
        tri_labels = VGroup(
            MathTex("h", color=H_COLOR, font_size=52).move_to(self.screen((hb + top_pt) / 2) + LEFT * 0.3),
            MathTex(r"\rho", color=RHO_COLOR, font_size=52).move_to(self.screen((top_pt + edge_pt) / 2) + UP * 0.3),
            MathTex("r", color=R_COLOR, font_size=52).move_to(self.screen((hb + edge_pt) / 2) + RIGHT * 0.3 + DOWN * 0.2),
        )
        self.fixed(tri_labels)
        self.remove(tri_labels)
        self.set_caption("Радиус среза ρ —\nпо теореме Пифагора", Create(tri), FadeIn(tri_labels))
        pyth = self.fixed(MathTex(r"\rho^2", "=", "r^2", "-", "h^2", font_size=64).move_to(UP * 2.4))
        pyth[0].set_color(RHO_COLOR)
        pyth[2].set_color(R_COLOR)
        pyth[4].set_color(H_COLOR)
        self.remove(pyth)
        self.play(Write(pyth))
        self.wait(1.2)

        # Дырка в цилиндре: у конуса радиус = высоте
        cone_pt = cb + OUT * h0
        cone_marks = VGroup(
            Line(cb, cone_pt, color=H_COLOR, stroke_width=6),
            Line(cone_pt, cone_pt + h0 * RIGHT, color=H_COLOR, stroke_width=6),
        )
        cone_labels = VGroup(
            MathTex("h", color=H_COLOR, font_size=52).move_to(self.screen((cb + cone_pt) / 2) + LEFT * 0.3),
            MathTex("h", color=H_COLOR, font_size=52).move_to(self.screen(cone_pt + h0 * RIGHT / 2) + UP * 0.3),
        )
        self.fixed(cone_labels)
        self.remove(cone_labels)
        self.set_caption("У конуса радиус = высоте,\nзначит радиус дырки — h",
                         FadeOut(pyth), FadeOut(tri), FadeOut(tri_labels), Create(cone_marks), FadeIn(cone_labels))
        self.wait(1.2)

        # Поднимаем срезы над телами и разворачиваем к зрителю
        up_l = hemi_slice(h0)
        up_r = cyl_slice(h0)
        self.set_caption("Сравним площади срезов", FadeOut(cone_marks), FadeOut(cone_labels))
        self.play(
            Transform(up_l, lifted(hemi_slice(h0), LX)),
            Transform(up_r, lifted(cyl_slice(h0), RX)),
            run_time=1.8,
        )
        self.remove(up_l, up_r)
        up_l = always_redraw(lambda: lifted(hemi_slice(h.get_value()), LX))
        up_r = always_redraw(lambda: lifted(cyl_slice(h.get_value()), RX))
        self.add(up_l, up_r)

        label_y = self.screen([0, 0, LIFT_Z])[1] - R * LIFT_SCALE * ZOOM - 0.55
        s1 = MathTex(r"\pi", r"\rho^2", font_size=56).move_to([self.screen([LX, 0, 0])[0], label_y, 0])
        s1[1].set_color(RHO_COLOR)
        s1_full = MathTex(r"\pi", "(", "r^2", "-", "h^2", ")", font_size=56).move_to(s1)
        s2 = MathTex(r"\pi", "r^2", "-", r"\pi", "h^2", font_size=56).move_to([self.screen([RX, 0, 0])[0], label_y, 0])
        self.fixed(s1, s2)
        self.remove(s1, s2)
        self.set_caption("Слева круг, справа кольцо")
        self.play(Write(s1))
        self.fixed(s1_full)
        self.remove(s1_full)
        self.play(TransformMatchingTex(s1, s1_full))
        self.play(Write(s2))
        self.wait(0.6)

        eq = self.fixed(MathTex("=", font_size=72).move_to([0, label_y, 0]))
        self.remove(eq)
        self.set_caption("Площади равны!", Write(eq))
        self.play(Indicate(s1_full), Indicate(s2))
        self.wait(0.6)

        self.set_caption("И так на любой высоте")
        self.play(h.animate.set_value(0.1 * R), run_time=1.8)
        self.play(h.animate.set_value(0.93 * R), run_time=2.6)
        self.play(h.animate.set_value(0.5 * R), run_time=1.4)
        self.wait(0.3)

        self.set_caption("Все срезы равны —\nзначит, равны и объёмы")
        note = self.fixed(Text("(принцип Кавальери)", font_size=32, color=GREY_B).next_to(self.caption, DOWN, buff=0.15))
        self.remove(note)
        self.play(FadeIn(note))
        self.wait(1.8)

        for mob in (plane, cut_l, cut_r, up_l, up_r):
            mob.clear_updaters()
        self.play(FadeOut(VGroup(plane, cut_l, cut_r, up_l, up_r)), FadeOut(VGroup(s1_full, s2, eq, note)))

    # ------------------------------------------------------------------
    def volumes(self):
        self.set_caption("Объём половинки = объём\nцилиндра минус конус")

        line1 = MathTex(r"V_{\frac12}", "=", r"\pi r^2\cdot r", "-", r"\tfrac{1}{3}\pi r^2\cdot r",
                        font_size=64).move_to(UP * 3.1)
        line1[0].set_color(HEMI_COLOR)
        line1[2].set_color(CYL_COLOR)
        cyl_note = Text("цилиндр", font_size=30, color=CYL_COLOR).next_to(line1[2], DOWN, buff=0.15)
        cone_note = Text("конус", font_size=30, color=CONE_COLOR).next_to(line1[4], DOWN, buff=0.15)
        self.fixed(line1, cyl_note, cone_note)
        self.remove(line1, cyl_note, cone_note)

        self.play(Write(line1[:3]), FadeIn(cyl_note), Indicate(self.cyl, color=CYL_COLOR))
        # Конус вынимаем из цилиндра — это и есть «минус»
        self.play(self.cone.animate.shift(OUT * 1.9), run_time=1.2)
        self.play(Write(line1[3:]), FadeIn(cone_note))
        self.wait(0.6)
        self.play(FadeOut(self.cone, shift=OUT * 0.5))
        self.wait(0.4)

        line2 = self.fixed(MathTex(r"V_{\frac12}", "=", r"\tfrac{2}{3}", r"\pi r^3", font_size=80).move_to(line1))
        line2[0].set_color(HEMI_COLOR)
        self.remove(line2)
        self.set_caption("Упрощаем", FadeOut(VGroup(cyl_note, cone_note)))
        self.play(TransformMatchingTex(line1, line2))
        self.wait(1)

        line3 = self.fixed(MathTex("V", "=", "2", r"\cdot", r"\tfrac{2}{3}", r"\pi r^3", "=",
                                   r"\frac{4}{3}", r"\pi", "r^3", font_size=72).move_to(UP * 1.6))
        line3[0].set_color(HEMI_COLOR)
        self.remove(line3)
        self.set_caption("Целый шар — две половинки")
        self.play(Write(line3[:6]))
        self.wait(0.4)
        self.play(Write(line3[6:]))
        box = self.fixed(SurroundingRectangle(line3[7:], color=YELLOW, buff=0.15))
        self.remove(box)
        self.play(Create(box))
        self.wait(1.5)

        self.play(FadeOut(VGroup(self.hemi, self.cyl)),
                  FadeOut(VGroup(line2, line3, box, self.caption, self.title)))
        self.caption = None
        self.title = None

    # ------------------------------------------------------------------
    def outro(self):
        c = np.array([0, 0, BIG_Z])
        ball = Sphere(radius=BIG_R, resolution=(16, 32), checkerboard_colors=HEMI_COLORS,
                      fill_opacity=0.85, stroke_width=0.4, stroke_color=BLUE_A).shift(c)
        formula = MathTex("V", "=", r"\frac{4}{3}", r"\pi", "r^3", font_size=110).move_to(DOWN * 2.85)
        formula[0].set_color(HEMI_COLOR)
        sub = Text("объём шара", font_size=44, color=GREY_B).next_to(formula, DOWN, buff=0.3)
        credit = Text("Архимед, III век до н. э.", font_size=34, color=GREY_C).move_to(UP * TITLE_Y)
        self.fixed(formula, sub, credit)
        self.remove(formula, sub, credit)

        ball.add_updater(lambda m, dt: m.rotate(0.4 * dt, axis=OUT, about_point=c))
        self.play(FadeIn(ball), FadeIn(formula, shift=UP * 0.3), FadeIn(sub, shift=UP * 0.3))
        self.play(FadeIn(credit))
        self.wait(3)
