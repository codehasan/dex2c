#!/usr/bin/env python
# coding=utf-8
import argparse
import os
import re
import sys
import json
import io
import zipfile

from os import path
from logging import getLogger, INFO
from androguard.core import androconf
from androguard.core.analysis import analysis
from androguard.core.androconf import show_logging
from androguard.core.bytecodes import apk, dvm
from androguard.util import read
from dex2c.compiler import Dex2C
from dex2c.util import (
    JniLongName,
    get_method_triple,
    get_access_method,
    is_synthetic_method,
    is_native_method,
)
from subprocess import check_call, STDOUT, run
from random import choice
from string import ascii_letters, digits
from shutil import copy, move, make_archive, rmtree, copytree


APKTOOL = "tools/apktool.jar"
APKTOOL2 = 'tools/apktool.bat'
APKTOOL3 = 'tools/apktool'
SIGNJAR = "tools/apksigner.jar"
MANIFEST_EDITOR = "tools/manifest-editor.jar"
NDKBUILD = "ndk-build"

SKIP_SYNTHETIC_METHODS = False
IGNORE_APP_LIB_ABIS = False
Logger = getLogger("dcc")


def is_windows():
    return os.name == "nt"


def cpu_count():
    num_processes = os.cpu_count()
    if num_processes is None:
        num_processes = 2
    return num_processes


# n
def create_tmp_directory():
    Logger.info("Creating .tmp folder")
    if not path.exists(".tmp"):
        os.mkdir(".tmp")


# n
def get_random_str(length=8):
    characters = ascii_letters + digits
    result = "".join(choice(characters) for i in range(length))
    return result


# n
def make_temp_dir(prefix="dcc"):
    random_str = get_random_str()
    tmp = path.join(".tmp", prefix + random_str)

    while path.exists(tmp) and path.isdir(tmp):
        random_str = get_random_str()
        tmp = path.join(".tmp", prefix + random_str)
    os.mkdir(tmp)

    return tmp


# n
def make_temp_file(suffix=""):
    random_str = get_random_str()
    tmp = path.join(".tmp", random_str + suffix)

    while path.exists(tmp) and path.isfile(tmp):
        random_str = get_random_str()
        tmp = path.join(".tmp", random_str + suffix)
    open(tmp, "w")

    return tmp


# n
def clean_tmp_directory():
    tmpdir = ".tmp"
    try:
        Logger.info("Removing .tmp folder")
        rmtree(tmpdir)
    except OSError as e:
        run(["rd", "/s", "/q", tmpdir], shell=True)


class ApkTool(object):
    dcc_cfg = {}
    with open("dcc.cfg") as fp:
        dcc_cfg = json.load(fp)

    APKTOOL = dcc_cfg["apktool"]

    @staticmethod
    def decompile(apk):
        outdir = make_temp_dir("dcc-apktool-")
        if is_windows():
            check_call([APKTOOL2, 'd', '-r', '-f', '-o', outdir, apk])
        else:
            check_call(['bash', APKTOOL3, 'd', '-r', '-f', '-o', outdir, apk])
        return outdir

    @staticmethod
    def compile(decompiled_dir):
        unsiged_apk = make_temp_file("-unsigned.apk")
        check_call(
            [
                "java",
                "-jar",
                APKTOOL,
                "b",
                "--advanced",
                "-o",
                unsiged_apk,
                decompiled_dir,
            ],
            stderr=STDOUT,
        )
        return unsiged_apk


# n
def change_min_sdk(command=list(), min_sdk="21", update_existing=True):
    if "--min-sdk-version" in command:
        if update_existing:
            min_sdk_value_index = command.index("--min-sdk-version") + 1
            command[min_sdk_value_index] = min_sdk
        else:
            return
    else:
        command.append("--min-sdk-version")
        command.append(min_sdk)


# n
def change_max_sdk(command=list(), max_sdk="33", update_existing=True):
    if "--max-sdk-version" in command:
        if update_existing:
            max_sdk_value_index = command.index("--max-sdk-version") + 1
            command[max_sdk_value_index] = max_sdk
        else:
            return
    else:
        command.append("--max-sdk-version")
        command.append(max_sdk)


