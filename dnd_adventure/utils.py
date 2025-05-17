import os
import json
import logging

logger = logging.getLogger(__name__)

def load_json_file(file_path: str) -> dict:
    logger.debug(f"Reading JSON from {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.debug(f"JSON loaded from {file_path}")
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load JSON from {file_path}: {e}")
        raise

def load_graphics() -> dict:
    graphics_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'graphics.json')
    logger.debug(f"Reading graphics.json from {graphics_path}")
    try:
        with open(graphics_path, 'r', encoding='utf-8') as f:
            graphics = json.load(f)
        logger.debug("Graphics loaded and cached")
        return graphics
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load graphics: {e}")
        return {"maps": {}}