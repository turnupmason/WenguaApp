"""Actual failed Swift clock: preserve exact hour relation wording."""
import unittest
from tests.test_health_discomfort_injury_gate_20261102 import live_board
from src.wengua.health_discomfort_v19_parity import compose, load_sources

class ActualHourParityRegression(unittest.TestCase):
    def test_original_failed_same_palace_clock(self):
        chart, actor = live_board('2026-11-09T11:00:00-05:00')
        reading = compose(chart, actor, '弟弟', 'none', load_sources())
        hour = next(x['text'] for x in reading['sections'] if x['id'] == '04_hour')
        self.assertEqual(hour, '时干丙落坤二宫，属阴遁内盘，力量极小，此干主额、鼻；与天芮同宫，同指脾胃。')
