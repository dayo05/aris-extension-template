package me.ddayo.arisentity.engine

import me.ddayo.aris.engine.InitEngine
import me.ddayo.aris.luagen.LuaFunction
import me.ddayo.aris.luagen.LuaProvider
import org.apache.logging.log4j.LogManager

@LuaProvider("EntityInitProviderGenerated")
object InitFunction {
    @LuaFunction(name = "test")
    fun testFunction() {
        LogManager.getLogger().info("Test")
    }
}