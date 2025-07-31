-- DeSmuME Lua script to export party data every 2 seconds
-- Memory offsets for Pokemon Diamond/Pearl (U)

local PARTY_START = 0x02101D2C   -- start address of player's party data
local POKEMON_SIZE = 0xEC        -- size of one Pokemon data structure
local NUM_SLOTS = 6              -- maximum party size

-- Offsets within each Pokemon structure
local SPECIES_OFFSET = 0x08      -- 2 bytes
local LEVEL_OFFSET = 0x84        -- 1 byte
local HP_OFFSET = 0x86           -- 2 bytes (current HP)
local MAX_HP_OFFSET = 0x88       -- 2 bytes (max HP)

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

