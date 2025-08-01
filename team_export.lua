-- Configuration for various games. The addresses are examples and may need to
-- be adjusted for your ROM version.
local GAME_CONFIGS = {
    ["Diamond/Pearl"] = {
        PARTY_START = 0x02101D2C,
        POKEMON_SIZE = 0xEC,
        SPECIES_OFFSET = 0x08,
        LEVEL_OFFSET = 0x84,
        HP_OFFSET = 0x86,
        MAX_HP_OFFSET = 0x88
    },
    ["HeartGold/SoulSilver"] = {
        PARTY_START = 0x02111870,
        POKEMON_SIZE = 0xEC,
        SPECIES_OFFSET = 0x08,
        LEVEL_OFFSET = 0x84,
        HP_OFFSET = 0x86,
        MAX_HP_OFFSET = 0x88
    },
    ["Black/White"] = {
        PARTY_START = 0x02257C20,
        POKEMON_SIZE = 0x1EC,
        SPECIES_OFFSET = 0x08,
        LEVEL_OFFSET = 0x84,
        HP_OFFSET = 0x86,
        MAX_HP_OFFSET = 0x88
    },
    ["Black2/White2"] = {
        PARTY_START = 0x02256A20,
        POKEMON_SIZE = 0x1EC,
        SPECIES_OFFSET = 0x08,
        LEVEL_OFFSET = 0x84,
        HP_OFFSET = 0x86,
        MAX_HP_OFFSET = 0x88
    }
}

local NUM_SLOTS = 6 -- maximum party size

-- Determine which game is running based on config.txt
local selected
do
    local file = io.open("config.txt", "r")
    local game_name = file and file:read("*l")
    if file then file:close() end
    if game_name and GAME_CONFIGS[game_name] then
        selected = GAME_CONFIGS[game_name]
    else
        selected = GAME_CONFIGS["Diamond/Pearl"]
    end
end

local PARTY_START = selected.PARTY_START
local POKEMON_SIZE = selected.POKEMON_SIZE

-- Offsets within each Pokemon structure
local SPECIES_OFFSET = selected.SPECIES_OFFSET
local LEVEL_OFFSET = selected.LEVEL_OFFSET
local HP_OFFSET = selected.HP_OFFSET
local MAX_HP_OFFSET = selected.MAX_HP_OFFSET

-- Simple JSON encoder
local function json_encode(value)
    local t = type(value)
    if t == "table" then
        local is_array = (#value > 0)
        local items = {}
        if is_array then
            for i, v in ipairs(value) do
                items[#items+1] = json_encode(v)
            end
            return "[" .. table.concat(items, ",") .. "]"
        else
            for k, v in pairs(value) do
                items[#items+1] = string.format("%q:%s", k, json_encode(v))
            end
            return "{" .. table.concat(items, ",") .. "}"
        end
    elseif t == "string" then
        return string.format("%q", value)
    elseif t == "number" or t == "boolean" then
        return tostring(value)
    elseif t == "nil" then
        return "null"
    else
        error("Unsupported type: " .. t)
    end
end

local function read_pokemon(base)
    local species = memory.readword(base + SPECIES_OFFSET)
    local level = memory.readbyte(base + LEVEL_OFFSET)
    local hp = memory.readword(base + HP_OFFSET)
    local max_hp = memory.readword(base + MAX_HP_OFFSET)
    local fainted = hp == 0
    return {
        species = species,
        level = level,
        hp = hp,
        max_hp = max_hp,
        fainted = fainted
    }
end

local function dump_team()
    local team = {}
    for i = 0, NUM_SLOTS - 1 do
        local base = PARTY_START + i * POKEMON_SIZE
        local species = memory.readword(base + SPECIES_OFFSET)
        if species ~= 0 then
            team[#team + 1] = read_pokemon(base)
        end
    end
    local file = io.open("team_data.json", "w")
    if file then
        file:write(json_encode(team))
        file:close()
    end
end

local frame_counter = 0
while true do
    emu.frameadvance()
    frame_counter = frame_counter + 1
    if frame_counter >= 120 then  -- ~2 seconds at 60 FPS
        dump_team()
        frame_counter = 0
    end
end

