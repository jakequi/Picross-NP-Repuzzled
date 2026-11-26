-- Auto-solver for Picross NP (drive.py extra Lua). Call AUTOSOLVE() from a plan step
-- ('lua AUTOSOLVE()') once the puzzle is live, then wait for the queued inputs to play out.
-- Field: 7E:75F9 + y*0x24 + x; solution cells 0x27 = filled, 0x26 = empty.
-- Cursor: 7E:74F7 = x, 7E:74F9 = y (field coordinates). We place the cursor directly and press A.
QUEUE = {}
QI = 1
local FIELD = 0x7E75F9
local CX, CY = 0x7E74F7, 0x7E74F9
function AUTOSOLVE()
  local base = nil
  for a = 0, 0x500 do
    local v = emu.read(FIELD + a, emu.memType.snesMemory)
    if v == 0x26 or v == 0x27 then base = a; break end
  end
  if not base then print("no grid"); return end
  local ox, oy = base % 0x24, base // 0x24
  local rows, cols = 0, 0
  while true do
    local v = emu.read(FIELD + base + rows * 0x24, emu.memType.snesMemory)
    if v ~= 0x26 and v ~= 0x27 then break end
    rows = rows + 1
  end
  while true do
    local v = emu.read(FIELD + base + cols, emu.memType.snesMemory)
    if v ~= 0x26 and v ~= 0x27 then break end
    cols = cols + 1
  end
  print(string.format("grid origin (%d,%d) %dx%d", ox, oy, cols, rows))
  QUEUE = {}; QI = 1
  for r = 0, rows - 1 do
    for c = 0, cols - 1 do
      if emu.read(FIELD + base + r * 0x24 + c, emu.memType.snesMemory) == 0x27 then
        for k = 1, 12 do QUEUE[#QUEUE + 1] = {"", ox + c, oy + r} end
        for k = 1, 4 do QUEUE[#QUEUE + 1] = {"a", ox + c, oy + r} end
        for k = 1, 4 do QUEUE[#QUEUE + 1] = {"", ox + c, oy + r} end
      end
    end
  end
end
emu.addEventCallback(function()
  if QI <= #QUEUE then
    local q = QUEUE[QI]; QI = QI + 1
    emu.write(CX, q[2], emu.memType.snesMemory)
    emu.write(CY, q[3], emu.memType.snesMemory)
    if q[1] ~= "" then local t = {}; t[q[1]] = true; emu.setInput(t, 0) end
  end
end, emu.eventType.inputPolled)
