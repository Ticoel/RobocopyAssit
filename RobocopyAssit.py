# RobocopyAssit
# Nicolas Troupel
# version: 20220210

import datetime
import inspect
import json
import pathlib
import platform
import subprocess
import sys

# Gére l'affichage pour le debug du script. 
def debug(text):
	print("{:>^80}".format("DEBUG!"))
	print(text)
	print("{:<^80}".format("DEBUG!"))

# Gére le soulèvement d'exception. Par défault, la fonction termine dès qu'une
# exception est soulevé avec le code d'erreur 0.
def handle_exception(to_exit=True, error_code=0):
	# Récupère une liste non modifiable (tuple) regroupant des informations
	# sur l'exception soulevée.
	exc_info = sys.exc_info()
	# debug(exc_info)
	# Récupère le non de la classe qui a soulevé l'exception.
	exc_type = exc_info[0]
	# Récupère la valeur de l'exception.
	exc_value = exc_info[1]
	# Récupère une liste regroupant des informations relative au cadre.
	exc_trace = inspect.trace()
	# debug(exc_trace)
	# Définie une variable contenant le nom du fichier
	# où est soulevé l'exception.
	exc_file = None
	# Définie une variable contenant la ligne du fichier
	# où est soulevé l'exception.
	exc_line = None
	# Définie une variable contenant le nom de la fonction
	# où est soulevé l'exception
	exc_name = None

	if exc_type != SystemExit:
		exc_file = exc_trace[-1][1]
		exc_line = exc_trace[-1][2]
		exc_name = exc_trace[-1][3]

		print("{:-<80}".format(""))
		print("In file {} at the line #{}".format(exc_file, exc_line))
		print("{:<3}{} had met an error {} of type {}"\
			.format("", exc_name, error_code, exc_type))
		if exc_value:
			print("{:<3}because {}".format("", exc_value))
		print("{:-<80}".format(""))

		if (to_exit):
			input("Press Enter to quit...")
			sys.exit(error_code)

	else:
		sys.exit(error_code)

# Vérrifie que le système d'exploitation est Windows
# et que la version 3 de Python est utilisé. Si cela n'est pas le cas,
# la fonction termine le script.
# Code d'erreurs: 20; 21.
def check_system():
	print("Check system...")

	try:
		if platform.system() != "Windows":
			# debug(platform.system())
			raise OSError("Windows is required")
	except:
		handle_exception(error_code=20)

	try:
		if int(platform.python_version_tuple()[0]) < 3:
			# debug(platform.python_version_tuple)
			raise SystemError("Python 3 is required")
	except:
		handle_exception(error_code=21)

	print("System checked!")

# A partir du chemin du dossier de travail,
# indique si le dossier est à la racine du lecteur,
# en retournant le cas échant son chemin.
# Code d'erreur: 30.
def get_source():
	print("Get Source...")

	try:
		directory_path = pathlib.WindowsPath.cwd()
		# debug(directory_path)

		if not directory_path.parent.match(directory_path.anchor):
			raise UserWarning("{} don't found in a directory at the root of drive {}"\
				.format(directory_path.name, directory_path.drive))

	except:
		handle_exception(error_code=30)

	else:
		print("SourceGotten!")
		return directory_path.anchor

