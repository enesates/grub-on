#-*- coding:utf-8 -*-

import re

DEFAULT_GRUB_PATH="/etc/default/grub"
GRUB_CFG_PATH="/boot/grub/grub.cfg"

class DefaultGrubConfig(object):
    def __init__(self):
        self.path=DEFAULT_GRUB_PATH
    def read(self):
        self.contents=open(self.path).read()
        self.settings=dict(re.findall("^(GRUB_.*?)=(.*)", self.contents, re.MULTILINE))
    def write(self):
        for option_name, option_value in self.settings.items():
            if option_value=="#":
                self.contents, count=re.subn("#?{0}=".format(option_name), "#{0}=".format(option_name), self.contents)
                if not count:
                    self.contents+="\n#{0}={1}".format(option_name, option_value)
                continue
            self.contents, count=re.subn("#?{0}=.*".format(option_name), "{0}={1}".format(option_name, option_value), self.contents)
            if not count:
                    self.contents+="\n{0}={1}".format(option_name, option_value)
                    
        open(self.path, "w").write(self.contents)

class GrubCfgConfig(object):
    def __init__(self):
        self.path=GRUB_CFG_PATH
    def read(self):
        self.contents=open(self.path).read()
        menuentries=re.findall("menuentry .*?{.*?}", self.contents,  re.DOTALL)
        self.entries=[]
        for entry in menuentries:
            entryName=re.findall("menuentry ['\"](.*?)['\"]", entry)[0]
            entryContents=entry
            self.entries.append({"name":entryName, "content":entryContents})
    def write(self):
        self.contents=open(self.path).read()
        self.contents=re.sub(re.compile("menuentry.*?{.*?}", re.DOTALL), "",  self.contents)
        self.contents+="\n"
        for entry in self.entries:
            self.contents+=(entry["content"])
            self.contents+=("\n")
        open(self.path, "w").write(self.contents)
