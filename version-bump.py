#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import hashlib
import datetime
import optparse

def get_and_save_user_info():
    name = "PACKAGER_NAME"
    email = "PACKAGER_EMAIL"

    conf_file = os.path.expanduser("~/.packagerinfo")
    if os.path.exists(conf_file):
        # Read from it
        name, email = open(conf_file, "r").read().strip().split(",")

    else:
        print("Please enter your full name as seen in pspec files")
        name = input("> ")
        print("Please enter your e-mail as seen in pspec files")
        email = input("> ")
        print("Saving packager info into {}".format(conf_file))

        open(conf_file, "w").write("{},{}".format(name, email))

    return name, email

def bump_spec(spec, ver, packager_name, packager_email,
          critical, security, bumptype, comment):
    lines = open(spec).readlines()
    name_line = -1
    archive_line = -1
    dep_line = -1
    update_line = -1
    dep_lines = []

    for n, line in enumerate(lines):
        if "<Source>" in line:
            name_line = n + 1

        elif "<Archive" in line:
            archive_line = n

        elif "<Dependency" in line:
            dep_lines.append(n)

        elif "<History>" in line:
            update_line = n + 1

    m = re.match(r" *<Name>(.+)</Name>", lines[name_line])
    name = m.groups()[0]
    lang = name.split("-", 1)[-1]

    m = re.match(r' *<Archive type=".+" sha1sum="(.+)">(.+)</Archive>', lines[archive_line])
    if m is None:
        m = re.match(r' *<Archive sha1sum="(.+)" type=".+">(.+)</Archive>', lines[archive_line])

    sha1sum, uri = m.groups()
    archive_name = os.path.basename(uri)

    m = re.match(r' *<Update release="(.*?)"', lines[update_line])
    release = int(m.groups()[0])

    m = re.match(r" *<Version>(.+)</Version>", lines[update_line + 2])
    old_version = m.groups()[0]

    if old_version == version:
        print("{} is already at version {}".format(name, version))
        return

    lines[archive_line] = lines[archive_line].replace(old_version, version)
    new_archive_name = archive_name.replace(old_version, version)

    if not os.path.exists("/var/cache/inary/archives/{}".format(new_archive_name)):
        print("Archive not found downloading via inary...")

        tmp_spec_file = spec_file.replace("pspec", "tmp_pspec")
        open(tmp_spec_file, "w").writelines(lines)
        os.system("sudo inary build {} --fetch".format(tmp_spec_file))
        os.unlink(tmp_spec_file)
    else:
        print("Using existing archive from cache...")

    new_sha1sum = hashlib.sha1(open("/var/cache/inary/archives/{}".format(new_archive_name), 'rb').read()).hexdigest()
    lines[archive_line] = lines[archive_line].replace(sha1sum, new_sha1sum)


    for dep_line in dep_lines:
        m = re.match(r' *<Dependency versionFrom="(.*)">.*', lines[dep_line])
        if m:
            dep_version = m.groups()[0]
            if dep_version == old_version:
                lines[dep_line] = lines[dep_line].replace(old_version, version)

    if not comment=="":
        pass
    else:
        comment="Version bump to {}".format(version)

    if bumptype:
        updatetype = " type=\"{}\"".format(bumptype)
    else:
        updatetype=""

    crit_or_sec = ""

    if security:
        for pkg in security:
            crit_or_sec += "\n            <Type package=\"{}\">security</Type>".format(pkg)
    elif critical:
        for pkg in critical:
            crit_or_sec += "\n            <Type package=\"{}\">critical</Type>".format(pkg)


    update_lines = ['        <Update release="{}">{}\n'.format(release + 1, bumptype),
                    '            <Date>{}</Date>\n'.format(datetime.date.isoformat(datetime.date.today())),
                    '            <Version>{}</Version>\n'.format(version),
                    '            <Comment>{}</Comment>{}\n'.format(comment, crit_or_sec),
                    '            <Name>{}</Name>\n'.format(packager_name),
                    '            <Email>{}</Email>\n'.format(packager_email),
                    '        </Update>\n']


    lines[update_line:update_line] = update_lines

    open(spec_file, "w").writelines(lines)
    print("{} updated".format(spec_file))
    print()
    print("Old SHA1SUM: {}".format(sha1sum))
    print("New SHA1SUM: {}".format(new_sha1sum))
    print("Old Archive: {}".format(archive_name))
    print("New Archive: {}".format(new_archive_name))
    print("Comment: {}".format(comment))
    print("Version: {}".format(version))
    print("Date:    {}".format(datetime.date.isoformat(datetime.date.today())))


if __name__ == "__main__":
    usage = "Usage: %prog <Release comment> [Bumped version] [options] [Pspec list]"
    parser = optparse.OptionParser(usage)
    parser.add_option("--comment",
                      dest="comment",
                      default="",
                      help="Update specfile to x version from old one.")
    parser.add_option("--to-version",
                      dest="to_version",
                      default=None,
                      help="Update specfile to x version from old one.")
    parser.add_option("-n", "--no-increment",
                      dest="no_increment",
                      default=False,
                      help="Do not increment release, just update sha1sums.",
                      action="store_true")
    parser.add_option("-c", "--critical",
                      dest="critical",
                      default=False,
                      help="Mark update as critical and add Type=critical for those packages",
                      action="store_true")
    parser.add_option("-s", "--security",
                      dest="security",
                      default=False,
                      help="Mark update as security and add Type=security for those packages",
                      action="store_true")
    parser.add_option("--all-critical",
                      dest="bumptype",
                      action="store_const",
                      const="critical",
                      help="Mark the update critical for all packages [old way]")
    parser.add_option("--all-security",
                      dest="bumptype",
                      action="store_const",
                      const="security",
                      help="Mark the update security for all packages [old way]")

    (options,args) = parser.parse_args()


    if len(sys.argv) < 2:
        print(usage)
        sys.exit(1)

    files=[]
    for i in sys.argv:
        if i.endswith("pspec.xml"):
            files.append(i)
    if not files:
        print(usage)
        sys.exit(1)

    version = options.to_version
    comment = options.comment
    packager_name, packager_email = get_and_save_user_info()

    for spec_file in files:
        bump_spec(spec_file, version, packager_name, packager_email,
                                      options.critical, options.security,
                                      options.bumptype, comment)
