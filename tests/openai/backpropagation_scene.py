from manim import *


class Backpropagation(Scene):
    def construct(self):
        # Title
        title = Text("Backpropagation in Neural Networks", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))

        # Define colors
        blue = BLUE
        brown = "#8B4513"  # Define a brown color as a hex string

        # Neural network layers
        input_layer = VGroup(*[Circle(radius=0.3, color=blue) for _ in range(3)])
        hidden_layer = VGroup(*[Circle(radius=0.3, color=blue) for _ in range(3)])
        output_layer = VGroup(*[Circle(radius=0.3, color=brown) for _ in range(1)])

        input_layer.arrange(DOWN, buff=0.5).shift(LEFT * 4)
        hidden_layer.arrange(DOWN, buff=0.5)
        output_layer.arrange(DOWN, buff=0.5).shift(RIGHT * 4)

        self.play(Create(input_layer), Create(hidden_layer), Create(output_layer))

        # Arrows between layers
        arrows_input_hidden = VGroup(
            *[
                Arrow(
                    start=input_layer[i].get_right(),
                    end=hidden_layer[j].get_left(),
                    buff=0.1,
                )
                for i in range(3)
                for j in range(3)
            ]
        )
        arrows_hidden_output = VGroup(
            *[
                Arrow(
                    start=hidden_layer[i].get_right(),
                    end=output_layer[j].get_left(),
                    buff=0.1,
                )
                for i in range(3)
                for j in range(1)
            ]
        )

        self.play(Create(arrows_input_hidden), Create(arrows_hidden_output))

        # Forward pass explanation
        forward_pass = Text("Forward Pass", font_size=24)
        self.play(Write(forward_pass))
        self.play(forward_pass.animate.next_to(hidden_layer, UP))

        # Forward pass flow
        self.play(Indicate(input_layer[0]), Indicate(hidden_layer[0]))
        self.play(Indicate(input_layer[1]), Indicate(hidden_layer[1]))
        self.play(Indicate(input_layer[2]), Indicate(hidden_layer[2]))
        self.play(Indicate(hidden_layer[0]), Indicate(output_layer[0]))
        self.play(Indicate(hidden_layer[1]), Indicate(output_layer[0]))
        self.play(Indicate(hidden_layer[2]), Indicate(output_layer[0]))

        self.play(FadeOut(forward_pass))

        # Backward pass explanation
        backward_pass = Text("Backward Pass (Backpropagation)", font_size=24)
        self.play(Write(backward_pass))
        self.play(backward_pass.animate.next_to(hidden_layer, UP))

        # Backward pass flow
        self.play(Indicate(output_layer[0]), Indicate(hidden_layer[0]))
        self.play(Indicate(output_layer[0]), Indicate(hidden_layer[1]))
        self.play(Indicate(output_layer[0]), Indicate(hidden_layer[2]))
        self.play(Indicate(hidden_layer[0]), Indicate(input_layer[0]))
        self.play(Indicate(hidden_layer[1]), Indicate(input_layer[1]))
        self.play(Indicate(hidden_layer[2]), Indicate(input_layer[2]))

        self.play(FadeOut(backward_pass))

        # Conclusion
        conclusion = Text(
            "Backpropagation adjusts weights to minimize error", font_size=24
        )
        self.play(Write(conclusion))
        self.play(conclusion.animate.to_edge(DOWN))

        self.wait(3)


# To run the scene, use:
# manim -pql <filename>.py Backpropagation
