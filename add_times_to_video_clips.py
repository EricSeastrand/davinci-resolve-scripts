
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

# first_fusion_comp = next((c.GetFusionCompByIndex(1) for c in resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline().GetItemListInTrack('video',1) if c.GetFusionCompCount()>0),None)

# set_text_on_fusion_comp(first_fusion_comp, 'test 1233', 'test 243')

def ensure_video_track(timeline, index):
    track_count = timeline.GetTrackCount('video')
    if track_count < index:
        timeline.AddTrack('video')
    return index


def find_media_pool_item_by_name_fragment(name_fragment):
    """
    Search the entire Media Pool (all folders) for a clip whose name contains
    the given substring (case-insensitive). Returns the first MediaPoolItem found,
    or None if not found.
    """
    media_pool = project.GetMediaPool()
    root = media_pool.GetRootFolder()
    name_fragment = name_fragment.lower()

    def recurse(folder):
        # scan clips in this folder
        for clip in folder.GetClipList() or []:
            name = clip.GetName() or ""
            if name_fragment in name.lower():
                return clip
        # recurse into subfolders
        for subfolder in folder.GetSubFolderList() or []:
            found = recurse(subfolder)
            if found:
                return found
        return None

    res = recurse(root)
    if res is None:
        raise Exception(f'Could not find media pool item: ~{name_fragment}')
    return res



def make_fusion_clip(timeline):
    fusion_template = r"X:\Davinci Settings\Fusion\lower-third-text-template.setting"

    ti = timeline.InsertFusionCompositionIntoTimeline()  # blank Fusion comp at playhead
    comp = ti.ImportFusionComp(fusion_template)          # load your template into that clip

#make_fusion_clip(timeline)

def prep_timeline_for_texts():
    timeline = get_timeline()
    
    
    ensure_video_track(timeline, 2)

    timeline.SetTrackEnable('video', 2, True)

    # fusion_template = "X:\\Davinci Settings\\Fusion\\lower-third-text-template.setting"
    # fusion_items = media_pool.ImportMedia([fusion_template])
    fusion_item = find_media_pool_item_by_name_fragment('Lower Third')
    print(fusion_item)
    return fusion_item


def apply_text_to_timeline_clips(text_creator_func=None, timeline_clips = None):
    global resolve

    if timeline_clips is None:
        timeline_clips = timeline.GetItemListInTrack('video', 1)

    fusion_item = prep_timeline_for_texts()

    for clip in timeline_clips:
        start_frame = clip.GetStart()

        if text_creator_func is None:
            clip_name = clip.GetName()  # or derive date from metadata
            texts = [clip_name, 'Testing Text']
        else:
            texts = text_creator_func(clip)

        media_pool = resolve.GetProjectManager().GetCurrentProject().GetMediaPool()
        print(media_pool.AppendToTimeline)
        fusion_clip = media_pool.AppendToTimeline([{
            "mediaPoolItem": fusion_item,
            "trackIndex": 2,
            "recordFrame": start_frame,     # where it should appear
            "startFrame": 0,
            "endFrame": 60
        }])[0]

        fusion_comp = fusion_clip.GetFusionCompByIndex(1)
        
        set_text_on_fusion_comp(fusion_comp, *texts)

resolve = None

def set_resolve(new_resolve):
    global resolve
    resolve = new_resolve

def get_timeline():
    global media_pool, timeline, project
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    timeline = project.GetCurrentTimeline()
    media_pool = project.GetMediaPool()
    return timeline

if __name__ == "__main__":
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    timeline = project.GetCurrentTimeline()
    media_pool = project.GetMediaPool()
    if not timeline:
        raise RuntimeError("No active timeline")
    apply_text_to_timeline_clips()
