from flask import Flask, request, jsonify, render_template, send_file
import google.generativeai as genai
import base64
import io
from PIL import Image, ImageDraw, ImageFont, ImageStat
import textwrap
from flask_cors import CORS
import logging
import random
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request

# Load environment variables from .env
load_dotenv()


# Get API key from environment
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY not found in environment variables. Please set it in .env file.")

app = Flask(__name__, template_folder='templates')
CORS(app)  # Enable CORS globally
genai.configure(api_key=API_KEY)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# ---------- FRONTEND ROUTES ----------
@app.route("/landing")
def landing():
    return render_template("landing.html") 

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/caption')
def caption():
    return render_template('caption.html')

@app.route('/meme')
def meme():
    return render_template('meme.html')

@app.route('/story')
def story():
    return render_template('story.html')

# ---------- CAPTION & STORY ----------
@app.route("/analyze", methods=["POST"])
def analyze_image():
    try:
        data = request.get_json()
        image_base64 = data.get("image")
        gen_type = data.get("type", "caption")
        tone = data.get("tone", "")
        context = data.get("context", "")
        hashtags = data.get("hashtags", False)

        if not image_base64:
            return jsonify({"error": "No image provided"}), 400

        if gen_type == "caption":
            prompt = (
                f"Generate exactly 2 short, catchy, modern social media captions "
                f"for this image in a {tone} tone about {context}. "
                f"They should sound like Instagram/Twitter captions people post today. "
                f"Output ONLY the 2 captions, each on a new line, with no numbers, no bullet points, "
                f"no introductions, and no explanations."
            )
            if hashtags:
                prompt += " Add 2-4 relevant trending hashtags to each caption."
        elif gen_type == "story":
            prompt = (
                f"Write one {tone} short story inspired by this image. "
                f"Do not add explanations, only output the story."
            )
        else:
            prompt = "Describe this image in a creative way, output only the description."

        # Prepare image for Gemini
        image_part = {
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": image_base64  # raw base64 string (no data URL prefix)
            }
        }

        # Call Gemini model
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([image_part, prompt])

        app.logger.debug(f"Gemini Raw Response: {response}")
        text = getattr(response, "text", "")
        if text is None:
            text = ""
        text = text.strip()

        # --- Response Handling ---
        if gen_type == "caption":
            # Normalize and split into lines
            raw_captions = text.replace("\r", "").split("\n")
            captions = [cap.strip() for cap in raw_captions if cap.strip()]

            # Ensure exactly 2 captions
            if len(captions) >= 2:
                captions = captions[:2]
            elif len(captions) == 1:
                captions = [captions[0], captions[0] + " ✨"]
            else:
                captions = ["No caption generated", "No caption generated"]

            app.logger.info(f"Final Captions Sent: {captions}")
            return jsonify({"caption1": captions[0], "caption2": captions[1]})

        elif gen_type == "story":
            if not text:
                return jsonify({"error": "No story generated"}), 500
            return jsonify({"story_title": f"A {tone.capitalize()} Story", "story": text})

        else:
            if not text:
                return jsonify({"error": "No description generated"}), 500
            return jsonify({"result": text})

    except Exception as e:
        app.logger.error("Error in /analyze endpoint", exc_info=True)
        return jsonify({"error": str(e)}), 500

