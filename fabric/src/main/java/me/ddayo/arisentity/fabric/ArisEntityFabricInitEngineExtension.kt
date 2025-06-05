package me.ddayo.arisentity.fabric

import me.ddayo.aris.engine.EngineInitializer
import me.ddayo.aris.engine.InitEngine
import me.ddayo.arisentity.lua.glue.EntityInitProviderGenerated

class ArisEntityFabricInitEngineExtension: EngineInitializer<InitEngine> {
    override fun initLua(engine: InitEngine) {
        EntityInitProviderGenerated.initEngine(engine)
    }
}