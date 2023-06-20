from serial import Serial

class Tama:
	buttons = {"A", "B", "C"}
	def __init__(self, port, baud):
		self._serial = Serial(port, baud)

	def _write(self, line):
		self._serial.write(f"{line}\r\n".encode())

	def press(self, button):
		if button in Tama.buttons:
			self._write(button)
		else:
			raise ValueError(f"Button {button} does not exist")