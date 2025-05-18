import json
import logging
from typing import Dict, List, Any
from colorama import Fore, Style

logger = logging.getLogger(__name__)

class LoreManager:
    def __init__(self, lore_file: str):
        self.lore_data: Dict[str, List[Dict[str, Any]]] = {}
        try:
            with open(lore_file, 'r') as f:
                self.lore_data = json.load(f)
            logger.debug(f"Loaded lore data: {self.lore_data}")
        except FileNotFoundError:
            logger.error(f"Lore file not found at {lore_file}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding lore file: {e}")

    def print_lore(self) -> None:
        logger.debug("Printing lore")
        for era, events in self.lore_data.items():
            print(f"{Fore.CYAN}{era}{Style.RESET_ALL}")
            if not isinstance(events, list):
                logger.warning(f"Invalid events format for era {era}: {events}")
                continue
            for event in events:
                try:
                    if isinstance(event, dict) and 'year' in event and 'desc' in event:
                        print(f"{Fore.CYAN}  Year {event['year']}: {event['desc']}{Style.RESET_ALL}")
                    else:
                        logger.warning(f"Invalid event format: {event}")
                except (TypeError, KeyError) as e:
                    logger.warning(f"Error processing event {event}: {e}")
                    continue