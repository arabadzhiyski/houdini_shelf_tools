# Sets the 'hatchingTex#' multiparm string fields of PxrStylizedHatching display filter
# from a sequence of up to 8 *.tex files in Houdini. If the sequence contains less than
# 8 textures, the beginning and the end will be clamped (repeated).
# It's yours to use for free. Happy hatching!

import hou
import os

tool_title= "Set Hatching Textures"
filter_type = "pxrstylizedhatching::3.0"
selected = hou.selectedNodes()
target = None

try:
    if not selected:
        raise Exception("Nothing is selected.")
    else:
        target = selected[0]
        
    if target.type() == hou.nodeType(hou.vopNodeTypeCategory(), filter_type):
        
        # Ask user to select a tex file sequence.
        # A full sequence will be 1-8.
        # Partial sequences e.g. 3-7 will be clamped.
        tex_seq = hou.ui.selectFile(start_directory = "$HIP/tex",
                                    title = tool_title,
                                    collapse_sequences = True,
                                    file_type = hou.fileType.Any,
                                    pattern = "*.tex",
                                    default_value = None,
                                    multiple_select = False,
                                    image_chooser = False,
                                    chooser_mode = hou.fileChooserMode.Read)
    
        if(tex_seq != ""):
            file_paths = []
            valid_tex_index = []

            # Check if the files actually exist on disk
            for n in range(8):
                abs_tex_file_path = hou.text.expandStringAtFrame(tex_seq, n + 1)
                if os.path.isfile(abs_tex_file_path):
                    file_paths.append((abs_tex_file_path, True))
                    valid_tex_index.append(n)
                else:
                    file_paths.append((abs_tex_file_path, False))

            for idx, val in enumerate(file_paths):
                parm_index = idx + 1
                parm_name = "hatchingTex{num}".format(num = parm_index)
                tex_parm = target.parm(parm_name)
                target_index = None

                # Clamp if tex files do not exist on disk.
                # This may be the case if the file was deleted
                # while the user was browsing for it.
                if val[1] is False:
                    if idx < valid_tex_index[0]:
                        # Take the index of the first valid tex file
                        target_index = valid_tex_index[0]
                    else:
                        # Take the index of the last valid tex file
                        target_index = valid_tex_index[-1]
                else:
                    target_index = idx
                
                # Finally set the string field parameters
                tex_parm.set(hou.text.collapseCommonVars(file_paths[target_index][0], vars = ["$HIP"]))             
        else:
            raise Exception("Cancelled")
            
    else:
        raise Exception("Target node must be of type {required_type}, not {selected_type}".format(required_type = filter_type,
                                                                                                  selected_type = target.type().name()))

except Exception as inst:
    print(inst.args[0])
