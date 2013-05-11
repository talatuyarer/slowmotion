-- find last created file on hacked camera with chdk
function dircomp(d1, d2)
    -- compare the digits of a DCIM subdirectory.
    return string.sub(d1, 1, 3) < string.sub(d2, 1, 3)
end

function file_comp(f1, f2)
    -- compare the digits of an image/video file in a DCIM subdirectory.
    return string.sub(f1, 5, 8) < string.sub(f2, 5, 9)
end

local entries = os.listdir("A/DCIM")
local max_dir = nil
local max_file = nil
local i
if #entries == 0 then
    write_usb_msg(nil)
    return
end
table.sort(entries, dircomp)
for i = table.getn(entries), 1, -1 do
    local dir_name = entries[i]
    if string.find(dir_name, '^%d%d%d') then
        dir_name = "A/DCIM/" .. dir_name
        if os.stat(dir_name)['is_dir'] then
            max_dir = dir_name
            break
        end
    end
end
if max_dir == nil then
    write_usb_msg(nil)
    return
end
-- Without the sleep(1), the SX30 powers off quite reliably...
sleep(1)
entries = os.listdir(max_dir)
table.sort(entries, file_comp)
for i = table.getn(entries), 1, -1 do
    local filename = entries[i]
    if string.find(filename, '^....%d%d%d%d') then
        -- XXX would it make sense to also check if we have a
        -- real file, not a directory? Or the name's suffix?
        write_usb_msg(max_dir .. '/' .. filename)
        return
    end
end
-- this happens if we have an empty directory.
write_usb_msg(max_dir)
