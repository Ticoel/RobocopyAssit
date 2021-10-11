# RobocopyAssit
# Nicolas Troupel
# version: 20211011

import inspect
import pathlib
import platform
import subprocess
import sys
import os

# Gére le soulèvement d'exception. La fonction récupère
# les informations relative à l'exception afin de poursuivre l'arret
# ou d'affiche ces informations. Par défault, la fonction termine dès qu'une
# exception est soulevé.
def handle_func_exception(exit=True, exit_value="1"):
	try:
		exc_info = sys.exc_info()
		exc_type = str(exc_info[0])[8:-2]
		exc_value = exc_info[1]
		exc_trace = inspect.trace()
		exc_file = None
		exc_line = None
		exc_name = None

		if exc_type == "SystemExit":
			raise(SystemExit(exc_value))
		else:
			print("{:-<80}".format(""))
			for i in exc_trace:
				exc_file = i[1]
				exc_line = i[2]
				exc_name = i[3]
				print("In file {} at the line #{}"\
				.format(exc_file, exc_line))
				print("{:<3}{} had met an type error {}"\
				.format("", exc_name, exc_type))
				if exc_value:
					print("{:<3}{}".format("", exc_value))
				print("Error code: {0}".format(exit_value))

		if exit:
			input("Press Enter to quit...")
			raise(SystemExit(exit_value))

	except SystemExit as value:
		sys.exit(value)

# Vérrifie que le système d'exploitation est Windows
# et que la version 3 de Python est utilisé. Si cela n'est pas le cas,
# la fonction termine.
def check_system():
	try:
		if platform.system() != "Windows":
			raise OSError("Windows is required")

		if int(platform.python_version_tuple()[0]) != 3:
			raise SystemError("Python 3 is required")

	except:
		handle_func_exception(exit_value="02")

# A partir du chemin du fichier en cours d'execution,
# la fonction retourne dans une tulpe le nom du lecteur,
# le dossier où se trouve le fichier et le chemin du fichier.
# Ce est dernier est passé en argument par la variable frame
# via la fonction inspect.currentframe().
def check_file_location(frame=None, root=None):
	try:
		frame_path = pathlib.WindowsPath(os.getcwd())
		directory_path = frame_path.parent

		if root and directory_path != pathlib.WindowsPath(frame_path.anchor):
			raise UserWarning("{} don't found at the root of drive {}"\
			.format(frame_path.name, frame_path.drive))

		result = (frame_path.drive, str(directory_path), str(frame_path))

	except:
		handle_func_exception(exit_value="03")
	else:
		return result

# Si la variable source est True, récupère à partir de la lettre d'un lecteur
# son nom et vérifie que celui ne se termine pas par -cop, sinon la fonction
# déclenche une exception.
# Si la variable source est False, récupère à partir du nom
# auquels "-cop" est ajouté la lettre d'un lecteur.
# Vérifie aussi que le lecteur est sain.
def get_volume(source=None, letter=None, label=None):
	try:
		if source and letter:
			if letter.endswith(":"):
				letter = letter[:-1]
			infos = subprocess.check_output(["powershell", "get-volume",\
			"-driveletter", letter]).decode(sys.stdout.encoding).split()
			label = infos[17]
			if label.endswith("-bak"):
				raise UserWarning("{} is not the source volume".format(label))

		elif not source and label:
			label = "{}-bak".format(label)
			try:
				infos = subprocess.check_output(["powershell", "get-volume",\
				"-filesystemlabel", label]).decode(sys.stdout.encoding).split()
			except:
				raise UserWarning("The volume {} is not found".format(label))
			letter = infos[16]

		else:
			raise UserWarning("The arguments are not valid")

		health = infos[20]
		if health != "Healthy":
			raise UserWarning("The {} is maybe endomaged"\
			.format(label))

		result = ("{}:".format(letter), label)

	except:
		handle_func_exception(exit_value="04")
	else:
		return result

# Déclenche Robocopy en excluant le dossier "System Volume Information".
# La sortie est affiché en temps réel. Une exception est déclenché si Robocopy
# termine en renvoyant une valeur supérieur à 3.
def run_robocopy(src, dst):
	try:
		robocopy = subprocess.Popen(["robocopy", "{0}\\".format(src), "{0}\\".format(dst),\
		"*.*", "/dcopy:T", "/copyall", "/secfix", "/timfix", "/mir", "/a+:RA",\
		"/xd", "System Volume Information", "$RECYCLE.BIN", "/it", "/xj", "/fft",\
		"/r:1", "/w:2", "/v", "/ts", "/bytes"],\
		stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		while robocopy.returncode == None:
			line = robocopy.stdout.readline().decode("cp850").rstrip('\n')
			if not line:
				robocopy.wait()
			else:
				print(line)

		if robocopy.returncode > 3:
			raise UserWarning("Robocopy had meet error no. {}"\
			.format(robocopy.returncode))

	except:
		handle_func_exception(exit_value="05")

# Ceci s'execute lorsque le fichier est dirrectement éxécuté.
if __name__ == "__main__":
	try:
		print("RobocopyAssit")
		print("Version 20211011")

		print("Check system...")
		check_system()

		print("Research volumes...")
		file_location = check_file_location(frame=inspect.currentframe(), root=False)
		source = get_volume(source=True, letter=file_location[0])
		destination = get_volume(source=False, label=source[1])

		print("Bakup from \"{0}\" to \"{1}\"...".format(source[1], destination[1]))

		print("Quit (tape q) or Continue (press Enter)...")
		keys = input()
		if keys == 'q':
			raise UserWarning("User has quit bakup.")
		

		run_robocopy(source[0], destination[0])

		print("Bakup is complete.")

	except:
		handle_func_exception(exit_value="06")
	else:
		print("{:-<80}".format(""))

		input("Press Enter for quit...")

		sys.exit(0)
