from subprocess import Popen, PIPE
import os
from pathlib import Path
import glob
import shutil
import sys

python_versions = {
'3': ['0',
'1',
'2',
'3',
'4',
'5',
'6',
'7',
'8',
'9',
'10',
'11'
]
}

def run_cmd(cmd, with_output=False, with_err=False):
	proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
	cmd_stdout, cmd_stderr = proc.communicate()
	cmd_stdout = cmd_stdout.decode().replace('\r', '')
	cmd_stderr = cmd_stderr.decode().replace('\r', '')
	if with_err and with_output:
		return cmd_stdout, cmd_stderr, proc.returncode
	elif with_err:
		return cmd_stderr, proc.returncode
	elif with_output:
		return cmd_stdout
	else:
		return None

def get_python_versions_dir():
	return Path(run_cmd('where python', True).split('\n')[0]).parent.parent

class Compile:
	def __init__(self, ver='', test_name=''):
		self.ver = ver
		self.test_name = test_name

	def py_compile_verion(self, python_path, python_source_path):
		cmd_in = '"{}" -m py_compile "{}"'.format(python_path, python_source_path)
		stderr, ret_code = run_cmd(cmd_in, with_err=True)
		return stderr

	def check_compiled_dir(self):
		if not os.path.isdir('./compiled/'):
			os.makedirs('./compiled/')
	
	def print_start(self):
		print('======================')
		print('Starting compile...', end='')
		print('======================')
	
	def compile_python_source_file(self, py_major_ver, py_minor_ver, python_source_file, python_path):
		python_source_file = Path(python_source_file)
		print(python_source_file.name, end='')
		sys.stdout.flush()
		stderr = self.py_compile_verion(python_path, python_source_file.absolute())
		if stderr:
			print('\n\n[-] Error compiling %s' % python_source_file.name)
			print('------------------')
			print(stderr)
			print('------------------')
			print('Exiting...')
			sys.exit()
		
		pyc_out_path = python_source_file.parent / (python_source_file.stem + '.pyc')
		if not pyc_out_path.is_file():
			pyc_out_path = python_source_file.parent / '__pycache__' / ('%s.cpython-%s.pyc' % (python_source_file.stem, py_major_ver + py_minor_ver))
		pyc_out_new_path = Path('./compiled/') / (python_source_file.stem + '.%s.%s' % (py_major_ver, py_minor_ver) + '.pyc')
		pyc_out_path.replace(pyc_out_new_path.absolute())
		printed_filename_len = len(python_source_file.name)
		to_erase_str = '\b'*printed_filename_len
		to_erase_str += ' '*printed_filename_len
		to_erase_str += '\b'*printed_filename_len
		print(to_erase_str , end='')
	
	def compile_all(self):
		self.print_start()
		python_versions_dir = get_python_versions_dir()
		self.check_compiled_dir()
		versions = python_versions
		if self.ver:
			versions = {self.ver[0]: [self.ver[1:]]}
		for py_major_ver, py_minor_versions in versions.items():
			for py_minor_ver in py_minor_versions:
				print('Compiling Version [ %s.%s ]... ' % (py_major_ver, py_minor_ver), end='')
				sys.stdout.flush()
				python_path = python_versions_dir / ('Python%s' % py_major_ver + py_minor_ver) / 'python.exe'
				if self.test_name:
					self.compile_python_source_file(py_major_ver, py_minor_ver, './input/%s.py' % self.test_name, python_path)
				else:
					for python_source_file in glob.glob('./input/*.py'):
						self.compile_python_source_file(py_major_ver, py_minor_ver, python_source_file, python_path)
				print('Done.')
		print('')
		if os.path.isdir('./input/__pycache__/'):
			os.rmdir('./input/__pycache__/')


def main():
	ver = ''
	test_name = ''
	if len(sys.argv) > 1:
		for arg in sys.argv[1:]:
			if arg.isdigit():
				ver = arg
			elif arg.startswith('test='):
				test_name = arg.split('=',1)[1]
	compile = Compile(ver=ver, test_name=test_name)
	compile.compile_all()


if __name__ == '__main__':
	main()