# n
def sign(unsigned_apk, signed_apk):
    signature = {}
    keystore = ""

    Logger.info(f"Signing {unsigned_apk} -> {signed_apk}")

    with open("dcc.cfg") as fp:
        dcc_cfg = json.load(fp)
        signature = dcc_cfg["signature"]
        keystore = signature["keystore_path"]

    if (
        signature["v1_enabled"] is False
        and signature["v2_enabled"] is False
        and signature["v3_enabled"] is False
    ):
        Logger.warning("At least one signing scheme should be enabled from v1, v2 & v3")
        move_unsigned(unsigned_apk, signed_apk)
        return

    if not path.exists(keystore) or not path.isfile(keystore):
        Logger.error("KeyStore not found in defined path or not recognized as a file")
        move_unsigned(unsigned_apk, signed_apk)
        return

    command = [
        "java",
        "-jar",
        SIGNJAR,
        "sign",
        "--in",
        unsigned_apk,
        "--out",
        signed_apk,
        "--ks",
        keystore,
        "--ks-key-alias",
        signature["alias"],
        "--ks-pass",
        "pass:" + signature["keystore_pass"],
        "--key-pass",
        "pass:" + signature["store_pass"],
    ]

    command.append("--v1-signing-enabled")
    command.append("true" if signature["v1_enabled"] is True else "false")
    command.append("--v2-signing-enabled")
    command.append("true" if signature["v2_enabled"] is True else "false")
    command.append("--v3-signing-enabled")
    command.append("true" if signature["v3_enabled"] is True else "false")
    command.append("--v4-signing-enabled")
    command.append("false")

    if signature["v1_enabled"] is True:
        change_min_sdk(command, "21")
        change_max_sdk(command, "23")
        command.append("--v1-signer-name")
        command.append("ANDROID")

    if signature["v2_enabled"] is True:
        change_min_sdk(command, "24", False)
        change_max_sdk(command, "26")

    if signature["v3_enabled"] is True:
        change_min_sdk(command, "28", False)
        change_max_sdk(command, "29")

    try:
        check_call(command, stderr=STDOUT)
    except Exception as ex:
        Logger.error("Signing %s failed!" % unsigned_apk, exc_info=True)
        print(f"{str(ex)}")
        move_unsigned(unsigned_apk, signed_apk)


def move_unsigned(unsigned_apk, signed_apk):
    Logger.info("Moving unsigned apk -> " + signed_apk)
    copy(unsigned_apk, signed_apk)


def build_project(project_dir, num_processes=0):
    check_call([NDKBUILD, "-j%d" % cpu_count(), "-C", project_dir], stderr=STDOUT)


def auto_vm(filename):
    ret = androconf.is_android(filename)

    if ret == "APK":
        dex_files = list()

        for dex in apk.APK(filename).get_all_dex():
            dex_files.append(dvm.DalvikVMFormat(dex))

        return dex_files

    elif ret == "DEX":
        return list(dvm.DalvikVMFormat(read(filename)))

    elif ret == "DEY":
        return list(dvm.DalvikVMFormat(read(filename)))

    raise Exception("Unsupported file %s" % filename)


