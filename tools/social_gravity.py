"""
Social Gravity Engine
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum


class IntegrityPulse(Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


@dataclass
class GravityEntity:
    entity_id: str
    mass: float
    confidence: float
    time_until_event: float
    metadata: Optional[Dict] = None


class SocialGravityEngine:
    """
    Calculates gravitational force from multiple entities.

    Formula: F_raw = Σ (M_i × PF_i) / D_i²
    """

    MIN_DISTANCE = 0.1

    def __init__(self, sigmoid_k: float = 500.0, sigmoid_steepness: float = 0.01):
        self.sigmoid_k = sigmoid_k
        self.sigmoid_steepness = sigmoid_steepness

    @staticmethod
    def calculate_raw_gravity(entities: List[GravityEntity]) -> float:
        if not entities:
            return 0.0

        total_force = 0.0

        for entity in entities:
            distance = max(entity.time_until_event, SocialGravityEngine.MIN_DISTANCE)
            force = (entity.mass * entity.confidence) / (distance ** 2)
            total_force += force

        return total_force

    def normalize_to_urgency(self, f_raw: float) -> float:
        exponent = -self.sigmoid_steepness * (f_raw - self.sigmoid_k)

        if exponent > 700:
            return 0.0
        if exponent < -700:
            return 1.0

        u_norm = 1.0 / (1.0 + np.exp(exponent))
        return u_norm

    def classify_pulse(self, u_norm: float) -> IntegrityPulse:
        if u_norm >= 0.8:
            return IntegrityPulse.RED
        elif u_norm >= 0.5:
            return IntegrityPulse.YELLOW
        else:
            return IntegrityPulse.GREEN

    def calculate_inhibitory_delay(self, u_norm: float, tau_base: float = 0.0, tau_max: float = 10.0) -> float:
        tau = tau_base + (u_norm * tau_max)
        return tau

    def process(self, entities: List[GravityEntity]) -> Dict:
        f_raw = self.calculate_raw_gravity(entities)
        u_norm = self.normalize_to_urgency(f_raw)
        pulse = self.classify_pulse(u_norm)
        tau = self.calculate_inhibitory_delay(u_norm)

        return {
            'raw_gravity': f_raw,
            'urgency_norm': u_norm,
            'integrity_pulse': pulse,
            'inhibitory_delay': tau,
            'num_entities': len(entities)
        }


if __name__ == "__main__":
    print("=" * 60)
    print("SOCIAL GRAVITY ENGINE SELF-TEST")
    print("=" * 60)

    engine = SocialGravityEngine()

    print("\n1. Testing calculation...")
    entities = [
        GravityEntity("pattern", 900.0, 0.9, 0.1, {'type': 'pattern'}),
        GravityEntity("calendar", 200.0, 1.0, 2.0, {'type': 'event'})
    ]

    result = engine.process(entities)

    print(f"   Raw gravity: {result['raw_gravity']:.1f}")
    print(f"   Urgency: {result['urgency_norm']:.3f}")
    print(f"   Pulse: {result['integrity_pulse'].value}")

    assert result['raw_gravity'] > 50000
    assert result['urgency_norm'] > 0.8
    assert result['integrity_pulse'] == IntegrityPulse.RED
    print("   ✓ PASSED")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)
