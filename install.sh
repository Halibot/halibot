#!/usr/bin/env bash
#
# *nix halibot installer

BINLOC=/usr/bin/halibot
SRCLOC=/usr/local/share/halibot
VERBOSE=

# Detect existing installation and override default (BIN|SRC)LOC if already installed
if command -v halibot 2>&1 >/dev/null; then
	BINLOC=$(command -v halibot)
	SRCLOC=$(grep SRCLOC= $BINLOC) # THere should be a SRCLOC=... line in the run script
	SRCLOC=${SRCLOC/SRCLOC=/}      # Remove the SRCLOC=
fi

# Define functions
function uninstall {
	rm -f $VERBOSE $BINLOC &&
	rm -rf $VERBOSE $SRCLOC
}

function install {
	# Sed was being fussy on FreeBSD, used ed, the one true text editor
	printf "1a\nSRCLOC=$SRCLOC\n.\n,p\nQ\n" | ed -s run-scripts/halibot > $BINLOC &&
	chmod +x $BINLOC &&

	mkdir -p $SRCLOC &&
	cp $VERBOSE main.py $SRCLOC &&
	cp -r $VERBOSE halibot $SRCLOC/halibot &&
	cp -r $VERBOSE packages $SRCLOC/packages &&
	cp -r $VERBOSE config $SRCLOC/config
}

# Handle arguments
while getopts huvb:s: opt; do
	case "${opt}" in
		h) cat <<EOF
Halibot installer

Options:
  -b [path] Specify the path to install the run script to (should be in \$PATH)
            Default: $BINLOC
  -h        Print this useful help
  -s [path] Specify the path to install the halibot source files
            Default: $SRCLOC
  -u        Uninstall existing installation
  -v        Turn on verbose mode
EOF
exit 0
;;
		v) VERBOSE=-v ;;
		b) BINLOC=$OPTARG ;;
		s) SRCLOC=$OPTARG ;;
		u)
			echo "Uninstalling..."
			if uninstall; then
				echo "Successfully uninstalled."
				exit 0
			fi
			echo "Uninstallation failed!"
			exit 1
			;;
		*)
			echo "Use -h for help"
			exit 1
			;;
	esac
done

# Check if there is already an installation
if [ -d "$SRCLOC" ]; then
	while true; do
		read -p "Halibot appears to be already installed, reinstall? [yn] " answer
		case $answer in
			[Yy]* )
				echo "Okay, removing previous installation..."
				uninstall
				if [ $? -ne 0 ]; then
					echo "Could not remove previous installation."
					exit 1
				fi
				break
				;;
		  [Nn]* )
				echo "Okay, bye."
				exit 0
				;;
			* )
				echo "You should answer yes or no"
		esac
	done
fi

echo "Installing halibot..."
install
if [ $? -ne 0 ]; then
	echo "Failed to install!"
	# TODO remove half-installed stuff
	exit 1
fi

echo "Successfully installed."
