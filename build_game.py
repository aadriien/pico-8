###############################################################################
##  `build_game.py`                                                          ##
##                                                                           ##
##  Creator: Adrien Lynch (GitHub: aadriien)                                 ##
##  Purpose: Assembles multiple .lua files into single .p8 file (PICO-8)     ##
##  Notes: Preserves graphics and map data by only editing code section      ##
###############################################################################


import os


def find_files() -> tuple[str, list[str]]:
    # Automatically find all .lua files in current folder, sorted alphabetically
    lua_files = sorted([
        f for f in os.listdir(".") 
        if f.endswith(".lua")
    ])

    # Automatically find the .p8 file (assuming there's only one)
    p8_files = [f for f in os.listdir(".") if f.endswith(".p8")]

    if not p8_files:
        raise Exception("No .p8 file found in current directory.")
    elif len(p8_files) > 1:
        raise Exception("Multiple .p8 files found. Please specify one explicitly.")
    else:
        p8_file = p8_files[0]

    print(f"Found .p8 file: {p8_file}")
    print("Found .lua files:")
    for lua in lua_files:
        print(f"   - {lua}")

    return p8_file, lua_files


def read_and_parse(p8_file: str) -> tuple[str, str]:
    # Read entire contents of p8 file (ensures preservation of sprites, map, etc)
    with open(p8_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Split content at __lua__ (updating only code on reassemble)
    parts = content.split("__lua__")

    if len(parts) < 2:
        raise Exception("No __lua__ section found in p8 file")

    header = parts[0] # content before __lua__
    rest = parts[1] # content after __lua__

    # Find where next section after __lua__ starts (gfx, gff, map, etc)
    section_headers = [
        "__gfx__",
        "__gff__",
        "__map__",
        "__sfx__",
        "__music__",
        "__label__",
        "__cartdata__"
    ]

    next_section_pos = None
    for header_name in section_headers:
        pos = rest.find(header_name)
        if pos != -1:
            if next_section_pos is None or pos < next_section_pos:
                next_section_pos = pos

    if next_section_pos is not None:
        trailing_sections = rest[next_section_pos:]
    else:
        trailing_sections = ""

    return header, trailing_sections


def strip_leading_trailing_blank_lines(text: str) -> str:
    lines = text.splitlines()

    # Remove leading blank lines, then remove trailing blank lines
    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop()

    return "\n".join(lines)


def ensure_tab_marker(content: str) -> str:
    # Ensure PICO-8 tab marker (-->8) at top of file for native editor
    lines = content.splitlines()
    lines = [line for line in lines if line.strip() != "-->8"]
    lines.insert(0, "-->8")

    return "\n".join(lines)


def write_assembled_code(p8_file: str, include_files: list[str], 
                         header: str, trailing_sections: str
                        ) -> None:
    # Build new lua code from separate / modular files 
    lua_code = ""
    for file_name in include_files:
        with open(file_name, "r", encoding="utf-8") as f:
            # Read contents, stripping trailing spaces & newlines 
            content = f.read()
            content = strip_leading_trailing_blank_lines(content)
            
            # Add filename comment, then ensure PICO-8 tab marker at top (-->8) 
            content = f"-- >>> {file_name} <<<\n{content}"
            content = ensure_tab_marker(content)

            lua_code += content + "\n\n\n"

    # Reconstruct full p8 file content (+ strip whitespace)
    new_content = header + "__lua__\n" + lua_code.lstrip() + trailing_sections

    # Overwrite original p8 file (without editing any graphics parts)
    with open(p8_file, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Updated {p8_file} with new Lua code, preserving graphics and map data.")



if __name__ == "__main__":
    p8_file, lua_files = find_files()
    header, trailing_sections = read_and_parse(p8_file=p8_file)

    write_assembled_code(
        p8_file=p8_file, 
        include_files=lua_files, 
        header=header, 
        trailing_sections=trailing_sections
    )


