"""Drive Mesen2 headless with an input plan.
Plan steps (strings): 'w N' wait N frames; 'p BTN[+BTN] [hold]' press buttons; 'shot NAME';
'dump NAME' dump WRAM+VRAM+CGRAM+OAM; 'lua CODE' run Lua (globals: outdir).
"""
import os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import MESEN

LUA = r'''
local plan = %s
outdir = [[%s]]
local i, wait, hold, held = 1, 0, 0, {}
function wf(name, data) local f = io.open(outdir .. name, "wb"); f:write(data); f:close() end
local function dumpmem(name, mt, size)
  local t = {}
  for a = 0, size - 1 do t[#t+1] = string.char(emu.read(a, mt)) end
  wf(name, table.concat(t))
end
%s
emu.addEventCallback(function()
  if hold > 0 then emu.setInput(held, 0) end
end, emu.eventType.inputPolled)
emu.addEventCallback(function()
  if hold > 0 then hold = hold - 1; if hold == 0 then held = {} end; return end
  if wait > 0 then wait = wait - 1; return end
  while i <= #plan do
    local s = plan[i]; i = i + 1
    local cmd, a1, a2 = s[1], s[2], s[3]
    if cmd == "w" then wait = a1; return
    elseif cmd == "p" then held = {}; for b in string.gmatch(a1, "[^+]+") do held[b] = true end; hold = a2; return
    elseif cmd == "shot" then wf(a1 .. ".png", emu.takeScreenshot())
    elseif cmd == "dump" then
      dumpmem(a1 .. ".wram", emu.memType.snesWorkRam, 0x20000)
      dumpmem(a1 .. ".vram", emu.memType.snesVideoRam, 0x10000)
      dumpmem(a1 .. ".cgram", emu.memType.snesCgRam, 0x200)
      dumpmem(a1 .. ".oam", emu.memType.snesSpriteRam, 0x220)
      dumpmem(a1 .. ".sram", emu.memType.snesSaveRam, emu.getMemorySize(emu.memType.snesSaveRam))
      local st = emu.getState(); local keys = {}
      for k, v in pairs(st) do if string.sub(k, 1, 4) == "ppu." then keys[#keys+1] = k .. "=" .. tostring(v) end end
      table.sort(keys); wf(a1 .. ".ppu", table.concat(keys, "\n"))
    elseif cmd == "lua" then load(a1)()
    end
  end
  emu.stop(0)
end, emu.eventType.endFrame)
'''


def to_lua(plan):
    out = []
    for s in plan:
        parts = s.split(None, 1) if s.startswith('lua ') else s.split()
        cmd = parts[0]
        if cmd == 'w':
            out.append('{"w",%d}' % int(parts[1]))
        elif cmd == 'p':
            out.append('{"p","%s",%d}' % (parts[1], int(parts[2]) if len(parts) > 2 else 4))
        elif cmd == 'lua':
            out.append('{"lua",[==[%s]==]}' % parts[1])
        else:
            out.append('{"%s","%s"}' % (cmd, parts[1]))
    return '{' + ','.join(out) + '}'


def fix_settings():
    """Mesen rewrites settings.json on exit; re-enable Lua IO and a SNES pad on port 1."""
    sp = os.path.join(os.path.dirname(MESEN), 'settings.json')
    if not os.path.exists(sp):
        return
    t = open(sp, encoding='utf-8').read()
    t = t.replace('"AllowIoOsAccess": false', '"AllowIoOsAccess": true')
    t = re.sub(r'"ScriptTimeout": \d+', '"ScriptTimeout": 100', t)
    i = t.find('"Snes": {')
    j = t.find('"Port1": {', i)
    k = t.find('"Type": ', j)
    e = t.find('\n', k)
    comma = ',' if t[e - 1] == ',' else ''
    t = t[:k] + '"Type": "SnesController"' + comma + t[e:]
    open(sp, 'w', encoding='utf-8').write(t)


def run(rom, plan, outdir, extra_lua='', timeout=600, fresh=True, sram=None):
    fix_settings()
    saves = os.path.join(os.path.dirname(MESEN), 'Saves')
    if fresh:  # start without battery save so navigation is reproducible
        import shutil
        shutil.rmtree(saves, ignore_errors=True)
    if sram is not None:  # preload a battery save (e.g. from tools/savegen.py)
        os.makedirs(saves, exist_ok=True)
        open(os.path.join(saves, os.path.splitext(os.path.basename(rom))[0] + '.srm'), 'wb').write(sram)
    os.makedirs(outdir, exist_ok=True)
    od = os.path.join(os.path.abspath(outdir), '')
    script = os.path.join(outdir, '_drive.lua')
    with open(script, 'w') as f:
        f.write(LUA % (to_lua(plan), od, extra_lua))
    r = subprocess.run([MESEN, '--testrunner', os.path.abspath(rom), script],
                       capture_output=True, text=True, timeout=timeout)
    return r.stdout


if __name__ == '__main__':
    rom, outdir, planfile = sys.argv[1:4]
    plan = [l.strip() for l in open(planfile) if l.strip() and not l.startswith('#')]
    extra = open(sys.argv[4]).read() if len(sys.argv) > 4 else ''
    print(run(rom, plan, outdir, extra))
