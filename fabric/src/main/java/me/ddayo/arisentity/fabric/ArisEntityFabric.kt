package me.ddayo.arisentity.fabric

import me.ddayo.aris.engine.EngineInitializer
import me.ddayo.arisentity.ArisEntity
import net.fabricmc.api.ModInitializer

class ArisEntityFabric : ModInitializer {
    override fun onInitialize() {
        // This code runs as soon as Minecraft is in a mod-load-ready state.
        // However, some things (like resources) may still be uninitialized.
        // Proceed with mild caution.

        // Run our common setup.

        ArisEntity.init()
    }
}
