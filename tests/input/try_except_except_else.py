print('start')

try:
	print('start try')
	print('end try')
except TypeError:
	print('start except1')
	print('end except1')
except ZeroDivisionError:
	print('start except2')
	print('end except2')
else:
	print('start else')
	print('end else')

print('end')