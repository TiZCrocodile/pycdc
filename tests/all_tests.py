from subprocess import Popen, PIPE
import os
from pathlib import Path
import glob
import shutil
import sys
import re
import time

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

def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)

def create_dir_if_not_exists(dir_path):
	if not os.path.isdir(dir_path):
		os.makedirs(dir_path)

def print_info(indicate_char, info, head, max_align):
	print('[{}] {} {}--> {}'.format(
		indicate_char*2, 
		head, 
		'-'*(max_align - len(head)),
		info))

def start_print_filename(filename):
	sys.stdout.write(filename)
	sys.stdout.flush()
	
def end_print_filename(filename_len):
	to_erase_str = '\b'*filename_len
	to_erase_str += ' '*filename_len
	to_erase_str += '\b'*filename_len
	sys.stdout.write(to_erase_str)

def print_start(file_basename_exp):
	print('======================')
	print('Starting TESTS...')
	if file_basename_exp != '*':
		print('Files expression: < %s >' % file_basename_exp)
	print('======================')

def compile(input_dir, compiled_dir, versions, file_basename_exp):
	def get_python_versions_dir():
		return Path(run_cmd('where python', True).split('\n')[0]).parent.parent
	
	create_dir_if_not_exists(compiled_dir)
	python_path = get_python_versions_dir() / ('Python%s' % versions[0]) / 'python.exe'
	pycache_dir = input_dir / '__pycache__'
	
	for py_ver in versions:
		print('Compiling Version [ %s ]... ' % py_ver, end='')
		sys.stdout.flush()
		
		python_path =  python_path.parent.parent / ('Python%s' % py_ver) / 'python.exe'
		for source_file in glob.glob(str(input_dir  / (file_basename_exp + '.py'))):
			source_file = Path(source_file)
			start_print_filename(source_file.name)
			
			pyc_file = compiled_dir / (source_file.stem + '_%s' % py_ver + '.pyc')
			
			if pyc_file.is_file():
				end_print_filename(len(source_file.name))
				continue
			
			cmd_in = '"{}" -m py_compile "{}"'.format(str(python_path), source_file)
			cmd_out, cmd_err, retcode = run_cmd(cmd_in, True, True)
			if retcode:
				end_print_filename(len(source_file.name))
				print('ERROR.')
				sys.stderr.write(cmd_err)
				sys.exit(retcode)
			
			# move pyc file
			pyc_out_path = input_dir / (source_file.stem + '.pyc')
			if not pyc_out_path.is_file():
				pyc_out_path = pycache_dir / ('%s.cpython-%s.pyc' % (source_file.stem, py_ver))
			pyc_out_path.replace(pyc_file)
			
			end_print_filename(len(source_file.name))
		print('Done.')
	print('')
	if os.path.isdir(pycache_dir):
		os.rmdir(pycache_dir)

def decompile(compiled_dir, decompiled_dir, versions, file_basename_exp, pycdc_path):
	def get_decompiled_output(pyc_file):
		cmd_in = '"{}" "{}"'.format(pycdc_path, pyc_file)
		cmd_out, cmd_err, retcode = run_cmd(cmd_in, True, True)
		if retcode:
			decompiled_output = ('#ERROR0\n' +
									'Unexpected return code: ' +
									str(hex(retcode)) + '\n' +
									cmd_err.strip())
		elif cmd_err:
			decompiled_output = ('#ERROR1\n' + 
									cmd_err.strip())
		else:
			decompiled_output = cmd_out
		return decompiled_output
	
	create_dir_if_not_exists(decompiled_dir)
	
	for py_ver in versions:
		print('Decompiling Version [ %s ]... ' % py_ver, end='')
		sys.stdout.flush()
		
		for pyc_file in glob.glob(str(compiled_dir / (file_basename_exp + '_%s' % py_ver + '.pyc'))):
			pyc_file = Path(pyc_file)
			start_print_filename(pyc_file.name)
			
			decompiled_output = get_decompiled_output(pyc_file.resolve(strict=1))
			source_out_path = decompiled_dir / (pyc_file.stem + '.py')
			with open(source_out_path, 'w') as f:
				f.write(decompiled_output)
			
			end_print_filename(len(pyc_file.name))
		print('Done.')
	print('')

def check_error0(source_file, decompiled_source_file_first_line, decompiled_source_file_after_first_line):
	if decompiled_source_file_first_line.startswith('#ERROR0'):
		print_info('-', 'Failed (pycdc crashed in runtime)', source_file.name, max_align_need)
		if debug:
			print('-----------------')
			print(decompiled_source_file_after_first_line)
			print('-----------------')
		return True
	return False

def check_error1(source_file, decompiled_source_file_first_line, decompiled_source_file_after_first_line):
	if decompiled_source_file_first_line.startswith('#ERROR1'):
		print_info('-', 'Failed (Unsupported / Warning, etc.)', source_file.name, max_align_need)
		if debug:
			print('-----------------')
			print(decompiled_source_file_after_first_line)
			print('-----------------')
		return True
	return False

