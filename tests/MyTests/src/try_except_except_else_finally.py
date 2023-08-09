print('start')

try:
	print('start try')
	a = 1/0
	print('end try')
except TypeError:
	print('except1')
except ZeroDivisionError:
	print('except2')
else:
	print('else')
finally:
	print('start finally')
	print('end finally')
	
print('middle')

try:
	print('start try')
	a = str(1) + 1
	print('end try')
except TypeError:
	print('except1')
except ZeroDivisionError:
	print('except2')
else:
	print('else')
finally:
	print('start finally')
	print('end finally')
	
print('middle2')

try:
	print('start try')
	a = 1
	print('end try')
except TypeError:
	print('except1')
except ZeroDivisionError:
	print('except2')
else:
	print('else')
finally:
	print('start finally')
	print('end finally')

print('end')
