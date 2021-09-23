# Sets the 'hatchingTex#' multiparm string fields of PxrStylizedHatching display filter
# from a sequence of up to 8 *.tex files in Houdini. If the sequence contains less than
# 8 textures, the beginning and the end will be clamped (repeated).
# It's yours to use for free. Happy hatching!

import hou
import os

tool_title= "Set Hatching Textures"
filter_type = "pxrstylizedhatching::3.0"
tex_isfile = []
selected = hou.selectedNodes()
target = None

try:
    if not selected:
        raise Exception("Nothing is selected.")
    else:
        target = selected[0]
        
    if target.type() == hou.nodeType(hou.vopNodeTypeCategory(), filter_type):
        
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
            for n in range(8):
                parm_name = "hatchingTex{num}".format(num = n+1)
                tex_parm = target.parm(parm_name)
                abs_tex_file_path = hou.text.expandStringAtFrame(tex_seq, n+1)
                tex_parm.set(hou.text.collapseCommonVars(abs_tex_file_path, vars = ["$HIP"]))

                if os.path.isfile(abs_tex_file_path):
                    tex_isfile.append(True)
                else:
                    tex_isfile.append(False)

            if not all(tex_isfile):
                valid_tex_index = [i+1 for i, x in enumerate(tex_isfile) if x is True]
                
                for idx, val in enumerate(tex_isfile):
                    parm_index = idx + 1
                    slot = None
                    if val is False:
                        if parm_index < valid_tex_index[0]:
                            slot = valid_tex_index[0]
                        else:
                            slot = valid_tex_index[-1]
                    else:
                        slot = parm_index

                    next_available = target.parm("hatchingTex{num}".format(num = slot)).eval()
                    target.parm("hatchingTex{num}".format(num = idx+1)).set(hou.text.collapseCommonVars(next_available, vars = ["$HIP"]))             
        else:
            raise Exception("Cancelled")
            
    else:
        raise Exception("Target node must be of type {required_type}, not {selected_type}".format(required_type = filter_type,
                                                                                                  selected_type = target.type().name()))

except Exception as inst:
    print(inst.args[0])
