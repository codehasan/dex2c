<a name="readme-top"></a>

<div align="center">
  <h1 align="center">𝐃𝐞𝐱𝟐𝐂</h1>




[![Stars](https://img.shields.io/github/stars/codehasan/Dex2C?color=yellow)](https://github.com/TeamUltroid/Ultroid/stargazers)
[![Python](https://img.shields.io/badge/Python-v3.10.3-blue)](https://www.python.org/)
[![Forks](https://img.shields.io/github/forks/codehasan/Dex2C?color=orange)](https://github.com/codehasan/Dex2C/fork)
[![Size](https://img.shields.io/github/repo-size/codehasan/Dex2C?color=green)](https://github.com/codehasan/Dex2C/)
[![Contributors](https://img.shields.io/github/contributors/codehasan/Dex2C?color=green)](https://github.com/codehasan/Dex2C/graphs/contributors)
[![License](https://img.shields.io/badge/License-Apache-blue)](./LICENSE)


  
  <p align="center">
    Method-based AOT compiler that can wrap Dalvik bytecode with JNI native code.
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
<summary>Table of contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About the project</a>
      <ul>
        <li><a href="#built-with">Built with</a></li>
      </ul>
    </li>
    <li>
      <a href="#installation">Installation</a>
      <ul>
        <li><a href="#linux">Linux</a></li>
        <li><a href="#windows">Windows</a></li>
        <li><a href="#termux">Android (Termux)</a></li>
      </ul>
    </li>
    <li>
      <a href="#usage">Usage</a>
        <ul>
          <li><a href="#filters">Filters</a></li>
          <li><a href="#protect-apps">Protect apps</a></li>
        </ul>
    </li>
    <li><a href="#how-to-change-lib-name">How to change lib name</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->
# About the project

This project is a forked version of [amimo/dcc](https://github.com/amimo/dcc), which aims to make it easy for everyone to use this tool. We automated plenty of processes that you had to do manually in the original DCC. Moreover, we always try to add new features to make this tool more usable in real-world applications.
Check out <a href="#roadmap">Roadmap</a> to know about the changes we made and also the changes we are planning to make in the feature.

### Built with


* ![Python][Python-Badge]
* [![Androguard][Androguard-Badge]][Androguard_Repository]


<!-- GETTING STARTED -->
# Installation

Python 3.8 or higher is required for running this tool. So, make sure your python is up-to-date.

1. Clone the repo.
   ```bash
   git clone https://github.com/codehasan/dex2c
   ```
2. Open the cloned directory.
   ```bash
   cd dex2c
   ```
3. Download **Apktool** latest version from [bitbucket](https://bitbucket.org/iBotPeaches/apktool/downloads/) and save it in `tools` folder with the name `apktool.jar`
   ```bash
   wget -O tools/apktool.jar https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.9.3.jar
   ```
4. <a href="https://developer.android.com/ndk/downloads">Download</a> android NDK for your OS and extract it. Copy the folder path where `ndk-build` executable is located inside the extracted folder and configure `ndk_dir` in `dcc.cfg`

### Linux

![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)

1. Install required dependencies.
   ```bash
   pip3 install -r requirements.txt
   ```
2. Install JRE/JDK if you don't have it installed. The recommended JDK version is 11.
   ```bash
   sudo apt-get install openjdk-11-jdk
   ```

### Windows

![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)

1. Install required dependencies.
   ```bash
   pip3 install -r requirements.txt
   ```
2. Install JRE/JDK from <a href="https://www.oracle.com/java/technologies/javase/jdk11-archive-downloads.html">oracle</a> if you don't have it installed. Search in Google, how to install JDK in Windows if you need more guidance on this topic. The recommended JDK version is 11.

### Termux

![Android](https://img.shields.io/badge/Android-3DDC84?style=for-the-badge&logo=android&logoColor=white)

One Step Installation: Run Below Command
   ```bash
   pkg install wget && wget -O termux_install.sh https://raw.githubusercontent.com/codehasan/dex2c/termux_install.sh && chmod -R +x termux_install.sh && ./termux_install.sh
   ```
> NOTE: Some users have reported about installation errors with latest `clang` on termux. If you happen to face the same issue, then uncomment the lines stated in `termux_install.sh` and then proceed with the installation.


<!-- USAGE EXAMPLES -->
# Usage

### Filters

Add all your filters in `filter.txt` file - one rule for each line. Filters are made using regex patterns. There are two types of filters available in **Dex2c** - whitelist, and blacklist. You can use them whenever you need them.

#### WhiteList

- Protect just one method in a specific class.
```
com/some/class;some_method(some_parameters)return_type
```

- Protect all methods in a specific class.
```
com/some/class;.*
```

- Protect all methods in all classes under a package path.
```
com/some/package/.*;.*
```

- Protect a method with the name onCreate in all classes.
```
.*;onCreate\(.*
```

#### BlackList

Adding an exclamation `!` sign before a rule will mark that rule as a blacklist.

- Exclude one method in a specific class from being protected.
```
!com/some/class;some_method(some_parameters)return_type
```

- Exclude all methods in a specific class from being protected.
```
!com/some/class;.*
```

- Exclude all methods in all classes under a package path from being protected.
```
!com/some/package/.*;.*
```

- Exclude a method with the name onCreate in all classes from being protected.
```
!.*;onCreate\(.*
```


### Protect apps

- Copy your apk file to `dex2c` folder where `dcc.py` is located and run this command.

```bash
python3 dcc.py -a input.apk -o output.apk
```

- Run this command to know about all the other options available in dcc to find the best ones for your needs.

```bash
python3 dcc.py --help
```


<!-- CHANGE LIB NAME -->
# How to change lib name

Open `project/jni/Android.mk` file in the cloned directory. You will find a variable named `LOCAL_MODULE`, initially with the value `stub`. Please change it to your desired lib name. Keep in mind the following instructions to prevent possible errors.
- Don't use spaces in lib name, use hyphen `-` or underscore `_`
- Don't use any kind of symbols or punctuations in lib name other than underscores and hyphens
- Don't start the lib name with the text `lib` itself



<!-- ROADMAP -->
# Roadmap

- [x] Add custom lib loader
- [x] Add new apksigner
- [x] Add multi-dex support
- [x] Add app abi handler
- [x] Add signature configuration in `dcc.cfg`
- [x] Add new options
    - [x] --skip-synthetic
    - [x] --custom-loader
    - [x] --force-keep-libs
    - [x] --obfuscate

See the [open issues](https://github.com/codehasan/dex2c/issues) for a full list of proposed features and known issues.



<!-- CONTRIBUTING -->
# Contributing

Contributions are what makes the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give this project a star! Thanks again!

1. Fork the project
2. Create your feature branch. (`git checkout -b feature/AmazingFeature`)
3. Commit your changes. (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch. (`git push origin feature/AmazingFeature`)
5. Open a pull request.



<!-- LICENSE -->
# License

Distributed under the Apache License. See `LICENSE.txt` for more information.



<!-- ACKNOWLEDGMENTS -->
# Acknowledgments

### Projects

* [DCC](https://github.com/amimo/dcc)
* [Androguard](https://github.com/androguard/androguard)

### People

* Rahat - [Telegram](https://t.me/botxrahat)
* GoldenBoot - [Telegram](https://t.me/goldenboot)

<p align="right"><a href="#readme-top">Go to top</a></p>

<!-- MARKDOWN LINKS & IMAGES -->
[Python-Badge]: https://img.shields.io/badge/Python-F6D049?style=for-the-badge&logo=python
[Androguard-Badge]: https://img.shields.io/badge/Androguard-FFFFFF?style=for-the-badge&logo=android
[Androguard_Repository]: https://github.com/androguard/androguard
