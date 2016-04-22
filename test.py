import time
from threading import Timer
def print_time():
	print "From print_time", time.time()

def print_some_times():
	print time.time()
	Timer(1, print_time).start()
	Timer(2, print_time).start()
	time.sleep(3)  # sleep while time-delay events execute
	print time.time()
	Timer(1, print_time).start()

print_some_times()