class MethodFilter(object):
    def __init__(self, configure, vm):
        self._compile_filters = []
        self._keep_filters = []
        self._compile_full_match = set()

        self.conflict_methods = set()
        self.native_methods = set()
        self.annotated_methods = set()

        self._load_filter_configure(configure)
        self._init_conflict_methods(vm)
        self._init_native_methods(vm)
        self._init_annotation_methods(vm)

    def _load_filter_configure(self, configure):
        if not path.exists(configure):
            return

        with open(configure) as fp:
            for line in fp:
                line = line.strip()
                if not line or line[0] == "#":
                    continue

                if line[0] == "!":
                    line = line[1:].strip()
                    self._keep_filters.append(re.compile(line))
                elif line[0] == "=":
                    line = line[1:].strip()
                    self._compile_full_match.add(line)
                else:
                    self._compile_filters.append(re.compile(line))

    def _init_conflict_methods(self, vm):
        all_methods = {}
        for m in vm.get_methods():
            method_triple = get_method_triple(m, return_type=False)
            if method_triple in all_methods:
                self.conflict_methods.add(m)
                self.conflict_methods.add(all_methods[method_triple])
            else:
                all_methods[method_triple] = m

    def _init_native_methods(self, vm):
        for m in vm.get_methods():
            cls_name, name, _ = get_method_triple(m)

            access = get_access_method(m.get_access_flags())
            if "native" in access:
                self.native_methods.add((cls_name, name))

    def _add_annotation_method(self, method):
        if not is_synthetic_method(method) and not is_native_method(method):
            self.annotated_methods.add(method)

    def _init_annotation_methods(self, vm):
        for c in vm.get_classes():
            adi_off = c.get_annotations_off()
            if adi_off == 0:
                continue

            adi = vm.CM.get_obj_by_offset(adi_off)
            annotated_class = False
            # ref:https://github.com/androguard/androguard/issues/175
            if adi.get_class_annotations_off() != 0:
                ann_set_item = vm.CM.get_obj_by_offset(adi.get_class_annotations_off())
                for aoffitem in ann_set_item.get_annotation_off_item():
                    annotation_item = vm.CM.get_obj_by_offset(
                        aoffitem.get_annotation_off()
                    )
                    encoded_annotation = annotation_item.get_annotation()
                    type_desc = vm.CM.get_type(encoded_annotation.get_type_idx())
                    if type_desc.endswith("Dex2C;"):
                        annotated_class = True
                        for method in c.get_methods():
                            self._add_annotation_method(method)
                        break

            if not annotated_class:
                for mi in adi.get_method_annotations():
                    method = vm.get_method_by_idx(mi.get_method_idx())
                    ann_set_item = vm.CM.get_obj_by_offset(mi.get_annotations_off())

                    for aoffitem in ann_set_item.get_annotation_off_item():
                        annotation_item = vm.CM.get_obj_by_offset(
                            aoffitem.get_annotation_off()
                        )
                        encoded_annotation = annotation_item.get_annotation()
                        type_desc = vm.CM.get_type(encoded_annotation.get_type_idx())
                        if type_desc.endswith("Dex2C;"):
                            self._add_annotation_method(method)

    def should_compile(self, method):
        # don't compile functions that have same parameter but differ return type
        if method in self.conflict_methods:
            return False

        # synthetic method
        if is_synthetic_method(method) and SKIP_SYNTHETIC_METHODS:
            return False

        # native method
        if is_native_method(method):
            return False

        method_triple = get_method_triple(method)
        cls_name, name, _ = method_triple

        # Skip static constructor
        if name == "<clinit>":
            return False

        # Android VM may find the wrong method using short jni name
        # don't compile function if there is a same named native method
        if (cls_name, name) in self.native_methods:
            return False

        full_name = "".join(method_triple)
        for rule in self._keep_filters:
            if rule.search(full_name):
                return False

        if full_name in self._compile_full_match:
            return True

        if method in self.annotated_methods:
            return True

        for rule in self._compile_filters:
            if rule.search(full_name):
                return True

        return False


def copy_compiled_libs(project_dir, decompiled_dir):
    compiled_libs_dir = path.join(project_dir, "libs")
    decompiled_libs_dir = path.join(decompiled_dir, "lib")
    if not path.exists(compiled_libs_dir):
        return
    if not path.exists(decompiled_libs_dir):
        copytree(compiled_libs_dir, decompiled_libs_dir)
        return

    for abi in os.listdir(decompiled_libs_dir):
        dst = path.join(decompiled_libs_dir, abi)
        src = path.join(compiled_libs_dir, abi)
        if not path.exists(src) and abi == "armeabi":
            src = path.join(compiled_libs_dir, "armeabi-v7a")
            Logger.warning("Use armeabi-v7a for armeabi")

        if not path.exists(src):
            if IGNORE_APP_LIB_ABIS:
                continue
            else:
                raise Exception("ABI %s is not supported!" % abi)
        # n
        android_mk_filename = "project/jni/Android.mk"
        local_module_value = None
        with open(android_mk_filename, "r") as android_mk_file:
            for line in android_mk_file:
                if line.startswith("LOCAL_MODULE"):
                    _, local_module_value = line.split(":=", 1)
                    local_module_value = local_module_value.strip()
                    break

        libnc = path.join(src, "lib" + local_module_value + ".so")
        copy(libnc, dst)


