# This Houdini shelf tool will split your sop geo using blast nodes based on point or prim string attributes.
# It will ask you to select either all attribute values found or specific ones.
# Have fun!

import hou
import re
tool_title = "Null from String Attribute"
null_nodes = []
selected = hou.selectedNodes()
geo = None

try:
    if selected:
        selected = selected[0]
        if type(selected) is not hou.SopNode:
            raise Exception("Not a SOP node. Try again.")
        else:
            geo = selected.geometry()
    else:
        raise Exception("Nothing is selected. Try again.")
    
    pointStrAttribs = tuple([attrib for attrib in geo.pointAttribs() if attrib.dataType() == hou.attribData.String])
    primStrAttribs = tuple([attrib for attrib in geo.primAttribs() if attrib.dataType() == hou.attribData.String])
    validAttribTypes = {"point" : hou.attribType.Point, "prim" : hou.attribType.Prim}
    targetAttribType = None
    targetAttribTypeName = None
    targetAttribVals = None
    targetAttrib = None
    targetAttribName = None
    strAttribList = None
    
    if not pointStrAttribs and not primStrAttribs:
        raise Exception("No string point or prim attributes found.")
        
    elif pointStrAttribs and primStrAttribs:
        keys = validAttribTypes.keys()
        targetAttribTypeIdx = hou.ui.selectFromList(keys,
                                                    default_choices = (),
                                                    exclusive = True,
                                                    message = "Select Attribute Type",
                                                    title = tool_title,
                                                    column_header = "Attrib Type",
                                                    num_visible_rows = 5,
                                                    clear_on_cancel = True,
                                                    width = 0,
                                                    height = 200)
        if targetAttribTypeIdx == ():
            raise Exception("Cancelled.")
        
        key = keys[targetAttribTypeIdx[0]]
        targetAttribType = validAttribTypes[key]

    elif pointStrAttribs and not primStrAttribs:
        targetAttribType = validAttribTypes["point"]
        
    elif primStrAttribs and not pointStrAttribs:
        targetAttribType = validAttribTypes["prim"]

    else:
        raise Exception("Something went wrong with string attibs of type point or prim.")
        
        
        
    if targetAttribType == validAttribTypes["point"]:
        strAttribList = [attrib.name() for attrib in pointStrAttribs]
        targetAttribTypeName = "point"
        print(strAttribList)
    else:
        strAttribList = [attrib.name() for attrib in primStrAttribs]
        targetAttribTypeName = "prim"
        
    attribTypeName = str(targetAttribType).split(".")[1]
    targetAttribNameIdx = hou.ui.selectFromList(strAttribList,
                                                default_choices = (),
                                                exclusive = True,
                                                message = "Select a String {t} Attribute.".format(t = attribTypeName),
                                                title = tool_title,
                                                column_header = "Str {s} Attribs".format(s = attribTypeName),
                                                num_visible_rows = 5,
                                                clear_on_cancel = True,
                                                width = 0,
                                                height = 200)
    if targetAttribNameIdx == ():
        raise Exception("Cancelled")
    else:
        targetAttribName = strAttribList[targetAttribNameIdx[0]]
        
    if targetAttribType == validAttribTypes["point"]:
        targetAttrib = geo.findPointAttrib(targetAttribName)
    else:
        targetAttrib = geo.findPrimAttrib(targetAttribName)
    
    targetAttribVals = targetAttrib.strings()
    targetAttribValCount = len(targetAttribVals)
    
    if targetAttribValCount > 1:
        info = "There are {n} unique '{a}' attribute values.".format(n = targetAttribValCount, a = targetAttribName)
        whichVals = hou.ui.displayMessage("Select specific attribute values or proceed with all?",
                                                    buttons = ("Select Specific Values",
                                                               "Use All Values",
                                                               "Cancel"),
                                                    default_choice = 0,
                                                    title = tool_title,
                                                    help = info)
    
        if whichVals == 2:
            raise Exception("Cancelled")
        elif whichVals == 0:
            targetAttribValsIdx = hou.ui.selectFromList(targetAttribVals,
                                                        default_choices = (),
                                                        exclusive = False,
                                                        message = "Select Attribute Value(s)",
                                                        title = tool_title,
                                                        column_header = "{a}".format(s = targetAttribName),
                                                        num_visible_rows = 10,
                                                        clear_on_cancel = True,
                                                        width = 0,
                                                        height = 0)
            if targetAttribValsIdx:
                targetAttribVals = [targetAttribVals[i] for i in targetAttribValsIdx]
            else:
                raise Exception("Cancelled")
    
    
    nullNamePrefix = hou.ui.readInput("Enter null name prefix.",
                                        buttons = ("OK", "No Prefix", "Cancel"),
                                        severity = hou.severityType.Message,
                                        default_choice = 0,
                                        close_choice = -1,
                                        help = "The null name will be the attribute value prefixed by this.",
                                        title = tool_title,
                                        initial_contents = "OUT_") 
    if nullNamePrefix[0] == -1:
        raise Exception("Aborted")
    elif nullNamePrefix[0] == 2:
        raise Exception("Cancelled")
    elif nullNamePrefix[0] == 1:
        nullNamePrefix = ""
    else:
        nullNamePrefix = re.sub("[^\w]", "_", nullNamePrefix[1], flags = re.M)

    thisLocation = selected.parent()
    
    for val in targetAttribVals:
        nullName = val.split("/")[-1]
        nullName = re.sub("[^\w]", "_", nullName, flags = re.M)
        nullName = "{p}{n}".format(p = nullNamePrefix, n = nullName)
        null = thisLocation.createNode("null", nullName);
        blast = thisLocation.createNode("blast")
        
        null.setInput(0, blast)
        blast.setInput(0, selected)
        
        blast.parm("group").set("@{a}={v}".format(a = targetAttribName, v = val))
        blast.parm("negate").set(1)
        blast.parm("grouptype").set("{n}s".format(n = targetAttribTypeName))
        
        blast.moveToGoodPosition()
        null.moveToGoodPosition()
        print("{n} created.".format(n = nullName))
except Exception as inst:
    print(inst.args[0])
