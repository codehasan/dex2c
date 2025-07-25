#!/data/data/com.termux/files/usr/bin/bash

if ! command -v termux-setup-storage; then
  echo "This script can be executed only on Termux"
  exit 1
fi

termux-setup-storage

cd $HOME

pkg update
pkg upgrade -y
pkg i -y ncurses-utils

green="$(tput setaf 2)"
nocolor="$(tput sgr0)"
red="$(tput setaf 1)"
blue="$(tput setaf 32)"
yellow="$(tput setaf 3)"
note="$(tput setaf 6)"

echo "${green}━━━ Basic Requirements Setup ━━━${nocolor}"

pkg install -y python git cmake rust clang make wget ndk-sysroot zlib libxml2 libxslt pkg-config libjpeg-turbo build-essential binutils openssl aapt
# UnComment below line if you face clang error during installation procedure
# _file=$(find $PREFIX/lib/python3.11/_sysconfigdata*.py)
# rm -rf $PREFIX/lib/python3.11/__pycache__
# sed -i 's|-fno-openmp-implicit-rpath||g' "$_file"
pkg install -y python-cryptography
LDFLAGS="-L${PREFIX}/lib/" CFLAGS="-I${PREFIX}/include/" pip install --upgrade wheel pillow
pip install cython setuptools
CFLAGS="-Wno-error=incompatible-function-pointer-types -O0" pip install --upgrade lxml

echo "${green}━━━ Starting SDK Tools installation ━━━${nocolor}"
if [ -d "android-sdk" ]; then
  echo "${red}Seems like sdk tools already installed, skipping...${nocolor}"
elif [ -d "androidide-tools" ]; then
  rm -rf androidide-tools
  git clone https://github.com/AndroidIDEOfficial/androidide-tools
  cd androidide-tools/scripts
  ./idesetup -c
else
  git clone https://github.com/AndroidIDEOfficial/androidide-tools
  cd androidide-tools/scripts
  ./idesetup -c
fi

echo "${yellow}ANDROID SDK TOOLS Successfully Installed!${nocolor}"

cd $HOME
echo
echo "${green}━━━ Starting NDK installation ━━━${nocolor}"
echo "Now You'll be asked about which version of NDK to isntall"
echo "${note}If your Android Version is 9 or above then choose ${red}'9'${nocolor}"
echo "${note}If your Android Version is below 9 or if you faced issues with '9' (A9 and above users) then choose ${red}'8'${nocolor}"
echo "${red} If you're choosing other options then you're on your own and experiment yourself ¯⁠\⁠_⁠ಠ⁠_⁠ಠ⁠_⁠/⁠¯${nocolor}"
if [ -f "ndk-install.sh" ]; then
  chmod +x ndk-install.sh && bash ndk-install.sh
else
  cd && pkg upgrade && pkg install wget && wget https://github.com/MrIkso/AndroidIDE-NDK/raw/main/ndk-install.sh --no-verbose --show-progress -N && chmod +x ndk-install.sh && bash ndk-install.sh
fi

if [ -f "ndk-install.sh" ]; then
  rm ndk-install.sh
fi

ndk_versions=("17.2.4988734" "18.1.5063045" "19.2.5345600" "20.1.5948944" "21.4.7075529" "22.1.7171670" "23.2.8568313" "24.0.8215888" "26.1.10909125" "27.1.12297006" "27.2.12479018" "28.1.13356709" "29.0.13113456")
ndk_version=""

for version in "${ndk_versions[@]}"; do
  if [ -d "$HOME/android-sdk/ndk/$version" ]; then
    ndk_version="$version"
    break
  fi
done

if [ -z "$ndk_version" ]; then
  echo "${red}You didn't install any NDK. Terminating!"
  exit 1
fi
echo "${yellow}ANDROID NDK Successfully Installed!${nocolor}"

cd $HOME
echo
echo "${green}━━━ Setting up apktool ━━━${nocolor}"
if [ -f "$PREFIX/bin/apktool.jar" ]; then
  echo "${blue}apktool is already installed${nocolor}"
else
  sh -c 'wget https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.10.0.jar -O $PREFIX/bin/apktool.jar'

  chmod +r $PREFIX/bin/apktool.jar

  sh -c 'wget https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool -O $PREFIX/bin/apktool' && chmod +x $PREFIX/bin/apktool || exit 2