def native_class_methods(smali_path, compiled_methods):
    def next_line():
        return fp.readline()

    def handle_annotanion():
        while True:
            line = next_line()
            if not line:
                break
            s = line.strip()
            code_lines.append(line)
            if s == ".end annotation":
                break
            else:
                continue

    def handle_method_body():
        while True:
            line = next_line()
            if not line:
                break
            s = line.strip()
            if s == ".end method":
                break
            elif s.startswith(".annotation runtime") and s.find("Dex2C") < 0:
                code_lines.append(line)
                handle_annotanion()
            else:
                continue

    code_lines = []
    class_name = ""
    with open(smali_path, "r") as fp:
        while True:
            line = next_line()
            if not line:
                break
            code_lines.append(line)
            line = line.strip()
            if line.startswith(".class"):
                class_name = line.split(" ")[-1]
            elif line.startswith(".method"):
                current_method = line.split(" ")[-1]
                param = current_method.find("(")
                name, proto = current_method[:param], current_method[param:]
                if (class_name, name, proto) in compiled_methods:
                    if line.find(" native ") < 0:
                        code_lines[-1] = code_lines[-1].replace(
                            current_method, "native " + current_method
                        )
                    handle_method_body()
                    code_lines.append(".end method\n")

    with open(smali_path, "w") as fp:
        fp.writelines(code_lines)


def native_compiled_dexes(decompiled_dir, compiled_methods):
    # smali smali_classes2 smali_classes3 ...
    classes_output = list(
        filter(lambda x: x.find("smali") >= 0, os.listdir(decompiled_dir))
    )
    todo = []
    for classes in classes_output:
        for method_triple in compiled_methods.keys():
            cls_name, name, proto = method_triple
            cls_name = cls_name[1:-1]  # strip L;
            smali_path = path.join(decompiled_dir, classes, cls_name) + ".smali"
            if path.exists(smali_path):
                todo.append(smali_path)

    for smali_path in todo:
        native_class_methods(smali_path, compiled_methods)


def write_compiled_methods(project_dir, compiled_methods):
    source_dir = path.join(project_dir, "jni", "nc")
    if not path.exists(source_dir):
        os.makedirs(source_dir)

    for method_triple, code in compiled_methods.items():
        full_name = JniLongName(*method_triple)
        filepath = path.join(source_dir, full_name) + ".cpp"
        if path.exists(filepath):
            Logger.warning("Overwrite file %s %s" % (filepath, method_triple))

        try:
            with open(filepath, "w") as fp:
                fp.write('#include "Dex2C.h"\n' + code)
        except Exception as e:
            print(f"{str(e)}\n")

    with open(path.join(source_dir, "compiled_methods.txt"), "w") as fp:
        fp.write("\n".join(list(map("".join, compiled_methods.keys()))))


def archive_compiled_code(project_dir):
    outfile = make_temp_file("-dcc")
    outfile = make_archive(outfile, "zip", project_dir)
    return outfile


def compile_dex(apkfile, filtercfg, obfus):
    dex_files = auto_vm(apkfile)
    dex_analysis = analysis.Analysis()

    X_compiled_method_code = {}
    X_errors = []

    for dex in dex_files:
        dex_analysis.add(dex)

    for dex in dex_files:
        method_filter = MethodFilter(filtercfg, dex)

        compiler = Dex2C(dex, dex_analysis, obfus)

        compiled_method_code = {}
        errors = []

        for m in dex.get_methods():
            method_triple = get_method_triple(m)

            jni_longname = JniLongName(*method_triple)
            full_name = "".join(method_triple)

            if len(jni_longname) > 220:
                Logger.debug("Name to long %s(> 220) %s" % (jni_longname, full_name))
                continue

            if method_filter.should_compile(m):
                Logger.debug("compiling %s" % (full_name))
                try:
                    code = compiler.get_source_method(m)
                except Exception as e:
                    Logger.warning(
                        "compile method failed:%s (%s)" % (full_name, str(e)),
                        exc_info=True,
                    )
                    errors.append("%s:%s" % (full_name, str(e)))
                    X_errors.extend(errors)
                    continue

                if code:
                    compiled_method_code[method_triple] = code
                    X_compiled_method_code.update(compiled_method_code)

    return X_compiled_method_code, X_errors


def is_apk(name):
    return name.endswith(".apk")


# n
def get_heap_size():
    return


