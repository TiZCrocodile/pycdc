print('start')

try:
	print('start try')
	print('end try')
except ZeroDivisionError:
	print('start except')
	print('end except')
finally:
	print('start finally')
	print('end finally')

print('end')
