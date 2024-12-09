import requests
import base64
import os
from dotenv import load_dotenv
from PIL import Image

class CaptchaSolver:
    def __init__(self, api_key=None):
        load_dotenv()  # Load environment variables
        self.api_key = api_key or os.getenv('API_KEY')  # Use API key from env if not provided
        if not self.api_key:
            raise ValueError("API_KEY is missing. Set it in .env or pass it as an argument.")

    @staticmethod
    def convert_gif_to_png(image_path):
        if image_path.lower().endswith(".gif"):
            # Open the GIF image
            with Image.open(image_path) as img:
                # Extract the first frame if it's animated
                img = img.convert("RGB")  # Convert to RGB mode
                png_path = image_path.replace(".gif", ".png")
                img.save(png_path, "PNG")
                print(f"Converted GIF to PNG: {png_path}")
                return png_path
        return image_path

    @staticmethod
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def solve_captcha(self, image_path, model="gpt-4o"):
        # Convert GIF to PNG if necessary
        image_path = self.convert_gif_to_png(image_path)

        # Encode the image
        base64_image = self.encode_image(image_path)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What’s in this image? Only tell the captcha code, nothing else."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        # Handle the response
        if response.status_code != 200:
            raise Exception(f"API Request Failed: {response.status_code}, {response.text}")

        try:
            captch_code = response.json()["choices"][0]["message"]["content"].strip()
            return captch_code
        except KeyError as e:
            raise Exception(f"Error parsing response: {e}, Response: {response.json()}")

# Usage example (can be placed in a separate file)
if __name__ == "__main__":
    solver = CaptchaSolver()  # Automatically loads API key from .env
    captcha_code = solver.solve_captcha("captcha.gif")  # Handles both GIF and PNG
    print(f"Decoded CAPTCHA: {captcha_code}")