# n
def get_application_name_from_manifest(apk_file):
    a = apk.APK(apk_file)
    manifest_data = a.get_android_manifest_xml()
    application_element = manifest_data.find("application")
    application_name = application_element.get(
        "{http://schemas.android.com/apk/res/android}name", ""
    )
    return application_name


# n
def get_smali_folders(decompiled_dir):
    folders = os.listdir(decompiled_dir)
    folders = [
        folder
        for folder in folders
        if path.isdir(path.join(decompiled_dir, folder)) and folder.startswith("smali")
    ]
    return folders


# n
def get_application_class_file(decompiled_dir, smali_folders, application_name):
    if not application_name == "":
        fileName = application_name.replace(".", os.sep) + ".smali"

        for smali_folder in smali_folders:
            filePath = path.join(decompiled_dir, smali_folder, fileName)

            if path.exists(filePath):
                return filePath

    return ""


# n
def backup_jni_project_folder():
    Logger.info("Backing up jni folder")

    src_path = path.join("project", "jni")
    dest_path = make_temp_dir("jni-")

    copytree(src_path, dest_path, dirs_exist_ok=True)
    return dest_path


# n
def restore_jni_project_folder(src_path):
    Logger.info("Restoring jni folder")

    dest_path = path.join("project", "jni")

    if path.exists(dest_path) and path.isdir(dest_path):
        rmtree(dest_path)

    copytree(src_path, dest_path)


# n
def adjust_application_mk(apkfile):
    Logger.info("Adjusting Application.mk file using available abis from apk")

    supported_abis = {"armeabi-v7a", "arm64-v8a", "x86_64", "x86"}
    depreacated_abis = {"armeabi"}
    available_abis = set()

    if is_apk(apkfile):
        zip_file = zipfile.ZipFile(io.BytesIO(bytearray(read(apkfile))), mode="r")

        for file_name in zip_file.namelist():
            if file_name.startswith("lib/"):
                abi_name = file_name.split("/")[1].strip()

                if len(file_name.split("/")) <= 2:
                    continue

                if abi_name in supported_abis:
                    available_abis.add(abi_name)
                elif abi_name in depreacated_abis:
                    Logger.warning(
                        "ABI 'armeabi' is depreacated, using 'armeabi-v7a' instead"
                    )
                    available_abis.add("armeabi-v7a")
                else:
                    raise Exception(
                        f"ABI '{abi_name}' is unsupported, please remove it from apk or use flag --force-keep-libs and try again"
                    )

        if len(available_abis) == 0:
            Logger.info(
                "No lib abis found in apk, using the ones defined in Application.mk file"
            )
            return

        application_mk_path = "project/jni/Application.mk"
        temp_application_mk_path = make_temp_file("-application.mk")

        with open(application_mk_path, "r") as application_mk_file:
            with open(temp_application_mk_path, "w") as temp_application_mk_file:
                for line in application_mk_file:
                    if line.startswith("APP_ABI"):
                        line = "APP_ABI := " + " ".join(available_abis) + "\n"
                    temp_application_mk_file.write(line)

        os.remove(application_mk_path)
        copy(temp_application_mk_path, application_mk_path)
    else:
        raise Exception(f"{apkfile} is not an apk file")


