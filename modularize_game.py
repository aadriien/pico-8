###############################################################################
##  `modularize_game.py`                                                     ##
##                                                                           ##
##  Creator: Adrien Lynch (GitHub: aadriien)                                 ##
##  Purpose: Separates single .p8 file (PICO-8) into multiple .lua files     ##
##  Notes: Only pulls from code section, and leaves .p8 file untouched       ##
###############################################################################


import os
import re


def find_p8_file() -> str:
    # Find exactly one .p8 file in current directory
    p8_files = [f for f in os.listdir(".") if f.endswith(".p8")]

    if not p8_files:
        raise Exception("No .p8 file found in current directory.")
    elif len(p8_files) > 1:
        raise Exception("Multiple .p8 files found. Please specify one explicitly.")
    else:
        p8_file = p8_files[0]

    print(f"Found .p8 file: {p8_file}")
    return p8_file


def read_and_parse(p8_file: str) -> tuple[str, str, str]:
    # Read entire p8 content
    with open(p8_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Split content at __lua__ (get header & rest)
    parts = content.split("__lua__")
    if len(parts) < 2:
        raise Exception("No __lua__ section found in p8 file")

    header = parts[0]
    rest = parts[1]

    section_headers = [
        "__gfx__",
        "__gff__",
        "__map__",
        "__sfx__",
        "__music__",
        "__label__",
        "__cartdata__"
    ]

    # Find next section headers to isolate Lua code only
    next_section_pos = None
    for header_name in section_headers:
        pos = rest.find(header_name)
        if pos != -1:
            if next_section_pos is None or pos < next_section_pos:
                next_section_pos = pos

    if next_section_pos is not None:
        lua_code = rest[:next_section_pos]
        trailing_sections = rest[next_section_pos:]
    else:
        lua_code = rest
        trailing_sections = ""

    return header, lua_code, trailing_sections


def strip_leading_trailing_blank_lines(text: str) -> str:
    lines = text.splitlines()

    # Remove leading blank lines, then remove trailing blank lines
    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop()

    return "\n".join(lines)


def split_and_write_modules(lua_code: str) -> None:
    # Split Lua code by -->8 tab markers (keep in place via positive lookahead)
    parts = re.split(r"\n(?=-->8\n)", lua_code)
    modules = [p.strip() for p in parts if p.strip()]

    written_lua_files = []
    for i, module in enumerate(modules):
        lines = module.splitlines()

        # Start with default fallback for filename
        filename = f"module_{i+1}.lua" 

        # Look for filename comment -- >>> name.lua <<< anywhere in early lines
        for line in lines[:5]:  
            if line.strip().startswith("-- >>>") and line.strip().endswith("<<<"):
                m = re.match(r"-- >>> (.+?) <<<", line.strip())
                if m:
                    filename = m.group(1).strip()
                    break

        # Reassemble module content
        content = "\n".join(lines).strip()

        # Save to file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        written_lua_files.append(filename)

    print("Wrote .lua module files:")
    for lua in written_lua_files:
        print(f"   - {lua}")



if __name__ == "__main__":
    p8_file = find_p8_file()
    header, lua_code, trailing_sections = read_and_parse(p8_file=p8_file)

    lua_code = strip_leading_trailing_blank_lines(text=lua_code)
    split_and_write_modules(lua_code=lua_code)


