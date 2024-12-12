from PIL import Image, ImageDraw, ImageFont
import hashlib
import base64
import io

class FingerprintService:
    def generate(self) -> str:
        """Generate a unique fingerprint by hashing the canvas-based image."""
        unique_url = self.get_unique_url_from_canvas()
        return self.hash(unique_url)

    def hash(self, input_data: str) -> str:
        """Hash a given input string using MD5."""
        return hashlib.md5(input_data.encode('utf-8')).hexdigest()

    def get_unique_url_from_canvas(self) -> str:
        """Create a unique canvas-like image and return its data URL."""
        # Create an image with RGBA mode
        width, height = 200, 200
        image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)

        # Text and shapes for rendering
        text = "❡ I Want me a Tasty Fruit Salad!\n\r <🍏🍎🍐🍊🍋🍌🍉🍇🍓🍈🍒🍍🥝> ă 4fds ứ"

        # Load a Unicode-compatible font (e.g., DejaVu, Arial, or Noto)
        try:
            font = ImageFont.truetype("arial.ttf", 14)  # Ensure the font file exists
        except IOError:
            raise Exception("Font file not found. Please install a Unicode-compatible font like Arial or DejaVu.")

        # Draw text and shapes
        draw.text((2, 15), text, fill=(255, 102, 0), font=font)  # Orange text
        draw.text((4, 17), text, fill=(0, 102, 153, 178), font=font)  # Semi-transparent blue text
        draw.ellipse((0, 0, 100, 100), fill=(255, 0, 255))  # Magenta circle
        draw.ellipse((50, 0, 150, 100), fill=(0, 255, 255))  # Cyan circle
        draw.ellipse((25, 50, 125, 150), fill=(255, 255, 0))  # Yellow circle

        # Create a mask for 'evenodd' effect
        mask = Image.new('L', (width, height), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((25, 25, 175, 175), fill=255)
        mask_draw.ellipse((75, 75, 125, 125), fill=0)
        image.putalpha(mask)

        # Convert the image to a base64 data URL
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{img_base64}"

# Usage example
service = FingerprintService()
fingerprint = service.generate()
print("Fingerprint:", fingerprint)
