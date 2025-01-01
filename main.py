import jinja2
import pickle
import argparse
from os import sep, listdir, path, makedirs, remove, _exit
from shutil import copy2, copytree, rmtree
from glob import glob
from pathlib import Path



def custom_copy(src, dst, symlinks=False, ignore=None):

    def custom_copy2(s, d):
        if _cmd_line_args.debug:
            print(f"Copying from {s} to {d}")
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
    
    # Simple dictionary to list 
    _template_vars_as_set = set([(k,v) for k,v in _template_vars.items()])

    if _cmd_line_args.debug:
        print(f"\n_template_vars:\n")

        for x in _template_vars_as_set: 
            print(f"{x[0]} = {x[1]}")

        print(f"\n\n")

    templateLoader = jinja2.FileSystemLoader(searchpath="./")

    templateEnv = jinja2.Environment(
        loader=templateLoader, 
        trim_blocks=True, 
        lstrip_blocks=True
        )

    current_dir = path.realpath(__file__)
    template_input_dir = _cmd_line_args.template_input_dir or f".pre{sep}templates{sep}"
    template_demp_dir_relative = f"{sep}.pre{sep}.pre_temp{sep}"
    template_temp_dir_full = f"{path.dirname(current_dir)}{template_demp_dir_relative}"
    template_output_dir = "."

    if _cmd_line_args.debug:
        print(f"Copying temporary files from: {template_input_dir}, outputting to {template_temp_dir_full}")

    custom_copy(template_input_dir, template_temp_dir_full)

    for filepath in glob(f'{template_temp_dir_full}/**/*', recursive=True):
        dest_filename = filepath.replace(".pre.", '.')
        dest_filename = Path(str(dest_filename).replace(template_temp_dir_full, f"{template_output_dir}{sep}"))
        if ".pre." in filepath:
            filepath_for_jinja = Path(str(filepath).replace(template_temp_dir_full, template_demp_dir_relative)).as_posix()
            print(filepath_for_jinja)
            template = templateEnv.get_template(filepath_for_jinja)
            outputFromJinja = template.render(_template_vars_as_set)

            if _cmd_line_args.debug:
                print(f"Processing template: {filepath}, outputting to {filepath_for_jinja}")

            # If the output file is not in the same path as this script, make the directory tree needed
            if f"{sep}" in str(dest_filename):
                Path(dest_filename.parent).mkdir(parents=True, exist_ok=True)
            with open(dest_filename, 'w') as dest_file:
                dest_file.write(outputFromJinja)
        else:
            custom_copy(filepath, dest_filename)

    # Clean up, remove temp dir
    rmtree(template_temp_dir_full)



def handleCmdLineArgs():

    global _cmd_line_args

    parser = argparse.ArgumentParser()
    parser.add_argument("--template_destination")
    parser.add_argument("--template_vars",
                        help=r"List of variable pairs ('name = value' 'name2 = value 2')",
                        nargs='+')
    parser.add_argument("--debug", 
                        help="Enable debug output (Could include output of secret values!)",
                        action="store_true")
    parser.add_argument("--template_input_dir", 
                        help="Input directory for templates"
                        )
    _cmd_line_args = parser.parse_args()


    if _cmd_line_args.template_vars is not None:
        for pair in _cmd_line_args.template_vars:
            split_pair = pair.split('=')
            try:
                _template_vars[split_pair[0].strip()] = split_pair[1].lstrip()
            except IndexError as e:
                print("ERROR: There is an issue with the template_vars provided, maybe with an equal sign?")


    # if _cmd_line_args.debug:
    #     if _cmd_line_args.template_vars is not None:
    #         print(_template_vars)



# MAIN #
if __name__ == "__main__":
    _template_vars = {}
    handleCmdLineArgs()
    handleTemplates()










# with open("dotpre.pkl", 'ab') as pickle_file:
#     pickle.dump(_template_vars, pickle_file) 

# with open("dotpre.pkl", 'rb') as pickle_file:
#     _data = pickle.load(pickle_file)

# print(_data)
