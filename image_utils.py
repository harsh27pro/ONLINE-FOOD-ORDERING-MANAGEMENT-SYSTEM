# image_utils.py — Foodly Image Loader
# Downloads images from URL and returns CTkImage objects with caching

import urllib.request
import threading
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import customtkinter as ctk

_cache: dict = {}
_cache_lock = threading.Lock()   # protects _cache for multi-thread access

# ── Food item images (keyword → URL) ─────────────────────────────────────────
FOOD_URL_MAP = {
    "pizza":       "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=300&h=200&fit=crop&auto=format",
    "margherita":  "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=300&h=200&fit=crop&auto=format",
    "pepperoni":   "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=300&h=200&fit=crop&auto=format",
    "burger":      "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=300&h=200&fit=crop&auto=format",
    "cheeseburger":"https://images.unsplash.com/photo-1551782450-a2132b4ba21d?w=300&h=200&fit=crop&auto=format",
    "biryani":     "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=300&h=200&fit=crop&auto=format",
    "curry":       "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=300&h=200&fit=crop&auto=format",
    "dal":         "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=300&h=200&fit=crop&auto=format",
    "paneer":      "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=300&h=200&fit=crop&auto=format",
    "chicken":     "https://images.unsplash.com/photo-1598103442097-8b74394b95c7?w=300&h=200&fit=crop&auto=format",
    "mutton":      "https://images.unsplash.com/photo-1544025162-d76694265947?w=300&h=200&fit=crop&auto=format",
    "naan":        "https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=300&h=200&fit=crop&auto=format",
    "roti":        "https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=300&h=200&fit=crop&auto=format",
    "samosa":      "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=300&h=200&fit=crop&auto=format",
    "noodle":      "https://images.unsplash.com/photo-1569050467447-ce54b3bbc37d?w=300&h=200&fit=crop&auto=format",
    "noodles":     "https://images.unsplash.com/photo-1569050467447-ce54b3bbc37d?w=300&h=200&fit=crop&auto=format",
    "fried rice":  "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=300&h=200&fit=crop&auto=format",
    "rice":        "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=300&h=200&fit=crop&auto=format",
    "manchurian":  "https://images.unsplash.com/photo-1585032226651-759b368d7246?w=300&h=200&fit=crop&auto=format",
    "momos":       "https://images.unsplash.com/photo-1496116218417-1a781b1c416c?w=300&h=200&fit=crop&auto=format",
    "cake":        "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=300&h=200&fit=crop&auto=format",
    "ice cream":   "https://images.unsplash.com/photo-1497034825429-c343d7c6a68f?w=300&h=200&fit=crop&auto=format",
    "icecream":    "https://images.unsplash.com/photo-1497034825429-c343d7c6a68f?w=300&h=200&fit=crop&auto=format",
    "gulab":       "https://images.unsplash.com/photo-1666380800946-37a86fe07d2e?w=300&h=200&fit=crop&auto=format",
    "lassi":       "https://images.unsplash.com/photo-1527661591475-527312dd65f5?w=300&h=200&fit=crop&auto=format",
    "juice":       "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=300&h=200&fit=crop&auto=format",
    "coffee":      "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=300&h=200&fit=crop&auto=format",
    "sandwich":    "https://images.unsplash.com/photo-1553909489-cd47e0907980?w=300&h=200&fit=crop&auto=format",
    "fries":       "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=300&h=200&fit=crop&auto=format",
    "pasta":       "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=300&h=200&fit=crop&auto=format",
    "wrap":        "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=300&h=200&fit=crop&auto=format",
}

