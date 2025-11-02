
pm = resolve.GetProjectManager()
project = pm.GetCurrentProject()
timeline = project.GetCurrentTimeline()
if not timeline:
    raise RuntimeError("No active timeline")



def set_tool_values(comp, values_to_set, tool_list_filter='TextPlus'):
    tools = comp.GetToolList(tool_list_filter) or {}
    for new in values_to_set:
        tool = get_tool_by_name(new['tool'], tools)
        tool.SetInput(new['input'], new['value'])

def set_text_on_fusion_comp(comp, mainText, secondaryText):
    new_values = [
        {'tool': 'mainText',      'input': 'StyledText', 'value': mainText},
        {'tool': 'secondaryText', 'input': 'StyledText', 'value': secondaryText}
    ]

    return set_tool_values(comp, new_values)

def get_tool_by_name(name, tools):
    tools = tools.values()
    for tool in tools:
        attrs = tool.GetAttrs() or {}
        regid = attrs.get("TOOLS_RegID", "")
        loopToolName = attrs.get("TOOLS_Name", "")
        
        if loopToolName == name:
            print(f"{regid=} {loopToolName=}")
            return tool

    raise Exception(f"Tool not found! No hits after {len(tools)} tools, looking for {name}.")

first_fusion_comp = next((c.GetFusionCompByIndex(1) for c in resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline().GetItemListInTrack('video',1) if c.GetFusionCompCount()>0),None)

set_text_on_fusion_comp(first_fusion_comp, 'test 1233', 'test 243')
