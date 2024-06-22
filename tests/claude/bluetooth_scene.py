from manim import *


class BluetoothExplanationScene(Scene):
    def construct(self):
        # Set up devices
        phone = RoundedRectangle(height=2, width=1, corner_radius=0.1).set_fill(
            GRAY, opacity=0.5
        )
        phone_label = Text("Phone").next_to(phone, DOWN)
        phone_group = VGroup(phone, phone_label).to_edge(LEFT)

        # Create simple headphones shape using circles and rectangles
        earpiece = Circle(radius=0.3, color=GRAY).set_fill(GRAY, opacity=0.5)
        band = AnnularSector(
            inner_radius=0.8, outer_radius=1, angle=PI, start_angle=PI / 2, color=GRAY
        ).set_fill(GRAY, opacity=0.5)
        headphones = VGroup(
            earpiece.copy().shift(LEFT * 0.5), earpiece.copy().shift(RIGHT * 0.5), band
        )
        headphones_label = Text("Headphones").next_to(headphones, DOWN)
        headphones_group = VGroup(headphones, headphones_label).to_edge(RIGHT)

        self.play(Create(phone_group), Create(headphones_group))
        self.wait()

        # Bluetooth logo (simplified)
        bluetooth_logo = (
            VGroup(
                RegularPolygon(n=3, stroke_width=0, fill_opacity=1, fill_color=BLUE)
                .rotate(TAU / 4)
                .scale(0.3),
                Line(UP * 0.3, DOWN * 0.3, color=BLUE),
                Line(UP * 0.3 + RIGHT * 0.2, DOWN * 0.3 + LEFT * 0.2, color=BLUE),
            )
            .scale(0.5)
            .next_to(phone, UP)
        )
        self.play(FadeIn(bluetooth_logo))
        self.wait()

        # Device discovery
        discovery_waves = [
            AnnularSector(
                inner_radius=0.5,
                outer_radius=0.5 + 0.5 * i,
                angle=TAU * 3 / 4,
                start_angle=TAU / 6,
                color=BLUE,
                fill_opacity=0.3 - 0.1 * i,
            ).move_to(phone)
            for i in range(3)
        ]

        self.play(
            AnimationGroup(*[Create(wave) for wave in discovery_waves], lag_ratio=0.5)
        )
        self.wait()

        # Headphones detected
        checkmark = Text("✓", color=GREEN).next_to(headphones, UP)
        self.play(Write(checkmark))
        self.wait()

        # Pairing process
        pairing_line = DashedLine(
            phone.get_right(), headphones.get_left(), color=YELLOW
        )
        pairing_text = Text("Pairing...", color=YELLOW).next_to(pairing_line, UP)

        self.play(Create(pairing_line), Write(pairing_text))
        self.wait()

        paired_text = Text("Paired!", color=GREEN).next_to(pairing_line, UP)
        self.play(
            Transform(pairing_text, paired_text), pairing_line.animate.set_color(GREEN)
        )
        self.wait()

        # Data transfer
        data_packets = VGroup(
            *[Square(side_length=0.1, fill_opacity=1, color=BLUE) for _ in range(5)]
        ).arrange(RIGHT, buff=0.05)
        data_packets.next_to(phone, RIGHT)

        def transfer_data(data):
            self.play(data.animate.move_to(headphones.get_left() + LEFT * 0.2))
            self.play(FadeOut(data))

        for packet in data_packets:
            transfer_data(packet)

        self.wait()

        # Clean up
        self.play(
            FadeOut(phone_group),
            FadeOut(headphones_group),
            FadeOut(bluetooth_logo),
            FadeOut(checkmark),
            FadeOut(pairing_line),
            FadeOut(pairing_text),
            *[FadeOut(wave) for wave in discovery_waves]
        )
        self.wait()

        # Final text
        final_text = Text(
            "Bluetooth: Wireless communication\nfor short-range devices", font_size=36
        )
        self.play(Write(final_text))
        self.wait(2)
