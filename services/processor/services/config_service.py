import json
import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class ConfigService:
    """Service for managing dynamic configuration updates"""
    
    def __init__(self):
        self.roi_zones = []
        self.analytics_config = {}
        self.config_file_path = "/opt/nvidia/deepstream/deepstream/configs/analytics_config.txt"
    
    def load_config(self) -> bool:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file_path):
                with open(self.config_file_path, 'r') as f:
                    self.analytics_config = json.load(f)
                logger.info("Configuration loaded successfully")
                return True
            else:
                # Create default configuration
                self.create_default_config()
                return True
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return False
    
    def create_default_config(self):
        """Create default analytics configuration"""
        self.analytics_config = {
            "roi_zones": [
                {
                    "name": "entrance_zone",
                    "type": "zone",
                    "points": [(100, 100), (500, 100), (500, 400), (100, 400)],
                    "alert_on_entry": True,
                    "alert_on_exit": False
                }
            ],
            "line_counters": [],
            "overcrowd_detection": {
                "enabled": True,
                "threshold": 10
            },
            "dwell_time": {
                "enabled": True,
                "threshold_seconds": 300
            }
        }
        self.save_config()
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file_path), exist_ok=True)
            with open(self.config_file_path, 'w') as f:
                json.dump(self.analytics_config, f, indent=2)
            logger.info("Configuration saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def generate_roi_config(self, roi_config: Dict[str, Any]) -> str:
        """Generate ROI configuration in DeepStream format"""
        try:
            config_lines = []
            
            # Add ROI zones
            if "roi_zones" in roi_config:
                for i, zone in enumerate(roi_config["roi_zones"]):
                    zone_name = zone.get("name", f"zone_{i}")
                    points = zone.get("points", [])
                    
                    # Convert points to DeepStream format
                    points_str = ";".join([f"{x},{y}" for x, y in points])
                    
                    config_lines.append(f"[roi-filtering-stream-{i}]")
                    config_lines.append(f"enable=1")
                    config_lines.append(f"roi-{zone_name}={points_str}")
                    config_lines.append(f"inverse-roi=0")
                    config_lines.append("")
            
            # Add line counters
            if "line_counters" in roi_config:
                for i, line in enumerate(roi_config["line_counters"]):
                    line_name = line.get("name", f"line_{i}")
                    start_point = line.get("start", (0, 0))
                    end_point = line.get("end", (100, 100))
                    
                    config_lines.append(f"[line-crossing-stream-{i}]")
                    config_lines.append(f"enable=1")
                    config_lines.append(f"line-{line_name}={start_point[0]},{start_point[1]};{end_point[0]},{end_point[1]}")
                    config_lines.append("")
            
            return "\n".join(config_lines)
            
        except Exception as e:
            logger.error(f"Failed to generate ROI config: {e}")
            return ""
    
    def is_point_in_roi(self, x: float, y: float, roi_name: str = None) -> bool:
        """Check if a point is within any defined ROI"""
        try:
            if not self.analytics_config.get("roi_zones"):
                return False
            
            for zone in self.analytics_config["roi_zones"]:
                if roi_name and zone["name"] != roi_name:
                    continue
                
                if self._point_in_polygon(x, y, zone["points"]):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking point in ROI: {e}")
            return False
    
    def _point_in_polygon(self, x: float, y: float, polygon: List[Tuple[float, float]]) -> bool:
        """Check if a point is inside a polygon using ray casting algorithm"""
        try:
            n = len(polygon)
            inside = False
            
            p1x, p1y = polygon[0]
            for i in range(n + 1):
                p2x, p2y = polygon[i % n]
                if y > min(p1y, p2y):
                    if y <= max(p1y, p2y):
                        if x <= max(p1x, p2x):
                            if p1y != p2y:
                                xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                            if p1x == p2x or x <= xinters:
                                inside = not inside
                p1x, p1y = p2x, p2y
            
            return inside
            
        except Exception as e:
            logger.error(f"Error in point-in-polygon calculation: {e}")
            return False
    
    def update_roi_zone(self, zone_name: str, new_points: List[Tuple[float, float]]) -> bool:
        """Update an existing ROI zone"""
        try:
            for zone in self.analytics_config.get("roi_zones", []):
                if zone["name"] == zone_name:
                    zone["points"] = new_points
                    self.save_config()
                    logger.info(f"Updated ROI zone: {zone_name}")
                    return True
            
            logger.warning(f"ROI zone not found: {zone_name}")
            return False
            
        except Exception as e:
            logger.error(f"Error updating ROI zone: {e}")
            return False
    
    def add_roi_zone(self, zone_config: Dict[str, Any]) -> bool:
        """Add a new ROI zone"""
        try:
            if "roi_zones" not in self.analytics_config:
                self.analytics_config["roi_zones"] = []
            
            self.analytics_config["roi_zones"].append(zone_config)
            self.save_config()
            logger.info(f"Added new ROI zone: {zone_config.get('name', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding ROI zone: {e}")
            return False
    
    def remove_roi_zone(self, zone_name: str) -> bool:
        """Remove an ROI zone"""
        try:
            if "roi_zones" in self.analytics_config:
                self.analytics_config["roi_zones"] = [
                    zone for zone in self.analytics_config["roi_zones"]
                    if zone["name"] != zone_name
                ]
                self.save_config()
                logger.info(f"Removed ROI zone: {zone_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing ROI zone: {e}")
            return False