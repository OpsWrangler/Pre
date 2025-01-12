version = "{{pree_version}}"

import jinja2
# import pickle
import argparse
from os import sep, listdir, path, makedirs, remove, _exit, walk
from shutil import copy2, copytree, rmtree
from glob import glob
from pathlib import Path


def custom_copy(src, dst, symlinks=False, ignore=None):

    def custom_copy2(s, d):
        # if _cmd_line_args.debug:
        #     print(f"Copying from {s} to {d}")
        copy2(s, d)

    if path.exists(src):
        if path.isdir(src):
 
            if not path.exists(dst):
                makedirs(dst)
            for item in listdir(src):
                s = path.join(src, item)
                d = path.join(dst, item)
                if path.isdir(s):
                    custom_copy(s, d, symlinks, ignore)
                else:
                    custom_copy2(s, d)
        else:
            custom_copy2(src, dst)
    else:
        print(f"ERROR: source {src} does not exist")
        _exit(1)


def handleTemplates():

    template_input_dirs = _cmd_line_args.template_input_dirs or [f".pree{sep}templates{sep}"]
    template_output_dir = _cmd_line_args.template_output_dir or "."
    templateLoader = jinja2.FileSystemLoader(searchpath="") #searchpath is empty as all filepaths we feed to Jinja are absolute

    print(f"Template source folder(s): {template_input_dirs}\nTemplate destination folder: {template_output_dir}")

    # Simple dictionary to list 
    _template_vars_as_set = set([(k,v) for k,v in _template_vars.items()])

    if _cmd_line_args.debug:
        print(f"\n_template_vars:\n")

        for x in _template_vars_as_set: 
            print(f"{x[0]} = {x[1]}")

        print(f"\n\n")

    templateEnv = jinja2.Environment(
        loader=templateLoader, 
        trim_blocks=True, 
        lstrip_blocks=True)


    for a_template_source_dir in template_input_dirs:
        a_template_source_dir = path.join(a_template_source_dir, '') #Add a trailing slash if not present
        for a_source_filepath in glob(f'{a_template_source_dir}/**/*', recursive=True, include_hidden=True):
            if(Path.is_file(Path(a_source_filepath))):
                a_source_filepath_for_jinja = Path(a_source_filepath).as_posix()
                a_source_filepath_relative_to_output = str(a_source_filepath).replace(a_template_source_dir,'')
                dest_filename = Path(path.join(Path(template_output_dir), Path(a_source_filepath_relative_to_output)))

                template = templateEnv.get_template(a_source_filepath_for_jinja)
                try:
                    outputFromJinja = template.render(_template_vars_as_set)
                except Exception as e:
                    print(f"Jinja template error, exiting: {e}")
                    _exit()

                if _cmd_line_args.debug:
                    print(f"Processing template: {a_source_filepath}, outputting to {dest_filename}")

                # If the output directory structure does not exist, make it
                try:
                    if sep in str(dest_filename):
                        Path(dest_filename.parent).mkdir(parents=True, exist_ok=True)
                    with open(dest_filename, 'w') as dest_file:
                        dest_file.write(outputFromJinja)
                except Exception as e:
                    print(f"Error outputting processed template {dest_filename}:\n{e}")
                    exit(1)


def handleCmdLineArgs():

    global _cmd_line_args

    parser = argparse.ArgumentParser()

    parser.add_argument("action",
                        help="The action for Pree to take. This is required, and needs to be one of: \"templates\" or \"vault\" ")
    parser.add_argument("action2",
                        help="Second part of action for Pree to take. For \"templates\" there are no second actions. For \"vault\", ...",
                        nargs='?') #nargs='?' means optional parameter in this usage
    parser.add_argument("--debug",
                        help="Enable debug output (Could include output of secret values!)",
                        action="store_true")
    parser.add_argument("--template_vars",
                        help=r"List of variable pairs ('name = value' 'name2 = value 2')",
                        nargs='+')
    parser.add_argument("--template_input_dirs",
                        help=f"Input director(ies) for templates. By default, Pree loads templates from one folder: .{sep}.pree{sep}templates{sep}",
                        nargs='+')
    parser.add_argument("--template_output_dir",
                        help=f"Output directory for assembled templates. By default, Pree outputs processed templates to: .{sep}")
    _cmd_line_args = parser.parse_args()


    if _cmd_line_args.template_vars is not None:
        for pair in _cmd_line_args.template_vars:
            split_pair = pair.split('=')
            try:
                _template_vars[split_pair[0].strip()] = split_pair[1].lstrip()
            except IndexError as e:
                print("ERROR: There is an issue with the template_vars provided") # User issue, potentially due to equal sign


    # if _cmd_line_args.debug:
    #     if _cmd_line_args.template_vars is not None:
    #         print(_template_vars)


# MAIN #
if __name__ == "__main__":
    print(f"Pree v{version or '???'}\n")
    _template_vars = {}
    handleCmdLineArgs()

    if _cmd_line_args.action == "templates":
        handleTemplates()
    elif _cmd_line_args.action == "vault":
        print("Vault functions will be in a future version")
    else:
        print(f"\"{_cmd_line_args.action}\" is not a valid action!")
        _exit(1)

    # Python 3.10 and above
    # match _cmd_line_args.action:
    #     case "templates": 
    #         handleTemplates()
    #     case "vault":
    #         print("Vault functions will be in a future version")
    #     case _:
    #         print(f"\"{_cmd_line_args.action}\" is not a valid action!")
    #         _exit(1)