# ── Restaurant banner images keyed by keyword ─────────────────────────────────
RESTAURANT_URL_MAP = {
    "pizza":    "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400&h=160&fit=crop&auto=format",
    "burger":   "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&h=160&fit=crop&auto=format",
    "biryani":  "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=400&h=160&fit=crop&auto=format",
    "chinese":  "https://images.unsplash.com/photo-1569050467447-ce54b3bbc37d?w=400&h=160&fit=crop&auto=format",
    "indian":   "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&h=160&fit=crop&auto=format",
    "punjabi":  "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400&h=160&fit=crop&auto=format",
    "dhaba":    "https://images.unsplash.com/photo-1517244683847-7456b63c5969?w=400&h=160&fit=crop&auto=format",
    "cafe":     "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=400&h=160&fit=crop&auto=format",
    "sweet":    "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&h=160&fit=crop&auto=format",
    "grill":    "https://images.unsplash.com/photo-1544025162-d76694265947?w=400&h=160&fit=crop&auto=format",
    "tandoor":  "https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=400&h=160&fit=crop&auto=format",
    "mughal":   "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=400&h=160&fit=crop&auto=format",
    "south":    "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=400&h=160&fit=crop&auto=format",
    "roll":     "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=400&h=160&fit=crop&auto=format",
    "pasta":    "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=400&h=160&fit=crop&auto=format",
    "shawarma": "https://images.unsplash.com/photo-1529006557810-274b9b2fc783?w=400&h=160&fit=crop&auto=format",
    "sandwich": "https://images.unsplash.com/photo-1553909489-cd47e0907980?w=400&h=160&fit=crop&auto=format",
    "juice":    "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400&h=160&fit=crop&auto=format",
    "noodle":   "https://images.unsplash.com/photo-1569050467447-ce54b3bbc37d?w=400&h=160&fit=crop&auto=format",
    "chicken":  "https://images.unsplash.com/photo-1598103442097-8b74394b95c7?w=400&h=160&fit=crop&auto=format",
    "paneer":   "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=400&h=160&fit=crop&auto=format",
    "momos":    "https://images.unsplash.com/photo-1496116218417-1a781b1c416c?w=400&h=160&fit=crop&auto=format",
    "ice":      "https://images.unsplash.com/photo-1497034825429-c343d7c6a68f?w=400&h=160&fit=crop&auto=format",
    "cake":     "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&h=160&fit=crop&auto=format",
    "dal":      "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400&h=160&fit=crop&auto=format",
    "samosa":   "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400&h=160&fit=crop&auto=format",
    "lassi":    "https://images.unsplash.com/photo-1527661591475-527312dd65f5?w=400&h=160&fit=crop&auto=format",
    "coffee":   "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400&h=160&fit=crop&auto=format",
    "mutton":   "https://images.unsplash.com/photo-1544025162-d76694265947?w=400&h=160&fit=crop&auto=format",
}

# ── Large pool of distinct fallback restaurant images ─────────────────────────
# All different food/restaurant ambiance shots — used when no keyword matches
RESTAURANT_FALLBACKS = [
    "https://images.unsplash.com/photo-1466978913421-dad2ebd01d17?w=400&h=160&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400&h=160&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400&h=160&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1552566626-52f8b828add9?w=400&h=160&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1537047902294-62a40c20a6ae?w=400&h=160&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1424847651672-bf20a4b0982b?w=400&h=160&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1533777324565-a040eb52fac9?w=400&h=160&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&h=160&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1600891964599-f61ba0e24092?w=400&h=160&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=400&h=160&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=400&h=160&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1484980972926-edee96e0960d?w=400&h=160&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=400&h=160&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1544148103-0773bf10d330?w=400&h=160&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1506354666786-959d6d497f1a?w=400&h=160&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1498654896293-37aacf113fd9?w=400&h=160&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1590846406792-0adc7f938f1d?w=400&h=160&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=400&h=160&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1482049016688-2d3e1b311543?w=400&h=160&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=400&h=160&fit=crop&auto=format",
]

