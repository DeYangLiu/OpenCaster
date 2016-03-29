How to Use OpenCaster with FFmpeg
====

# background
ffmpeg now can merge multiple services to a single ts file, eg:

```{r, engine='bash', count_lines}
ffmpeg -i cctv5.ts -i hunan.ts -i cctv1.ts -i hlj.ts \
 -map 0:0 -map 0:1 -map 1:0 -map 1:1 -map 2:0 -map 2:1 -map 3:0 -map 3:1 \
-program title="cctv5":st=0:st=1 -program title="HuNan":st=2:st=3 \
-program title="cctv1":st=4:st=5 -program title="HeiLongJiang":st=6:st=7 \
-codec copy \
-muxrate 29M -minrate 29M -maxrate 29M -t 127 -y out.ts

ffplay -vst p:123 -ast p:123 out.ts
```
the output has set pat/pmt/sdt nicely, except pcr [note1]. play the service with program number equals 123.

   the next thing we want to add eit table to the ts file.
I tried mplex13818, it will drop any unspecified pids. furthermore, it will cause av sync problem.
 

# OpenCaster 3.2.2 changed by ludi
 * add doc
 * add this file

# when you can't sudo install python-dev
```
mkdir $DESTDIR
export DESTDIR=path_to_install
make -C tools install

cp -rf libs/dvbobjects/dvbobjects $DESTDIR/
cp doc/_crc32.so $DESTDIR/dvbobjects/utils/

export PYTHONPATH=$DESTDIR
export PATH=$DESTDIR:$PATH
```

# common usage

```
tsfilter src.ts +1009 +1010  > cctv1_filterd.ts //keep pids
tsmask src.ts -pid0 -pid1 > audio.ts //remove pids

doc/eitconfig.py 
tscbrmuxer b:60 pat.ts b:60 pmt.ts b:15 sdt.ts  b:15 eit.ts b:3 nit.ts b:1 tdt.ts c:6000 cctv1_filterd.ts > cctv1_merged.ts
```

the parameter b:60 means "bitrate 60 bps", but in fact, it's just a relative value for comparision[note2]
we've done adding PSI/SI tables to the ts file, original data still exist.

the following adjust timestamps and send ts to QAM:

    tsstamp fifo1.ts 13271000 >fifo2.ts
    DtPlay fifo2.ts -t 110 -mt OFDM -mC QAM16 -mG 1/4 -mc 2/3 -mf 578

```
ffmpeg ... -muxrate 38M -minrate 38M -maxrate 38M -y out.ts
doc/db2sec.py my.db
tsnullshaper out.ts t:1900 eit_pf.ts t:9500 eit_sched.ts t:9900 nit.ts t:29000 tdt.ts  > out2.ts 
```

[note1]
only the last service's pmt has pcr which refer to the first video pid. it's a bug in mpegtsenc.c.
my modification goes in patch_ffmpeg

[note2]

```
 -- interval(t in seconds) -- TS packets(r=30/t)
pat 0.5		60
pmt 0.5		60
sdt 2		15
eit 2/4		15
nit 10		3
tdt 30		1
av  0.005	6000(=: x)

y = x/(154+x) ==> x = 154*y/(1-y)
```

# refs
[1] Guidelines on implementation and usage of Service Information
http://www.etsi.org/deliver/etsi_etr/200_299/211/02_60/etr_211e02p.pdf

