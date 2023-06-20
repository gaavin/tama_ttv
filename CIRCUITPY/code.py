from asyncio import create_task, get_event_loop, Lock, sleep
from board import D9, D8, D7
from digitalio import Direction, DigitalInOut

class Button:
	def __init__(self, pin):
		self._pin = DigitalInOut(pin)
		# input mode is used to keep the original buttons responsive
		self._pin.direction = Direction.INPUT
		# used to ensure button presses are uninterrupted
		self._lock = Lock()

	# set pin high momentarily to recreate a button press
	async def press(self):
		async with self._lock:
			self._pin.direction = Direction.OUTPUT
			self._pin.value = True
			# this is long enough to press the button
			await sleep(5/100)
			self._pin.value = False
			self._pin.direction = Direction.INPUT

class Tama:
	def __init__(self):
		self.A = Button(D9)
		self.B = Button(D8)
		self.C = Button(D7)

		self._commands = {
			"A": self.A.press,
			"B": self.B.press,
			"C": self.C.press
		}

	# listen for commands over serial
	async def listen(self):
		while True:
			rx = input()
			try:
				await create_task(self._commands[rx]())
			except:
				print(f"invalid button: {rx}")

async def main():
	tama = Tama()
	await create_task(tama.listen())

if __name__ == "__main__":
	loop = get_event_loop()
	loop.run_until_complete(main())