# app/processing/weight_distribution.py
"""
Weight distribution logic for invoice processing
"""
import random
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class WeightDistributor:
    """
    Handles generation and distribution of weights for invoice processing
    """
    def __init__(self, min_percent: float = -2, max_percent: float = 2):
        """
        Initialize the weight distributor
        
        Args:
            min_percent: Minimum percentage variation
            max_percent: Maximum percentage variation
        """
        self.min_percent = min_percent
        self.max_percent = max_percent
    
    def distribute_weight(self, target_weight: float, num_items: int) -> List[float]:
        """
        Distribute weight with random variations
        
        Args:
            target_weight: Total weight to distribute
            num_items: Number of items to distribute weight among
            
        Returns:
            List of weights that sum to target_weight
        """
        if num_items <= 0:
            logger.warning("Cannot distribute weight to 0 items")
            return []
            
        base = target_weight / num_items
        weights = []
        remaining = target_weight
        
        # Generate weights for all but the last item
        for _ in range(num_items - 1):
            variation = random.uniform(self.min_percent, self.max_percent) / 100
            weight = round(base * (1 + variation) * 100) / 100
            weights.append(weight)
            remaining -= weight
        
        # Add last weight to ensure exact total
        weights.append(round(remaining * 100) / 100)
        
        # Shuffle to avoid having the balancing item always at the end
        random.shuffle(weights)
        
        logger.debug(f"Distributed {target_weight} among {num_items} items with variations between {self.min_percent}% and {self.max_percent}%")
        logger.debug(f"Sum of distributed weights: {sum(weights)}")
        
        return weights
    
    def validate_distribution(self, weights: List[float], target_weight: float, tolerance: float = 0.01) -> bool:
        """
        Validate that a weight distribution sums to the target
        
        Args:
            weights: List of weights
            target_weight: Expected total weight
            tolerance: Acceptable difference tolerance
            
        Returns:
            True if sum of weights is within tolerance of target_weight
        """
        total = sum(weights)
        difference = abs(total - target_weight)
        
        if difference > tolerance:
            logger.warning(f"Weight distribution validation failed. Total: {total}, Target: {target_weight}, Difference: {difference}")
            return False
            
        return True
    
    def calculate_statistics(self, weights: List[float]) -> Dict[str, float]:
        """
        Calculate statistics for a weight distribution
        
        Args:
            weights: List of weights
            
        Returns:
            Dictionary of statistics (min, max, avg, etc.)
        """
        if not weights:
            return {
                "min": 0,
                "max": 0, 
                "avg": 0,
                "total": 0,
                "count": 0
            }
            
        return {
            "min": min(weights),
            "max": max(weights),
            "avg": sum(weights) / len(weights),
            "total": sum(weights),
            "count": len(weights)
        }