# ── Vivid colors for placeholder tiles ───────────────────────────────────────
PLACEHOLDER_COLORS = [
    "#FF5722", "#E91E63", "#9C27B0", "#3F51B5",
    "#2196F3", "#009688", "#4CAF50", "#FF9800",
    "#795548", "#607D8B", "#F44336", "#00BCD4",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _match_keyword(name: str, url_map: dict) -> str | None:
    """Return URL if any keyword found in name, else None."""
    name_lower = name.lower()
    for keyword, url in url_map.items():
        if keyword in name_lower:
            return url
    return None


def _load_from_url(url: str, size: tuple) -> Image.Image | None:
    """Download, resize, and cache an image. Returns None on any failure.
    Thread-safe: safe to call from background threads."""
    cache_key = f"{url}|{size[0]}x{size[1]}"
    with _cache_lock:
        if cache_key in _cache:
            return _cache[cache_key]
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = resp.read()
        if len(data) < 2000:   # too small → likely an error response, not a real image
            print(f"[image_utils] Response too small ({len(data)} bytes) for {url}")
            return None
        img = Image.open(BytesIO(data)).convert("RGBA")
        img = img.resize(size, Image.LANCZOS)
        with _cache_lock:
            _cache[cache_key] = img
        return img
    except Exception as e:
        print(f"[image_utils] Failed: {url} — {e}")
        return None


def _make_placeholder(size: tuple, text: str, color_idx: int = 0) -> Image.Image:
    """Colored tile with bold initials text."""
    bg = PLACEHOLDER_COLORS[color_idx % len(PLACEHOLDER_COLORS)]
    r, g, b = int(bg[1:3], 16), int(bg[3:5], 16), int(bg[5:7], 16)
    img = Image.new("RGBA", size, (r, g, b, 255))
    draw = ImageDraw.Draw(img)
    try:
        font_size = min(size) // 3
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", min(size) // 3)
        except:
            font = ImageFont.load_default()
    draw.text((size[0] // 2, size[1] // 2), text, fill="white", anchor="mm", font=font)
    return img


# ── Public API ────────────────────────────────────────────────────────────────

def get_food_image(item_name: str, size=(160, 110)) -> ctk.CTkImage:
    """Return a CTkImage for a food item by name."""
    url = _match_keyword(item_name, FOOD_URL_MAP)
    img = _load_from_url(url, size) if url else None
    if img is None:
        color_idx = abs(hash(item_name)) % len(PLACEHOLDER_COLORS)
        initials = item_name[:2].upper() if item_name else "FD"
        img = _make_placeholder(size, initials, color_idx)
    return ctk.CTkImage(light_image=img, dark_image=img, size=size)


def get_restaurant_image(res_name: str, size=(340, 130)) -> ctk.CTkImage:
    """Return a CTkImage for a restaurant banner.

    Priority:
      1. Keyword match  → relevant food photo
      2. Fallback pool  → unique photo per restaurant name (via hash)
      3. Colored tile   → initials placeholder as last resort
    """
    # 1. Keyword match
    url = _match_keyword(res_name, RESTAURANT_URL_MAP)

    # 2. Unique fallback from pool
    if url is None:
        idx = abs(hash(res_name)) % len(RESTAURANT_FALLBACKS)
        url = RESTAURANT_FALLBACKS[idx]

    img = _load_from_url(url, size)

    # 3. Colored placeholder
    if img is None:
        color_idx = abs(hash(res_name)) % len(PLACEHOLDER_COLORS)
        initials = "".join(w[0].upper() for w in res_name.split()[:2]) if res_name else "R"
        img = _make_placeholder(size, initials, color_idx)

    return ctk.CTkImage(light_image=img, dark_image=img, size=size)


def load_image_async(fetch_fn, callback, *args, widget=None, **kwargs):
    """Run fetch_fn(*args, **kwargs) in a background thread.
    Once done, schedules callback(ctk_image) on the main thread via widget.after().
    widget must be a tk widget that is still alive when the image arrives."""
    def _worker():
        try:
            result = fetch_fn(*args, **kwargs)
        except Exception as e:
            print(f"[load_image_async] error: {e}")
            result = None
        try:
            if widget and widget.winfo_exists():
                widget.after(0, lambda: callback(result))
        except Exception:
            pass  # widget was destroyed before image arrived

    threading.Thread(target=_worker, daemon=True).start()


def get_avatar_image(name: str, size=(80, 80)) -> ctk.CTkImage:
    """Circular avatar with initials."""
    color_idx = abs(hash(name)) % len(PLACEHOLDER_COLORS)
    bg = PLACEHOLDER_COLORS[color_idx]
    r, g, b = int(bg[1:3], 16), int(bg[3:5], 16), int(bg[5:7], 16)
    img = Image.new("RGBA", size, (r, g, b, 255))
    draw = ImageDraw.Draw(img)
    initials = "".join(w[0].upper() for w in name.split()[:2]) if name else "?"
    try:
        font = ImageFont.truetype("arial.ttf", size[0] // 3)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size[0] // 3)
        except:
            font = ImageFont.load_default()
    draw.text((size[0] // 2, size[1] // 2), initials, fill="white", anchor="mm", font=font)
    # Circular mask
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size[0], size[1]), fill=255)
    img.putalpha(mask)
    return ctk.CTkImage(light_image=img, dark_image=img, size=size)