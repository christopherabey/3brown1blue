from manim import *

class VideoScene(Scene):
    def construct(self):
        # Title
        title = Text("Practical Tips for Troubleshooting CORS Issues", font_size=40).to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # Debugging tools
        debugging_tools_text = Text("Use Browser Debugging Tools", font_size=32).next_to(title, DOWN, buff=0.5)
        self.play(Write(debugging_tools_text))
        self.wait(1)

        # Showing Headers
        headers_text = Text("Inspect Network Requests", font_size=32).next_to(debugging_tools_text, DOWN, buff=0.5)
        self.play(Write(headers_text))
        self.wait(1)

        browser_image = self.create_browser().next_to(headers_text, DOWN, buff=0.5)
        self.play(FadeIn(browser_image))
        self.wait(1)

        origin_header = Text("Origin", font_size=20, color=YELLOW).next_to(browser_image, LEFT, buff=0.5)
        allow_origin_header = Text("Access-Control-Allow-Origin", font_size=20, color=GREEN).next_to(browser_image, RIGHT, buff=0.5)
        self.play(Write(origin_header), Write(allow_origin_header))
        self.wait(2)

        # Debugging disclaimer
        disclaimer = Text("Use CORS Disable Extensions Only for Development and Testing", font_size=28).next_to(browser_image, DOWN, buff=1)
        self.play(Write(disclaimer))
        self.wait(2)

        # End Scene
        thanks_text = Text("Thanks for joining me today,\nand happy coding!", font_size=36).next_to(disclaimer, DOWN, buff=1)
        self.play(Write(thanks_text))
        self.wait(3)

    def create_browser(self):
        browser = VGroup()
        
        # Browser window outline
        outline = Rectangle(width=10, height=6, color=WHITE)
        address_bar = Rectangle(width=9.5, height=0.5, color=BLUE).shift(UP*2.3)
        
        # Address bar elements
        address_text = Text("http://localhost", font_size=20, color=WHITE).move_to(address_bar.get_center())
        
        # Network panel
        network_panel = Rectangle(width=9.5, height=4.5, color=GRAY).shift(DOWN*0.75)
        
        # Header examples
        origin_header_example = Text("Origin: http://example.com", font_size=18, color=YELLOW).move_to(network_panel.get_center()).shift(UP*1.5)
        allow_origin_header_example = Text("Access-Control-Allow-Origin: *", font_size=18, color=GREEN).move_to(network_panel.get_center())
        
        browser.add(outline, address_bar, address_text, network_panel, origin_header_example, allow_origin_header_example)
        return browser
