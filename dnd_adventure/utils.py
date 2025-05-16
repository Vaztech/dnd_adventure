import json
import logging
from dnd_adventure.paths import get_resource_path

logger = logging.getLogger(__name__)

# Cache for graphics data
_graphics_cache = None

def load_graphics():
    global _graphics_cache
    if _graphics_cache is not None:
        logger.debug("Using cached graphics data")
        return _graphics_cache
    graphics_path = get_resource_path("graphics.json")
    logger.debug(f"Reading graphics.json from {graphics_path}")
    print(f"DEBUG: Loading graphics from {graphics_path}...")
    try:
        with open(graphics_path, "r", encoding="utf-8") as f:
            _graphics_cache = json.load(f)
        logger.debug("Graphics loaded and cached")
        return _graphics_cache
    except Exception as e:
        logger.error(f"Failed to load graphics: {e}")
        raise