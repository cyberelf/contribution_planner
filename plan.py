import datetime
from enum import Enum
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from icalendar import Calendar as ICalender, Event


GithubContributionLevels = 4

class Mode(Enum):
    """Mode for the GitHubPlanner colors"""
    DEPTH = "depth"
    PLAIN = "plain"
    
class Calendar:
    """Represents a GitHub contribution calendar"""    
    def __init__(self, year: int, plan_matrix: np.ndarray):
        self._year = year
        self._matrix = plan_matrix
    
    def _get_first_sunday(self) -> datetime:
        """Returns the first Sunday of the year"""
        date = datetime.datetime(self._year, 1, 1)
        # Calculate how many days to add to get to the first Sunday
        days_to_add = (6 - date.weekday()) % 7  # weekday() returns 0 for Monday, 6 for Sunday
        first_sunday = date + datetime.timedelta(days=days_to_add)
        return first_sunday
    
    def get_contribution_days(self) -> List[Tuple[datetime.datetime, int]]:
        start_date = self._get_first_sunday()
        contribution_days = []
        # Calculate the date for each contribution in the matrix
        for week in range(self._matrix.shape[1]):  # Iterate over weeks (columns)
            for day in range(self._matrix.shape[0]):  # Iterate over days (rows)
                if self._matrix[day, week] == 0:
                    continue
                # Calculate the date for this cell
                current_date = start_date + datetime.timedelta(days=week*7 + day)
                # Append the date and contribution level to the list
                contribution_days.append((current_date, self._matrix[day, week]))

        return contribution_days
    
    def to_image(self, cell_size: int = 20, padding: int = 2) -> Image:
        """Creates an image representing the contribution calendar"""
        # Define colors for different levels of contributions (feel free to adjust)
        colors = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]  # GitHub color scheme

        # Calculate the size of the full image
        width = cell_size * self._matrix.shape[1] + padding * (self._matrix.shape[1] - 1)
        height = cell_size * self._matrix.shape[0] + padding * (self._matrix.shape[0] - 1)
        image = Image.new('RGB', (width, height), color=colors[0])
        draw = ImageDraw.Draw(image)

        # Draw each cell
        for row in range(self._matrix.shape[0]):
            for col in range(self._matrix.shape[1]):
                contribution_level = self._matrix[row, col]
                color = colors[contribution_level]

                # Calculate position and size of each cell
                top_left = (col * (cell_size + padding), row * (cell_size + padding))
                bottom_right = (top_left[0] + cell_size, top_left[1] + cell_size)
                draw.rectangle([top_left, bottom_right], fill=color)

        return image
    
    def save_icalendar(self, file_name: str='contributions.ics') -> str:
        # Create a calendar
        cal = ICalender()

        for day, contribution in self.get_contribution_days():
            event = Event()
            event.add('summary', f'Make {contribution} contributions')
            event.add('dtstart', day.date())
            event.add('dtend', (day + datetime.timedelta(days=1)).date())
            cal.add_component(event)

        # Write the calendar to an ics file
        with open(file_name, 'wb') as f:
            f.write(cal.to_ical())

        return file_name

class GitHubPlanner:
    def __init__(self, font_path: str, mode: Mode):
        self._font_size = 30
        self.font_path = font_path
        self.mode = mode
    
    def plan(self, text: str, year: Optional[int]) -> Calendar:
        """Creates a calendar with the given text"""
        if year is None:
            year = datetime.now().year
            
        ascii_image = self._text_to_image(text)
        contribution_matrix = self._image_to_contribution(ascii_image)
        
        return Calendar(year, contribution_matrix)

    def _text_to_image(self, text: str) -> Image:
        """Converts text to a black and white image"""
        image_mode = 'L' if self.mode == Mode.DEPTH else '1'
        font = ImageFont.truetype(self.font_path, self._font_size)
        dummy_image = Image.new(image_mode, (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_image)
        width, height = dummy_draw.textbbox((0,0), text, font=font, spacing=10, align='center')[2:]
        image = Image.new(image_mode, (width, height), "black")
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), text, fill="white", font=font, spacing=10)

        # Crop the image to remove unnecessary whitespace
        # Find the bounding box of the non-white area
        bbox = image.getbbox()
        if bbox:
            image = image.crop(bbox)
        return image

    def _image_to_contribution(self, image: Image, size: Tuple[int, int]=(52,7)) -> np.ndarray:
        # Calculate the aspect ratio of the original image
        aspect_ratio = image.width / image.height

        # Calculate new dimensions based on aspect ratio
        new_height = int(size[1])
        new_width = min(int(new_height * aspect_ratio), size[0])

        # Resize image to fit GitHub contributions while maintaining aspect ratio
        img_resized = image.resize((new_width, new_height), Image.LANCZOS)

        # Create a new blank image with the target size
        final_img = Image.new('L', size, color='black')
        # Calculate top-left position to paste the resized image for centering
        paste_x = (size[0] - new_width) // 2
        paste_y = (size[1] - new_height) // 2

        # Paste the resized image onto the center of the blank image
        final_img.paste(img_resized, (paste_x, paste_y))

        # Convert image to numpy array
        img_array = np.array(final_img)

        # Normalizing the array to have values between 0 and 4
        min_val, max_val = img_array.min(), img_array.max()
        if min_val == max_val:
            return np.zeros_like(img_array)
        max_level = GithubContributionLevels if self.mode == Mode.DEPTH else 1
        normalized_array = (img_array - min_val) / (max_val - min_val) * max_level
        contribution_matrix = np.rint(normalized_array).astype(int)

        return contribution_matrix


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='GitHub Contribution Planner')
    parser.add_argument('text', help='Text to plan')
    parser.add_argument('-y', '--year', type=int, help='Year to plan for')
    parser.add_argument('--font', type=str, help='Font to use')
    parser.add_argument('-c', '--commit-level', action="store_true", help='Use commit level colors')
    parser.add_argument('-o', '--save-icalendar', action="store_true", help='Save to icalendar file')
    parser.add_argument('-s', '--save-image', action="store_true", help='show image')
    args = parser.parse_args()
    
    if not args.save_icalendar and not args.save_image:
        parser.error("Either --save-icalendar or --save-image is required")
    
    font_path = args.font if args.font else "font/DejaVuSans-Bold.ttf"
    mode = Mode.DEPTH if args.commit_level else Mode.PLAIN
    year = args.year if args.year else datetime.datetime.now().year
        
    planner = GitHubPlanner(font_path, mode)
    calendar = planner.plan(args.text, year)
    
    if args.save_image:
        calendar.to_image().save("calendar.png")
    
    if args.save_icalendar:
        calendar.save_icalendar("contributions.ics")