# n
def dcc_main(
    apkfile,
    obfus,
    filtercfg,
    custom_loader,
    outapk,
    do_compile=True,
    project_dir=None,
    source_archive="project-source.zip",
):
    if not path.exists(apkfile):
        Logger.error("Input apk file %s does not exist", apkfile)
        return

    if not outapk:
        Logger.error("\033[31mOutput file name required\n\033[0m")
        return

    if custom_loader.rfind(".") == -1:
        Logger.error(
            "\n[ERROR] Custom Loader must have at least one package, such as \033[31mDemo.%s\033[0m\n",
            custom_loader,
        )
        return

    # Modify the dex2c file to use the custom loader path for integrity check
    with open("project/jni/nc/Dex2C.cpp", "r") as file:
        dex2c_file_data = file.read()

    dex2c_file_data = dex2c_file_data.replace(
        'env->FindClass("amimo/dcc/DccApplication");',
        'env->FindClass("' + custom_loader.replace(".", "/") + '");',
    )
    dex2c_file_data = dex2c_file_data.replace(
        "Java_amimo_dcc_DccApplication", "Java_" + custom_loader.replace(".", "_")
    )

    with open("project/jni/nc/Dex2C.cpp", "w") as file:
        file.write(dex2c_file_data)

    if not IGNORE_APP_LIB_ABIS:
        adjust_application_mk(apkfile)

    # Convert dex to cpp
    compiled_methods, errors = compile_dex(apkfile, filtercfg, obfus)

    if errors:
        Logger.warning("================================")
        Logger.warning("\n".join(errors))
        Logger.warning("================================")

    if len(compiled_methods) == 0:
        Logger.info("No methods compiled! Check your filter file.")
        return

    if project_dir:
        if not path.exists(project_dir):
            copytree("project", project_dir)
        write_compiled_methods(project_dir, compiled_methods)
    else:
        project_dir = make_temp_dir("dcc-project-")
        rmtree(project_dir)
        copytree("project", project_dir)
        write_compiled_methods(project_dir, compiled_methods)

        if not do_compile:
            src_zip = archive_compiled_code(project_dir)
            move(src_zip, source_archive)

    if do_compile:
        build_project(project_dir)

    if is_apk(apkfile) and outapk:
        decompiled_dir = ApkTool.decompile(apkfile)
        native_compiled_dexes(decompiled_dir, compiled_methods)
        copy_compiled_libs(project_dir, decompiled_dir)

        # n
        smali_folders = get_smali_folders(decompiled_dir)
        android_mk_file_path = "project/jni/Android.mk"
        loader_file_path = "loader/DccApplication.smali"
        temp_loader = make_temp_file("-Loader.smali")

        local_module_value = None
        with open(android_mk_file_path, "r") as android_mk_file:
            for line in android_mk_file:
                if line.startswith("LOCAL_MODULE"):
                    _, local_module_value = line.split(":=", 1)
                    local_module_value = local_module_value.strip()
                    break

        if local_module_value:
            pattern = r'const-string v0, "[\w\W]+"'
            replacement = 'const-string v0, "' + local_module_value + '"'
        else:
            raise Exception("Invalid LOCAL_MODULE defined in project/jni/Android.mk")

        with open(loader_file_path, "r") as file:
            filedata = file.read()

        filedata = re.sub(pattern, replacement, filedata)
        filedata = filedata.replace(
            "Lamimo/dcc/DccApplication;", "L" + custom_loader.replace(".", "/") + ";"
        )

        with open(temp_loader, "w") as file:
            file.write(filedata)

        apk_file_path = apkfile
        application_class_name = get_application_name_from_manifest(apk_file_path)
        file_path = get_application_class_file(
            decompiled_dir, smali_folders, application_class_name
        )

        if application_class_name == "" or file_path == "":
            try:
                Logger.info(
                    "\nApplication class not found in the AndroidManifest.xml or doesn't exist in dex, adding \033[32m"
                    + custom_loader
                    + "\033[0m\n"
                )

                check_call(
                    [
                        "java",
                        "-jar",
                        MANIFEST_EDITOR,
                        path.join(decompiled_dir, "AndroidManifest.xml"),
                        custom_loader,
                    ],
                    stderr=STDOUT,
                )
            except Exception as e:
                Logger.error(f"Error: {e.returncode} - {e.output}", exec_info=True)
        else:
            Logger.info(
                "\nApplication class from AndroidManifest.xml, \033[32m"
                + application_class_name
                + "\033[0m\n"
            )

            check_call(
                [
                    "java",
                    "-jar",
                    MANIFEST_EDITOR,
                    path.join(decompiled_dir, "AndroidManifest.xml"),
                    application_class_name,
                ],
                stderr=STDOUT,
            )

            line_to_insert = (
                "    invoke-static {}, L"
                + custom_loader.replace(".", "/")
                + ";->initDcc()V\n"
            )

            code_block_to_append = f"""
                .method static final constructor <clinit>()V
                    .registers 0

                {line_to_insert}

                    return-void
                .end method
                """

            with open(file_path, "r") as file:
                content = file.readlines()

            index = next(
                (i for i, line in enumerate(content) if "<clinit>" in line), None
            )

            if index is not None:
                locals_index = next(
                    (
                        i
                        for i, line in enumerate(content[index:])
                        if ".locals" in line or ".registers" in line
                    ),
                    None,
                )
                if locals_index is not None:
                    content.insert(index + locals_index + 1, line_to_insert)
                else:
                    Logger.error("Couldn't read <clinit> method in Application class")
            else:
                content.append(code_block_to_append)

            with open(file_path, "w") as file:
                file.writelines(content)

        if custom_loader.rfind(".") > -1:
            loaderDir = path.join(
                decompiled_dir,
                smali_folders[-1],
                custom_loader[0 : custom_loader.rfind(".")].replace(".", os.sep),
            )
            try:
                rmtree(loaderDir)
            except OSError as e:
                run(["rd", "/s", "/q", loaderDir], shell=True)
            os.makedirs(loaderDir)

        copy(
            temp_loader,
            path.join(
                decompiled_dir,
                smali_folders[-1],
                custom_loader.replace(".", os.sep) + ".smali",
            ),
        )
        unsigned_apk = ApkTool.compile(decompiled_dir)
        sign(unsigned_apk, outapk)