fi

cd $HOME
if [ -d "dex2c" ]; then
  cd dex2c
elif [ -f "dcc.py" ] && [ -d "tools" ]; then
  :
else
  git clone https://github.com/ratsan/dex2c || exit 2
  cd dex2c || exit 2
fi

if [ -f "$HOME/dex2c/tools/apktool.jar" ]; then
  rm $HOME/dex2c/tools/apktool.jar
  cp $PREFIX/bin/apktool.jar $HOME/dex2c/tools/apktool.jar
else
  sh -c 'wget https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.10.0.jar -O $HOME/dex2c/tools/apktool.jar'
fi

cd ~/dex2c
python3 -m pip install -r requirements.txt || exit 2

update_rc() {
  local file="$1"
  sed -i '/export ANDROID_HOME=/d' "$file"
  sed -i '/export PATH=.*\/android-sdk\/cmdline-tools\/latest\/bin/d' "$file"
  sed -i '/export PATH=.*\/android-sdk\/platform-tools/d' "$file"
  sed -i '/export PATH=.*\/android-sdk\/build-tools\/34.0.4/d' "$file"
  sed -i '/export PATH=.*\/android-sdk\/ndk\/.*/d' "$file"
  sed -i '/export ANDROID_NDK_ROOT=/d' "$file"

  echo -e "export ANDROID_HOME=$HOME/android-sdk\nexport PATH=\$PATH:$HOME/android-sdk/cmdline-tools/latest/bin\nexport PATH=\$PATH:$HOME/android-sdk/platform-tools\nexport PATH=\$PATH:$HOME/android-sdk/build-tools/34.0.4\nexport PATH=\$PATH:$HOME/android-sdk/ndk/$ndk_version\nexport ANDROID_NDK_ROOT=$HOME/android-sdk/ndk/$ndk_version" >> "$file"
}

update_xonsh_rc() {
  local file="$1"
  sed -i '/\$ANDROID_HOME =/d' "$file"
  sed -i '/\$PATH.*\/android-sdk\/cmdline-tools\/latest\/bin/d' "$file"
  sed -i '/\$PATH.*\/android-sdk\/platform-tools/d' "$file"
  sed -i '/\$PATH.*\/android-sdk\/build-tools\/34.0.4/d' "$file"
  sed -i '/\$PATH.*\/android-sdk\/ndk\/.*/d' "$file"
  sed -i '/\$ANDROID_NDK_ROOT =/d' "$file"
  cat <<EOF >> "$file"
\$ANDROID_HOME = "${HOME}/android-sdk"
\$PATH.append('${HOME}/android-sdk/cmdline-tools/latest/bin')
\$PATH.append('${HOME}/android-sdk/platform-tools')
\$PATH.append('${HOME}/android-sdk/build-tools/34.0.4')
\$PATH.append('${HOME}/android-sdk/ndk/${ndk_version}')
\$ANDROID_NDK_ROOT = "${HOME}/android-sdk/ndk/${ndk_version}"
EOF
}

if [ -f "$HOME/.bashrc" ]; then
  update_rc "$HOME/.bashrc"
fi
if [ -f "$HOME/.zshrc" ]; then
  update_rc "$HOME/.zshrc"
fi
if [ -f "$HOME/.xonshrc" ]; then
  update_xonsh_rc "$HOME/.xonshrc"
fi
if [ -f "$PREFIX/etc/bash.bashrc" ]; then
  update_rc "$PREFIX/etc/bash.bashrc"
fi

cat > $HOME/dex2c/dcc.cfg << EOL
{
    "apktool": "tools/apktool.jar",
    "ndk_dir": "$HOME/android-sdk/ndk/${ndk_version}",
    "signature": {
        "keystore_path": "keystore/debug.keystore",
        "alias": "androiddebugkey",
        "keystore_pass": "android",
        "store_pass": "android",
        "v1_enabled": true,
        "v2_enabled": true,
        "v3_enabled": true
    }
}
EOL

echo "${green}============================"
echo "Great! dex2c installed successfully!"
echo "============================${nocolor}"
