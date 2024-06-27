import sys
import time

def AddTimelineToRender( project, timeline, presetName, targetDirectory, renderFormat, renderCodec ):
	project.SetCurrentTimeline(timeline)
	project.LoadRenderPreset(presetName)
	
	# print("Setting codec")
	# Not needed; it's in the preset.
	# if not project.SetCurrentRenderFormatAndCodec(renderFormat, renderCodec):
	# 	return False
	
	print("setting frames and dir")
	project.SetRenderSettings({"SelectAllFrames" : 1, "TargetDir" : targetDirectory})
	print("Add job")
	return project.AddRenderJob()

def should_skip_timeline(timeline_name, existing_render_job):
	if timeline_name in ["Timeline 1", "All Clips"]:
		return "It's a Default timeline"

	if len(timeline_name) == 14: # "2024-04-04 Thu".length == 14
		return "It lacks a more specific name than the date"

	if existing_render_job and "JobStatus" in existing_render_job:
		return f"Its render status is: {existing_render_job["JobStatus"]}"

    # "JobId": "1c705ff7-8a82-4f29-be3e-cc1d10086e41",
    # "RenderJobName": "Job 2",
    # "TimelineName": "2024-03-17 Sun",
    # "TargetDir": "C:\\Users\\Eric\\Desktop\\test0deleteme",
    # "IsExportVideo": True,
    # "IsExportAudio": True,
    # "FormatWidth": 3840,
    # "FormatHeight": 2160,
    # "FrameRate": "23.976",
    # "PixelAspectRatio": 1.0,
    # "MarkIn": 86400,
    # "MarkOut": 101656,
    # "AudioBitDepth": 16,
    # "AudioSampleRate": 48000,
    # "ExportAlpha": False,
    # "OutputFilename": "2024-03-17 Sun.mov",
    # "RenderMode": "Single clip",
    # "PresetName": "Custom",
    # "VideoFormat": "QuickTime",
    # "VideoCodec": "H.265 NVIDIA",
    # "AudioCodec": "aac",
    # "EncodingProfile": "Main10",
    # "MultiPassEncode": False,
    # "NetworkOptimization": True,
    # "JobStatus": "Ready",
    # "CompletionPercentage": 0,

	return False


def GetRenderStatusForTimelines():
	project = resolve.GetProjectManager().GetCurrentProject()
	jobs = resolve.GetProjectManager().GetCurrentProject().GetRenderJobList()

	# Collect job status and merge into jobs dict list
	jobs_with_status = map(lambda j: {**j, **project.GetRenderJobStatus(j["JobId"])}, jobs)
	
	return list(jobs_with_status)

def GetRenderJobForTimeline(timeline_name):
	if not current_jobs or len(current_jobs) < 1:
		return {}

	jobs_for_timeline = list(filter(lambda j: j["TimelineName"] == timeline_name, current_jobs))

	if len(jobs_for_timeline) < 1:
		return {}

	return jobs_for_timeline[0]

def RenderAllTimelines( resolve, presetName, targetDirectory, renderFormat, renderCodec ):
	projectManager = resolve.GetProjectManager()
	project = projectManager.GetCurrentProject()
	if not project:
		return False

	renderjob_list = GetRenderStatusForTimelines()
	
	
	resolve.OpenPage("Deliver")
	timelineCount = project.GetTimelineCount()
	
	for index in range (0, int(timelineCount)):
		timeline = project.GetTimelineByIndex(index + 1)
		timeline_name = timeline.GetName()
		existing_render_job = GetRenderJobForTimeline(timeline_name)
		
		skip_reason = should_skip_timeline(timeline_name, existing_render_job)
		if skip_reason:
			print(f"Skipping {timeline_name} because {skip_reason}")
			continue

		
		# print(f"Would have rendered: {timeline_name}")
		# continue

		print(f"{index}/{timelineCount} Name: {timeline_name}")
		if not AddTimelineToRender(project, timeline, presetName, targetDirectory, renderFormat, renderCodec):
			print(f"Error on: {timeline_name}")
			return False

	
	#render_result = project.StartRendering()
	#return render_result
	return True

def IsRenderingInProgress( resolve ):
	projectManager = resolve.GetProjectManager()
	project = projectManager.GetCurrentProject()
	if not project:
		return False
		
	return project.IsRenderingInProgress()

def WaitForRenderingCompletion( resolve ):
	while IsRenderingInProgress(resolve):
		time.sleep(1)
	return

def DeleteAllRenderJobs( resolve ):
	projectManager = resolve.GetProjectManager()
	project = projectManager.GetCurrentProject()
	project.DeleteAllRenderJobs()
	return

# Get currently open project
print(f"resolve: {resolve}")
# Inputs: 
# - preset name for rendering
# - render path
# - render format
# - render codec

renderPresetName = "h.265 CQP"
renderPath = "Y:\\Davinci Resolve\\Temp Output"
renderFormat = "mov"
renderCodec = "H265"

current_jobs = GetRenderStatusForTimelines() # This gets cached in a variable.

if not RenderAllTimelines(resolve, renderPresetName, renderPath, renderFormat, renderCodec):
	print("Unable to set all timelines for rendering")
	sys.exit()

# WaitForRenderingCompletion(resolve)

# DeleteAllRenderJobs(resolve)

print("Rendering is completed.")
