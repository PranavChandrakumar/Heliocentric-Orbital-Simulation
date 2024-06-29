import pygame
import sys
import math
from pygame.locals import QUIT
import pygame_gui

class SolarSystemApp:
    def __init__(self, planets):
        pygame.init()

        self.width, self.height = 800, 1000 #GUI dimensions
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Solar System Simulation")

        self.clock = pygame.time.Clock()

        self.planets = planets
        self.slider_value = 1  # Default value
        self.show_planet_gui = False  # Flag to control whether to show the planet GUI

        self.create_gui()

        # Calculate the orbital periods based on provided ratios
        for planet in self.planets:
            planet["angle"] = 0
            planet["path"] = []

            # Initialize the orbital path
            for j in range(0, 360):
                x = int(self.width / 2 + planet["distance"] * math.cos(math.radians(j)))
                y = int(self.height / 2 + planet["distance"] * math.sin(math.radians(j)))
                planet["path"].append((x, y))

            # Close the path by appending the starting point
            planet["path"].append(planet["path"][0])

        self.update_positions()

    def create_gui(self):
        self.manager = pygame_gui.UIManager((self.width, self.height))
        slider_rect = pygame.Rect(10, 10, 200, 20)
        self.slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=slider_rect,
            start_value=1,
            value_range=(0, 100), #only int values
            manager=self.manager
        )

        label_rect = pygame.Rect(220, 10, 220, 20)
        self.label = pygame_gui.elements.UILabel(
            relative_rect=label_rect,
            text="1 Year",
            manager=self.manager
        )

    def update_positions(self):
        while True:
            time_increment = self.slider.get_current_value() *  (2*math.pi)/(29.8 / (149.6 * 10e5)) # Use slider's current value, multiply by the amount of time to get one full rotation of earth

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                # Process events for the GUI manager
                self.manager.process_events(event)

            self.screen.fill((0, 0, 0))

            # Draw a small yellow circle at the center to represent the Sun
            pygame.draw.circle(self.screen, pygame.Color("Yellow"), (self.width / 2, self.height / 2), 10)

            if self.show_planet_gui and self.current_planet:
                # Draw the clicked planet at the center
                x = self.width / 2
                y = self.height / 2
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
            self.label.set_text(f"{int(self.slider.get_current_value())} Earth Years per Second")

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    planets_data = [ # These values are published online and available through nasa.gov
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
    
