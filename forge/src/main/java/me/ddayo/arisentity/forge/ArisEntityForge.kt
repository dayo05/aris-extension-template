package me.ddayo.arisentity.forge

import me.ddayo.aris.forge.ArisForge
import me.ddayo.arisentity.ArisEntity
import me.ddayo.arisentity.lua.glue.EntityInitProviderGenerated
import net.minecraftforge.fml.common.Mod
import net.minecraftforge.fml.event.lifecycle.FMLConstructModEvent
import org.apache.logging.log4j.LogManager
import thedarkcolour.kotlinforforge.forge.MOD_BUS

@Mod(ArisEntity.MOD_ID)
class ArisEntityForge {
    init {
        LogManager.getLogger().info("CTOR Entity")
        ArisEntity.init()
        MOD_BUS.addListener { it: FMLConstructModEvent ->
            ArisForge.initExtensions.add {
                EntityInitProviderGenerated.initEngine(it)
            }
        }
    }
}
