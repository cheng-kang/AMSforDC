import time
from threading import Timer
def print_time(a):
	print a
	print "From print_time", time.time()

def print_some_times():
	print time.time()
	Timer(3, print_time, [1]).start()
	Timer(0, print_time, [1]).start()
	time.sleep(3)  # sleep while time-delay events execute
	print time.time()
	Timer(1, print_time, [1]).start()

print_some_times()