# ---------- MEME GENERATOR ----------
@app.route("/generate-meme", methods=["POST"])
def generate_meme():
    try:
        logging.debug("Received /generate-meme request")
        image_file = request.files.get("image")
        if not image_file:
            return "No image provided.", 400

        # NEW: optional controls
        tone = request.form.get("tone", "").strip().lower()  # "random" or one of: funny/sarcastic/relatable/dark/wholesome/absurdist/motivational
        font_size_raw = request.form.get("font_size", "").strip()
        font_color_hex = request.form.get("font_color", "#FFFFFF").strip()
        position = request.form.get("position", "bottom").strip().lower()  # "bottom" (default) or "top"

        # Load image
        image_bytes = image_file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        logging.debug("Image loaded successfully")

        # Prepare base64 for Gemini
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        # Style selection (keeps your original random if no tone provided)
        styles = [
            "Make it sarcastic.",
            "Make it relatable.",
            "Make it dark humor.",
            "Make it wholesome.",
            "Make it absurdist."
        ]
        tone_map = {
            "funny": "Make it funny.",
            "sarcastic": "Make it sarcastic.",
            "relatable": "Make it relatable.",
            "dark": "Make it dark humor.",
            "dark humor": "Make it dark humor.",
            "wholesome": "Make it wholesome.",
            "absurdist": "Make it absurdist.",
            "motivational": "Make it motivational."
        }
        if tone and tone != "random" and tone in tone_map:
            style = tone_map[tone]
        else:
            style = random.choice(styles)

        prompt = (
            f"You are a professional meme creator. Generate ONE single funniest meme caption "
            f"for this image. {style} Keep it short, witty, and viral-worthy. "
            f"Output only the meme text."
        )

        image_part = {
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": base64_image
            }
        }

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([image_part, prompt])
        meme_text = getattr(response, "text", "").strip().upper()
        if not meme_text:
            return "No meme text generated.", 500

        # --- NEW: font size + color handling ---
        try:
            font_size = int(font_size_raw) if font_size_raw else 50
        except ValueError:
            font_size = 50
        font_size = max(24, min(font_size, 96))  # clamp

        def hex_to_rgb(hx: str):
            hx = hx.lstrip("#")
            if len(hx) == 3:
                hx = "".join([c * 2 for c in hx])
            if len(hx) != 6:
                return (255, 255, 255)
            return tuple(int(hx[i:i+2], 16) for i in (0, 2, 4))

        text_color = hex_to_rgb(font_color_hex or "#FFFFFF")

        # Prepare font
        try:
            FONT_PATH = os.path.join("static", "fonts", "impact.ttf")
            font = ImageFont.truetype(FONT_PATH, size=font_size)
        except Exception:
            font = ImageFont.load_default()

        # --- Proper text wrapping (unchanged logic) ---
        draw = ImageDraw.Draw(image)
        max_text_width = image.width - 40  # padding
        words = meme_text.split()
        lines, current_line = [], ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_text_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        # Calculate text height
        line_heights = [draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0,0), line font=font)[1] for line in lines]
        total_text_height = sum(line_heights) + (15 * (len(lines) - 1))

        # --- Create bar either at bottom (default) or top (NEW) ---
        bar_height = total_text_height + 60
        if position == "top":
            new_img = Image.new("RGB", (image.width, image.height + bar_height), "black")
            # paste bar at top by leaving it as background, image below it
            new_img.paste(image, (0, bar_height))
            y_text = (bar_height - text_height) // 2  # vertically center in bar
        else:
            # bottom
            new_img = Image.new("RGB", (image.width, image.height + bar_height), (0,0,0))
            new_img.paste(image, (0, 0))
            y_text = image.height + (bar_height - total_text_height) // 2

        # Draw text centered inside the black bar
        new_draw = ImageDraw.Draw(new_img)
        for line, h in zip(lines, line_heights):
            bbox = new_draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            x = (new_img.width - line_width) // 2

            # Outline for visibility (kept)
            outline = max(2, font_sizen//15)
            for ox in range(-outline, outline + 1):
                for oy in range(-outline, outline + 1):
                    if ox == 0 and oy == 0:
                        continue
                    new_draw.text((x + ox, y_text + oy), line, font=font, fill="black")

            # Main text with chosen color (NEW)
            new_draw.text((x, y_text), line, font=font, fill=(255, 255, 255) 
            y_text += h + 15  # line height + spacing

        # Save & return
        output = io.BytesIO()
        new_img.save(output, format="PNG")
        output.seek(0)
        return send_file(output, mimetype="image/png")

    except Exception as e:
        logging.error("Error in /generate-meme endpoint", exc_info=True)
        return str(e), 500
# ---------- MAIN ----------
if __name__ == "__main__":
    for rule in app.url_map.iter_rules():
        logging.info(f"Route: {rule} -> {rule.endpoint}")
    app.run(debug=True)
