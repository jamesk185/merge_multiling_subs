
import re
import datetime as dt
from datetime import datetime
import re
import sys

def parse_subs(text):
	# initialise
	prevline = "blank"
	content = ""
	subs_dict = {}
	
	# loop through text line by line
	for count, line in enumerate(text):
		line = line.strip()
		
		# line is subtitle number so start new block
		if line.isnumeric() and prevline == "blank":
			id = line
			prevline = "id"
		# line is time stamp
		elif " --> " in line and prevline == "id":
			start_time, end_time = line.split(" --> ")
			# parse the timestamps
			start_time = datetime.strptime(start_time, time_format)
			end_time = datetime.strptime(end_time, time_format)
			prevline = "time"
		# line is text
		elif line and prevline in ["time", "content"]:
			content += " " + line
			content = content.strip()
			prevline = "content"
		# line is blank so start new block
		elif not line:
			# add to all block's data to dict
			if id not in subs_dict:
				subs_dict[id] = (start_time, end_time, content)
			else:
				print(f"ID used a second time on line {count}. Exited early")
				sys.exit()
			content = ""
			prevline = "blank"
		# unknown
		else:
			print(f"Issue on line {count}. Exited early")
	
	return subs_dict


def merge_subs(first_sub, second_sub):
	
	out = ""
	
	# create lists for both
	first_sub_list = [(value, key) for key, value in first_sub.items()]
	second_sub_list = [(value, key) for key, value in second_sub.items()]
	
	# find starting sub ID in second_sub
	for i in range(3):
		# getting starting time in first_sub
		start_time = first_sub_list[i][0][0]
		# find starting point in second_sub
		starting_second_sub = [x[1] for x in second_sub_list if dates2seconds_diff(x[0][0], start_time) < 0.5]
		if starting_second_sub:
			starting_second_sub = starting_second_sub[0]
			starting_first_sub = first_sub_list[i][1]
			break
		elif not starting_second_sub and i == 2:
			print("Could not find the starting point in the second file.")
	
	# remove subs that come before the starting points
	first_sub_list = [x for x in first_sub_list if int(x[1]) >= int(starting_first_sub)]
	second_sub_list = [x for x in second_sub_list if int(x[1]) >= int(starting_second_sub)]
	
	for sub, key in first_sub_list:
		done = None
		first_start_time = sub[0]
		first_end_time = sub[1]
		first_content = sub[2]
		
		if not second_sub_list:
			continue
		second_start_time = second_sub_list[0][0][0]
		second_end_time = second_sub_list[0][0][1]
		second_content = second_sub_list[0][0][2]
		
		if dates2seconds_diff(second_start_time, first_start_time) > 1:
			print(f"No good starting point for first sub {key}")
			# add to output text with no match
			out += key + "\n" + first_start_time.strftime(time_format) + " --> " + first_end_time.strftime(time_format) + "\n" + first_content + "\n\n"
			continue
		
		if dates2seconds_diff(second_end_time, first_end_time) < 0.75:
			# choose longest interval
			start_time = first_start_time if first_start_time < second_start_time else second_start_time
			end_time = first_end_time if first_end_time > second_end_time else second_end_time
			# add to output with match
			out += key + "\n" + start_time.strftime(time_format) + " --> " + end_time.strftime(time_format) + "\n" + first_content + "\n" + second_content + "\n\n"
			done = "yes"
			# remove ouputted sub from second_sub_list
			second_sub_list = second_sub_list[1:]
			continue
		
		# see if merging two from second_sub gives a match
		if len(second_sub_list) < 2:
			continue
		second_start_time_ = second_sub_list[1][0][0]
		second_end_time_ = second_sub_list[1][0][1]
		second_content_ = second_sub_list[1][0][2]
		
		if dates2seconds_diff(second_end_time_, first_end_time) < 0.75 and second_start_time_ < first_end_time:
			# choose longest interval
			start_time = first_start_time if first_start_time < second_start_time else second_start_time
			end_time = first_end_time if first_end_time > second_end_time_ else second_end_time_
			# add to output with merged match
			# TO DO maybe add - between second_contents
			out += key + "\n" + start_time.strftime(time_format) + " --> " + end_time.strftime(time_format) + "\n" + first_content + "\n" + second_content + " " + second_content_ + "\n\n"
			done = "yes"
			# remove ouputted sub from second_sub_list
			second_sub_list = second_sub_list[2:]
			continue
		
		if not done:
			print(f"No good match for first sub {key}")
			# add to output text with no match
			out += key + "\n" + first_start_time.strftime(time_format) + " --> " + first_end_time.strftime(time_format) + "\n" + first_content + "\n\n"
		
	#### first idea
