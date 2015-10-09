

set("log.file.path","/tmp/liquidsoap-79500996294.log")
set("log.level", 4)
set("server.socket",true)
set("server.socket.path","/tmp/testliq.sock")
	
iMusic = interactive.string("music","music0")
	
		sMusic0 = single("/usr/scripts/liquidsoap/music/mono-8000.wav")
		
		sMusic1 = single("/usr/scripts/liquidsoap/music/mono2-8000.wav")
		
		sMusic2 = single("/usr/scripts/liquidsoap/music/mono3-8000.wav")
		
	# By default advices randomized before play in playlist
	sAdvices = playlist.once("/usr/scripts/liquidsoap/music/advices/")
	
	def crossfade(a,b)
		add(normalize=false,
		[
			sequence([ blank(duration=0.5),
			fade.initial(duration=1.,b) ]),
			fade.final(duration=1.,a)
		])
	end

	sResult = mksafe(
		switch(track_sensitive=false,
		transitions=[crossfade, crossfade, crossfade],
		[
	
				({"music0" == iMusic()},sMusic0),
		
				({"music1" == iMusic()},sMusic1),
		
				({"music2" == iMusic()},sMusic2),
		
		])
	)
	
	# delay advices
	sDelayedAdvices = delay(initial=true,30.,sAdvices)

	# say balance or position if requested
	#sResult = add([sResult, switch([
	#	(checkSaybalance, sBalance),
	#	({true}, request.queue(id="qposition")),
	#	({true}, sDelayedAdvices),		
	#])],weights=[1,10])	
	sResult = smooth_add(delay=1., p=0.1, normal=sResult, special=switch([
		(checkSaybalance, request.queue(id="balance")),
		({true}, request.queue(id="qposition")),
		({true}, sDelayedAdvices),		
	]))

	##### Output wav to stdout#####
	# clock must be in sync=true so there is no output buffer
	# clock.assign_new(sync=false,[sResult])
	# flush=true makes it send data as soon as possible, not 64k every 5 sec (makes no delay before start)
	out = output.file(%wav(header=false, channels=1, samplerate=8000), "/dev/stdout", sResult, flush=true)
	
