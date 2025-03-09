import os
import pandas as pd
from colorthief import ColorThief

def get_poster(movie):
    poster = movie.get("poster_path", "").strip()
    if poster and pd.notnull(poster) and os.path.exists(poster):
        return poster
    return "static/posters/default.jpg"

def get_dominant_color(image_path):
    if not os.path.exists(image_path):
        return ("rgb(255, 255, 255)", "rgb(0, 0, 0)", "rgb(0, 0, 0)",
                "rgba(0, 0, 0, 0.25)", "rgba(0, 0, 0, 0.4)", "rgb(0, 0, 0)")
    try:
        color_thief = ColorThief(image_path)
        dominant_color = color_thief.get_color(quality=10)
        r, g, b = dominant_color
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        text_color = "rgb(0, 0, 0)" if luminance > 0.5 else "rgb(255, 255, 255)"
        border_color = text_color
        pill_bg = "rgba(0, 0, 0, 0.25)" if luminance > 0.5 else "rgba(255, 255, 255, 0.25)"
        pill_bg_hover = "rgba(0, 0, 0, 0.4)" if luminance > 0.5 else "rgba(255, 255, 255, 0.4)"
        pill_text = text_color
        return (f"rgb({r}, {g}, {b})", text_color, border_color, pill_bg, pill_bg_hover, pill_text)
    except Exception as e:
        print("Error in get_dominant_color:", e)
        return ("rgb(255, 255, 255)", "rgb(0, 0, 0)", "rgb(0, 0, 0)",
                "rgba(0, 0, 0, 0.25)", "rgba(0, 0, 0, 0.4)", "rgb(0, 0, 0)")
