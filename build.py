
# import sys
# sys.path.insert(0, "C:\dev\Python311\Lib\site-packages")

# import yaml
# from scfbuild.scfbuild.builder import Builder

# f = open("scfbuild.yml")
# conf = yaml.safe_load(f)
# f.close()

# builder = Builder(conf)
# builder.run()
from __future__ import annotations
import os
import toml
import subprocess
import typing as t
from preprocess import Preprocess

TConfig: t.TypeAlias = t.Dict[str, t.Union[str, int, t.List[t.Union[str, int]]]]

class Builder:
    def __init__(self, config_file: str) -> None:
        self.proc = Preprocess(config_file)
    
    # return the path of the toml file
    def __make_toml_config(self, srcs: t.List[str], format: t.Optional[str] = None) -> str:
        toml_cfg = {
            "family": self.proc.config["family"],
            "output_file": os.path.join(self.proc.config["dist_directory"], f'{self.proc.config["family"]}.ttf'),
            "version_major": self.proc.config["version_major"],
            "version_minor": self.proc.config["version_minor"],
            "color_format": self.proc.config["color_format"],
            "clipbox_quantization": 32,
            "axis": {
                "wght": {
                    "name": "Weight",
                    "default": 400
                }
            },
            "master": {
                "regular": {
                    "style_name": "Regular",
                    "srcs": srcs,
                    "position":{
                        "wght": 400
                    }
                }
            }
        }
        if (format):
            toml_cfg["output_file"] = os.path.join(self.proc.config["dist_directory"], f'{self.proc.config["family"]}-{format}.ttf')
            toml_cfg["color_format"] = format
        
        toml_cfg["output_file"] = os.path.abspath(toml_cfg["output_file"])
        tomlcfg_directory = self.proc.config["tomlcfg_directory"]
        tomlcfg_file = self.proc.config["tomlcfg_prefix"] + toml_cfg["color_format"] + ".toml"
        path = os.path.abspath(os.path.join(tomlcfg_directory, tomlcfg_file))

        with open(path, "w") as f:
            f.write(toml.dumps(toml_cfg))

        return path
    
    def run(self):
        svgs = self.proc.run()

        configs: t.List[str] = []
        configs.append(self.__make_toml_config(svgs))

        if "additional_color_formats" in self.proc.config:
            for format in self.proc.config["additional_color_formats"]:
                configs.append(self.__make_toml_config(svgs, format))

        for config in configs:
            subprocess.run(f"nanoemoji \"{config}\"")

builder = Builder("config/config_dark.json")
builder.run()

builder = Builder("config/config_light.json")
builder.run()