local iup = require('iuplua')

local games = {
  'Black/White',
  'Black2/White2',
  'Diamond/Pearl',
  'HeartGold/SoulSilver'
}

local game_list = iup.list{dropdown = 'YES', value = 1, size = '200x'}
for i, name in ipairs(games) do
  game_list[i] = name
end

local ok = iup.button{title = 'OK'}
local cancel = iup.button{title = 'Cancel'}

local dialog = iup.dialog{
  iup.vbox{
    iup.label{title = 'Select a Pokémon game:'},
    game_list,
    iup.hbox{ok, cancel, gap = '10'},
    margin = '10x10',
    gap = '5'
  },
  title = 'Pokémon Game Selector',
  size = 'QUARTERxEIGHTH'
}

local selection

function ok:action()
  selection = game_list[tonumber(game_list.value)]
  return iup.CLOSE
end

function cancel:action()
  selection = nil
  return iup.CLOSE
end

dialog:showxy(iup.CENTER, iup.CENTER)
iup.MainLoop()

print(selection or 'Canceled')

