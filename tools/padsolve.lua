-- Solve the live puzzle with real pad input. FIELD = first cell address; reads 0x27 = filled.
-- PADSOLVE(limit): queue inputs for the first `limit` filled cells (nil = all).
PQ = {}; PI = 1
function PADSOLVE(limit)
  local F = nil
  for a = 0x7E7600, 0x7E7C00 do
    local ok = true
    for k = 0, 4 do local v = emu.read(a + k, emu.memType.snesMemory); if v ~= 0x26 and v ~= 0x27 then ok = false; break end end
    if ok then F = a; break end
  end
  if not F then print("no grid"); return end
  local rows, cols = 0, 0
  while true do local v = emu.read(F + rows * 0x24, emu.memType.snesMemory); if v ~= 0x26 and v ~= 0x27 then break end; rows = rows + 1 end
  while true do local v = emu.read(F + cols, emu.memType.snesMemory); if v ~= 0x26 and v ~= 0x27 then break end; cols = cols + 1 end
  print(string.format("pad grid %dx%d", cols, rows))
  local function push(b, n) for k = 1, n do PQ[#PQ + 1] = b end end
  local x, y, done = 0, 0, 0
  for r = 0, rows - 1 do
    local cs = {}
    for c = 0, cols - 1 do if emu.read(F + r * 0x24 + c, emu.memType.snesMemory) == 0x27 then cs[#cs + 1] = c end end
    if r % 2 == 1 then local t = {}; for k = #cs, 1, -1 do t[#t + 1] = cs[k] end; cs = t end
    for _, c in ipairs(cs) do
      if limit and done >= limit then return end
      while y < r do push("down", 3); push("", 9); y = y + 1 end
      while x < c do push("right", 3); push("", 9); x = x + 1 end
      while x > c do push("left", 3); push("", 9); x = x - 1 end
      push("a", 3); push("", 9); done = done + 1
    end
  end
end
emu.addEventCallback(function()
  if PI <= #PQ then
    local b = PQ[PI]; PI = PI + 1
    if b ~= "" then local t = {}; t[b] = true; emu.setInput(t, 0) end
  end
end, emu.eventType.inputPolled)