def check_stdout_failed(source_file, decompiled_source_file_contents):
	if source_file.name not in source_files_contents:
		with open(source_file) as f:
			source_file_contents = f.read()
		# replace tabs with spaces on source files
		source_file_contents = source_file_contents.replace('\t', ' '*4)
		# strip lines and remove empty lines
		source_file_contents = '\n'.join(list(filter(lambda x: x.strip(), source_file_contents.split('\n'))))
		source_files_contents[source_file.name] = source_file_contents
	
	# remove first commment lines on decompiled source files
	decompiled_source_file_contents = '\n'.join(decompiled_source_file_contents.split('\n')[3:])
	# strip lines and remove empty lines
	decompiled_source_file_contents = '\n'.join(list(filter(lambda x: x.strip(), decompiled_source_file_contents.split('\n'))))
	
	if source_files_contents[source_file.name] != decompiled_source_file_contents:
		print_info('-', 'Failed (Different stdout)', source_file.name, max_align_need)
		# putting a lot of prints so i can switch to .encode() easily
		if debug:
			print('-----------------')
			print(source_files_contents[source_file.name])
			print('=================')
			print(decompiled_source_file_contents)
			print('-----------------')
		return True
	return False

def check_failed(source_file, decompiled_source_path):
	with open(decompiled_source_path, 'r') as f:
		decompiled_source_content = f.read()
	decompiled_source_file_first_line, decompiled_source_file_after_first_line = decompiled_source_content.split('\n', 1)
	if check_error0(source_file, decompiled_source_file_first_line, decompiled_source_file_after_first_line):
		return True
	elif check_error1(source_file, decompiled_source_file_first_line, decompiled_source_file_after_first_line):
		return True
	elif check_stdout_failed(source_file, decompiled_source_content):
		return True
	return False

def print_summary(version_to_decompiled_count, input_files_count, first_version):
	print('Summary:')
	version_format = 'Version %s'
	max_align_need = len(version_format % first_version)
	for py_ver, decompiled_count in version_to_decompiled_count.items():
		if decompiled_count == input_files_count:
			indicate_char = '+'
			info_str = 'Passed'
		elif decompiled_count > 0:
			indicate_char = '*'
			info_str = 'Partially passed'
		else:
			indicate_char = '-'
			info_str = 'Failed'
		print_info(indicate_char, info_str + ' (%d / %d)' % (decompiled_count, input_files_count), version_format % py_ver, max_align_need)

def main():
	global max_align_need
	global source_files_contents
	global debug
	
	debug = False
	old = False
	file_basename_exp = '*'
	ver = ''
	if len(sys.argv) > 1:
		for arg in sys.argv[1:]:
			if arg == 'debug':
				debug = True
			elif arg == 'old':
				old = True
			elif arg.startswith('exp='):
				file_basename_exp = arg.split('=', 1)[1]
				file_basename_exp = re.sub('[^*a-zA-Z0-9_-]', '', file_basename_exp)
			elif arg.isdigit():
				ver = arg
	
	pycdc_path = run_cmd('where pycdc%s' % ('_old' if old else ''), True).split('\n')[0]
	if ver:
		versions = [ver]
	else:
		versions = python_versions = [
			'30',
			'31',
			'32',
			'33',
			'34',
			'35',
			'36',
			'37',
			'38',
			'39',
			'310',
			#'311',
			]
	
	input_dir = Path('./input/')
	input_dir_exp = str(input_dir / (file_basename_exp + '.py'))
	input_files = glob.glob(input_dir_exp)
	if not input_files:
		print('No input files matched expression.')
		return
	
	print_start(file_basename_exp)
	max_align_need = len(max(input_files, key=len))
	source_files_contents = {}
	
	compiled_dir = Path('./compiled/')
	compile(input_dir, compiled_dir, versions, file_basename_exp)
	decompiled_dir = Path('./decompiled/')
	decompile(compiled_dir, decompiled_dir, versions, file_basename_exp, pycdc_path)
	
	version_to_decompiled_count = {}
	
	for py_ver in versions:
		print('Testing Version [ %s ]... ' % py_ver)
		print('=====================')
		if py_ver not in version_to_decompiled_count:
			version_to_decompiled_count[py_ver] = 0
		
		for source_file in input_files:
			source_file = Path(source_file)
			decompiled_source_path = decompiled_dir / (source_file.stem + '_%s' % py_ver + '.py')
			if check_failed(source_file, decompiled_source_path):
				continue
			print_info('+', 'Succeeded', source_file.name, max_align_need)
			version_to_decompiled_count[py_ver] += 1
		print()
	print('Done.')
	print_summary(version_to_decompiled_count, len(input_files), versions[0])


if __name__ == '__main__':
	main()
		

