from manim import *


class BluetoothExplanation(Scene):
    def construct(self):
        # Title
        title = Text("How Bluetooth Works", font_size=48)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))

        # Introduction to Bluetooth
        intro = Text(
            "Bluetooth is a wireless technology for exchanging data over short distances.",
            font_size=24,
        )
        self.play(Write(intro))
        self.wait(2)
        self.play(FadeOut(intro))

        # Device Pairing
        pairing_title = Text("Device Pairing", font_size=36)
        self.play(Write(pairing_title))
        self.play(pairing_title.animate.to_edge(UP))

        phone = Circle(radius=0.5, color=BLUE).shift(LEFT * 3)
        phone_label = Text("Phone", font_size=24).next_to(phone, DOWN)
        laptop = Circle(radius=0.5, color=GREEN).shift(RIGHT * 3)
        laptop_label = Text("Laptop", font_size=24).next_to(laptop, DOWN)
        self.play(
            FadeIn(phone), Write(phone_label), FadeIn(laptop), Write(laptop_label)
        )

        pairing = Text("Pairing Request", font_size=24)
        pairing_arrow = Arrow(start=phone.get_right(), end=laptop.get_left(), buff=0.1)
        self.play(Write(pairing), Create(pairing_arrow))
        self.wait(1)
        self.play(FadeOut(pairing), FadeOut(pairing_arrow))

        # Pairing accepted
        paired = Text("Pairing Accepted", font_size=24)
        paired_arrow = Arrow(start=laptop.get_left(), end=phone.get_right(), buff=0.1)
        self.play(Write(paired), Create(paired_arrow))
        self.wait(1)
        self.play(FadeOut(paired), FadeOut(paired_arrow))

        # Data Transfer
        data_title = Text("Data Transfer", font_size=36)
        self.play(Transform(pairing_title, data_title))

        data_packet = Text("Data Packet", font_size=24)
        data_arrow = Arrow(start=phone.get_right(), end=laptop.get_left(), buff=0.1)
        self.play(Write(data_packet), Create(data_arrow))
        self.wait(1)
        self.play(FadeOut(data_packet), FadeOut(data_arrow))

        data_packet = Text("Data Packet", font_size=24)
        data_arrow = Arrow(start=laptop.get_left(), end=phone.get_right(), buff=0.1)
        self.play(Write(data_packet), Create(data_arrow))
        self.wait(1)
        self.play(FadeOut(data_packet), FadeOut(data_arrow))

        # Signal Range
        range_title = Text("Signal Range", font_size=36)
        self.play(Transform(pairing_title, range_title))

        signal_range = Circle(radius=3, color=BLUE).shift(LEFT * 3)
        range_text = Text("10 meters (Class 2)", font_size=24).next_to(
            signal_range, DOWN
        )
        self.play(Create(signal_range), Write(range_text))
        self.wait(2)

        self.play(
            FadeOut(phone),
            FadeOut(laptop),
            FadeOut(phone_label),
            FadeOut(laptop_label),
            FadeOut(signal_range),
            FadeOut(range_text),
            FadeOut(pairing_title),
        )

        # Conclusion
        conclusion = Text(
            "Bluetooth enables easy and wireless communication between devices.",
            font_size=24,
        )
        self.play(Write(conclusion))
        self.wait(3)


# To run the scene, use:
# manim -pql <filename>.py BluetoothExplanation
