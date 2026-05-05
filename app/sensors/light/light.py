import argparse
import pigpio
import logging

# hardware_PWM duty cycle range: 0 (off) to 1,000,000 (fully on)
_HW_PWM_RANGE = 1_000_000

class Light:
    def __init__(self, pin=18, frequency=25000, pin_factory=None):
        """
        Control LED lights via pigpio hardware PWM.

        Uses pigpio.hardware_PWM() directly instead of gpiozero's PWMLED to allow
        PWM frequencies above the audible range (>20 kHz). gpiozero's software PWM
        is limited to 8 kHz at the default pigpiod sample rate, which causes audible
        whine in LED driver circuitry.

        GPIO 18 is one of the Raspberry Pi's dedicated hardware PWM pins (PWM0),
        supporting frequencies up to 125 MHz via the BCM2835 hardware peripheral.

        Args:
            pin (int): GPIO pin number (must be a hardware PWM capable pin: 12, 13, 18, or 19).
            frequency (int): PWM frequency in Hz. Default 25 kHz (above human hearing).
            pin_factory: Accepted for API compatibility with mqtt.py but not used.
                         Hardware PWM is controlled directly via pigpio.
        """
        self.pin = pin
        self.frequency = frequency
        self._duty_pct = 0  # Track duty cycle as 0-100 percentage

        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("Failed to connect to pigpiod daemon. Ensure it's running and accessible.")

        # Initialize with PWM off
        self.pi.hardware_PWM(self.pin, self.frequency, 0)
        logging.info(f"Light initialized on GPIO {self.pin} at {self.frequency} Hz (hardware PWM)")

    def on(self):
        """
        Turn on lights.
        """
        if self._duty_pct > 0:
            logging.info("Light already on, skipping")
            return

        logging.info("Turning light on")
        self._duty_pct = 100
        self.pi.hardware_PWM(self.pin, self.frequency, _HW_PWM_RANGE)

    def off(self):
        """
        Turn off lights.
        """
        logging.info("Turning light off")
        self._duty_pct = 0
        self.pi.hardware_PWM(self.pin, self.frequency, 0)

    def set_brightness(self, brightness_percentage):
        """
        Wrapper function around set_duty_cycle. Provides more intuitive function name.

        Args:
        - brightness_percentage (int): A value between 0 (off) and 100 (max brightness).
        """
        self.set_duty_cycle(brightness_percentage)

    def get_brightness(self):
        """
        Wrapper function around get_duty_cycle. Provides more intuitive function name.

        Returns:
        - float: The current duty cycle percentage.
        """
        return self.get_duty_cycle()

    def set_frequency(self, frequency):
        """
        Change the PWM frequency. Re-applies the current duty cycle at the new frequency.
        """
        logging.info(f"Setting light frequency to {frequency}")
        self.frequency = frequency
        hw_duty = int(self._duty_pct / 100.0 * _HW_PWM_RANGE)
        self.pi.hardware_PWM(self.pin, self.frequency, hw_duty)

    def set_duty_cycle(self, duty_cycle_percentage):
        """
        Set the duty cycle percentage, i.e. brightness level.

        Args:
        - duty_cycle_percentage (int): A value between 0 (off) and 100 (full brightness).
        """
        if 0 <= duty_cycle_percentage <= 100:
            self._duty_pct = duty_cycle_percentage
            hw_duty = int(duty_cycle_percentage / 100.0 * _HW_PWM_RANGE)
            logging.info(f"Setting light duty_cycle to {duty_cycle_percentage}%")
            self.pi.hardware_PWM(self.pin, self.frequency, hw_duty)
        else:
            raise ValueError("Brightness must be between 0 and 100")

    def get_duty_cycle(self):
        """
        Get the current duty cycle percentage.

        Returns:
        - float: The current duty cycle percentage.
        """
        logging.info(f"Light duty_cycle is {self._duty_pct}%")
        return self._duty_pct

    def close(self):
        """
        Turn off PWM and release the pigpio connection.
        """
        self.pi.hardware_PWM(self.pin, self.frequency, 0)
        self.pi.stop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Control an IoT light.')
    parser.add_argument('--on', action='store_true', help='Turn the light on.')
    parser.add_argument('--off', action='store_true', help='Turn the light off.')
    parser.add_argument('--brightness', type=int, default=None,
                        help='Set the brightness level (0-100).')

    args = parser.parse_args()

    light = Light(18)  # Default frequency of 25kHz (hardware PWM)

    if args.on:
        light.on()
        if args.brightness is not None:
            light.set_brightness(args.brightness)
    elif args.off:
        light.off()
    elif args.brightness is not None:
        light.on()
        light.set_brightness(args.brightness)
    else:
        logging.info("No action specified. Use --on, --off, or --brightness.")
