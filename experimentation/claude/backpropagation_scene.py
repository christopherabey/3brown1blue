from manim import *


class BackpropagationScene(Scene):
    def construct(self):
        # Create a simple neural network structure
        network = VGroup()
        layers = [3, 4, 2]
        for i, layer_size in enumerate(layers):
            layer = VGroup(*[Circle(radius=0.2) for _ in range(layer_size)])
            layer.arrange(DOWN, buff=0.5)
            network.add(layer)
        network.arrange(RIGHT, buff=1.5)
        self.add(network)

        # Add labels
        input_label = Text("Input").next_to(network[0], UP)
        hidden_label = Text("Hidden").next_to(network[1], UP)
        output_label = Text("Output").next_to(network[2], UP)
        self.add(input_label, hidden_label, output_label)

        # Forward pass animation
        forward_arrows = VGroup()
        for i in range(len(layers) - 1):
            layer_arrows = VGroup(
                *[
                    Arrow(start.get_right(), end.get_left(), buff=0.1)
                    for start in network[i]
                    for end in network[i + 1]
                ]
            )
            forward_arrows.add(layer_arrows)

        self.play(Create(forward_arrows), run_time=2)
        self.wait()

        # Backward pass animation
        backward_arrows = VGroup()
        for i in range(len(layers) - 1, 0, -1):
            layer_arrows = VGroup(
                *[
                    Arrow(end.get_left(), start.get_right(), buff=0.1, color=RED)
                    for start in network[i - 1]
                    for end in network[i]
                ]
            )
            backward_arrows.add(layer_arrows)

        self.play(Create(backward_arrows), run_time=2)
        self.wait()

        # Update weights animation
        weight_updates = VGroup(
            *[
                Text("Δw", font_size=24).move_to(arrow.get_center())
                for layer in forward_arrows
                for arrow in layer
            ]
        )

        self.play(Write(weight_updates), run_time=2)
        self.wait(2)

        # Clean up
        self.play(
            FadeOut(forward_arrows),
            FadeOut(backward_arrows),
            FadeOut(weight_updates),
            run_time=2,
        )
        self.wait()
