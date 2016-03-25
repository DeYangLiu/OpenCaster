#!/usr/bin/env python
# encoding: gbk

import sqlite3,os,sys
from datetime import *

from dvbobjects.PSI.PAT import *
from dvbobjects.PSI.NIT import *
from dvbobjects.PSI.SDT import *
from dvbobjects.PSI.TDT import *
from dvbobjects.PSI.EIT import *
from dvbobjects.PSI.PMT import *
from dvbobjects.DVB.Descriptors import *
from dvbobjects.MPEG.Descriptors import *

if(len(sys.argv) < 2): 
	print "usage: db2sec.py epg.db"
	sys.exit(-1)

cx = sqlite3.connect(sys.argv[1])
c=cx.cursor()

tmp = c.execute(
"select id, table_id, service_id, transport_stream_id, original_network_id, segment_last_section_number, version_number, section_number, last_section_number from eit_header_tab")

r = c.fetchall()
out = open("./eit.sec", "wb")

for tab in r:
	eit = event_information_section(
			table_id = tab[1],
			service_id = tab[2],
			transport_stream_id = tab[3],
			original_network_id = tab[4],
			segment_last_section_number = tab[5],
			version_number = tab[6],
			section_number = tab[7],
			last_section_number = tab[8],
			event_loop = [],
			)

	tmp = c.execute("select event_id, start_time,end_time,ISO_639_language_code, event_name_char,text_char from event_header_tab where eit_header_id = %d"%tab[0])
	events = c.fetchall()
	cnt = 0;
	for evt in events:
		start_time	= datetime.fromtimestamp(evt[1])
		end_time	= datetime.fromtimestamp(evt[2])
		duration	= end_time - start_time
		s = duration.seconds
		hour = s/3600
		s = s%3600
		minute = s/60
		s = s%60
		start_time = start_time.timetuple()
		end_time = end_time.timetuple()

		if evt[4] == "(NULL)": continue

		el = event_loop_item(
				event_id = evt[0],
				start_year = start_time.tm_year - 1900,
				start_month = start_time.tm_mon,
				start_day = start_time.tm_mday,
				start_hours = start_time.tm_hour,
				start_minutes = start_time.tm_min,
				start_seconds = start_time.tm_sec,
				duration_hours = hour,
				duration_minutes = minute,
				duration_seconds = s,
				running_status = 4,
				free_CA_mode = 0,
				event_descriptor_loop = [
					short_event_descriptor(
					ISO639_language_code = evt[3].encode("gbk"),
					event_name = evt[4].encode("gbk"),
					text = evt[5].encode("gbk"),
					),
					],
				)
		cnt = cnt + 1;
		eit.event_loop.append(el);
	#print tab[0], cnt
	if cnt > 0 : out.write(eit.pack())

out.close()