sys.setrecursionlimit(5000)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-a", "--input", nargs="?", help="Input apk file path")
    parser.add_argument("-o", "--out", nargs="?", help="Output apk file path")
    parser.add_argument("-p", "--obfuscate", action="store_true", default=False,
        help="Obfuscate string constants.",
    )
    parser.add_argument(
        "--filter", default="filter.txt", help="Method filters configuration file."
    )
    parser.add_argument(
        "--custom-loader",
        default="amimo.dcc.DccApplication",
        help="Loader class, default: amimo.dcc.DccApplication",
    )
    parser.add_argument(
        "--skip-synthetic",
        action="store_true",
        default=False,
        help="Skip synthetic methods in all classes.",
    )
    parser.add_argument(
        "--no-build",
        action="store_true",
        default=False,
        help="Do not build the compiled code",
    )
    parser.add_argument(
        "--force-keep-libs",
        action="store_true",
        default=False,
        help="Forcefully keep the lib abis defined in Application.mk, regardless of the abis already available in the apk",
    )
    parser.add_argument("--source-dir", help="The compiled cpp code output directory.")
    parser.add_argument(
        "--project-archive",
        default="project-source.zip",
        help="Converted cpp code, compressed as zip output file.",
    )

    args = vars(parser.parse_args())
    input_apk = args["input"]
    out_apk = args["out"]
    obfus = args["obfuscate"]
    filtercfg = args["filter"]
    custom_loader = args["custom_loader"]
    SKIP_SYNTHETIC_METHODS = args["skip_synthetic"]
    IGNORE_APP_LIB_ABIS = args["force_keep_libs"]
    do_compile = not args["no_build"]
    source_archive = args["project_archive"]

    if args["source_dir"]:
        project_dir = args["source_dir"]
    else:
        project_dir = None

    dcc_cfg = {}
    with open("dcc.cfg") as fp:
        dcc_cfg = json.load(fp)

    if "ndk_dir" in dcc_cfg and path.exists(dcc_cfg["ndk_dir"]):
        ndk_dir = dcc_cfg["ndk_dir"]
        if is_windows():
            NDKBUILD = path.join(ndk_dir, "ndk-build.cmd")
        else:
            NDKBUILD = path.join(ndk_dir, "ndk-build")

        if not path.exists(NDKBUILD):
            raise Exception("Invalid ndk_dir path, file not found at " + NDKBUILD)

    if "apktool" in dcc_cfg and path.exists(dcc_cfg["apktool"]):
        APKTOOL = dcc_cfg["apktool"]

    show_logging(level=INFO)

    # n
    # Must be invoked first before invoking any other mehtod
    create_tmp_directory()

    # Bakcing up jni folder because modifications will be made in runtime
    backup_jni_folder_path = backup_jni_project_folder()

    try:
        dcc_main(
            input_apk,
            obfus,
            filtercfg,
            custom_loader,
            out_apk,
            do_compile,
            project_dir,
            source_archive,
        )
    except Exception as e:
        Logger.error("Compile %s failed!" % input_apk, exc_info=True)
        print(f"{str(e)}")
    finally:
        # n
        restore_jni_project_folder(backup_jni_folder_path)
        clean_tmp_directory()
