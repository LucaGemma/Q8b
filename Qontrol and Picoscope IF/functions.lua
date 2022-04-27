readings_captured = 0
function do_setup(capture_time, sample_rate)
	reset()
	dmm.digitize.func = dmm.FUNC_DIGITIZE_CURRENT
	dmm.digitize.range = 1
	dmm.digitize.samplerate = sample_rate
	format.data = format.REAL32
 
	trigger.model.setblock(1, trigger.BLOCK_DIGITIZE,
	defbuffer1,
	trigger.COUNT_INFINITE)
 
	trigger.model.setblock(2, trigger.BLOCK_DELAY_CONSTANT,capture_time)
 
	trigger.model.setblock(3, trigger.BLOCK_DIGITIZE,defbuffer1,trigger.COUNT_STOP)
	waitcomplete()
	print("ok")
end

function trig()
	readings_captured = 0
	trigger.model.initiate()
	print("ok")
end

function get_data()
	chunker = 249
	while buffer.getstats(defbuffer1).n - readings_captured < chunker do
		delay(0.001)
	end
	local index1 = math.mod(readings_captured, 100000) + 1
	local index2 = index1 + (chunker - 1)
	if index2 > 100000 then
		index2 = 100000
	end
	printbuffer(index1, index2, defbuffer1)
	readings_captured = readings_captured + chunker
end

function disp_state(screen, state)
	if screen == 0 then
		display.changescreen(display.SCREEN_HOME)
	elseif screen == 1 then
		display.changescreen(display.SCREEN_GRAPH)
	elseif screen == 16 then
		display.changescreen(16)
	end
	if state == 0 then
		display.lightstate = display.STATE_LCD_OFF
	else
		display.lightstate = display.STATE_LCD_100
	end 
	print("ok")
end
print("functions loaded")