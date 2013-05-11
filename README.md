slowmotion
==========

I developed a social event application for Beko, The Sponsor of Turkish Basketball League. Visitors register with 
Facebook Login from the registration desk and go to playground recorded by two cameras from different position in speed 
motion. Operator presses the record button. They try to make a smash point. When operator finishes the record, applicati
on connects with PTP protocol to the cameras to copy the visitor's video. We find last visitors video by Lua script on 
CHDK firmware. Application combines these two videos and adds the song of the fest using ffmpeg. Then application upload 
files with ssh to remote server using Celery Task Queue. In upload action application check file's md5sum using special 
ssh function and posts it to the player's Facebook Wall.
