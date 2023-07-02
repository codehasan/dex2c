<a name="readme-top"></a>

<div align="center">
  <h1 align="center">𝐃𝐞𝐱𝟐𝐂</h1>
  <p align="center">
    Method based aot compiler that can wrap dalvik bytecode with jni native
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<summary>Table of Contents</summary>
  <ul>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#installation">Installation</a>
      <ul>
        <li><a href="#linux">Linux</a></li>
        <li><a href="#windows">Widndows</a></li>
      </ul>
    </li>
    <li>
      <a href="#usage">Usage</a>
        <ul>
          <li><a href="#filters">Filters</a></li>
          <li><a href="#protect-apps">Protect Apps</a></li>
        </ul>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ul>



<!-- ABOUT THE PROJECT -->
## About The Project

This project is a forked version of [amimo/dcc](https://github.com/amimo/dcc), which aims to make it easy for everyone to use this tool. We automated plenty of process that you had to do manually in original dcc. Moreover, we always try to add new features to make this tool more usable in real world applications.


### Built With

* ![Python][Python3]
* [![Androguard][Androguard3]][Androguard_Url]


<!-- GETTING STARTED -->
## Installation

It requires python 3.8 or higher version to run this tool. So, make sure your python is up-to-date.

1. Clone the repo
   ```bash
   git clone https://github.com/ratsan/dex2c.git
   ```
2. Open cloned directory
   ```bash
   cd dex2c
   ```
3. Download apktool latest version from [bitbucket](https://bitbucket.org/iBotPeaches/apktool/downloads/) and save it in `tools` folder with name `apktool.jar`
   ```bash
   wget -O tools/apktool.jar https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.7.0.jar
   ```
4. <a href="https://developer.android.com/ndk/downloads">Download</a> andorid ndk for your operating system and extract it. Copy the folder path where `ndk-build` executable is located inside the extracted folder and configure `ndk_dir` in `dcc.cfg`

### Linux

1. Install required dependencies
   ```bash
   pip3 install -r requirements.txt
   ```
2. Install JRE or JDK if not already installed
   ```bash
   sudo apt-get install openjdk-11-jdk
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Windows

1. Install required dependencies
   ```bash
   pip3 install -r requirements.txt
   ```
2. Install JRE or JDK from <a href="https://www.oracle.com/java/technologies/javase/jdk11-archive-downloads.html">oracle</a> if not already installed. Then add the bin folder path in PATH environment variable. Search in google, how to install jdk in windows if you need more guidance on this topic.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

### Filters

Add all your filters in `filter.txt` file - one rule each line. Filters are are made using regex patterns. There are two types of filters avilable in dcc - whitelist, blacklist. Use them according to your need.

#### WhiteList

- Protect just one method in a specific class. It's just a demo.
```
com/some/class;some_method(some_parameters)return_type
```

- Protect all methods in a specific class. It's also just a demo.
```
com/some/class;.*
```

- Protect all methods in all classes under a package path. It's also just a demo.
```
com/some/package/.*;.*
```

- Protect a method with the name onCreate in all classes. It's also just a demo.
```
.*;onCreate\(.*
```

##### BlackList

Adding an exclamation `!` sign before a rule will mark that rule as a blacklist.

- Exclude one method in a specific class from being protected. It's just a demo.
```
!com/some/class;some_method(some_parameters)return_type
```

- Exclude all methods in a specific class from being protected. It's also just a demo.
```
!com/some/class;.*
```

- Exclude all methods in all classes under a package path from being protected. It's also just a demo.
```
!com/some/package/.*;.*
```

- Exclude a method with the name onCreate in all classes from being protected. It's also just a demo.
```
!.*;onCreate\(.*
```

### Protect Apps

- Copy your apk file in `dex2c` folder where `dcc.py` is located and run this command

```bash
python3 dcc.py -a input.apk -o output.apk
```

- Run this command to know about all the other options available in dcc to find the best ones for your need

```bash
python3 dcc.py --help
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] Add custom lib loader
- [x] Add apksigner
- [x] Add abi handler
- [x] Add signature configuration in `dcc.cfg`
- [x] Add new options
    - [x] --skip-synthetic
    - [x] --custom-loader
    - [x] --force-keep-libs

See the [open issues](https://github.com/ratsan/dex2c/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the Apache License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

### Projects

* [DCC](https://github.com/amimo/dcc)
* [Androguard][Androguard_Url]

### People

* GoldenBoot - [Telegram](https://t.me/goldenboot)
* Rahat - [Telegram](https://t.me/botxrahat)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[Python3]: https://img.shields.io/badge/Python-F6D049?style=for-the-badge&logo=python
[Androguard3]: https://img.shields.io/badge/Androguard-FFFFFF?style=for-the-badge&logo=androguard
[Androguard_Url]: https://github.com/androguard/androguard
