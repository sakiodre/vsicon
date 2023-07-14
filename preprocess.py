
import os
import shutil
import re
import typing as t

import json
import xml.etree.ElementTree as xml

with open("templates/vsicon.css", "r") as f:
    css_template = f.read()

with open("templates/index.html", "r") as f:
    html_template = f.read()

css_icon_fmt = ".vsicon-{}:before {{ content: \"\\{:x}\" }}"

html_icon_fmt = """
        <div class="icon" data-name="{0}" title="{0}">
            <span class="inner">
                <i class="vsicon vsicon-{0}" aria-hidden="true"></i>
            </span>
            <br>
            <span class='label'>{0}</span>
            <span class='description'></span>
        </div>"""

STYLE_REGEX = re.compile(r"\.(?P<class>[-.\w]+)\s*{(?P<content>.+?)}")

xml.register_namespace("", "http://www.w3.org/2000/svg")

# default value
# {
#     "canvas"              : "fill: none; opacity: 0;",
#     "cls-1"               : "opacity:0.75;",
#     "cls-101"             : "fill:url(#radial-gradient);",
#     "cls-103"             : "fill:url(#linear-gradient);"
#     "cls-2"               : "opacity:0.75;",
#     "cls-3"               : "opacity:0.75;",
#     "dark-green"          : "fill: #5fb55f; opacity: 1;",
#     "dark-orange"         : "fill: #f27446; opacity: 1;",
#     "dark-teal"           : "fill: #309d90; opacity: 1;",
#     "dark-yellow"         : "fill: #ffc733; opacity: 1;",
#     "light-blue"          : "fill: #005dba; opacity: 1;",
#     "light-blue-10"       : "fill: #005dba; opacity: 0.1;",
#     "light-darkblue"      : "fill: #313c9e; opacity: 1;",
#     "light-darkblue-10"   : "fill: #313c9e; opacity: 0.1;",
#     "light-darkpurple"    : "fill: #533182; opacity: 1;",
#     "light-darkpurple-10" : "fill: #533182; opacity: 0.1;",
#     "light-defaultgrey"   : "fill: #212121; opacity: 1;",
#     "light-defaultgrey-10": "fill: #212121; opacity: 0.1;",
#     "light-defaultgrey-25": "fill: #212121; opacity: 0.25;",
#     "light-green"         : "fill: #1f801f; opacity: 1;",
#     "light-green-10"      : "fill: #1f801f; opacity: 0.1;",
#     "light-lightblue"     : "fill: #0077a0; opacity: 1;",
#     "light-lightblue-10"  : "fill: #0077a0; opacity: 0.1;",
#     "light-offwhite"      : "fill: #f6f6f6; opacity: 1;",
#     "light-orange"        : "fill: #b73d18; opacity: 1;",
#     "light-orange-10"     : "fill: #b73d18; opacity: 0.1;",
#     "light-purple"        : "fill: #6936aa; opacity: 1;",
#     "light-purple-10"     : "fill: #6936aa; opacity: 0.1;",
#     "light-red"           : "fill: #c50b17; opacity: 1;",
#     "light-red-10"        : "fill: #c50b17; opacity: 0.1;",
#     "light-teal"          : "fill: #006758; opacity: 1;",
#     "light-teal-10"       : "fill: #006758; opacity: 0.1;",
#     "light-shadow"        : "fill: #000000; opacity: 0.1;",
#     "light-yellow"        : "fill: #996f00; opacity: 1;",
#     "light-yellow-10"     : "fill: #996f00; opacity: 0.1;",
#     "light-yellow-25"     : "fill: #996f00; opacity: 0.25;",
#     "white"               : "fill: #ffffff; opacity: 1;",
# }

    
class Preprocess:
    def __init__(self, config_file: str) -> None:
        with open(config_file) as f:
            self.config = json.loads(f.read())
        self.css_icons : t.List[str] = []
        self.div_icons : t.List[str] = []
        self.js_descriptions : t.List[t.Dict[str, str]] = []

    # process svg and convert its colors
    def __process_svg(self, filename: str) -> t.Optional[xml.ElementTree]:        
        filepath = os.path.join(self.config["input_directory"], filename)
        try: svg = xml.parse(filepath)
        except xml.ParseError as err: 
            print(f"Invalid svg file: {filepath}, error: {err.msg}, skipping")
            return None

        theme = self.config["theme"]
        svg_name = filename[:filename.rfind(".")]
        isOverride = (svg_name in theme["overrides"])
        default_style: t.Dict[str, str] = {}
        defs = svg.getroot().find("{http://www.w3.org/2000/svg}defs")
        for style in defs.findall("{http://www.w3.org/2000/svg}style"):
            for match in re.findall(r"\.([-.\w]+)\s*{(.+?)}", style.text):
                default_style[match[0]] = match[1]

        def process_style(el: xml.Element):
            if "class" in el.attrib:
                c = el.attrib["class"]
                del el.attrib["class"]

                if isOverride and c in theme["overrides"][svg_name]:
                    el.attrib["style"] = theme['overrides'][svg_name][c]
                elif c in theme:
                    el.attrib["style"] = theme[c]
                else:
                    el.attrib["style"] = default_style[c]

            for child in el:
                process_style(child)

        process_style(svg.getroot())
        return svg
            
    # add icon to css file and return the css name
    def __process_css(self, filename: str, codepoint: int) -> str:
        css_name = filename[:-4].replace(".", "_") # strip ".svg"
        self.css_icons.append(css_icon_fmt.format(css_name, codepoint))
        return css_name

    # add icon to html file
    def __process_html(self, css_name: str):
        self.div_icons.append(html_icon_fmt.format(css_name))

        description = " ".join(re.findall("[A-Z][^A-Z]*", css_name))
        self.js_descriptions.append("""\t{{
            name: "{}",
            description: "{}"
        }},""".format(css_name, description))
    
    # process svg files and returns a list (file path) of processed svg
    def run(self) -> t.List[str]:
        input_directory = self.config["input_directory"]
        output_directory = self.config["output_directory"]
        dist_directory = self.config["dist_directory"]
        codepoint = int(self.config["codepoint"][2:], 16)
        outputs: t.List[str] = []

        shutil.rmtree(output_directory, True)
        shutil.rmtree(dist_directory, True)
        os.makedirs(output_directory)
        os.makedirs(dist_directory)
        
        for file in os.listdir(input_directory):
            filename = os.fsdecode(file)
            if not filename.endswith(".svg"): continue
            
            svg = self.__process_svg(filename)
            if (svg == None): continue

            css_name = self.__process_css(filename, codepoint)
            self.__process_html(css_name)

            outname = "{:x}.svg".format(codepoint)
            outpath = os.path.join(output_directory, outname)
            outputs.append(os.path.abspath(outpath))
            svg.write(outpath)

            codepoint += 1
        
        with open(os.path.join(dist_directory, "vsicon.css"), "w") as f:
            css_content = (css_template + "\n".join(self.css_icons))\
                .replace("{FONT_FAMILY}", self.config["family"])\
                .replace("{FONT_FILE}", self.config["family"] + ".ttf")
            f.write(css_content)
                       
        with open(os.path.join(dist_directory, "index.html"), "w") as f:
            html_content = html_template\
                .replace("{HTML_ICONS_DIV}", "\n".join(self.div_icons))\
                .replace("{JS_ICON_DESCRIPTION}", "\n".join(self.js_descriptions))
            f.write(html_content)
        
        return outputs

if __name__ == "__main__":
    proc = Preprocess("config/config_dark.json")
    proc.run()