#	for key, sub in first_sub.items():
#		done = None
#		start_time = sub[0]
#		end_time = sub[1]
#		content = sub[2]
#		
#		# (1) start time and end time difference less than 500ms
#		second_sub_filtered = [x[1] for x in second_sub_list if
#			dates2seconds_diff(x[0][0], start_time) < 0.5 and 
#			dates2seconds_diff(x[0][1], end_time) < 0.5
#		]
#		if second_sub_filtered and len(second_sub_filtered) == 1:
#			second_content = "\n" + second_sub.get(second_sub_filtered[0])[2]
#			second_sub_list = [x for x in second_sub_list if x[1] != second_sub_filtered[0]]
#			out += key + "\n" + start_time.strftime(time_format) + " --> " + end_time.strftime(time_format) + "\n" + content + second_content + "\n\n"
#			done = "Y"
#			continue
#		
#		# (2) start time and end time difference less than 1s
#		second_sub_filtered = [x[1] for x in second_sub_list if
#			dates2seconds_diff(x[0][0], start_time) < 1 and 
#			dates2seconds_diff(x[0][1], end_time) < 1
#		]
#		if second_sub_filtered and len(second_sub_filtered) == 1:
#			second_content = "\n" + second_sub.get(second_sub_filtered[0])[2]
#			second_sub_list = [x for x in second_sub_list if x[1] != second_sub_filtered[0]]
#			out += key + "\n" + start_time.strftime(time_format) + " --> " + end_time.strftime(time_format) + "\n" + content + second_content + "\n\n"
#			done = "Y"
#			continue
#		
#		if not done:
#			out += key + "\n" + start_time.strftime(time_format) + " --> " + end_time.strftime(time_format) + "\n" + content + "\n\n"
	
	print(f"Unmatched in second_sub: {len(second_sub_list)}")
	
	return out


# calculate the difference in total seconds between two timestamps
def dates2seconds_diff(first_date, second_date):
	first_seconds = (first_date-dt.datetime(1900,1,1)).total_seconds()
	second_seconds = (second_date-dt.datetime(1900,1,1)).total_seconds()
	return abs(second_seconds - first_seconds)


def main():
	global time_format
	
	# define time format
	time_format = "%H:%M:%S,%f"
	
	# read first subtitle file
	first_sub_path = r"C:\Users\james\Documents\Python\merge_subtitles\La.Vie.de.Boheme.1990.Criterion.1080p.BluRay.x265.HEVC.AAC-SARTRE.srt"
	with open(first_sub_path, "r") as r:
		first_sub = r.readlines()
	
	# read second subtitle file
	second_sub_path = r"C:\Users\james\Documents\Python\merge_subtitles\[zmk.pw]The.Bohemian.Life.1992.1080p.BluRay.x264.AAC-[YTS.MX].srt"
	with open(second_sub_path, "r") as r:
		second_sub = r.readlines()
	
	# this will be the primary sub
	first_sub = parse_subs(first_sub)
	# this will be the secondary sub
	second_sub = parse_subs(second_sub)
	
	out = merge_subs(first_sub, second_sub)
	
	with open("merged_subs.srt", "w") as w:
		w.write(out)
	


if __name__ == "__main__":
    main()



