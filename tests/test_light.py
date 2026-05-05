import unittest
from unittest.mock import patch, MagicMock
import sys
import os
# Add the root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.sensors.light.light import Light

class TestLight(unittest.TestCase):
    @patch('app.sensors.light.light.pigpio.pi')
    def setUp(self, MockPi):
        self.mock_pi = MockPi.return_value
        self.mock_pi.connected = True
        self.light = Light(18)

    def test_init_sets_hardware_pwm(self):
        # Should initialize with PWM off at 25kHz
        self.mock_pi.hardware_PWM.assert_called_with(18, 25000, 0)

    def test_turn_on_from_0(self):
        self.light._duty_pct = 0
        self.light.on()
        self.mock_pi.hardware_PWM.assert_called_with(18, 25000, 1_000_000)
        self.assertEqual(self.light._duty_pct, 100)

    def test_turn_on_from_nonzero(self):
        self.light._duty_pct = 50
        self.light.on()
        # Should not change — light is already on
        self.assertEqual(self.light._duty_pct, 50)

    def test_off(self):
        self.light._duty_pct = 100
        self.light.off()
        self.mock_pi.hardware_PWM.assert_called_with(18, 25000, 0)
        self.assertEqual(self.light._duty_pct, 0)

    def test_set_brightness_valid(self):
        self.light.set_brightness(70)
        self.mock_pi.hardware_PWM.assert_called_with(18, 25000, 700_000)
        self.assertEqual(self.light._duty_pct, 70)

    def test_set_brightness_invalid(self):
        with self.assertRaises(ValueError):
            self.light.set_brightness(110)

    def test_set_frequency(self):
        self.light._duty_pct = 50
        self.light.set_frequency(30000)
        self.assertEqual(self.light.frequency, 30000)
        self.mock_pi.hardware_PWM.assert_called_with(18, 30000, 500_000)

    def test_get_duty_cycle(self):
        self.light._duty_pct = 75
        result = self.light.get_duty_cycle()
        self.assertEqual(result, 75)

    def test_get_brightness(self):
        self.light._duty_pct = 60
        result = self.light.get_brightness()
        self.assertEqual(result, 60)

    def test_close(self):
        self.light.close()
        self.mock_pi.hardware_PWM.assert_called_with(18, 25000, 0)
        self.mock_pi.stop.assert_called_once()

if __name__ == '__main__':
    unittest.main()