# Récupère à partir du lecteur source le lecteur de destination en y ajoutant
# -bak. Vérifie aussi que la santé des lecteurs.
# Code d'erreurs: 40, 41, 42, 43.
def get_destination_from_source(sourcePath):
	print("Get Destination...")

	try:
		sourceInfos = subprocess.check_output(["powershell", "get-volume",\
				"-FilePath", sourcePath, "|", "ConvertTo-Json"])\
				.decode(sys.stdout.encoding, errors="ignore")
		# debug(sourceInfos)

		sourceInfos = json.loads(sourceInfos)
		# debug(sourceInfos)

		# debug(sourceInfos["FileSystemLabel"])
		sourceLabel = sourceInfos["FileSystemLabel"]

		# debug(sourceInfos["HealthStatus"])
		sourceHealthStatus = sourceInfos["HealthStatus"]
	except:
		handle_exception(error_code=40)


	try:
		if sourceHealthStatus != "Healthy":
			raise UserWarning("{} is {}".format(sourceLabel, sourceHealthStatus))
	except:
		handle_exception(error_code=41)

	destinationLabel = "{}-bak".format(sourceLabel)
	# debug(destinationLabel)

	try:
		destinationInfos = subprocess.check_output(["powershell", "get-volume",\
				"-FileSystemLabel", destinationLabel, "|", "ConvertTo-Json"])\
				.decode(sys.stdout.encoding, errors="ignore")
		# debug(destinationInfos)

		destinationInfos = json.loads(destinationInfos)
		# debug(destinationInfos)

		if (isinstance(destinationInfos, list) and len(destinationInfos) > 1):
			raise UserWarning("There is two or more drive with same destination label.")

		# debug(destinationInfos["DriveLetter"])
		destinationDriveLetter = destinationInfos["DriveLetter"]

		# debug(destinationInfos["HealthStatus"])
		destinationHealthStatus = destinationInfos["HealthStatus"]
	except:
		handle_exception(error_code=42)

	try:
		if destinationHealthStatus != "Healthy":
			raise UserWarning("{} is {}".format(sourceLabel, sourceHealthStatus))
	except:
		handle_exception(error_code=43)

	print("Destination Gotten!")

	return ("{}:\\".format(destinationDriveLetter), destinationLabel, sourceLabel)

# Déclenche Robocopy en excluant le dossier "System Volume Information",
# la corbeille et le dossier LOG à la racine de la source.
# La sortie est affiché en temps réel et dans un fichier log.
# Une exception est déclenché si Robocopy
# termine en renvoyant une valeur supérieur à 3.
# Code d'erreur: 50.
def run_robocopy(src_path, dst_path):
	print("Start Robocopy...")

	try:
		log_file = pathlib.PureWindowsPath(src_path, "LOG", "robocopy-{}.log"\
		.format(datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")))
		# debug(log_file)

		robocopy = subprocess.Popen(["robocopy", src_path, dst_path,\
		# Options de copie
		"/e", "/zb", "/dcopy:dat", "/copyall", "/secfix", "/timfix", "/mir", "/a+:RA", "/a-:SHNT",\
		# Options de sélections de fichier
		"/xd", "System Volume Information", "$RECYCLE.BIN", "LOG",\
		# Options de nouvelle tentative
		"/r:3", "/w:10",\
		# Options du journal
		"/v", "/ts", "/fp", "/bytes", "/log:{}".format(log_file), "/tee"],\
		stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		while robocopy.returncode == None:
			line = robocopy.stdout.readline().decode("cp850", errors="ignore").rstrip('\n')
			if not line:
				robocopy.wait()
			else:
				print(line)

		if robocopy.returncode > 3:
			raise UserWarning("Robocopy had meet error no. {}"\
			.format(robocopy.returncode))

	except:
		handle_exception(error_code=50)
	else:
		print("Robocopy finished!")

# Ceci s'execute lorsque le fichier est dirrectement éxécuté.
if __name__ == "__main__":
	print("{:-^80}".format("RobocopyAssit"))
	print("{:-^80}".format("Version 20220210"))

	check_system()
	print("{:-<80}".format(""))

	source = get_source()
	# debug(source)
	print("{:-<80}".format(""))

	destination = get_destination_from_source(source)
	# debug(destination)
	print("{:-<80}".format(""))

	try:
		to_start = input("Start bakup from \"{}\" ({}) to \"{}\" ({})...\n\
Press y (yes) to continue or any key to quit...\n"\
		.format(destination[2], source, destination[1], destination[0]))
		# debug(to_start)	
		if not (to_start.lower() == "y" or to_start.lower() == "yes"):
			raise SystemExit("User has quit bakup.")
	except:
		handle_exception(60)
	else:
		print("{:-<80}".format(""))

	run_robocopy(source, destination[0])
	print("{:-<80}".format(""))

	print("Bakup completed!")
	input("Press Enter to quit...")
	