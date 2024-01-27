import pygame
import sys
import math
from pygame.locals import QUIT
import pygame_gui

class PlanetButton(pygame_gui.elements.UIButton):
    def __init__(self, relative_rect, text, manager, container, planet_data, app):
        super().__init__(relative_rect, text, manager, container)
        self.planet_data = planet_data
        self.app = app

    def disable(self):
        self.visible = False
        self.enabled = False

class SolarSystemApp:
    def __init__(self, planets):
        pygame.init()

        self.width, self.height = 800, 1000
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Solar System Simulation")

        self.clock = pygame.time.Clock()

        self.planets = planets
        self.current_planet = None
        self.slider_value = 1  # Default value
        self.planet_buttons = []  # Store planet buttons
        self.show_planet_gui = False  # Flag to control whether to show the planet GUI
        self.legend_panel = None  # Initialize the legend_panel attribute

        self.create_gui()

        # Calculate the orbital periods based on provided ratios
        for planet in self.planets:
            planet["angle"] = 0
            planet["path"] = []

            # Initialize the orbital path
            for j in range(0, 361):
                x = int(self.width // 2 + planet["distance"] * math.cos(math.radians(j)))
                y = int(self.height // 2 + planet["distance"] * math.sin(math.radians(j)))
                planet["path"].append((x, y))

            # Close the path by appending the starting point
            planet["path"].append(planet["path"][0])

        self.update_positions()

    def create_gui(self):
        self.manager = pygame_gui.UIManager((self.width, self.height))
        self.legend_panel = None  # Add this line

        slider_rect = pygame.Rect(10, 10, 200, 20)
        self.slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=slider_rect,
            start_value=1,
            value_range=(0.0, 100),
            manager=self.manager
        )

        label_rect = pygame.Rect(220, 10, 50, 20)
        self.label = pygame_gui.elements.UILabel(
            relative_rect=label_rect,
            text="50",
            manager=self.manager
        )

        # Add legend
        legend_rect = pygame.Rect(10, self.height - 50, self.width - 20, 40)
        self.legend_panel = pygame_gui.elements.UIPanel(
            relative_rect=legend_rect,
            starting_layer_height=2,
            manager=self.manager
        )

        for i, planet_data in enumerate(self.planets):
            label_rect = pygame.Rect(10 + i * 80, 10, 80, 20)
            planet_button = PlanetButton(
                relative_rect=label_rect,
                text=planet_data['name'],
                manager=self.manager,
                container=self.legend_panel,
                planet_data=planet_data,
                app=self
            )
            planet_button.bg_color = pygame.Color(planet_data['color'])  # Set background color

            # Workaround to set text color
            planet_button.image.set_colorkey((0, 0, 0))  # Set black as transparent
            planet_button.image = planet_button.image.convert_alpha()
            planet_button.image.fill(pygame.Color(planet_data['color']), special_flags=pygame.BLEND_RGBA_MULT)

            self.planet_buttons.append(planet_button)

        # Add Real Time button
        button_rect = pygame.Rect(280, 10, 100, 20)
        self.real_time_button = pygame_gui.elements.UIButton(
            relative_rect=button_rect,
            text="1 Day/tick",
            manager=self.manager
        )

        # Add Back to Solar System button (initially hidden)
        back_button_rect = pygame.Rect(400, 10, 150, 20)
        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=back_button_rect,
            text="Back to Solar System",
            manager=self.manager
        )
        self.back_button.disable()

    def show_planet_gui(self, planet_button):
        # Function to create a new GUI with the clicked planet as the center
        self.current_planet = planet_button.planet_data
        self.show_planet_gui = True
        for planet_button in self.planet_buttons:
            planet_button.disable()
        self.back_button.enable()

    def set_slider_to_real_time(self):
        # Function to set the slider to a specific value (0.003 in this case)
        self.slider.set_current_value(0.003)

    def update_positions(self):
        while True:
            time_increment = self.slider.get_current_value() * (3.154e7)  # Use slider's current value

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                # Process events for the GUI manager
                self.manager.process_events(event)

                if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.real_time_button:
                        self.set_slider_to_real_time()

                    elif event.ui_element == self.back_button:
                        # Show the planet buttons and hide the back button
                        for planet_button in self.planet_buttons:
                            planet_button.enable()
                        self.back_button.disable()
                        self.current_planet = None
                        self.show_planet_gui = False

            self.screen.fill((0, 0, 0))

            # Draw a small yellow circle at the center to represent the sun
            pygame.draw.circle(self.screen, pygame.Color("Yellow"), (self.width // 2, self.height // 2), 10)

            if self.show_planet_gui and self.current_planet:
                # Draw the clicked planet at the center
                x = self.width // 2
                y = self.height // 2
                pygame.draw.circle(self.screen, pygame.Color(self.current_planet["color"]), (x, y), 5)

            else:
                # Draw all planets in their orbits
                for planet in self.planets:
                    if self.show_planet_gui and self.current_planet and planet != self.current_planet:
                        continue  # Skip planets if showing a specific planet in the center

                    planet["angle"] += time_increment * planet["orbital_ratio"]

                    x = int(self.width / 2 + planet["distance"] * math.cos(math.radians(planet["angle"])))
                    y = int(self.height / 2 + planet["distance"] * math.sin(math.radians(planet["angle"])))

                    pygame.draw.circle(self.screen, pygame.Color(planet["color"]), (x, y), 5)
                    pygame.draw.aalines(self.screen, pygame.Color(planet["color"]), False, planet["path"], 1)

            self.manager.update(time_increment)
            self.manager.draw_ui(self.screen)

            # Update the label text with the current slider value
            self.label.set_text(f"{int(self.slider.get_current_value())}")

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    planets_data = [
        {"name": "Mercury", "distance": 40, "color": "Gray", "orbital_ratio": (47.4 / (57.9 * 10e5))},
        {"name": "Venus", "distance": 80, "color": "Orange", "orbital_ratio": (35 / (108.2 * 10e5))},
        {"name": "Earth", "distance": 120, "color": "Blue", "orbital_ratio": (29.8 / (149.6 * 10e5))},
        {"name": "Mars", "distance": 160, "color": "Red", "orbital_ratio": (24.1 / (228 * 10e5))},
        {"name": "Jupiter", "distance": 200, "color": "Brown", "orbital_ratio": (13.1 / (778.5 * 10e5))},
        {"name": "Saturn", "distance": 240, "color": "Gold", "orbital_ratio": (9.7 / (1432 * 10e5))},
        {"name": "Uranus", "distance": 280, "color": "Cyan", "orbital_ratio": (6.8 / (2867 * 10e5))},
        {"name": "Neptune", "distance": 320, "color": "Blue", "orbital_ratio": (5.4 / (4515 * 10e5))},
    ]

    app = SolarSystemApp(planets_data)
    app.create_gui()  # Move GUI creation outside of the update loop
    app.update_positions()